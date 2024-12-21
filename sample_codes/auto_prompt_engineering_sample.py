"""
このサンプルコードは、Auto Prompt Enginneringを有価証券報告書の分析に対して、
検証してみたものとなります.
一般的なフレームワークを利用していないため、今後はフレームワークを試しに利用してみたいと考えています.

下記の4つのLLMコンポーネントを用いて、プロンプトを再生成しています。
- Generator
    - 有価証券報告書の分析結果を生成
- Evaluator
    - 有価証券報告書の分析結果が妥当かを評価
- Rewriter
    - 分析結果から、Generatorのプロンプトを書き換える
- Generalizer
    - 複数の有価証券報告書の分析を行うプロンプト群を読み込み、プロンプトを汎用化

本サンプルコードを使う前に下記セットアップを実施してください。
1. GCPプロジェクトの作成
2. project idをGCP_PROJECT_IDに設定
3. 上記プロジェクト上にGCSのバケットを生成
4. 作成したバケット名をGCS_BUCKET_NAMEに設定
5. 任意の有価証券報告書をpdf形式で取得（edinet経由から取得可能）
6. 取得したPDFを前述したGCSバケット上にアップロード（複数のPDFをアップロードして良い）
7. アップロードしたPDFファイルを格納しているフォルダURIをPDF_FOLDER_URIに設定
8. 前述したフォルダURIに含まれるPDFのファイル名をPDF_FILE_LISTにリスト形式で記載
"""
import vertexai
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig, GenerationResponse
import os
import json
from datetime import datetime
from google.cloud import storage
from proto.marshal.collections import RepeatedComposite
import uuid
from typing import List


# サンプルコード実行時には下記パラメーターを設定してください
GCP_PROJECT_ID = "xxx"
GCS_BUCKET_NAME = "xxx"
PDF_FOLDER_URI = f"gs://{GCS_BUCKET_NAME}/sample"
PDF_FILE_NAME_LIST = [
    "aaaa.pdf", "bbbb.pdf"
]
MAX_LOOP_COUNT = 3


class InternalLog:
    def __init__(self) -> None:
        self.__queue = []
        self.__latest_prompts = {}

    def set_log(self,
                pdf_uri: str,
                iter_count: int,
                analyze_result: str,
                evaluate_result: str,
                analyze_prompt: str):
        self.__queue.append(
            {
                "pdf_uri": pdf_uri,
                "iter_count": iter_count,
                "analyze_result": analyze_result,
                "evaluate_result": evaluate_result,
                "analyze_prompt": analyze_prompt
            }
        )
        self.__latest_prompts[pdf_uri] = analyze_prompt

    def set_final_analysis_prompt(self, prompt: str):
        self.__queue.append(
            {
                "analyze_final_prompt": prompt
            }
        )

    def print_latest_log(self):
        item = self.__queue[-1]
        pdf_uri = item["pdf_uri"]
        iter_count = item["iter_count"]
        analyze_result = item["analyze_result"]
        evaluate_result = item["evaluate_result"]
        analyze_prompt = item["analyze_prompt"]
        print("=======================================")
        print(f"iter_count: {iter_count}")
        print("=======================================")
        print(f"pdf_uri: {pdf_uri}")
        print("=======================================")
        print(f"analyze_result: {analyze_result}")
        print("=======================================")
        print(f"evaluate_result: {evaluate_result}")
        print("=======================================")
        print(f"analyze_prompt: {analyze_prompt}")
        print("=======================================")

    def save_log_into_json(self, output_file_path: str):
        d = {}
        for i, item in enumerate(self.__queue):
            d[i] = item

        with open(output_file_path, "w") as f:
            json.dump(d, f, indent=2, ensure_ascii=False)

    def get_latest_prompts(self) -> dict:
        return self.__latest_prompts


def generate_analysis_result(
    request_id: str,
    pdf_uri: str,
    prompt: str,
    model_name: str,
    bucket_name: str,
    output_folder: str
) -> str:
    """
    LLMを利用して、有価証券報告書を分析する

    Args:
        pdf_uri (str): _description_
        prompt (str): _description_
        model_name (str): _description_
        bucket_name (str): _description_
        output_folder (str): _description_

    Returns:
        str
    """
    # LLMを利用するのに必要なパラメーターを設定
    vertexai.init(project=GCP_PROJECT_ID, location="us-central1")
    model = GenerativeModel(model_name=model_name)
    temperature = 0
    config = GenerationConfig(
        temperature=temperature
    )

    # LLMを利用して解析処理を実施
    pdf_file = Part.from_uri(uri=pdf_uri, mime_type="application/pdf")
    p = f"""
上記の決算資料から、後述する観点について企業分析を行い、将来の株価の増減具合を教えてください。

======
{prompt}
    """
    contents = [pdf_file, p]
    response = model.generate_content(contents=contents, generation_config=config)

    # ログの作成をし、GCSにアップロードする
    # GCSのフォルダ階層は、<bucket_name>/<日付>/<uuid>とする
    upload_llm_log_data(
        request_id=request_id,
        response=response,
        prompt=prompt,
        model_name=model_name,
        temperature=temperature,
        bucket_name=bucket_name,
        output_folder=output_folder,
        log_name="analyze_pdf_log"
    )

    return response.text


def evaluate_analysis_result(
    request_id: str,
    pdf_uri: str,
    analyze_result: str,
    model_name: str,
    bucket_name: str,
    output_folder: str
) -> str:
    """
    LLMを利用して、有価証券報告書の分析結果が妥当だったか？を評価する
    """

    # LLMを利用するのに必要なパラメーターを設定
    vertexai.init(project=GCP_PROJECT_ID, location="us-central1")
    model = GenerativeModel(model_name=model_name)
    temperature = 0
    config = GenerationConfig(
        temperature=temperature
    )
    prompt = f"""
あなたは有価証券報告書を分析するエキスパートです。
上記の有価証券報告書の分析結果として、下記の内容は妥当でしょうか？妥当でない場合、課題点を列挙してください。

=====
{analyze_result}
    """

    # LLMを利用して解析処理を実施
    pdf_file = Part.from_uri(uri=pdf_uri, mime_type="application/pdf")
    contents = [pdf_file, prompt]
    response = model.generate_content(contents=contents, generation_config=config)

    # 解析結果をログとしてGCSに出力する
    upload_llm_log_data(
        request_id=request_id,
        response=response,
        prompt=prompt,
        model_name=model_name,
        temperature=temperature,
        bucket_name=bucket_name,
        output_folder=output_folder,
        log_name="evaluate_analysis_result_log"
    )

    return response.text


def rewrite_analysis_prompt(
    request_id: str,
    evaluator_result: str,
    analyze_prompt: str,
    model_name: str,
    bucket_name: str,
    output_folder: str
) -> str:
    # LLMを利用するのに必要なパラメーターを設定
    vertexai.init(project=GCP_PROJECT_ID, location="us-central1")
    model = GenerativeModel(model_name=model_name)
    temperature = 0
    config = GenerationConfig(
        temperature=temperature
    )
    prompt = f"""
あなたはLLMのプロンプトを書き換えるエキスパートです。
下記の分析に関する評価結果と分析時に利用したプロンプトから、最適なプロンプトを出力してください。
ただし、後述するルールを守って、プロンプトを出力してください。

分析の評価結果: {evaluator_result}
分析時に利用したプロンプト: {analyze_prompt}

# ルール
・分析観点は一つに拘らず、複数の観点を出すようにしてください。
・プロンプトの変更点がない場合は、プロンプト内容自体をFINISH、と表記するようにしてください。
・会社名、具体的な決算資料の数値といった企業の固有情報をプロンプトに含めないでください。
    """

    # LLMを利用して解析処理を実施
    contents = [prompt]
    response = model.generate_content(contents=contents, generation_config=config)

    # 解析結果をログとしてGCSに出力する
    upload_llm_log_data(
        request_id=request_id,
        response=response,
        prompt=prompt,
        model_name=model_name,
        temperature=temperature,
        bucket_name=bucket_name,
        output_folder=output_folder,
        log_name="adjust_analysis_prompt_log"
    )

    return response.text


def generalize_analysis_prompt(
    request_id: str,
    prompt_dict: dict,
    model_name: str,
    bucket_name: str,
    output_folder: str
) -> str:
    # LLMを利用するのに必要なパラメーターを設定
    vertexai.init(project=GCP_PROJECT_ID, location="us-central1")
    model = GenerativeModel(model_name=model_name)
    temperature = 0
    config = GenerationConfig(
        temperature=temperature
    )
    target_prompts = ""
    for target_prompt in prompt_dict.values():
        p = f"prompt: {target_prompt}\n"
        target_prompts += p
    prompt = f"""
あなたはLLMのプロンプトを書き換えるエキスパートです。
下記の複数のプロンプトから、汎用的な有価証券報告書を分析するためのプロンプトに書き換えてください。
ただし、後述するルールを守って、プロンプトを出力してください。

# 複数のプロンプト情報
{target_prompts}

# ルール
・分析観点は一つに拘らず、複数の観点を出すようにしてください。
・会社名、具体的な決算資料の数値といった企業の固有情報をプロンプトに含めないでください。
    """

    # LLMを利用して解析処理を実施
    contents = [prompt]
    response = model.generate_content(contents=contents, generation_config=config)

    # 解析結果をログとしてGCSに出力する
    upload_llm_log_data(
        request_id=request_id,
        response=response,
        prompt=prompt,
        model_name=model_name,
        temperature=temperature,
        bucket_name=bucket_name,
        output_folder=output_folder,
        log_name="generalize_prompt_log"
    )

    return response.text


def upload_llm_log_data(
    request_id: str,
    response: GenerationResponse,
    prompt: str,
    model_name: str,
    temperature: float,
    bucket_name: str,
    output_folder: str,
    log_name: str
):
    llm_log_data = {
        "input": {
            "input_datas": [],
            "prompt": prompt,
            "model_name": model_name,
            "llm_config": {
                "temperature": temperature
            },
            "prompt_token_count": response._raw_response.usage_metadata.prompt_token_count,
        },
        "output": {
            "text": response.candidates[0].text,
            "finish_reason": response.candidates[0].finish_reason.name,
            "finish_message": response.candidates[0].finish_message,
            "safety_ratings": repeated_safety_ratings_to_list(response.candidates[0].safety_ratings),
            "citation_metadata" : repeated_citations_to_list(response.candidates[0].citation_metadata.citations),
            "candidates_token_count": response._raw_response.usage_metadata.candidates_token_count,
            "total_token_count": response._raw_response.usage_metadata.total_token_count
        },
        "meta": {
            "timestamp": datetime.now().strftime("%Y%m%d%H%M%S"),
            "request_id": request_id
        }
    }
    tmp_log_file = os.path.join(output_folder, "tmp_log.json")
    with open(tmp_log_file, "w") as f:
        json.dump(llm_log_data, f, ensure_ascii=False)

    try:
        storage_client = storage.Client(project=GCP_PROJECT_ID)
        datetime_str = datetime.now().strftime("%Y%m%d%H%M%S")
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(f"log/{datetime_str}/{request_id}/{log_name}.json")
        blob.upload_from_filename(tmp_log_file, if_generation_match=0)
    except Exception as e:
        print(e)
    finally:
        os.remove(tmp_log_file)


# citation_metadataオブジェクトをリストに変換する
def repeated_citations_to_list(citations: RepeatedComposite) -> list:
    citation_li = []
    for citation in citations:
        citation_dict = {}
        citation_dict["startIndex"] = citation.startIndex
        citation_dict["endIndex"] = citation.endIndex
        citation_dict["uri"] = citation.uri
        citation_dict["title"] = citation.title
        citation_dict["license"] = citation.license
        citation_dict["publicationDate"] = citation.publicationDate
        citation_li.append(citation_dict)
    return citation_li


# safety_ratingsオブジェクトをリストに変換する
def repeated_safety_ratings_to_list(safety_ratings: RepeatedComposite) -> list:
    safety_rating_li = []
    for safety_rating in safety_ratings:
        safety_rating_dict = {}
        safety_rating_dict["category"] = safety_rating.category.name
        safety_rating_dict["probability"] = safety_rating.probability.name
        safety_rating_li.append(safety_rating_dict)
    return safety_rating_li


def get_pdf_file_uri_list_in_gcs() -> List[str]:
    storage_client = storage.Client(project=GCP_PROJECT_ID)
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    files = bucket.list_blobs(prefix=PDF_FOLDER_NAME + "/")
    file_uri_list = [f"gs://{GCS_BUCKET_NAME}/{file.name}" for file in files]
    return list(filter(lambda x: x.endswith(".pdf"), file_uri_list))


def main():
    default_analyze_prompt = """
・有価証券報告書に含まれる情報を分析時に利用すること。
    """
    default_analyze_prompt = """
1. 経営戦略と事業内容:

企業のビジョン、ミッション、経営理念を明確化し、その内容を評価してください。
主要な事業セグメントとその内容、売上高、利益への貢献度を分析してください。
市場における競争優位性と、その持続可能性について評価してください。
今後の事業展開の方向性と、その実現可能性について分析してください。
事業ポートフォリオを分析し、多角化の程度やリスク分散の状況を評価してください。
2. 財務状況:

収益性、安全性、効率性の観点から財務状況を分析し、改善点や課題を指摘してください。
収益性分析では、売上高総利益率、営業利益率などの指標の推移を分析し、その要因を考察してください。
安全性分析では、流動比率、自己資本比率などの指標を分析し、財務リスクを評価してください。
効率性分析では、総資産回転率、棚卸資産回転率などの指標を分析し、資産の運用効率を評価してください。
キャッシュフロー計算書を分析し、資金繰りの状況を評価してください。
3. リスク:

事業報告書に記載されているリスク要因を分析し、その重要度と影響度を評価してください。
業界全体の動向や競合との競争環境などを考慮し、潜在的なリスクを特定してください。
リスク管理体制の adequacy を評価し、改善点があれば指摘してください。
4. コーポレートガバナンス:

コーポレートガバナンスの体制、取締役会の構成、独立役員の役割などを分析してください。
株主との関係、情報開示の状況などを評価してください。
企業倫理、コンプライアンスに関する取り組みを評価してください。
5. ESG:

環境問題への取り組み、社会貢献活動、企業統治の状況を分析してください。
ESGに関する情報開示の adequacy を評価してください。
ESGの観点から、企業の持続可能性を評価してください。
分析結果の出力形式:

各観点ごとに章立てし、分析結果を明確に記述してください。
図表やグラフなどを用いて、分析結果を視覚的に表現してください。
具体的な根拠に基づいた客観的な分析を行い、結論を明確に示してください。
必要に応じて、改善点や提言などを提示してください。
その他:

分析対象の有価証券報告書の発行企業、発行年を明記してください。
最新の情報やデータを入手し、分析に活用してください。
    """
    output_folder = os.path.join(os.path.dirname(__file__), "output", "auto_prompt_engineering_sample")
    os.makedirs(output_folder, exist_ok=True)
    internal_logger = InternalLog()
    datetime_str = datetime.now().strftime("%Y%m%d%H%M%S")
    display_analysis_log = False

    # gcs上のフォルダからPDFのファイルリストを取得する
    pdf_file_uri_list = get_pdf_file_uri_list_in_gcs()

    # 有価証券報告書の解析処理の実施
    print(f"target document count of analysis is {len(pdf_file_uri_list)}")
    for i, pdf_file_uri in enumerate(pdf_file_uri_list):
        print(f"{i+1}/{len(pdf_file_uri_list)} : start to analyze {pdf_file_uri} file...")
        analyze_prompt = default_analyze_prompt
        pdf_uri = pdf_file_uri
        for i in range(MAX_LOOP_COUNT):
            print(f"{i+1}/{MAX_LOOP_COUNT} : analyze financial report...")
            request_id = str(uuid.uuid4())

            # 有価証券報告書の分析を行う
            print("start to analyze the financial report...")
            analyze_result = generate_analysis_result(
                request_id=request_id,
                pdf_uri=pdf_uri,
                prompt=analyze_prompt,
                model_name="gemini-1.5-flash",
                bucket_name=GCS_BUCKET_NAME,
                output_folder=output_folder
            )

            # 分析結果を評価する
            print("start to evaluate the analysis result...")
            evaluate_result = evaluate_analysis_result(
                request_id=request_id,
                pdf_uri=pdf_uri,
                analyze_result=analyze_result,
                model_name="gemini-1.5-flash",
                bucket_name=GCS_BUCKET_NAME,
                output_folder=output_folder
            )

            # プロンプトを書き換える
            print("start to recreate the analysis prompt...")
            analyze_prompt = rewrite_analysis_prompt(
                request_id=request_id,
                evaluator_result=evaluate_result,
                analyze_prompt=analyze_prompt,
                model_name="gemini-1.5-flash",
                bucket_name=GCS_BUCKET_NAME,
                output_folder=output_folder
            )

            # 1イテレーション分の結果を出力する
            internal_logger.set_log(
                pdf_uri=pdf_uri,
                iter_count=i,
                analyze_result=analyze_result,
                evaluate_result=evaluate_result,
                analyze_prompt=analyze_prompt
            )
            if display_analysis_log:
                internal_logger.print_latest_log()

            if "FINISH" in analyze_prompt:
                print("analyze_prompt is end! break")
                break

    # 全てのプロンプト結果を元に汎用的なプロンプトを作り直す
    request_id = str(uuid.uuid4())
    final_prompt = generalize_analysis_prompt(
        request_id=request_id,
        prompt_dict=internal_logger.get_latest_prompts(),
        model_name="gemini-1.5-flash",
        bucket_name=GCS_BUCKET_NAME,
        output_folder=output_folder
    )
    print("=======================")
    print(f"final prompt: {final_prompt}")
    print("=======================")
    internal_logger.set_final_analysis_prompt(prompt=final_prompt)

    # ログをjsonファイルとして出力
    internal_logger.save_log_into_json(
        output_file_path=os.path.join(output_folder, f"internal_log_{datetime_str}.json")
    )


if __name__ == "__main__":
    main()
