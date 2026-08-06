from fastapi import FastAPI
from backend.api.routes.health import router as health_router
from backend.api.routes.auth import router as auth_router
from backend.api.routes.memory import router as memory_router
from backend.api.routes.ai import router as ai_router
from backend.api.routes.agent import router as agent_router

app = FastAPI(
    title="Offspace Backend API",
    version="1.0.0",
    description="Production API for the Offspace AI assistant platform.",
)

app.include_router(health_router, prefix="/api/v1/health")
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(memory_router, prefix="/api/v1/memory")
app.include_router(ai_router, prefix="/api/v1/ai")
app.include_router(agent_router, prefix="/api/v1/agents")
