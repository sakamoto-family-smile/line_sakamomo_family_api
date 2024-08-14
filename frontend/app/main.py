import pyrebase
import pyrebase.pyrebase
import streamlit as st
import os
import json

from google.auth.transport.requests import Request
from google.oauth2 import id_token
import requests


# Identity Platform Func
def load_firebase_auth():
    with open(os.path.join(os.path.dirname(__file__), "secret", "config.json")) as f:
        firebase_config = json.load(f)
    app = pyrebase.pyrebase.initialize_app(config=firebase_config)
    return app.auth()


def authenticate(auth, email: str, password: str):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        print(user)
        return user
    except Exception as e:
        print(e)


# Identity Aware Proxy Func
def get_client_id_for_iap():
    with open(os.path.join(os.path.dirname(__file__), "secret", "iap_config.json")) as f:
        iap_config = json.load(f)
    return iap_config["CLIENT_ID"]


def get_backend_url():
    with open(os.path.join(os.path.dirname(__file__), "secret", "iap_config.json")) as f:
        iap_config = json.load(f)
    return iap_config["BACKEND_URL"]


def request_for_iap(url, client_id, **kwargs):
    if 'timeout' not in kwargs:
        kwargs['timeout'] = 90

    open_id_connect_token = id_token.fetch_id_token(Request(), client_id)
    resp = requests.request(
        "GET", url,
        headers={'Authorization': 'Bearer {}'.format(
            open_id_connect_token)}, **kwargs)
    if resp.status_code == 403:
        raise Exception('Service account does not have permission to '
                        'access the IAP-protected application.')
    elif resp.status_code != 200:
        raise Exception(
            'Bad response from application: {!r} / {!r} / {!r}'.format(
                resp.status_code, resp.headers, resp.text))
    else:
        return resp.json()


def request_for_backend(url: str, token: str):
    resp = requests.request(
        "GET", url,
        headers={'Authorization': 'Bearer {}'.format(token)})
    if resp.status_code == 403:
        raise Exception(
            'Bad response from application: {!r} / {!r} / {!r}'.format(
                resp.status_code, resp.headers, resp.text))
        #raise Exception('Service account does not have permission to '
        #                'access the IAP-protected application.')
    elif resp.status_code != 200:
        raise Exception(
            'Bad response from application: {!r} / {!r} / {!r}'.format(
                resp.status_code, resp.headers, resp.text))
    else:
        return resp.json()


# Main Codes
def main():
    st.title("サンプルアプリ")
    st.text("email: ")
    email = st.text_input("email", "")
    st.text("password: ")
    password = st.text_input("password", type="password")

    if st.button("login"):
        if st.spinner("please wait for initialize.."):
            auth = load_firebase_auth()
        st.success("initialize is compeleted!")

        if st.spinner("please wait for authenticate.."):
            user = authenticate(auth=auth, email=email, password=password)

        # debug
        st.json(user)
        id_token = user["idToken"]
        st.write(f"user token is {id_token}")
        st.success("authenticate is completed!")

        if st.spinner("please wait for iap connection.."):
            client_id = get_client_id_for_iap()
        st.write(f"client_id is {client_id}")
        st.success("getting client id is completed!")

        if st.spinner("please wait for request backend.."):
            backend_url = get_backend_url()
            health_url = f"{backend_url}/health"
            # res = request_for_iap(url=health_url, client_id=client_id)
            res = request_for_backend(url=health_url, token=user["idToken"])

        # debug
        st.success(res)


if __name__ == "__main__":
    main()
