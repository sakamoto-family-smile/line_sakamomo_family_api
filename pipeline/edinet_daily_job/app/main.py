import os
from dotenv import load_dotenv
from google.cloud import bigquery

from edinet_wrapper import EdinetWrapper


def main(duration_days: int, api_key: str, table_id: str):
    # edinetから指定した日数分の有価証券報告書のリストをDataFrameで取得する
    print("start to get documents list from edinet")
    edinet = EdinetWrapper(
        api_key=api_key,
        output_folder=os.path.join(os.path.dirname(__file__), "output")
    )
    res = edinet.get_documents_list(duration_days=duration_days)
    df = res.df
    print(f"duration_days = {duration_days}")
    print(f"success days = {res.get_success_counts()}")
    print(f"error days = {res.get_error_counts()}")

    # 日付単位でドキュメント一覧をループし、bigqueryから該当日付のレコードを削除して、追加し直す
    # TODO : 現状はdataframeをそのままbigqueryのテーブルに入れるような設定となっているので修正が必要
    print("start to insert documents list into bigquery")
    client = bigquery.Client()
    job_config = bigquery.QueryJobConfig(
        write_disposition="WRITE_TRUNCATE",
        timeout_ms=3600000,
        query_parameters=[
            bigquery.ArrayQueryParameter(
                'df', 'STRUCT<...>', df.to_dict('records')
            )
        ]
    )

    # 重複を排除する条件を指定した MERGE 文
    merge_query = f"""
        MERGE `{table_id}` T
        USING (
            SELECT * FROM UNNEST(@df)
        ) S
        ON(
            T.docID = S.docID
            AND
            T.submitDateTime = S.submitDateTime
            AND
            T.docDescription = S.docDescription
            AND
            T.docInfoEditStatus = S.docInfoEditStatus
            AND
            T.issuerEdinetCode = S.issuerEdinetCode
            AND
            T.formCode = S.formCode
            AND
            T.docTypeCode = S.docTypeCode
            AND
            T.parentDocID = S.parentDocID
        )
        WHEN MATCHED THEN
            UPDATE SET ...  -- 更新するカラムを指定 (必要があれば)
        WHEN NOT MATCHED THEN
            INSERT ROW  -- 挿入するカラムを指定
    """
    query_job = client.query(merge_query, job_config=job_config)
    query_job.result()


if __name__ == "__main__":
    print("--- start edinet script job ---")

    # parser = ArgumentParser()
    # parser.add_argument("--duration_days", default=365, help="一覧取得対象の期間（日）を設定する")
    # parser.add_argument("--table_id", type=str, help="edinetのドキュメントリストのメタデータを挿入するbigqueryのテーブルID")
    # args = parser.parse_args()
    load_dotenv()
    api_key = os.environ["EDINET_API_KEY"]
    duration_days = int(os.getenv("DURATION_DAYS", 365))
    table_id = os.environ["TABLE_ID"]
    main(duration_days=duration_days, api_key=api_key, table_id=table_id)

    print("--- end edinet script job ---")
