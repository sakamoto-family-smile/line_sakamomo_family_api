from datetime import datetime
from logging import Logger, StreamHandler, getLogger
from typing import List

from pydantic import BaseModel

from .firebase_util import get_db_client_with_default_credentials

local_logger = getLogger(__name__)
local_logger.addHandler(StreamHandler())
local_logger.setLevel("DEBUG")


class TodoData(BaseModel):
    date: datetime
    content: str


class TodoHandler:
    def __init__(self, collection_id: str, document_id: str, custom_logger: Logger = None) -> None:
        self.collection_id = collection_id
        self.document_id = document_id
        self.logger = custom_logger if custom_logger is not None else local_logger
        self.db = get_db_client_with_default_credentials()

    def handle(self, input_text: str) -> str:
        # TODO情報かを判別する
        datas = input_text.split()
        if len(datas) == 1:
            raise TodoHandleError(f"input text format is invalid! text is {input_text}")

        if datas[0] != "TODO":
            raise TodoHandleError(f"input text format is invalid! head text data is not 'TODO'. text is {input_text}")

        # TODOに関する処理を実施
        if len(datas) == 2:
            # TODO一覧の取得処理
            target_date = datetime.strptime(datas[1], "%Y%m%d")
            self.get_todo_list_from_text(target_date=target_date)
        elif len(datas) == 3:
            # TODOの登録処理
            target_date = datetime.strptime(datas[1], "%Y%m%d")
            content = datas[2]
            self.register_todo_from_text(target_date=target_date, content=content)

    def register_todo_from_text(self, target_date: datetime, content: str):
        """文字列からTODOの内容と日付情報を取得する.

        Args:
            target_date (datetime): 日付情報
            content (str): 登録するTODO情報

        Raises:
            TodoRegisterationError: _description_
        """
        self.logger.info(f"start to register the todo. target_date is {target_date}, content is {content}")

        # 日付情報とTODO情報をデータベースに登録
        data = {"date": target_date, "content": content}
        try:
            self.db.collection(self.collection_id).document(self.document_id).set(data)
        except Exception as e:
            self.logger.error(e)
            raise TodoRegisterationError(f"inserting data into db is error! error detail is {e}")

    def get_todo_list_from_text(self, target_date: datetime) -> List[TodoData]:
        self.logger.info(f"start to get the todo list. target_date is {target_date}")

        # 日付情報から、TODO一覧を取得
        # TODO : 取得する際に日付でフィルタをするようにしたい。そして、かなり遅い取り方になっている
        try:
            documents = self.db.collection(self.collection_id).document(self.document_id).collections()
            res = []
            for document in documents:
                d = document.to_dict()
                res.append(TodoData(date=d["date"], content=d["content"]))
            return res
        except Exception as e:
            self.logger.error(e)
            raise TodoRegisterationError(f"getting data from db is error! error detail is {e}")


class TodoHandleError(Exception):
    pass


class TodoRegisterationError(Exception):
    pass


class TodoListError(Exception):
    pass
