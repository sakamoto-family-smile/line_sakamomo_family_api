from logging import StreamHandler, getLogger
from typing import List
from google.cloud import bigquery
import os

from agent import CustomAgent, CustomAgentConfig
from todo_util import TodoHandler
from edinet_wrapper import EdinetWrapper


logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel("DEBUG")


class Controller:
    def __init__(self, dialogue_session_id: str, edinet_api_key: str) -> None:
        agent_config = CustomAgentConfig(
            dialogue_session_id=dialogue_session_id,
            memory_store_type="firestore"
        )
        self.__agent = CustomAgent(agent_config=agent_config)
        self.__todo_handler = TodoHandler(
            family_id=agent_config.dialogue_session_id,
            collection_id="ToDoHistory",
            custom_logger=logger
        )
        self.__output_folder = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(self.__output_folder, exist_ok=True)
        self.__edinet_wrapper = EdinetWrapper(
            api_key=edinet_api_key,
            output_folder=self.__output_folder
        )

    # TODO : 内部で例外が発生した際は例外を返すようにした方がよさそう.
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
                res = self.__agent.get_llm_agent_response(text=message).text
            except Exception as e:
                logger.error(e)
                res = "LLMのレスポンスでエラーが発生しました."
        return res

    def search_financial_documents_if_existed(self, company_name: str) -> List[dict]:
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
        return items

    def analyze_financial_document(self, doc_id: str) -> str:
        # doc_idからpdfレポートを取得。取得できない場合は例外が発火される
        file_path = self.__edinet_wrapper.download_pdf_of_financial_report(doc_id=doc_id)

        # TODO : pdfをLLMに送って、解析させる(CustomAgentか新規のAgentを用いる)
        pass
