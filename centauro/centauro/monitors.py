from spidermon import Monitor, MonitorSuite, monitors
from spidermon.contrib.actions.discord.notifiers import SendDiscordMessageSpiderFinished
from spidermon.contrib.monitors.mixins import StatsMonitorMixin
from spidermon.contrib.scrapy.monitors import FinishReasonMonitor, UnwantedHTTPCodesMonitor
from centauro.actions import CloseSpiderAction


@monitors.name("Periodic job stats monitor")
class PeriodicJobStatsMonitor(Monitor, StatsMonitorMixin):
    @monitors.name("Maximum number of errors exceeded")
    def test_number_of_errors(self):
        accepted_num_errors = 5
        num_errors = self.data.stats.get("log_count/ERROR", 0)

        msg = "The job has exceeded the maximum number of errors"
        self.assertLessEqual(num_errors, accepted_num_errors, msg=msg)

class PeriodicMonitorSuite(MonitorSuite):
    monitors = [PeriodicJobStatsMonitor]
    monitors_failed_actions = [CloseSpiderAction, SendDiscordMessageSpiderFinished]


class SpiderCloseMonitorSuite(MonitorSuite):
    monitors = [FinishReasonMonitor, UnwantedHTTPCodesMonitor, PeriodicJobStatsMonitor]

    monitors_failed_actions = [SendDiscordMessageSpiderFinished]