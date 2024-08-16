import os
import json
import requests


class BackendRequester:
    def __init__(self) -> None:
        with open(os.path.join(os.path.dirname(__file__), "secret", "iap_config.json")) as f:
            iap_config = json.load(f)
        self.__backend_url = iap_config["BACKEND_URL"]

    def request_health_check(self, token: str) -> dict:
        url = f"{self.__backend_url}/health"
        resp = requests.request(
            "GET", url,
            headers={'Authorization': 'Bearer {}'.format(token)})
        if resp.status_code != 200:
            raise Exception(
                'Bad response from application: {!r} / {!r} / {!r}'.format(
                    resp.status_code, resp.headers, resp.text))
        else:
            return resp.json()

    def request_bot(self, token: str, text: str) -> dict:
        url = f"{self.__backend_url}/bot"
        data = {"message": text}
        resp = requests.request(
            "POST", url,
            data=json.dumps(data),
            headers={
                "Content-Type": "application/json",
                'Authorization': 'Bearer {}'.format(token)
            }
        )
        if resp.status_code != 200:
            raise Exception(
                'Bad response from application: {!r} / {!r} / {!r}'.format(
                    resp.status_code, resp.headers, resp.text))
        else:
            return resp.json()
