from logging import StreamHandler, getLogger

from fastapi import FastAPI
from pydantic import BaseModel
from starlette.exceptions import HTTPException
from typing import List
from enum import Enum

from .controller import Controller


class Response(BaseModel):
    status: int
    message: str


class BotRequest(BaseModel):
    message: str


class FinancialDocumentListRequest(BaseModel):
    company_name: str


class FinancialDocumentData(BaseModel):
    doc_id: str
    doc_url: str
    filer_name: str
    document_description: str


class FinancialDocumentListResponse(BaseModel):
    status: int
    document_list: List[FinancialDocumentData]


class AnalyzeFinancialReportRequest(BaseModel):
    analysis_type: int
    message: str
    gcs_uri: str


class AnalyzeFinancialReportResponse(BaseModel):
    text: str
    prompt: str


class UploadFinancialReportRequest(BaseModel):
    doc_id: str


class UploadFinancialReportResponse(BaseModel):
    gcs_uri: str


class FinancialReportAnalysisType(Enum):
    DEFAULT = 0
    QA = 1


logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel("DEBUG")


app = FastAPI(title="sakamomo_family_api", description="The API is sakamomo family bot.")
session_id = "sakamomo_family_session"
controller = Controller(dialogue_session_id=session_id)


@app.get("/health")
def health():
    return Response(status=0, message="OK")


@app.post("/bot")
def bot(request: BotRequest):
    try:
        res = controller.handle_message(message=request.message)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error. Bot process is failed.")
    return Response(status=0, message=res)


@app.post("/financial_document_list")
def financial_document_list(request: FinancialDocumentListRequest):
    try:
        res = controller.search_financial_documents_if_existed(company_name=request.company_name)
        document_list = [
            FinancialDocumentData(
                doc_id=item["doc_id"],
                doc_url=item["doc_url"],
                filer_name=item["filer_name"],
                document_description=item["doc_description"]
            )
            for item in res.deteil["items"]
        ]
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error. Search financial report process is failed.")
    return FinancialDocumentListResponse(status=0, document_list=document_list)


@app.post("/analyze_financial_document")
def analyze_financial_document(request: AnalyzeFinancialReportRequest):
    if request.analysis_type == FinancialReportAnalysisType.QA.value:
        message = request.message
    else:
        message = None

    try:
        res = controller.analyze_financial_document(
            gcs_uri=request.gcs_uri, message=message
        )
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error. Analysis Financial Report process is failed.")
    return AnalyzeFinancialReportResponse(
        text=res.deteil["reponse_text"],
        prompt=res.deteil["prompt"]
    )


# TODO : この機能はバイナリファイルを受け取れるようにするか、ユーザーには提供しない機能とするか、検討した方が良さそう
@app.post("/upload_financial_report")
def upload_financial_report(request: UploadFinancialReportRequest):
    try:
        res = controller.upload_financial_report_into_gcs(doc_id=request.doc_id)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error. Upload Financial Report Process is failed.")
    return UploadFinancialReportResponse(gcs_uri=res.deteil["gcs_uri"])
