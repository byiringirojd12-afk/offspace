from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.database.models import AgentTask
from backend.schemas.agent_schema import AgentTaskCreateSchema


class AgentService:
    def __init__(self, db: Session):
        self.db = db

    def create_task(self, user_id: int, request: AgentTaskCreateSchema) -> AgentTask:
        task = AgentTask(
            user_id=user_id,
            title=request.title,
            description=request.description,
            agent_type=request.agent_type,
            status="pending",
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_task_status(self, user_id: int, task_id: int):
        task = self.db.query(AgentTask).filter(AgentTask.id == task_id, AgentTask.user_id == user_id).first()
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent task not found")
        return {
            "task_id": task.id,
            "status": task.status,
            "summary": task.result_summary,
            "details": [f"Task type: {task.agent_type}"]
        }
