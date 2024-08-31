import requests
#import pandas as pd
from datetime import datetime


## global parameters ##
EDINET_API_KEY = "xxxx"


def get_documents(target_date: datetime) -> dict:
    url = 'https://disclosure.edinet-fsa.go.jp/api/v2/documents.json'
    params = {
        'date': target_date.strftime("%Y-%m-%d"),
        'type': 2,  # 2は有価証券報告書などの決算書類
        "Subscription-Key": EDINET_API_KEY
    }
    response = requests.get(url, params=params)
    return response.json()


if __name__ == "__main__":
    documents = get_documents(target_date=datetime.strptime("2024-05-17", "%Y-%m-%d"))
    print(documents)
