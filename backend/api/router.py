from fastapi import APIRouter

from backend.controllers.health_controller import router as health_router
from backend.controllers.user_controller import router as user_router
from backend.controllers.memory_controller import router as memory_router
from backend.controllers.chat_controller import router as chat_router
from backend.controllers.agent_controller import router as agent_router
from backend.controllers.settings_controller import router as settings_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router, prefix="/health", tags=["Health"])
api_router.include_router(user_router, prefix="/users", tags=["Users"])
api_router.include_router(memory_router, prefix="/memory", tags=["Memory"])
api_router.include_router(chat_router, prefix="/chat", tags=["Chat"])
api_router.include_router(agent_router, prefix="/agents", tags=["Agents"])
api_router.include_router(settings_router, prefix="/settings", tags=["Settings"])
