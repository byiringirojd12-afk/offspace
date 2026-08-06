import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from backend.intelligence.router import ModelRouter
from core.automation import AutomationManager
from core.personality import Personality
from core.router import CommandType, Router
from core.voice import VoiceController
from memory.memory_manager import MemoryManager

logger = logging.getLogger(__name__)


class Assistant:
    """OFFSPACE AI Assistant - Main orchestrator"""
    
    def __init__(self, owner_name: str = "Biringiro Jean Damascene", location: str = "Rwanda", debug: bool = False):
        self.owner_name = owner_name
        self.location = location
        self.debug = debug
        self.name = "OFFSPACE"
        self.wake_phrase = "Hey OFFSPACE"
        self.is_listening = False
        self.conversation_history: List[Dict[str, Any]] = []
        self.created_at = datetime.now()
        self.voice_controller = VoiceController()
        self.automation_manager = AutomationManager()
        self.memory_manager = MemoryManager()
        self.router = Router()
        self.personality = Personality()
        self.model_router = ModelRouter()
        self._register_handlers()
        logger.info(f"OFFSPACE Assistant initialized for {owner_name} in {location}")
    
    def start(self) -> None:
        logger.info("Starting OFFSPACE Assistant")
        self.is_listening = True
        print(f"🎙️ {self.name} is listening...")
        print(f"Wake phrase: '{self.wake_phrase}'")
    
    def stop(self) -> None:
        logger.info("Stopping OFFSPACE Assistant")
        self.is_listening = False
        print(f"🛑 {self.name} stopped")
    
    def _register_handlers(self) -> None:
        self.router.register_handler(CommandType.COMPUTER_CONTROL, self._handle_computer_control)
        self.router.register_handler(CommandType.MEMORY, self._handle_memory)
        self.router.register_handler(CommandType.CONVERSATION, self._handle_conversation)
        self.router.register_handler(CommandType.UNKNOWN, self._handle_conversation)

    async def process_command(self, user_input: str) -> str:
        logger.info(f"Processing command: {user_input}")
        if self.voice_controller.contains_wake_phrase(user_input):
            user_input = user_input.replace(self.voice_controller.WAKE_PHRASE, "", 1).strip()

        self.memory_manager.add_to_short_term("user", user_input)
        self.conversation_history.append({"timestamp": datetime.now(), "user": user_input, "type": "user_input"})

        response = await self.router.route(user_input)

        self.memory_manager.add_to_short_term("assistant", response)
        self.conversation_history.append({"timestamp": datetime.now(), "assistant": response, "type": "assistant_response"})
        return response

    async def _handle_computer_control(self, user_input: str) -> str:
        return self.automation_manager.execute_command(user_input)

    async def _handle_memory(self, user_input: str) -> str:
        lower_input = user_input.lower()
        if "remember" in lower_input or "save" in lower_input:
            payload = user_input.replace("remember", "").replace("save", "").strip()
            if not payload:
                return "I didn't catch what you wanted me to remember."
            key = payload.split(" ", 1)[0] if " " in payload else payload
            self.memory_manager.save_user_preference(key, payload)
            return f"Saved memory: {payload}"

        if "recall" in lower_input or "remember" in lower_input or "what" in lower_input:
            results = self.memory_manager.search_long_term(lower_input)
            if not results:
                return "I couldn't find that memory yet."
            return "; ".join([f"{item['key']}: {item['value']}" for item in results])

        return f"Memory command received: {user_input}."

    async def _handle_conversation(self, user_input: str) -> str:
        try:
            if self.model_router.get_provider().available():
                return self.model_router.chat(user_input)
        except Exception:
            pass

        style = self.personality.get_response_style("technical")
        return f"{self.name} is ready to support you. {user_input[:120]}"

    def get_status(self) -> dict:
        return {
            "name": self.name,
            "owner": self.owner_name,
            "location": self.location,
            "is_listening": self.is_listening,
            "uptime": (datetime.now() - self.created_at).total_seconds(),
            "messages_processed": len(self.conversation_history) // 2,
            "debug_mode": self.debug,
            "short_term_memory": len(self.memory_manager.get_short_term_context()),
            "long_term_memory": len(self.memory_manager.long_term_memory),
        }
    
    def __repr__(self) -> str:
        return f"<{self.name} Assistant for {self.owner_name}>"
