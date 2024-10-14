import json
import os

import requests
from requests import Response


class BackendRequester:
    def __init__(self) -> None:
        with open(os.path.join(os.path.dirname(__file__), "secret", "iap_config.json")) as f:
            iap_config = json.load(f)
        self.__backend_url = iap_config["BACKEND_URL"]

    def request_health_check(self, token: str) -> dict:
        url = f"{self.__backend_url}/health"
        resp = requests.request("GET", url, headers={"Authorization": "Bearer {}".format(token)})
        if resp.status_code != 200:
            raise Exception(
                "Bad response from application: {!r} / {!r} / {!r}".format(resp.status_code, resp.headers, resp.text)
            )
        else:
            return resp.json()

    def request_bot(self, token: str, text: str) -> dict:
        return self.request_api(token=token, request_name="bot", data={"message": text}).json()

    def request_financial_document_list(self, token: str, company_name: str) -> dict:
        return self.request_api(
            token=token, request_name="financial_document_list", data={"company_name": company_name}
        ).json()

    def request_upload_financial_report(self, token: str, doc_id: str) -> dict:
        return self.request_api(token=token, request_name="upload_financial_report", data={"doc_id": doc_id}).json()

    def request_analyze_financial_document(self, token: str, analysis_type: int, gcs_uri: str, message: str) -> dict:
        return self.request_api(
            token=token,
            request_name="analyze_financial_document",
            data={"analysis_type": analysis_type, "gcs_uri": gcs_uri, "message": message},
        ).json()

    def request_download_financial_document(self, token: str, gcs_uri: str) -> bytes:
        return self.request_get(
            token=token,
            request_name="download_financial_document",
            data={"gcs_uri": gcs_uri},
            mime_type="application/json",
        ).content

    def request_api(self, token: str, request_name: str, data: dict) -> Response:
        url = f"{self.__backend_url}/{request_name}"
        resp = requests.request(
            "POST",
            url,
            data=json.dumps(data),
            headers={"Content-Type": "application/json", "Authorization": "Bearer {}".format(token)},
        )
        if resp.status_code != 200:
            raise Exception(
                "Bad response from application: {!r} / {!r} / {!r}".format(resp.status_code, resp.headers, resp.text)
            )
        else:
            return resp

    def request_get(self, token: str, request_name: str, mime_type: str, data: dict) -> Response:
        url = f"{self.__backend_url}/{request_name}"
        resp = requests.request("GET", url, params=data, headers={"Authorization": "Bearer {}".format(token)})
        if resp.status_code != 200:
            raise Exception(
                "Bad response from application: {!r} / {!r} / {!r}".format(resp.status_code, resp.headers, resp.text)
            )
        else:
            return resp
