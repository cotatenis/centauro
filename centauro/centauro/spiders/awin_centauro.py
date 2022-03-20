from scrapy import Spider

from scrapy.utils.project import get_project_settings
from centauro.items import CentauroItem
import undetected_chromedriver as uc
from scrapy import signals
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from time import sleep
from pyvirtualdisplay import Display

class CentauroSpider(Spider):
    name = 'awin_centauro'
    allowed_domains = ['centauro.com.br']
    start_urls = ["https://quotes.toscrape.com/"]
    settings = get_project_settings()
    version = settings.get("VERSION")

    def __init__(self, eans=[""], urls=[""], *args, **kwargs):
        super(CentauroSpider, self).__init__(*args, **kwargs)
        self.urls = urls
        self.eans = eans

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(CentauroSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider
    
    def spider_opened(self, spider):
        display = Display(visible=True, size=(800, 600), backend="xvfb")
        display.start()
        options = uc.ChromeOptions()
        options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
        #options.add_argument('--headless')
        self.browser = uc.Chrome(options=options)
        self.browser.set_page_load_timeout(30)
        self.wdw = WebDriverWait(self.browser, 10)
    
    def spider_closed(self, spider):
        self.browser.close()

    def parse(self, response):
        for ean, url in zip(self.eans, self.urls):
            sleep(.5)
            image_urls = []
            self.logger.info(url)
            self.browser.get(url)
            try:
                _ = self.wdw.until(EC.presence_of_element_located((By.XPATH, "//button[contains(@title, 'tamanho')]/div")))
            except (NoSuchElementException, TimeoutException):
                continue
            else:
                size_elements = self.browser.find_elements(By.XPATH, "//button[contains(@title, 'tamanho')]/div") 
                sizes = [s.text for s in size_elements]
            try:
                pictures_elements = self.wdw.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'slick-slide')]//img")))
            except (NoSuchElementException, TimeoutException):
                pictures_elements = [""]
            else:
                image_urls = [elem.get_attribute("src") for elem in pictures_elements]
            image_urls = [img.replace("120x120", "400x400") for img in image_urls]
            image_uris = [
                f"{self.settings.get('IMAGES_STORE')}{ean}_{filename.split('/')[-2]}_{filename.split('/')[-1]}"
                for filename in image_urls
            ]
            img_search_page = image_uris[0]
            try:
                breadcrumbs_elements = self.wdw.until(EC.presence_of_all_elements_located((By.XPATH, "//ul[@itemtype='http://schema.org/BreadcrumbList']//a[@itemtype='https://schema.org/WebPage']/span")))
            except (NoSuchElementException, TimeoutException):
                genre = ""
            else:
                breadcrumb_element = breadcrumbs_elements[-1] 
                genre = breadcrumb_element.text
            for size in sizes:
                payload = {
                    'ean' : ean,
                    'url' : url,
                    'genre' : genre,
                    'img_search_page' : img_search_page,
                    'image_urls' : image_urls,
                    'image_uris' : image_uris,
                    'size' : size,
                    'in_stock' : True,
                    'qty_stock' : "",
                    'spider' : self.name,
                    'spider_version' : self.version
                }
                yield CentauroItem(**payload)


            
