import logging
from datetime import datetime
from typing import Optional

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
        self.conversation_history = []
        self.created_at = datetime.now()
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
    
    async def process_command(self, user_input: str) -> str:
        logger.info(f"Processing command: {user_input}")
        self.conversation_history.append({"timestamp": datetime.now(), "user": user_input, "type": "user_input"})
        response = f"I received your command: {user_input}"
        self.conversation_history.append({"timestamp": datetime.now(), "assistant": response, "type": "assistant_response"})
        return response
    
    def get_status(self) -> dict:
        return {
            "name": self.name,
            "owner": self.owner_name,
            "location": self.location,
            "is_listening": self.is_listening,
            "uptime": (datetime.now() - self.created_at).total_seconds(),
            "messages_processed": len(self.conversation_history) // 2,
            "debug_mode": self.debug
        }
    
    def __repr__(self) -> str:
        return f"<{self.name} Assistant for {self.owner_name}>"
