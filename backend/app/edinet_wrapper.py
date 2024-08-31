"""
EDINETから有価証券報告書を取得するためのラッパークラス
詳細なAPI仕様書は下記を参照
https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html
"""

import requests
import pandas as pd
from datetime import datetime
from copy import deepcopy
import urllib.request
import sys
import os


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


class EdinetWrapper:
    def __init__(self, api_key: str, output_folder: str = None) -> None:
        self.__api_key = api_key
        self.__output_folder = os.path.join(os.path.dirname(__file__), "output", datetime.now().strftime("%Y%m%d%H%M%S")) if output_folder is None else output_folder

    def get_documents_info_dataframe(self, target_date: datetime) -> pd.DataFrame:
        url = 'https://disclosure.edinet-fsa.go.jp/api/v2/documents.json'
        params = {
            'date': target_date.strftime("%Y-%m-%d"),
            'type': 2,  # 2は有価証券報告書などの決算書類
            "Subscription-Key": self.__api_key
        }
        response = requests.get(url, params=params)
        json_data = response.json()
        documents = json_data['results']
        df = pd.DataFrame(documents)
        return df

    def download_pdf_of_financial_report(self, doc_id: str):
        url = f'https://api.edinet-fsa.go.jp/api/v2/documents/{doc_id}'
        params = {
            "type": 2,  # PDFを取得する場合は2を指定
            "Subscription-Key": self.__api_key
        }

        try:
            res = requests.get(url, params=params, verify=False)
            output_path = os.path.join(self.__output_folder, f'{doc_id}.pdf')
            if res.status_code != 200:
                raise Exception(f"status code is {res.status_code}")

            with open(output_path, 'wb') as file_out:
                file_out.write(res.content)
        except urllib.error.HTTPError as e:
            if e.code >= 400:
                sys.stderr.write(e.reason + '\n')
            else:
                raise e

    def download_pdfs_of_financial_report_target_date(self, target_date: datetime) -> DownloadResult:
        # EDINETから指定した日付の有価証券報告書のリストを取得する
        df = self.get_documents_info_dataframe(target_date=target_date)

        # 有価証券報告書を指定したフォルダにダウンロードする
        res = DownloadResult()
        for _, doc in df.iterrows():
            print(doc['edinetCode'], doc['docID'], doc['filerName'], doc['docDescription'], doc['submitDateTime'], sep='\t')
            doc_id = doc['docID']

            try:
                self.download_pdf_of_financial_report(doc_id=doc_id)
                res.append_success_doc_id(doc_id=doc_id)
            except Exception as e:
                print(e)
                res.append_error_doc_id(doc_id=doc_id)

        return res
