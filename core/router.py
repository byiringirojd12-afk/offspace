import logging
from enum import Enum
from typing import Callable, Dict

logger = logging.getLogger(__name__)


class CommandType(Enum):
    CONVERSATION = "conversation"
    CODING = "coding"
    CYBERSECURITY = "cybersecurity"
    RESEARCH = "research"
    PRODUCTIVITY = "productivity"
    COMPUTER_CONTROL = "computer_control"
    MEMORY = "memory"
    UNKNOWN = "unknown"


class Router:
    def __init__(self):
        self.handlers: Dict[CommandType, Callable] = {}
        self.command_keywords = {
            CommandType.CODING: ["code", "python", "javascript", "create", "function", "debug", "error", "test", "run"],
            CommandType.CYBERSECURITY: ["security", "hack", "encrypt", "password", "firewall", "vulnerability"],
            CommandType.RESEARCH: ["research", "find", "search", "summarize", "analyze", "information"],
            CommandType.PRODUCTIVITY: ["plan", "schedule", "remind", "organize", "prioritize", "task"],
            CommandType.COMPUTER_CONTROL: ["open", "close", "delete", "create", "run", "execute", "file", "folder"],
            CommandType.MEMORY: ["remember", "forget", "recall", "save", "memory", "note"]
        }
    
    def detect_command_type(self, user_input: str) -> CommandType:
        lower_input = user_input.lower()
        for cmd_type, keywords in self.command_keywords.items():
            if any(keyword in lower_input for keyword in keywords):
                logger.info(f"Detected command type: {cmd_type}")
                return cmd_type
        return CommandType.UNKNOWN
    
    def register_handler(self, command_type: CommandType, handler: Callable) -> None:
        self.handlers[command_type] = handler
        logger.info(f"Handler registered for {command_type}")
    
    async def route(self, user_input: str) -> str:
        command_type = self.detect_command_type(user_input)
        if command_type in self.handlers:
            handler = self.handlers[command_type]
            return await handler(user_input)
        return f"I understand you said: {user_input}. Feature coming soon!"
