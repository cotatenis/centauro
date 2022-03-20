import pandas as pd
from typing import Optional
from credentials import credentials
def load_centauro_data() -> Optional[dict]:
    centauro = pd.read_gbq(
        query=f"SELECT * FROM `cotatenis.cotatenis.awin-centauro`",
        project_id="cotatenis",
        credentials=credentials,
        progress_bar_type="tqdm",
    )
    return {'eans' : centauro['ean'].tolist(), 'urls' : centauro['merchant_deep_link'].tolist()}
