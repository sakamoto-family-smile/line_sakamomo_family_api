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


def app():
    st.title("サンプルアプリ")
    st.text("email: ")
    st.text_input("email", "")
    st.text("password: ")
    st.text_input("password", type="password")

    if st.button("login"):
        st.write("hoge")


def main():
    load_firebase_auth()
    app()
