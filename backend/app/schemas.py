from pydantic import BaseModel


class SummaryRequest(BaseModel):
    transcript: str = ""
    prompt: str = ""
    username: str = "unknown"


class DocxRequest(BaseModel):
    markdown: str
