import pyrebase
import pyrebase.pyrebase
import streamlit as st
import os
import json


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
    except Exception as e:
        print(e)


# Identity Aware Proxy Func
def get_client_id_for_iap():
    with open(os.path.join(os.path.dirname(__file__), "secret", "iap_config.json")) as f:
        iap_config = json.load(f)
    return iap_config["CLIENT_ID"]


def request_for_iap(url, client_id, **kwargs):
    if 'timeout' not in kwargs:
        kwargs['timeout'] = 90

    open_id_connect_token = id_token.fetch_id_token(Request(), client_id)


# Main Codes
def app(auth):
    st.title("サンプルアプリ")
    st.text("email: ")
    email = st.text_input("email", "")
    st.text("password: ")
    password = st.text_input("password", type="password")

    if st.button("login"):
        authenticate(auth=auth, email=email, password=password)


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
            authenticate(auth=auth, email=email, password=password)
        st.success("authenticate is completed!")


if __name__ == "__main__":
    main()
