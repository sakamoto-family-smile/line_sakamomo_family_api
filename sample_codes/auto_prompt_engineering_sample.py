"""
このサンプルコードは、Auto Prompt Enginneringを有価証券報告書の分析に対して、
検証してみたものとなります.
一般的なフレームワークを利用していないため、今後はフレームワークを試しに利用してみたいと考えています.
"""
import vertexai
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig, GenerationResponse
import os
import json
from datetime import datetime
from google.cloud import storage
from proto.marshal.collections import RepeatedComposite
import uuid


GCP_PROJECT_ID = "xxx"
GCS_BUCKET_NAME = ""


class InternalLog:
    def __init__(self) -> None:
        self.__queue = []

    def set_log(self,
                analyze_result: str,
                evaluate_result: str,
                analyze_prompt: str):
        self.__queue.append(
            {
                "analyze_result": analyze_result,
                "evaluate_result": evaluate_result,
                "analyze_prompt": analyze_prompt
            }
        )

    def print_log(self, index: int):
        analyze_result = self.__queue[index]["analyze_result"]
        evaluate_result = self.__queue[index]["evaluate_result"]
        analyze_prompt = self.__queue[index]["analyze_prompt"]
        print(f"analyze_result: {analyze_result}")
        print(f"evaluate_result: {evaluate_result}")
        print(f"analyze_prompt: {analyze_prompt}")


def analyze_financial_report(
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
    temperature = 0.8
    config = GenerationConfig(
        temperature=temperature
    )

    # LLMを利用して解析処理を実施
    pdf_file = Part.from_uri(uri=pdf_uri, mime_type="application/pdf")
    contents = [pdf_file, prompt]
    response = model.generate_content(contents=contents, generation_config=config)

    # ログの作成をし、GCSにアップロードする
    # GCSのフォルダ階層は、<bucket_name>/<日付>/<uuid>とする
    request_id = str(uuid.uuid4())
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
    pdf_uri: str,
    analyze_result: str,
    model_name: str,
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
    return response.text


def adjust_analysis_prompt(
    evaluator_result: str,
    analyze_prompt: str,
    model_name: str
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
ただし、プロンプトの変更点がない場合は、END、と出力してください。

分析の評価結果: {evaluator_result}
分析時に利用したプロンプト: {analyze_prompt}
    """

    # LLMを利用して解析処理を実施
    contents = [prompt]
    response = model.generate_content(contents=contents, generation_config=config)
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
        print("end")


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


def main():
    pdf_uri = "gs://sakamomo_family_api/document/20240930071845/ccbc9f9c-7e3a-4607-b746-6ef749fb9c1d/S100T80B.pdf"
    analyze_prompt = """
上記の決算資料から、後述する観点について分析を行い、下記の内容について回答してください。

・財務三表（損益計算書、貸借対照表、キャッシュフロー表）について、分析を行ってください。
    """
    max_loop_count = 5
    output_folder = os.path.join(os.path.dirname(__file__), "output", "auto_prompt_engineering_sample")
    os.makedirs(output_folder, exist_ok=True)
    internal_logger = InternalLog()

    for i in range(max_loop_count):
        print(f"{i}/{max_loop_count} : analyze financial report...")

        # 有価証券報告書の分析を行う
        analyze_result = analyze_financial_report(
            pdf_uri=pdf_uri,
            prompt=analyze_prompt,
            model_name="gemini-1.5-flash",
            bucket_name=GCS_BUCKET_NAME,
            output_folder=output_folder
        )

        # 分析結果を評価する
        evaluate_result = evaluate_analysis_result(
            pdf_uri=pdf_uri,
            analyze_result=analyze_result,
            model_name="gemini-1.5-flash"
        )

        # プロンプトを書き換える
        analyze_prompt = adjust_analysis_prompt(
            evaluator_result=evaluate_result,
            analyze_prompt=analyze_prompt,
            model_name="gemini-1.5-flash"
        )

        # 1イテレーション分の結果を出力する
        internal_logger.set_log(
            analyze_result=analyze_result,
            evaluate_result=evaluate_result,
            analyze_prompt=analyze_prompt
        )
        internal_logger.print_log(index=i)

        if analyze_prompt == "END":
            print("analyze_prompt is end! break")
            break


if __name__ == "__main__":
    main()