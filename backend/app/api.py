from logging import StreamHandler, getLogger

from fastapi import FastAPI
from pydantic import BaseModel
from starlette.exceptions import HTTPException
from typing import List

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
    pass


@app.post("/analyze_financial_document")
def analyze_financial_document():
    pass
