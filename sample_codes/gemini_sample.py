import os
import google.generativeai as genai
import PyPDF2
from datetime import datetime


API_KEY = "xxxx"


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        extracted_text = ""
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text
        return extracted_text


def main(pdf_path: str):
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    pdf_file = extract_text_from_pdf(pdf_path=pdf_path)
    prompt = """
    内容に含まれる財務三表の内容を踏まえて、企業の分析を行なってください。
    """
    res = model.generate_content([prompt, pdf_file])

    # 結果を書き込む
    print(res.text)
    output_folder = os.path.join(os.path.dirname(__file__), "output", "gemini_sample")
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, "{}.txt".format(datetime.now().strftime("%Y%m%d%H%M%S")))
    with open(output_path, "w") as f:
        f.write(res.text)


if __name__ == "__main__":
    pdf_path = os.path.join(os.path.dirname(__file__), "sample_data", "S100T80B.pdf")
    main(pdf_path=pdf_path)
