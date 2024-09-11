import os
import google.generativeai as genai
import PyPDF2


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
    print(res)


if __name__ == "__main__":
    pdf_path = os.path.join(os.path.dirname(__file__), "sample_data", "S100T80B.pdf")
    main(pdf_path=pdf_path)
