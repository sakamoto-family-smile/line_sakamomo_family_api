import pyrebase
import pyrebase.pyrebase
import streamlit as st
import os
import json


def load_firebase_auth():
    with open(os.path.join("secret", "config.json")) as f:
        firebase_config = json.load(f)
    app = pyrebase.pyrebase.initialize_app(config=firebase_config)
    return app.auth()


def authenticate(auth, email: str, password: str):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        print(user)
    except Exception as e:
        print(e)


def app(auth):
    st.title("サンプルアプリ")
    st.text("email: ")
    email = st.text_input("email", "")
    st.text("password: ")
    password = st.text_input("password", type="password")

    if st.button("login"):
        authenticate(auth=auth, email=email, password=password)


def main():
    auth = load_firebase_auth()
    app(auth=auth)
