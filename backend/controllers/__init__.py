from backend.controllers.health_controller import router as health_router
from backend.controllers.user_controller import router as user_router
from backend.controllers.memory_controller import router as memory_router
from backend.controllers.chat_controller import router as chat_router
from backend.controllers.agent_controller import router as agent_router
from backend.controllers.settings_controller import router as settings_router

__all__ = ["health_router", "user_router", "memory_router", "chat_router", "agent_router", "settings_router"]
