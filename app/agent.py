from pydantic import BaseModel
import os
import requests
from logging import Logger


class WeatherInfo(BaseModel):
    area_name: str
    temperature: float
    pressure: int
    humidity: int
    weather_detail: str


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
                weather_detail=data["main"]["description"]
            )
        else:
            raise Exception(
                f"getting weather information is failed. http status code is {response.status_code}."
            )
        return info


class Agent:
    def __init__(self, logger: Logger) -> None:
        self.__logger = logger

    def get_weather_info(self, area_name: str) -> WeatherInfo:
        info = AgentUtil.get_weather_info(area_name=area_name)
        return info
