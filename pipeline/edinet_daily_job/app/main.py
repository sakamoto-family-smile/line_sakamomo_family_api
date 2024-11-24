import os
from dotenv import load_dotenv
from google.cloud import bigquery
from datetime import datetime, timedelta

from edinet_wrapper import EdinetWrapper


def main(duration_days: int,
         api_key: str,
         table_id: str,
         target_date: datetime,
         force_delete_of_target_date: bool):
    # edinetから指定した日数分の有価証券報告書のリストをDataFrameで取得する
    print("start to get documents list from edinet. debug hogehoge")
    edinet = EdinetWrapper(
        api_key=api_key,
        output_folder=os.path.join(os.path.dirname(__file__), "output")
    )
    res = edinet.get_documents_list(
        duration_days=duration_days,
        target_date=target_date
    )
    df = res.df

    # 日付単位でドキュメント一覧をループし、bigqueryから該当日付のレコードを削除して、追加し直す
    # まずbigqueryのテーブルから該当日付のレコードを削除する（submitDateTimeでフィルタを行う）
    if force_delete_of_target_date:
        print("start to delete records from bigquery..")
        start_date = (target_date - timedelta(duration_days)).strftime("%Y-%m-%d")
        end_date = target_date.strftime("%Y-%m-%d")
        print(f"start date is {start_date}, end_date is {end_date}")

        client = bigquery.Client()
        where_clause = f"submitDateTime BETWEEN '{start_date}' AND '{end_date}'"
        delete_query = f"""
            DELETE FROM `{table_id}`
            WHERE {where_clause}
        """
        query_job = client.query(delete_query)
        query_job.result()

    # 次にEDINETから取得したデータをbigqueryに挿入する
    print("start to insert documents list into bigquery")
    client = bigquery.Client()
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE"
    )
    job = client.load_table_from_dataframe(
        df,
        table_id,
        job_config=job_config
    )
    job.result()


if __name__ == "__main__":
    print("--- start edinet script job ---")

    load_dotenv()
    api_key = os.environ["EDINET_API_KEY"]
    duration_days = int(os.getenv("DURATION_DAYS", 365))
    delete_flag = bool(os.getenv("DELETE_FLAG", 0))
    table_id = os.environ["TABLE_ID"]
    target_date = datetime.now()
    main(duration_days=duration_days,
         api_key=api_key,
         table_id=table_id,
         target_date=target_date,
         force_delete_of_target_date=delete_flag)

    print("--- end edinet script job ---")
