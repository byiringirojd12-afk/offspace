from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List

router = APIRouter()

class AgentTask(BaseModel):
    title: str
    description: str
    agent_type: str

class AgentReport(BaseModel):
    task_id: str
    status: str
    summary: str
    details: List[str]

@router.post("/task", response_model=AgentReport)
def create_agent_task(task: AgentTask) -> AgentReport:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Agent task management is not implemented yet")

@router.get("/status/{task_id}", response_model=AgentReport)
def get_agent_task_status(task_id: str) -> AgentReport:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Agent task status is not implemented yet")
