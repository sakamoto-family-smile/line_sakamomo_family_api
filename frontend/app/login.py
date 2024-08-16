import streamlit as st
import pyrebase.pyrebase
import os
import json
import dataclasses


@dataclasses.dataclass
class User:
    email: str
    id_token: str


class LoginHelper:
    def __init__(self) -> None:
        # Identity Platformの認証処理を行うためのインスタンスを取得
        with open(os.path.join(os.path.dirname(__file__), "secret", "config.json")) as f:
            firebase_config = json.load(f)
        app = pyrebase.pyrebase.initialize_app(config=firebase_config)
        self.__auth = app.auth()

    def login(self, email: str, password: str) -> User:
        try:
            user = self.__auth.sign_in_with_email_and_password(email, password)
            return User(email=email, id_token=user["idToken"])
        except Exception as e:
            raise IdentityPlatformException(f"Sign in Error is occured! Exception detail is {e}")


class IdentityPlatformException(Exception):
    pass
