from pydantic import BaseModel
from typing import Optional


class ChatRequestSchema(BaseModel):
    prompt: str
    provider: Optional[str] = None
    model: Optional[str] = None


class ChatResponseSchema(BaseModel):
    response: str
    provider: str
