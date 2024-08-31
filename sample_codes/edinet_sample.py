import requests
import pandas as pd
from datetime import datetime
from copy import deepcopy
import urllib.request
import sys
import os


## global parameters ##
EDINET_API_KEY = "xxxx"


class DownloadResult:
    def __init__(self) -> None:
        self.__success_document_ids = []
        self.__error_document_ids = []

    def get_success_counts(self) -> int:
        return len(self.__success_document_ids)

    def get_error_counts(self) -> int:
        return len(self.__error_document_ids)

    def append_success_doc_id(self, doc_id: str):
        self.__success_document_ids.append(doc_id)

    def append_error_doc_id(self, doc_id: str):
        self.__error_document_ids.append(doc_id)

    def get_success_doc_ids(self) -> list:
        return deepcopy(self.__success_document_ids)

    def get_error_doc_ids(self) -> list:
        return deepcopy(self.__error_document_ids)


def get_documents_info_dataframe(target_date: datetime) -> pd.DataFrame:
    url = 'https://disclosure.edinet-fsa.go.jp/api/v2/documents.json'
    params = {
        'date': target_date.strftime("%Y-%m-%d"),
        'type': 2,  # 2は有価証券報告書などの決算書類
        "Subscription-Key": EDINET_API_KEY
    }
    response = requests.get(url, params=params)
    json_data = response.json()
    documents = json_data['results']
    df = pd.DataFrame(documents)
    return df


def download_document(output_folder: str, doc_id: str):
    url = f'https://api.edinet-fsa.go.jp/api/v2/documents/{doc_id}?type=5&Subscription-Key={EDINET_API_KEY}'
    print(doc['edinetCode'], doc['docID'], doc['filerName'], doc['docDescription'], doc['submitDateTime'], sep='\t')

    try:
        # ZIPファイルのダウンロード
        with urllib.request.urlopen(url) as res:
            content = res.read()
        output_path = os.path.join(output_folder, f'{doc_id}.zip')
        with open(output_path, 'wb') as file_out:
            file_out.write(content)
    except urllib.error.HTTPError as e:
        if e.code >= 400:
            sys.stderr.write(e.reason + '\n')
        else:
            raise e


if __name__ == "__main__":
    print("--- start to script ---")

    # EDINETから指定した日付の有価証券報告書のリストを取得する
    output_folder = os.path.join(os.path.dirname(__file__), "output", datetime.now().strftime("%Y%m%d%H%M%S"))
    os.makedirs(output_folder, exist_ok=True)
    df = get_documents_info_dataframe(target_date=datetime.strptime("2024-05-17", "%Y-%m-%d"))

    # doc_idから有価証券報告書をzip形式でダウンロードする
    res = DownloadResult()
    for index, doc in df.iterrows():
        doc_id = doc['docID']
        try:
            download_document(output_folder=output_folder, doc_id=doc_id)
            res.append_success_doc_id(doc_id=doc_id)
        except Exception as e:
            print(e)
            res.append_error_doc_id(doc_id=doc_id)

    # 取得結果を表示する
    print("--- download results ---")
    print(f"success count = {res.get_success_counts()}")
    print(f"error count = {res.get_error_counts()}")
