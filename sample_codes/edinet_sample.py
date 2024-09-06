import requests
import pandas as pd
from datetime import datetime, timedelta
from copy import deepcopy
import urllib.request
import sys
import os
from argparse import ArgumentParser
from enum import Enum




class Mode(Enum):
    DOWNLOAD_DOCUMENTS = 0
    DOCUMENTS_LIST = 1


class DownloadDocumentsResult:
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


class GetDocumentListResult:
    def __init__(self) -> None:
        self.df: pd.DataFrame
        self.__success_dates = []
        self.__error_dates = []

    def get_success_counts(self) -> int:
        return len(self.__success_dates)

    def get_error_counts(self) -> int:
        return len(self.__error_dates)

    def append_success_date(self, d: datetime):
        self.__success_dates.append(d)

    def append_error_date(self, d: datetime):
        self.__error_dates.append(d)

    def get_success_dates(self) -> list:
        return deepcopy(self.__success_dates)

    def get_error_dates(self) -> list:
        return deepcopy(self.__error_dates)


def get_documents_info_dataframe(target_date: datetime) -> pd.DataFrame:
    url = 'https://disclosure.edinet-fsa.go.jp/api/v2/documents.json'
    params = {
        'date': target_date.strftime("%Y-%m-%d"),
        'type': 2,  # 2は有価証券報告書などの決算書類
        "Subscription-Key": EDINET_API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"failed to get document list! http status code is {response.status_code}")

    json_data = response.json()
    status_code = int(json_data["metadata"]["status"])
    if status_code != 200:
        raise Exception(f"failed to get document list! status code is {status_code}")

    documents = json_data['results']
    df = pd.DataFrame(documents)
    return df


def download_document(output_folder: str, doc_id: str):
    url = f'https://api.edinet-fsa.go.jp/api/v2/documents/{doc_id}'
    params = {
        "type": 2,
        "Subscription-Key": EDINET_API_KEY
    }

    try:
        res = requests.get(url, params=params, verify=False)
        output_path = os.path.join(output_folder, f'{doc_id}.pdf')
        if res.status_code != 200:
            raise Exception(f"status code is {res.status_code}")

        with open(output_path, 'wb') as file_out:
            file_out.write(res.content)
    except urllib.error.HTTPError as e:
        if e.code >= 400:
            sys.stderr.write(e.reason + '\n')
        else:
            raise e


def download_documents(output_folder: str, target_date: datetime) -> DownloadDocumentsResult:
    df = get_documents_info_dataframe(target_date=target_date)
    df.to_csv(os.path.join(output_folder, "documents.csv"))

    # doc_idから有価証券報告書をzip形式でダウンロードする
    res = DownloadDocumentsResult()
    for _, doc in df.iterrows():
        print(doc['edinetCode'], doc['docID'], doc['filerName'], doc['docDescription'], doc['submitDateTime'], sep='\t')
        doc_id = doc['docID']
        try:
            download_document(output_folder=output_folder, doc_id=doc_id)
            res.append_success_doc_id(doc_id=doc_id)
        except Exception as e:
            print(e)
            res.append_error_doc_id(doc_id=doc_id)
    return res


def get_documents_list(duration_days: int) -> GetDocumentListResult:
    current_date = datetime.now()
    dfs = []
    res = GetDocumentListResult()
    for day in range(duration_days):
        target_date = current_date - timedelta(days=day)
        print(target_date.strftime("%Y-%m-%d"))

        try:
            df = get_documents_info_dataframe(target_date=target_date)
            dfs.append(df)
            res.append_success_date(target_date)
        except Exception as e:
            print(f"failed to get document list. error detail is {e}.")
            res.append_error_date(target_date)
            continue
    df = pd.concat(dfs, ignore_index=True)
    res.df = df
    return res


if __name__ == "__main__":
    print("--- start to script ---")

    parser = ArgumentParser()
    parser.add_argument("mode")
    parser.add_argument("--target_date", type=str, help="ドキュメント一覧を取得する際の日付情報. YYYY-MM-DDの文字列で記載")
    parser.add_argument("--duration_days", type=int, help="ドキュメント一覧情報を取得する際の期間を指定。最新日付から逆算した期間を日単位で指定")
    args = parser.parse_args()
    output_folder = os.path.join(os.path.dirname(__file__), "output", datetime.now().strftime("%Y%m%d%H%M%S"))
    os.makedirs(output_folder, exist_ok=True)

    mode = int(args.mode)
    if mode == Mode.DOWNLOAD_DOCUMENTS.value:
        # EDINETから指定した日付の有価証券報告書のリストを取得する
        target_date_str = args.target_date
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d")
        res = download_documents(output_folder=output_folder, target_date=target_date)

        # 取得結果を表示する
        print("--- document download results ---")
        print(f"target date = {target_date_str}")
        print(f"success count = {res.get_success_counts()}")
        print(f"error count = {res.get_error_counts()}")

    elif mode == Mode.DOCUMENTS_LIST.value:
        # EDINETからドキュメント一覧を、本日から逆算して、指定した日数分取得する
        # ドキュメントのpdfはダウンロードしない
        duration_days = int(args.duration_days)
        res = get_documents_list(duration_days=duration_days)
        df = res.df
        df.to_csv(os.path.join(output_folder, "documents.csv"), index=False)

        # 取得結果を表示する
        print("--- document list results ---")
        print(f"duration days = {duration_days}")
        print(f"document count is {len(df)}")
        print("detail is the following..")
        print(df)
    else:
        raise Exception(f"{args.mode} mode  is not implemented!")
