from typing import Any, Dict, List


class AgentCommunicator:
    def __init__(self):
        self.messages: List[Dict[str, Any]] = []

    def send(self, sender: str, message: str) -> None:
        self.messages.append({"sender": sender, "message": message})

    def receive(self) -> List[Dict[str, Any]]:
        return list(self.messages)

    def merge_results(self, responses: List[str]) -> str:
        return " \n".join(responses)
