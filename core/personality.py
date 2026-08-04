import logging

logger = logging.getLogger(__name__)


class Personality:
    """Define and manage OFFSPACE personality traits"""
    
    CORE_TRAITS = {
        "name": "OFFSPACE",
        "tone": "professional",
        "intelligence_level": "advanced",
        "communication_style": "direct_and_helpful",
        "privacy_focus": "strict",
        "learning_capability": True,
    }
    
    def __init__(self):
        self.traits = self.CORE_TRAITS.copy()
        logger.info("Personality system initialized")
    
    def get_response_style(self, context: str) -> dict:
        styles = {
            "technical": {"detail_level": "high", "use_code_examples": True, "precision": "exact"},
            "casual": {"detail_level": "medium", "use_humor": False, "precision": "practical"},
            "learning": {"detail_level": "educational", "explain_concepts": True, "provide_examples": True}
        }
        return styles.get(context, styles["technical"])
    
    def should_remember_user_preference(self, statement: str) -> bool:
        memory_keywords = ["remember", "my favorite", "i prefer", "i like", "my goal", "remember that"]
        return any(keyword in statement.lower() for keyword in memory_keywords)
