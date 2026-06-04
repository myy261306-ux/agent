"""
NLP Converter
Converts natural language intents to structured task parameters
"""

import logging
import json
from typing import Dict, Any, Optional
from .intent_types import IntentType, Intent

logger = logging.getLogger(__name__)


class NLPConverter:
    """
    Converts natural language input and detected intents into structured parameters
    for system operations
    """

    def __init__(self, llm_client=None):
        """
        Initialize the NLP converter

        Args:
            llm_client: Optional LLMClient for complex intent disambiguation
        """
        self.llm_client = llm_client

    def convert_to_task_params(self, intent: Intent) -> Dict[str, Any]:
        """
        Convert an Intent into structured task parameters

        Args:
            intent: Intent object from parser

        Returns:
            Dictionary of task parameters
        """
        if intent.intent_type == IntentType.TASK_CREATION:
            return self._handle_task_creation(intent)
        elif intent.intent_type == IntentType.PROJECT_WORK:
            return self._handle_project_work(intent)
        elif intent.intent_type == IntentType.LIST_ITEMS:
            return {"action": "list_projects"}
        elif intent.intent_type == IntentType.HELP_REQUEST:
            return {"action": "show_help"}
        elif intent.intent_type == IntentType.STATUS:
            return {"action": "show_status"}
        elif intent.intent_type == IntentType.GREETING:
            return {"action": "acknowledge"}
        elif intent.intent_type == IntentType.EXIT:
            return {"action": "exit"}
        else:  # UNCLEAR
            return {
                "action": "clarify",
                "message": intent.clarification_message or "Please clarify your request",
            }

    def _handle_task_creation(self, intent: Intent) -> Dict[str, Any]:
        """
        Convert task creation intent to parameters

        Args:
            intent: Intent object

        Returns:
            Task creation parameters
        """
        params = {"action": "create_project"}

        # Extract project type hints from input
        raw_input = intent.raw_input.lower()
        project_type = self._extract_project_type(raw_input)

        if project_type:
            params["project_type"] = project_type
            logger.debug(f"Detected project type: {project_type}")

        # Check for specific features/requirements in natural language
        params["extracted_input"] = intent.raw_input
        params["needs_clarification"] = intent.clarification_needed

        return params

    def _handle_project_work(self, intent: Intent) -> Dict[str, Any]:
        """
        Convert project work intent to parameters

        Args:
            intent: Intent object

        Returns:
            Project work parameters
        """
        params = {"action": "work_on_project"}
        params["needs_clarification"] = True  # Will need to ask which project

        return params

    def _extract_project_type(self, input_text: str) -> Optional[str]:
        """
        Extract project type from natural language input

        Args:
            input_text: User input (lowercase)

        Returns:
            Project type if detected, None otherwise
        """
        type_keywords = {
            "data-analysis": ["data analysis", "analytics", "dataframe", "pandas", "numpy"],
            "website": ["website", "site", "web", "html", "react", "next"],
            "api": ["api", "backend", "server", "endpoint", "rest"],
            "cli": ["cli", "command", "terminal", "console"],
            "script": ["script", "automation", "bot", "tool"],
            "library": ["library", "package", "module", "sdk", "framework"],
        }

        for project_type, keywords in type_keywords.items():
            for keyword in keywords:
                if keyword in input_text:
                    return project_type

        return None

    def extract_natural_requirements(self, input_text: str) -> Dict[str, Any]:
        """
        Extract specific requirements mentioned in natural language

        Args:
            input_text: Natural language input describing requirements

        Returns:
            Dictionary of extracted requirements
        """
        requirements = {"features": []}

        # Common feature keywords
        feature_keywords = {
            "authentication": ["login", "signin", "signup", "auth", "user account", "password"],
            "database": ["database", "db", "data", "storage", "save"],
            "api": ["api", "endpoint", "rest", "backend"],
            "ui": ["ui", "interface", "design", "visual", "button", "form"],
            "responsive": ["responsive", "mobile", "tablet", "desktop"],
            "testing": ["test", "unit test", "integration test"],
        }

        input_lower = input_text.lower()

        for feature, keywords in feature_keywords.items():
            for keyword in keywords:
                if keyword in input_lower:
                    if feature not in requirements["features"]:
                        requirements["features"].append(feature)

        return requirements

    def clarify_task_creation(self, user_input: str) -> Dict[str, Any]:
        """
        Get clarification questions for task creation

        Args:
            user_input: Original user input

        Returns:
            Dictionary with clarification questions
        """
        questions = {
            "project_name": "What should we call this project?",
            "project_type": "What type of project? (website, api, cli, script, data-analysis, library)",
            "description": "Can you describe what it should do?",
        }

        # Try to extract what we already know
        extracted = {
            "project_type": self._extract_project_type(user_input.lower()),
            "has_description": len(user_input) > 50,
        }

        # Only ask for what we don't know
        questions_needed = {
            "project_name": True,  # Always need project name
            "project_type": extracted["project_type"] is None,
            "description": not extracted["has_description"],
        }

        return {
            "questions": questions,
            "already_extracted": extracted,
            "questions_needed": questions_needed,
        }
