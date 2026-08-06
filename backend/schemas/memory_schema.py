from pydantic import BaseModel
from typing import Optional, List


class MemoryCreateSchema(BaseModel):
    key: str
    value: str
    category: Optional[str] = "general"


class MemoryItemSchema(BaseModel):
    id: int
    user_id: int
    key: str
    value: str
    category: Optional[str]

    model_config = {
        "from_attributes": True,
    }


class MemorySearchResponse(BaseModel):
    results: List[MemoryItemSchema]
