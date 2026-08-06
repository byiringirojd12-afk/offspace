"""Multi-agent collaboration package."""
from .manager import AgentManager, Agent
from .communicator import AgentCommunicator

__all__ = ["AgentManager", "Agent", "AgentCommunicator"]
