from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.schemas.agent_schema import AgentTaskCreateSchema, AgentTaskSchema, AgentTaskStatusResponse
from backend.services.agent_service import AgentService
from backend.api.dependencies import get_db
from backend.auth.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=AgentTaskSchema)
def create_agent_task(request: AgentTaskCreateSchema, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> AgentTaskSchema:
    return AgentService(db).create_task(current_user.id, request)

@router.get("/{task_id}", response_model=AgentTaskStatusResponse)
def get_agent_task_status(task_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> AgentTaskStatusResponse:
    return AgentService(db).get_task_status(current_user.id, task_id)
