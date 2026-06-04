"""
LLM-Based Intent Detector
Uses LLM for superior natural language understanding instead of fuzzy matching
"""

import logging
from typing import Optional, Dict, Any
from llm.llm_client import LLMClient
from .intent_types import IntentType, Intent

logger = logging.getLogger(__name__)


class LLMIntentDetector:
    """
    Advanced intent detector using LLM for natural language understanding.
    Provides more accurate and context-aware intent detection.
    """

    def __init__(self, llm_client: LLMClient):
        """
        Initialize LLM-based intent detector
        
        Args:
            llm_client: LLMClient instance
        """
        self.llm_client = llm_client

    def detect_intent(self, user_input: str) -> Intent:
        """
        Detect user intent using LLM
        
        Args:
            user_input: User input string
            
        Returns:
            Intent object with detected intent type and confidence
        """
        try:
            # Fast path: check for exact command matches first (backup)
            quick_intent = self._quick_check(user_input)
            if quick_intent and quick_intent.confidence > 0.95:
                return quick_intent

            # LLM-based detection for natural language
            prompt = self._build_intent_detection_prompt(user_input)
            
            messages = [
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ]

            response = self.llm_client.generate_text(
                messages=messages,
                max_tokens=200,
                temperature=0.3
            )

            return self._parse_intent_response(response, user_input)

        except Exception as e:
            logger.error(f"Error detecting intent: {str(e)}")
            return Intent(
                intent_type=IntentType.UNCLEAR,
                confidence=0.0,
                raw_input=user_input,
                clarification_message="I had trouble understanding. Could you rephrase that?"
            )

    def _get_system_prompt(self) -> str:
        """Get system prompt for intent detection"""
        return """You are an expert at understanding user intent in a project management system.
Analyze the user's input and determine their intent. Be precise and confident.

Valid intents: greeting, task_creation, project_work, list_items, status, help_request, exit, unclear

Rules:
- If user describes a project or asks to build/create something → task_creation
- If user asks to list, show, or see projects → list_items
- If user asks for status or how things are going → status
- If user asks for help or says 'help' → help_request
- If user says goodbye, exit, or quit → exit
- If user greets (hi, hello, hey, assalam) → greeting
- If you cannot determine intent clearly → unclear"""

    def _build_intent_detection_prompt(self, user_input: str) -> str:
        """Build prompt for intent detection"""
        prompt = f"""Analyze this user input and determine their intent:

User input: "{user_input}"

Respond in exactly this format:
INTENT: [intent_name]
CONFIDENCE: [0.0-1.0]
REASON: [brief reason]
CLARIFICATION: [optional clarification question or message if confidence < 0.9]"""
        return prompt

    def _parse_intent_response(self, response: str, user_input: str) -> Intent:
        """Parse LLM response into Intent object"""
        try:
            intent_type = IntentType.UNCLEAR
            confidence = 0.0
            clarification_message = None

            lines = response.strip().split('\n')
            
            for line in lines:
                if ':' not in line:
                    continue
                    
                key, value = line.split(':', 1)
                key = key.strip().upper()
                value = value.strip()

                if key == "INTENT":
                    intent_str = value.lower().strip()
                    try:
                        intent_type = IntentType[intent_str.upper().replace(' ', '_').replace('-', '_')]
                    except (KeyError, ValueError):
                        intent_type = IntentType.UNCLEAR

                elif key == "CONFIDENCE":
                    try:
                        confidence = float(value)
                    except ValueError:
                        confidence = 0.5

                elif key == "CLARIFICATION":
                    clarification_message = value

            return Intent(
                intent_type=intent_type,
                confidence=min(1.0, max(0.0, confidence)),
                raw_input=user_input,
                clarification_message=clarification_message,
                clarification_needed=confidence < 0.9
            )

        except Exception as e:
            logger.error(f"Error parsing intent response: {str(e)}")
            return Intent(
                intent_type=IntentType.UNCLEAR,
                confidence=0.0,
                raw_input=user_input
            )

    def _quick_check(self, user_input: str) -> Optional[Intent]:
        """
        Quick keyword-based check for obvious intents (backup to LLM)
        
        Args:
            user_input: User input
            
        Returns:
            Intent if obvious, None to use LLM
        """
        user_lower = user_input.lower().strip()

        # Exit commands
        if user_lower in ['exit', 'quit', 'bye', 'goodbye', 'quit()', 'exit()']:
            return Intent(IntentType.EXIT, 0.99, user_input)

        # Help commands
        if user_lower in ['help', '?', 'h', 'ayuda', 'madad', 'help()']:
            return Intent(IntentType.HELP_REQUEST, 0.99, user_input)

        # List commands
        if user_lower in ['list', 'ls', 'projects', 'my projects', 'show projects']:
            return Intent(IntentType.LIST_ITEMS, 0.99, user_input)

        # Status commands
        if user_lower in ['status', 'stat', 'state']:
            return Intent(IntentType.STATUS, 0.99, user_input)

        return None

    def detect_project_type(self, description: str) -> Optional[str]:
        """
        Detect project type from description using LLM
        
        Args:
            description: Project description
            
        Returns:
            Project type or None
        """
        try:
            prompt = f"""What type of project is being described?
Description: "{description}"

Respond with ONLY the project type from this list:
- website
- api
- cli
- script
- data-analysis
- library

If unclear, respond with 'unclear'."""

            messages = [
                {"role": "system", "content": "You are a project classifier."},
                {"role": "user", "content": prompt}
            ]

            response = self.llm_client.generate_text(
                messages=messages,
                max_tokens=20,
                temperature=0.1
            )

            project_type = response.strip().lower()
            
            valid_types = ['website', 'api', 'cli', 'script', 'data-analysis', 'library']
            if project_type in valid_types:
                return project_type
            
            return None

        except Exception as e:
            logger.error(f"Error detecting project type: {str(e)}")
            return None
