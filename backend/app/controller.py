from logging import StreamHandler, getLogger
from typing import List
from google.cloud import bigquery
import os
from uuid import uuid4
from pydantic import BaseModel
from datetime import datetime

from agent import MainAgent, MainAgentConfig, FinancialReportAgent, FinancialAgentConfig
from todo_util import TodoHandler
from edinet_wrapper import EdinetWrapper
from gcp_util import upload_file_into_gcs


logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel("DEBUG")


class Response(BaseModel):
    request_id: str
    timestamp: datetime
    deteil: dict


class Controller:
    def __init__(self, dialogue_session_id: str) -> None:
        # MainAgentの初期化
        agent_config = MainAgentConfig(
            dialogue_session_id=dialogue_session_id,
            memory_store_type="firestore"
        )
        self.__agent = MainAgent(agent_config=agent_config)
        self.__todo_handler = TodoHandler(
            family_id=agent_config.dialogue_session_id,
            collection_id="ToDoHistory",
            custom_logger=logger
        )

        # Edinetを利用するためのラッパークラスを初期化
        self.__output_folder = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(self.__output_folder, exist_ok=True)
        self.__edinet_wrapper = EdinetWrapper(
            api_key=os.environ["EDINET_API_KEY"],
            output_folder=self.__output_folder
        )

        # 決算書を分析するためのAgentを初期化
        self.__financial_agent_config = FinancialAgentConfig()
        self.__financial_agent = FinancialReportAgent(config=self.__financial_agent_config)

    # TODO : 内部で例外が発生した際は例外を返すようにした方がよさそう.
    # TODO : Responseを返すように修正
    def handle_message(self, message: str) -> str:
        # TODOの登録、取得処理を行う
        if message.startswith("TODO"):
            try:
                res = self.__todo_handler.handle(input_text=message)
            except Exception as e:
                logger.error(e)
                res = "TODOの設定処理でエラーが発生しました."
        # LLMでの解析処理を実施
        else:
            try:
                res = self.__agent.get_llm_agent_response(input_data=message).text
            except Exception as e:
                logger.error(e)
                res = "LLMのレスポンスでエラーが発生しました."
        return res

    def search_financial_documents_if_existed(self, company_name: str) -> Response:
        request_id = uuid4()
        current_time = datetime.now()

        # 会社名から、bigqueryを検索し、有価証券報告書のリストを取得する
        client = bigquery.Client()
        items: List[dict] = []
        with open(os.path.join("sql", "search_company.sql"), "r") as f:
            query = f.read().format(company_name=company_name)
            query_job = client.query(query)
            rows = query_job.result()
            for row in rows:
                doc_id = row["docID"]
                item = {
                    "doc_id": doc_id,
                    "filer_name": row["filerName"],
                    "doc_description": row["docDescription"],
                    "doc_url": f"{self.__edinet_wrapper.get_document_url(doc_id=doc_id)}"
                }
                items.append(item)
        return Response(
            request_id=str(request_id),
            timestamp=current_time,
            deteil={
                "items": items
            }
        )

    def upload_financial_report_into_gcs(self, doc_id: str) -> Response:
        request_id = uuid4()
        current_time = datetime.now()

        # doc_idからpdfレポートを取得。取得できない場合は例外が発火される
        file_path = self.__edinet_wrapper.download_pdf_of_financial_report(doc_id=doc_id)

        # 取得したpdfを、gcsにアップロードする
        file_name = os.path.basename(file_path)
        current_time_str = current_time.strftime("%Y%m%d%H%M%S")
        gcs_file_path = f"document/{current_time_str}/{request_id}/{file_name}"
        gcs_uri = upload_file_into_gcs(project_id=os.environ["GCP_PROJECT"],
                             bucket_name=self.__financial_agent_config.log_bucket_name,
                             remote_file_path=gcs_file_path,
                             local_file_path=file_path)

        return Response(request_id=str(request_id),
                        timestamp=current_time,
                        deteil={
                            "gcs_uri": gcs_uri
                        })

    def analyze_financial_document(self, gcs_uri: str, message: str | None = None) -> Response:
        request_id = uuid4()
        current_time = datetime.now()

        # pdfをLLMに送って、解析させる(CustomAgentか新規のAgentを用いる)
        default_prompt = """
        下記に含まれる財務三表の内容を踏まえて、企業の分析を行なってください。
        """
        prompt = message if message is not None else default_prompt
        input_data = {
            "gcs_uri": gcs_uri,
            "prompt": prompt
        }
        agent_response = self.__financial_agent.get_llm_agent_response(input_data=input_data)
        return Response(request_id=str(request_id),
                        timestamp=current_time,
                        deteil={
                            "response_text": agent_response.text,
                            "prompt": prompt
                        })
