import streamlit as st
from login import LoginHelper
from backend_util import BackendRequester


# グローバル変数
TOKEN_KEY = "authenticated"


def check_auth_key() -> bool:
    return TOKEN_KEY in st.session_state and st.session_state[TOKEN_KEY]


def login_page(placeholder):
    # ログインページ用のUIを作成
    with placeholder.container():
        st.text("email: ")
        email = st.text_input("email", "")
        st.text("password: ")
        password = st.text_input("password", type="password")
        login_button = st.button("Login")

    # ログイン処理の実施
    if login_button:
        with st.spinner("please wait for initialize.."):
            login_helper = LoginHelper()
        st.success("initialize is compeleted!")

        with st.spinner("please wait for login.."):
            user = login_helper.login(email=email, password=password)
            st.session_state[TOKEN_KEY] = user.id_token
        st.success("login is completed!")

    # トークンが取れていれば、ページをメインのページへ遷移する
    if check_auth_key():
        st.rerun()


def chat_page(placeholder):
    backend_requester = BackendRequester()

    # 一旦ダミーとして作成
    with placeholder.container():
        st.text("Main Page")
        with st.spinner("please wait for health check.."):
            backend_requester.request_health_check(token=st.session_state[TOKEN_KEY])
        st.success("health check is completed!")


def main():
    st.set_page_config(page_title='Sakamomo-Family-App',
                       page_icon=':chart_with_upwards_trend:',
                       layout='wide',
                       initial_sidebar_state="collapsed")
    placeholder = st.empty()

    # 認証済みの場合は、メインページへ
    if check_auth_key():
        chat_page(placeholder=placeholder)
    else:
        login_page(placeholder=placeholder)


if __name__ == "__main__":
    main()
