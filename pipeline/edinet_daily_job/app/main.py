from argparse import ArgumentParser
import os
from dotenv import load_dotenv
from google.cloud import bigquery

from .edinet_wrapper import EdinetWrapper


def main(table_id: str, duration_days: int):
    # edinetから指定した日数分の有価証券報告書のリストをDataFrameで取得する
    print("start to get documents list from edinet")
    load_dotenv()
    edinet = EdinetWrapper(
        api_key=os.environ["EDINET_API_KEY"],
        output_folder=os.path.join(os.path.dirname(__file__), "output")
    )
    res = edinet.get_documents_list(duration_days=duration_days)
    df = res.df
    print(f"duration_days = {duration_days}")
    print(f"success days = {res.get_success_counts()}")
    print(f"error days = {res.get_error_counts()}")

    # 日付単位でドキュメント一覧をループし、bigqueryから該当日付のレコードを削除して、追加し直す
    print("start to insert documents list into bigquery")
    client = bigquery.Client()
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE"
    )
    job = client.load_table_from_dataframe(
        df, table_id, job_config=job_config
    )
    job.result()


if __name__ == "__main__":
    print("--- start edinet script job ---")

    parser = ArgumentParser()
    parser.add_argument("--duration_days", default=365, help="一覧取得対象の期間（日）を設定する")
    parser.add_argument("--table_id", type=str, help="edinetのドキュメントリストのメタデータを挿入するbigqueryのテーブルID")
    args = parser.parse_args()
    main(table_id=args.table_id, duration_days=int(args.duration_days))

    print("--- end edinet script job ---")
