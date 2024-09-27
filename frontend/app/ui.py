import streamlit as st
from dataclasses import dataclass
import os

from login import LoginHelper
from backend_util import BackendRequester


# グローバル変数
TOKEN_KEY = "authenticated"
CHAT_HISTORY = "CHAT_MESSAGES"


@dataclass
class ChatMessage:
    role: str
    content: str


def check_auth_key() -> bool:
    return TOKEN_KEY in st.session_state and st.session_state[TOKEN_KEY]


def login_page(placeholder):
    # ログインページ用のUIを作成
    with placeholder.container():
        st.title("Login Page")
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


@st.dialog("Token Expired!")
def expired_token_dialogue():
    st.write("token is expired! please relogin!")
    if st.button("OK"):
        del st.session_state[TOKEN_KEY]
        st.rerun()


def chat_page():
    backend_requester = BackendRequester()

    # チャット画面の構築
    st.title("Chat Bot")

    # apiが使えるかをチェックしておく
    with st.spinner("please wait for health check.."):
        try:
            backend_requester.request_health_check(token=st.session_state[TOKEN_KEY])
        except Exception as e:
            print(e)

            # tokenの更新が必要と判断し、token情報を削除して、画面をリロードする
            expired_token_dialogue()

    # チャット画面を作成する
    chat_widget()


def chat_widget():
    # チャット履歴の情報がなければ、初期化する
    if CHAT_HISTORY not in st.session_state:
        st.session_state[CHAT_HISTORY] = []

    # チャット一覧と入力ボックスの位置調整のために、container上にチャット一覧を表示する
    chat_container = st.container()

    # チャット履歴を全て表示する
    for message in st.session_state[CHAT_HISTORY]:
        with chat_container.chat_message(message.role):
            st.markdown(message.content)

    # ユーザーのメッセージ入力処理
    if user_message := st.chat_input("メッセージを入力してね"):
        # ユーザーの入力結果を画面に追加
        with chat_container.chat_message("user"):
            st.markdown(user_message)

        # ユーザの入力をチャット履歴に追加する
        st.session_state[CHAT_HISTORY].append(ChatMessage(role="user", content=user_message))

        # バックエンドのAPIにリクエストを投げて、待機
        with st.spinner("please wait for AI response.."):
            backend_requester = BackendRequester()
            res = backend_requester.request_bot(token=st.session_state[TOKEN_KEY], text=str(user_message))

        # APIの結果を画面と履歴に出力
        ai_message = res["message"]
        with chat_container.chat_message("ai"):
            st.markdown(ai_message)
        st.session_state[CHAT_HISTORY].append(ChatMessage(role="ai", content=ai_message))


def financial_report_analysis_page():
    backend_requester = BackendRequester()

    # 決算書を分析するページの作成
    st.title("Analysis Financial Report")

    # apiが使えるかをチェックしておく
    with st.spinner("please wait for health check.."):
        try:
            backend_requester.request_health_check(token=st.session_state[TOKEN_KEY])
        except Exception as e:
            print(e)

            # tokenの更新が必要と判断し、token情報を削除して、画面をリロードする
            expired_token_dialogue()

    # 決算書を分析するためのUIを作成
    financial_report_analysis_widget()


def financial_report_analysis_widget():
    company_name = st.text_input(label="企業名")
    search_btn = st.button(label="検索")
    if search_btn:
        backend_requester = BackendRequester()

        with st.spinner("please wait to search the financial report.."):
            res = backend_requester.request_financial_document_list(
                token=st.session_state[TOKEN_KEY],
                company_name=company_name
            )
        st.text(res)


def main_page(placeholder):
    chat_tab, financial_report_analysis_tab = st.tabs(["チャット", "決算書分析"])

    with placeholder.container():
        with chat_tab:
            chat_page()
        with financial_report_analysis_tab:
            financial_report_analysis_page()


def main():
    st.set_page_config(page_title='Sakamomo-Family-App',
                       page_icon=':chart_with_upwards_trend:',
                       layout='wide',
                       initial_sidebar_state="collapsed")
    placeholder = st.empty()

    # 認証済みの場合は、メインページへ
    if check_auth_key():
        main_page(placeholder=placeholder)
    else:
        login_page(placeholder=placeholder)


if __name__ == "__main__":
    main()
