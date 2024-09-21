import os
import google.generativeai as genai
import vertexai
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig
from google.cloud import storage
import PyPDF2
from io import BytesIO
from datetime import datetime
from enum import Enum
from proto.marshal.collections import RepeatedComposite
import json
import uuid


API_KEY = ""
GCP_PROJECT_ID = ""
GCS_BUCKET_NAME = ""


class ModelType(Enum):
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    GEMINI_1_5_PRO = "gemini-1.5-pro-preview-0409"


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


def upload_file_into_gcs(
    storage_client: storage.Client,
    bucket_name: str,
    gcs_path: str,
    local_file_path: str
):
    try:
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(gcs_path)
        blob.upload_from_file(local_file_path)
    except Exception as e:
        print(f"Error uploading to Cloud Storage: {e}")


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        extracted_text = ""
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text
        return extracted_text


def analyze_pdf_by_genai(pdf_path: str, model_name: str):
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(model_name=model_name)
    pdf_file = extract_text_from_pdf(pdf_path=pdf_path)
    prompt = """
    下記に含まれる財務三表の内容を踏まえて、企業の分析を行なってください。
    """
    res = model.generate_content([prompt, pdf_file])
    return res.text


def analyze_pdf_by_vertexai(pdf_path: str, model_name: str, bucket_name: str, output_folder: str):
    # LLMを利用して解析処理を実施
    vertexai.init(project=GCP_PROJECT_ID, location="us-central1")
    model = GenerativeModel(model_name=model_name)

    # pdfをbyteデータに変換
    with open(pdf_path, "rb") as f:
        byte_datas = BytesIO(f.read())

    prompt = """
    下記に含まれる財務三表の内容を踏まえて、企業の分析を行なってください。
    """
    temperature = 0
    config = GenerationConfig(
        temperature=temperature
    )

    pdf_file = Part.from_data(data=byte_datas.getvalue(), mime_type="application/pdf")
    contents = [pdf_file, prompt]

    response = model.generate_content(contents=contents, generation_config=config)

    # debug
    #print(response._raw_response.usage_metadata)
    #for c in response.candidates:
    #    print(c)

    # ログの作成をし、GCSにアップロードする
    # GCSのフォルダ階層は、<bucket_name>/<日付>/<uuid>とする
    request_id = str(uuid.uuid4())
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
        blob = bucket.blob(f"log/{datetime_str}/{request_id}/llm_log.json")
        blob.upload_from_filename(tmp_log_file, if_generation_match=0)
    except Exception as e:
        print(e)
    finally:
        os.remove(tmp_log_file)
        print("end")

    return response.text


def main(pdf_path: str, analyze_type: int = 0, model_name: str = "gemini-1.5-flash"):
    output_folder = os.path.join(os.path.dirname(__file__), "output", "gemini_sample")
    os.makedirs(output_folder, exist_ok=True)

    if analyze_type == 0:
        res = analyze_pdf_by_genai(pdf_path=pdf_path, model_name=model_name)
    elif analyze_type == 1:
        res = analyze_pdf_by_vertexai(
            pdf_path=pdf_path,
            model_name=model_name,
            bucket_name=GCS_BUCKET_NAME,
            output_folder=output_folder
        )
    else:
        raise Exception(f"{analyze_type} is not defined.")

    # 結果を書き込む
    print(res)
    output_path = os.path.join(output_folder, "{}.txt".format(datetime.now().strftime("%Y%m%d%H%M%S")))
    with open(output_path, "w") as f:
        f.write(res)


if __name__ == "__main__":
    pdf_path = os.path.join(os.path.dirname(__file__), "sample_data", "S100T80B.pdf")
    main(pdf_path=pdf_path, analyze_type=1, model_name=ModelType.GEMINI_1_5_FLASH.value)
