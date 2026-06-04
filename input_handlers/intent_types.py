"""
Intent Type Definitions
Core enum and data classes for natural language intent detection
"""

from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass


class IntentType(Enum):
    """Enumeration of all possible user intents"""

    GREETING = "greeting"
    TASK_CREATION = "task_creation"
    HELP_REQUEST = "help_request"
    PROJECT_WORK = "project_work"
    LIST_ITEMS = "list_items"
    STATUS = "status"
    UNCLEAR = "unclear"
    EXIT = "exit"


@dataclass
class Intent:
    """Represents a parsed user intent with metadata"""

    intent_type: IntentType
    confidence: float  # 0.0 to 1.0
    raw_input: str
    extracted_params: Dict[str, Any]
    clarification_needed: bool = False
    clarification_message: Optional[str] = None

    def is_confident(self, threshold: float = 0.7) -> bool:
        """Check if intent confidence meets threshold"""
        return self.confidence >= threshold
