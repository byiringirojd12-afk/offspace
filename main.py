#!/usr/bin/env python
import asyncio
import logging
from dotenv import load_dotenv
import os

from core.assistant import Assistant
from memory.memory_manager import MemoryManager
from core.router import Router

load_dotenv()
logging.basicConfig(
    level=os.getenv("OFFSPACE_LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class OffspaceApp:
    def __init__(self):
        self.assistant = Assistant(
            owner_name=os.getenv("OFFSPACE_OWNER_NAME", "Biringiro Jean Damascene"),
            location=os.getenv("OFFSPACE_LOCATION", "Rwanda"),
            debug=os.getenv("OFFSPACE_DEBUG", "false").lower() == "true"
        )
        self.memory = MemoryManager()
        self.router = Router()
    
    async def run_interactive(self) -> None:
        self.assistant.start()
        print("\n" + "="*60)
        print(f"Welcome to {self.assistant.name} AI Assistant")
        print(f"Owner: {self.assistant.owner_name}")
        print(f"Location: {self.assistant.location}")
        print("="*60)
        print("\nType 'help' for commands, 'exit' to quit\n")
        
        try:
            while self.assistant.is_listening:
                try:
                    user_input = input("You: ").strip()
                    if not user_input:
                        continue
                    if user_input.lower() == "exit":
                        break
                    if user_input.lower() == "help":
                        self._show_help()
                        continue
                    if user_input.lower() == "status":
                        status = self.assistant.get_status()
                        print(f"\nStatus: {status}\n")
                        continue
                    
                    self.memory.add_to_short_term("user", user_input)
                    response = await self.assistant.process_command(user_input)
                    print(f"{self.assistant.name}: {response}\n")
                    self.memory.add_to_short_term("assistant", response)
                except KeyboardInterrupt:
                    break
        finally:
            self.assistant.stop()
            self.memory.clear_short_term()
    
    def _show_help(self) -> None:
        print("\n" + "="*60)
        print("OFFSPACE Commands:")
        print("="*60)
        print("  help        - Show this help message")
        print("  status      - Show assistant status")
        print("  exit        - Exit the application")
        print("\nExample commands:")
        print("  'Create a Python script'")
        print("  'Explain how encryption works'")
        print("  'Remember my favorite language is Python'")
        print("="*60 + "\n")


async def main():
    logger.info("Starting OFFSPACE AI Assistant")
    app = OffspaceApp()
    try:
        await app.run_interactive()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        raise
    finally:
        logger.info("OFFSPACE AI Assistant shutdown")


if __name__ == "__main__":
    asyncio.run(main())
