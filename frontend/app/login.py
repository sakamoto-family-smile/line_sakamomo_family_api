import streamlit as st
import pyrebase.pyrebase
import os
import json


# Identity Platform Func
def load_firebase_auth():
    with open(os.path.join(os.path.dirname(__file__), "secret", "config.json")) as f:
        firebase_config = json.load(f)
    app = pyrebase.pyrebase.initialize_app(config=firebase_config)
    return app.auth()


def sign_in_user(auth, email: str, password: str):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return user
    except Exception as e:
        raise IdentityPlatformException(f"Sign in Error is occured! Exception detail is {e}")


class IdentityPlatformException(Exception):
    pass


def main():
    pass


if __name__ == "__main__":
    main()
