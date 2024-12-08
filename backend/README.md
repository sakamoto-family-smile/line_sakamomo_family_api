# SAKAMOMO FAMILY SERVICE BACKEND

サービスのバックエンド部分（APIなど）のコードをまとめています

## セットアップ

### 環境変数の設定

.envファイルを作成し、下記の内容を記載してください.<br>

```
GOOGLE_CLOUD_PROJECT=xxx
LINE_CHANNEL_ACCESS_TOKEN=xxx
LINE_CHANNEL_SECRET=xxx
OPEN_WEATHER_KEY=xxx
OPENAI_API_KEY=xx
GOOGLE_API_KEY=xx
LANGCHAIN_API_KEY=xx
GOOGLE_CSE_ID=xx
LLM_MODEL_NAME=xx
EDINET_API_KEY=xx
```

各定数の詳細については下記に記載します.
| 定数名 | 概要 |
| ---- | ---- |
| GOOGLE_CLOUD_PROJECT |  |
| LINE_CHANNEL_ACCESS_TOKEN | |
| LINE_CHANNEL_SECRET | |
| OPEN_WEATHER_KEY | |
| OPENAI_API_KEY | |
| GOOGLE_API_KEY | |
| LANGCHAIN_API_KEY | |
| GOOGLE_CSE_ID | |
| LLM_MODEL_NAME | |
| EDINET_API_KEY | |

### 環境のセットアップ

描きコマンドを実行して、gcrへのpushするためのセットアップを行います.

```bash
$ make setup
```

## ビルド

下記のコマンドを実行して、docker imageを構築し、gcrへプッシュします.

```bash
$ make build
$ make push_image
```

## デプロイ

下記のコマンドを実行して、cloudrunにgcrにpushしたdocker imageをデプロイします.

```bash
$ make deploy_run
```
