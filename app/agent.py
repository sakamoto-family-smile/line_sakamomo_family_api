from pydantic import BaseModel
import os
import requests
from logging import Logger

from langchain.agents import AgentType, initialize_agent, load_tools
from langchain_openai import OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_vertexai import VertexAI


class WeatherInfo(BaseModel):
    area_name: str
    temperature: float
    pressure: int
    humidity: int
    weather: str


class LLMAgentResponse(BaseModel):
    text: str


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

        # OpenAI Agentの作成
        #llm = OpenAI(temperature=0)
        #llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-preview-0409", temperature=0.9) # gemini-pro
        llm = VertexAI(
            model_name="gemini-1.5-pro-preview-0409",
            temperature=0.5,
            max_output_tokens=400,
            location=os.environ["GCP_LOCATION"],
            project=os.environ["GCP_PROJECT"],
        )
        os.environ["OPENWEATHERMAP_API_KEY"] = os.environ["OPEN_WEATHER_KEY"]
        tools = load_tools(["openweathermap-api"], llm)
        self.__openai_agent = initialize_agent(
            tools=tools, llm=llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
        )

    def get_weather_info(self, area_name: str) -> WeatherInfo:
        info = AgentUtil.get_weather_info(area_name=area_name)
        return info

    def get_llm_agent_response(self, text: str) -> LLMAgentResponse:
        res = self.__openai_agent.run(text)
        return LLMAgentResponse(text=res)
