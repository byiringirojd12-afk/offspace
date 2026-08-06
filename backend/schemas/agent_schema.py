from pydantic import BaseModel
from typing import Optional, List


class AgentTaskCreateSchema(BaseModel):
    title: str
    description: str
    agent_type: str


class AgentTaskSchema(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    agent_type: str
    status: str
    result_summary: Optional[str]

    model_config = {
        "from_attributes": True,
    }


class AgentTaskStatusResponse(BaseModel):
    task_id: int
    status: str
    summary: Optional[str]
    details: List[str] = []
