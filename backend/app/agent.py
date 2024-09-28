import os
from datetime import datetime
from logging import Logger, StreamHandler, getLogger
from typing import List, Optional, Type
from abc import abstractmethod, ABC
import json
from collections.abc import Iterable

import google.cloud.firestore
import requests
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.memory import ConversationBufferMemory
from langchain.tools.base import BaseTool
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_google_firestore import FirestoreChatMessageHistory
from langchain_google_vertexai import VertexAI
from pydantic import BaseModel

import vertexai
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig, GenerationResponse
from proto.marshal.collections import RepeatedComposite
from google.cloud import storage

from .firebase_util import get_db_client_with_default_credentials

local_logger = getLogger(__name__)
local_logger.addHandler(StreamHandler())
local_logger.setLevel("DEBUG")


class WeatherInfo(BaseModel):
    area_name: str
    temperature: float
    pressure: int
    humidity: int
    weather: str


class LLMAgentResponse(BaseModel):
    text: str
    metadata: dict


class MainAgentConfig(BaseModel):
    dialogue_session_id: str
    memory_store_type: str = "firestore"
    debug_mode: bool = False


class FinancialAgentConfig(BaseModel):
    llm_model_name: str = "gemini-1.5-flash"
    temperature: int = 0
    log_bucket_name: str = "sakamomo_family_api"
    log_base_folder: str = "log"
    debug_mode: bool = False


class AgentUtil:
    @classmethod
    def get_weather_info(cls, area_name: str) -> WeatherInfo:
        api_key = os.environ["OPEN_WEATHER_KEY"]
        base_url = "http://api.openweathermap.org/data/2.5/weather"

        # TODO : area_nameを使うように修正(Tokyo,JPのように指定する)
        params = {"q": "Kanagawa-ken,JP", "units": "metric", "appid": api_key}

        # OpenWeatherMapにリクエストを投げて、天候情報を取得
        response = requests.get(base_url, params=params)
        data = response.json()
        if response.status_code == 200:
            info = WeatherInfo(
                area_name=data["name"],
                temperature=data["main"]["temp"],
                pressure=data["main"]["pressure"],
                humidity=data["main"]["humidity"],
                weather=data["weather"][0]["main"],
            )
        else:
            raise Exception(f"getting weather information is failed. http status code is {response.status_code}.")
        return info


class AbstractAgent(ABC):
    @abstractmethod
    def get_llm_agent_response(self, input_data: dict) -> LLMAgentResponse:
        pass


class MainAgent(AbstractAgent):
    def __init__(self, agent_config: MainAgentConfig, logger: Logger = None) -> None:
        self.__agent_config = agent_config
        self.__logger = logger if logger is not None else local_logger

        # LLM Agentの作成
        llm = VertexAI(
            model_name=os.environ.get("LLM_MODEL_NAME", "gemini-1.5-pro-preview-0409"),
            temperature=0.5,
            max_output_tokens=400,
            location=os.environ["GCP_LOCATION"],
            project=os.environ["GCP_PROJECT"],
        )
        os.environ["OPENWEATHERMAP_API_KEY"] = os.environ["OPEN_WEATHER_KEY"]
        tools = self.get_tools(llm=llm)
        self.__agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=True,
        )
        memory = self.get_chat_message_history(
            memory_type=self.__agent_config.memory_store_type,
            config={
                "session_id": self.__agent_config.dialogue_session_id,
                "collection": "HistoryMessages",
            },
        )

        # デバッグ用に過去履歴のメッセージを出力する
        if self.__agent_config.debug_mode:
            for i, message in enumerate(memory.messages):
                print(f"{i} : id={message.id}, name={message.name}, message={message.content}, add_kwargs={message.additional_kwargs}, metadata={message.response_metadata}")

        self.__agent_with_chat_history = RunnableWithMessageHistory(
            self.__agent,
            # This is needed because in most real world scenarios, a session id is needed
            # It isn't really used here because we are using a simple in memory ChatMessageHistory
            lambda session_id: memory,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

    def get_weather_info(self, area_name: str) -> WeatherInfo:
        info = AgentUtil.get_weather_info(area_name=area_name)
        return info

    def get_llm_agent_response(self, input_data: str) -> LLMAgentResponse:
        self.__logger.info("start get_llm_agent_response...")
        res = self.__agent_with_chat_history.invoke(
            {"input": input_data},
            config={"configurable": {"session_id": self.__agent_config.dialogue_session_id}},
        )
        return LLMAgentResponse(text=res["output"], metadata={})

    def get_chat_message_history(self, memory_type: str, config: dict) -> BaseChatMessageHistory:
        if memory_type == "local":
            chat_buffer = ConversationBufferMemory()
            return chat_buffer.chat_memory
        elif memory_type == "firestore":
            return FirestoreChatMessageHistory(session_id=config["session_id"], collection=config["collection"])
        else:
            raise NotImplementedError(f"{memory_type} memory type is not implemented!")

    def get_tools(self, llm) -> List[BaseTool]:
        tools = load_tools(["openweathermap-api", "google-search"], llm)
        # tools.append(TodoRegisterTool(
        #    document_id=self.__agent_config.dialogue_session_id,
        #    logger=self.__logger
        # ))
        return tools


# TODO : request_idをcontroller側のみで意識できるようにログのアップロード周りはcontroller側で実施した方が良いかもしれない
class FinancialReportAgent(AbstractAgent):
    def __init__(self, config: FinancialAgentConfig) -> None:
        super().__init__()

        vertexai.init(
            project=os.environ["GCP_PROJECT"],
            location=os.environ["GCP_LOCATION"]
        )
        self.__model = GenerativeModel(model_name=config.llm_model_name)
        self.__config = config
        self.__generation_config = GenerationConfig(
            temperature=config.temperature
        )
        self.__work_folder = os.path.join(os.path.dirname(__file__), "work")
        os.makedirs(self.__work_folder, exist_ok=True)

    def get_llm_agent_response(self, input_data: dict) -> LLMAgentResponse:
        # gcs uriからpdfデータを取得
        # TODO : 将来的に複数のデータタイプに対応させてもよさそう
        gcs_uri = input_data["gcs_uri"]
        prompt = input_data["prompt"]
        file_data = Part.from_uri(uri=gcs_uri, mime_type="application/pdf")

        # LLMを利用した解析処理を実施
        contents = [file_data, prompt]
        response = self.__model.generate_content(contents=contents,
                                                 generation_config=self.__generation_config)

        # 解析結果含めて、ログとして出力
        self.__upload_llm_log(response=response,
                              request_id=input_data["request_id"],
                              prompt=prompt,
                              timestamp=input_data["timestamp"],
                              gcs_uri=gcs_uri)

        # 解析結果を返す
        return LLMAgentResponse(text=response.text, metadata={})

    # TODO : リファクタリングする（内部関数とかをutilとかに切り出す）
    def __upload_llm_log(self,
                         response: GenerationResponse | Iterable[GenerationResponse],
                         request_id: str,
                         prompt: str,
                         timestamp: datetime,
                         gcs_uri: str):
        # citation_metadataオブジェクトをリストに変換する
        def repeated_citations_to_list(citations: RepeatedComposite) -> list:
            citation_li = []
            for citation in citations:
                citation_dict = {}
                citation_dict["startIndex"] = citation.startIndex
                citation_dict["endIndex"] = citation.endIndex
                citation_dict["uri"] = citation.uri
                citation_dict["title"] = citation.title
                citation_dict["license"] = citation.license
                citation_dict["publicationDate"] = citation.publicationDate
                citation_li.append(citation_dict)
            return citation_li

        # safety_ratingsオブジェクトをリストに変換する
        def repeated_safety_ratings_to_list(safety_ratings: RepeatedComposite) -> list:
            safety_rating_li = []
            for safety_rating in safety_ratings:
                safety_rating_dict = {}
                safety_rating_dict["category"] = safety_rating.category.name
                safety_rating_dict["probability"] = safety_rating.probability.name
                safety_rating_li.append(safety_rating_dict)
            return safety_rating_li

        # llmのログをローカルに生成
        llm_log_data = {
            "input": {
                "input_datas": [],
                "prompt": prompt,
                "model_name": self.__config.llm_model_name,
                "llm_config": {
                    "temperature": self.__config.temperature
                },
                "prompt_token_count": response._raw_response.usage_metadata.prompt_token_count,
                "gcs_uri": gcs_uri
            },
            "output": {
                "text": response.candidates[0].text,
                "finish_reason": response.candidates[0].finish_reason.name,
                "finish_message": response.candidates[0].finish_message,
                "safety_ratings": repeated_safety_ratings_to_list(response.candidates[0].safety_ratings),
                "citation_metadata": repeated_citations_to_list(response.candidates[0].citation_metadata.citations),
                "candidates_token_count": response._raw_response.usage_metadata.candidates_token_count,
                "total_token_count": response._raw_response.usage_metadata.total_token_count
            },
            "meta": {
                "timestamp": timestamp.strftime("%Y%m%d%H%M%S"),
                "request_id": request_id
            }
        }
        tmp_log_file = os.path.join(self.__work_folder, "tmp_log.json")
        with open(tmp_log_file, "w") as f:
            json.dump(llm_log_data, f, ensure_ascii=False)

        # ログをGCSにアップロードする
        try:
            storage_client = storage.Client(project=os.environ["GCP_PROJECT"])
            datetime_str = timestamp.strftime("%Y%m%d%H%M%S")
            bucket = storage_client.bucket(self.__config.log_bucket_name)
            blob = bucket.blob(f"{self.__config.log_base_folder}/{datetime_str}/{request_id}/llm_log.json")
            blob.upload_from_filename(tmp_log_file, if_generation_match=0)
        except Exception as e:
            print(e)
            raise Exception(e)
        finally:
            os.remove(tmp_log_file)
