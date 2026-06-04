"""
Command Parser
Intelligent intent detection from user input (natural language + command-based)
"""

import logging
from typing import Dict, List, Optional, Any
from .intent_types import IntentType, Intent

logger = logging.getLogger(__name__)


class CommandParser:
    """
    Parses user input and detects intent using keyword matching and pattern recognition
    Provides fallback to LLM for ambiguous inputs
    """

    def __init__(self, llm_client=None):
        """
        Initialize the command parser

        Args:
            llm_client: Optional LLMClient for complex intent resolution
        """
        self.llm_client = llm_client
        self.keyword_patterns = self._initialize_patterns()

    def _initialize_patterns(self) -> Dict[IntentType, Dict[str, List[str]]]:
        """Initialize keyword patterns for each intent type"""
        return {
            IntentType.GREETING: {
                "keywords": ["hello", "hi", "hey", "greetings", "namaste", "assalam", "salam"],
                "urdu_keywords": ["سلام", "ہلو", "ہیلو", "نمستے"],
            },
            IntentType.TASK_CREATION: {
                "keywords": ["create", "build", "make", "develop", "generate", "start", "new project", "new", "bana do"],
                "urdu_keywords": ["بنانا", "بناؤ", "بنا دو", "تیار کرو", "بنایا"],
            },
            IntentType.HELP_REQUEST: {
                "keywords": ["help", "how", "guide", "tutorial", "assist", "?", "what can you do"],
                "urdu_keywords": ["مدد", "کیسے", "رہنمائی", "مثال"],
            },
            IntentType.PROJECT_WORK: {
                "keywords": ["work", "open", "continue", "resume", "edit", "modify", "update"],
                "urdu_keywords": ["کریں", "کھولیں", "جاری رکھیں", "ترمیم"],
            },
            IntentType.LIST_ITEMS: {
                "keywords": ["list", "show", "display", "view", "projects", "all", "recent"],
                "urdu_keywords": ["لسٹ", "دکھایں", "دیکھیں", "ایل"],
            },
            IntentType.STATUS: {
                "keywords": ["status", "how are you", "what's up", "current", "stats", "progress"],
                "urdu_keywords": ["حالت", "کیسے ہو", "حالات"],
            },
            IntentType.EXIT: {
                "keywords": ["exit", "quit", "bye", "goodbye", "exit system", "close"],
                "urdu_keywords": ["باہر", "الوداع", "خدا حافظ"],
            },
        }

    def parse(self, user_input: str) -> Intent:
        """
        Parse user input and determine intent

        Args:
            user_input: Raw user input string

        Returns:
            Intent object with detected type and confidence
        """
        user_input = user_input.strip()

        if not user_input:
            return Intent(
                intent_type=IntentType.UNCLEAR,
                confidence=0.0,
                raw_input=user_input,
                extracted_params={},
                clarification_needed=True,
                clarification_message="Please enter a command or natural language request.",
            )

        # Try keyword-based matching first (fast)
        keyword_match = self._try_keyword_matching(user_input)
        if keyword_match and keyword_match.confidence > 0.8:
            return keyword_match

        # If LLM available and keyword matching is uncertain, use LLM for disambiguation
        if self.llm_client:
            llm_intent = self._try_llm_parsing(user_input)
            if llm_intent:
                return llm_intent

        # Fallback: return uncertain intent
        if keyword_match:
            return keyword_match

        return Intent(
            intent_type=IntentType.UNCLEAR,
            confidence=0.5,
            raw_input=user_input,
            extracted_params={"user_input": user_input},
            clarification_needed=True,
            clarification_message="I didn't understand that. Try: 'new', 'list', 'work', 'help', or describe what you want to do.",
        )

    def _try_keyword_matching(self, user_input: str) -> Optional[Intent]:
        """
        Try to match input against known keyword patterns

        Args:
            user_input: User input to match

        Returns:
            Intent if match found, None otherwise
        """
        user_input_lower = user_input.lower()
        best_match: Optional[Intent] = None
        best_score = 0.0

        for intent_type, patterns in self.keyword_patterns.items():
            keywords = patterns.get("keywords", []) + patterns.get("urdu_keywords", [])

            # Check for exact or partial matches
            for keyword in keywords:
                if keyword in user_input_lower:
                    # Calculate confidence based on match quality
                    confidence = min(1.0, len(keyword) / len(user_input_lower) * 2)

                    if confidence > best_score:
                        best_score = confidence
                        best_match = Intent(
                            intent_type=intent_type,
                            confidence=confidence,
                            raw_input=user_input,
                            extracted_params={"keyword": keyword},
                        )

        return best_match

    def _try_llm_parsing(self, user_input: str) -> Optional[Intent]:
        """
        Use LLM to parse ambiguous input for intent detection

        Args:
            user_input: User input to parse

        Returns:
            Intent if LLM can determine it, None otherwise
        """
        if not self.llm_client:
            return None

        try:
            # Prepare prompt for LLM
            prompt = f"""You are an intelligent command parser. Analyze this user input and determine the intent.

User input: "{user_input}"

Respond with ONLY a JSON object (no markdown, no extra text):
{{
  "intent": "greeting|task_creation|help_request|project_work|list_items|status|exit|unclear",
  "confidence": 0.0-1.0,
  "extracted_params": {{}}
}}

Example response:
{{"intent": "task_creation", "confidence": 0.95, "extracted_params": {{"project_type": "website"}}}}
"""

            # This would require making the parse method async, which we'll handle in the main loop
            # For now, return None to indicate LLM parsing wasn't possible
            logger.debug(f"LLM parsing requested for: {user_input}")
            return None

        except Exception as e:
            logger.error(f"LLM parsing error: {str(e)}")
            return None

    def get_keywords_for_intent(self, intent_type: IntentType) -> List[str]:
        """Get all keywords for a specific intent type"""
        patterns = self.keyword_patterns.get(intent_type, {})
        return patterns.get("keywords", []) + patterns.get("urdu_keywords", [])
