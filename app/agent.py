from pydantic import BaseModel
import os
import requests
from logging import Logger

from langchain.agents import AgentType, initialize_agent, load_tools
from langchain_google_vertexai import VertexAI
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain_google_firestore import FirestoreChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
import uuid


class WeatherInfo(BaseModel):
    area_name: str
    temperature: float
    pressure: int
    humidity: int
    weather: str


class LLMAgentResponse(BaseModel):
    text: str


# TODO : imp
class CustomAgentConfig(BaseModel):
    pass


class AgentUtil:
    @classmethod
    def get_weather_info(cls, area_name: str) -> WeatherInfo:
        api_key = os.environ["OPEN_WEATHER_KEY"]
        base_url = "http://api.openweathermap.org/data/2.5/weather"

        # TODO : area_nameを使うように修正(Tokyo,JPのように指定する)
        params = {
            "q": "Kanagawa-ken,JP",
            "units": "metric",
            "appid": api_key
        }

        # OpenWeatherMapにリクエストを投げて、天候情報を取得
        response = requests.get(base_url, params=params)
        data = response.json()
        if response.status_code == 200:
            info = WeatherInfo(
                area_name=data["name"],
                temperature=data["main"]["temp"],
                pressure=data["main"]["pressure"],
                humidity=data["main"]["humidity"],
                weather=data["weather"][0]["main"]
            )
        else:
            raise Exception(
                f"getting weather information is failed. http status code is {response.status_code}."
            )
        return info


class CustomAgent:
    def __init__(self, logger: Logger) -> None:
        self.__logger = logger

        # LLM Agentの作成
        #llm = OpenAI(temperature=0)
        #llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-preview-0409", temperature=0.9) # gemini-pro
        # TODO : メモリ機能を追加する
        llm = VertexAI(
            model_name="gemini-1.5-pro-preview-0409",
            temperature=0.5,
            max_output_tokens=400,
            location=os.environ["GCP_LOCATION"],
            project=os.environ["GCP_PROJECT"],
        )
        os.environ["OPENWEATHERMAP_API_KEY"] = os.environ["OPEN_WEATHER_KEY"]
        tools = load_tools(["openweathermap-api"], llm)
        self.__agent = initialize_agent(
            tools=tools, llm=llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
        )
        memory = self.get_chat_message_history(
            memory_type="firestore",
            config={
                "session_id": "session_id", "collection": "HistoryMessages"
            }
        )

        # debug
        messages = memory.messages
        for message in messages:
            self.__logger.info(message)

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

    def get_llm_agent_response(self, text: str) -> LLMAgentResponse:
        self.__logger.info("start get_llm_agent_response...")
        #res = self.__agent.run(text)
        #session_id = str(uuid.uuid4())
        res = self.__agent_with_chat_history.invoke(
            {
                "input": text
            },
            config = {
                "configurable": {"session_id": "session_id"}
            })
        return LLMAgentResponse(text=res["output"])

    def get_chat_message_history(self, memory_type: str, config: dict) -> BaseChatMessageHistory:
        if memory_type == "local":
            chat_buffer = ConversationBufferMemory()
            return chat_buffer.chat_memory
        elif memory_type == "firestore":
            return FirestoreChatMessageHistory(
                session_id=config["session_id"],
                collection=config["collection"]
            )
        else:
            raise NotImplementedError(f"{memory_type} memory type is not implemented!")
