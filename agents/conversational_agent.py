"""
Conversational Agent
Intelligent dialogue handler using LLM for natural conversation and project planning
"""

import logging
from typing import Optional, Dict, Any
from llm.llm_client import LLMClient

logger = logging.getLogger(__name__)


class ConversationalAgent:
    """
    Conversational agent that engages in natural dialogue with users.
    Uses LLM to understand intent and generate appropriate responses.
    """

    def __init__(self, llm_client: LLMClient):
        """
        Initialize conversational agent
        
        Args:
            llm_client: LLMClient instance for language model access
        """
        self.llm_client = llm_client
        self.conversation_history: list[Dict[str, str]] = []
        self.project_context: Dict[str, Any] = {}
        
        # System prompt for the agent
        self.system_prompt = """You are a helpful AI assistant for a software development automation system.
Your role is to:
1. Have natural conversations with users in English or Urdu
2. Understand what kind of project they want to build
3. Ask clarifying questions to gather requirements
4. Be friendly, concise, and helpful

When a user describes a project idea:
- Ask 2-3 clarifying questions about their requirements
- Understand the project type (website, API, CLI, etc.)
- Gather information about key features and functionality
- Be encouraging and supportive

Keep responses brief (1-3 sentences) and natural. Respond in the same language the user uses."""

    async def chat(self, user_message: str) -> str:
        """
        Process user message and generate response
        
        Args:
            user_message: User input message
            
        Returns:
            Agent response
        """
        try:
            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })

            # Format conversation as text
            conversation_text = self._format_conversation_for_prompt()

            # Get response from LLM
            response = await self.llm_client.generate(
                prompt=conversation_text,
                system_prompt=self.system_prompt,
                max_tokens=300,
                temperature=0.7
            )

            # Extract text from response
            agent_response = response.text.strip()

            # Add agent response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": agent_response
            })

            return agent_response

        except Exception as e:
            logger.error(f"Error in conversational agent: {str(e)}")
            return "I encountered an issue processing that. Could you please rephrase?"

    def _format_conversation_for_prompt(self) -> str:
        """
        Format conversation history into a prompt string
        
        Returns:
            Formatted conversation text
        """
        text_parts = []
        
        # Add recent conversation history
        for msg in self.conversation_history[-10:]:
            role = msg["role"].capitalize()
            content = msg["content"]
            text_parts.append(f"{role}: {content}")
        
        # Add prompt for agent to respond
        text_parts.append("Assistant:")
        
        return "\n".join(text_parts)

    async def analyze_project_description(self, description: str) -> Dict[str, Any]:
        """
        Analyze user's project description and extract key information
        
        Args:
            description: User's project description
            
        Returns:
            Structured project information
        """
        try:
            analysis_prompt = f"""Analyze this project description and extract key information in a structured format.

Project Description: "{description}"

Provide analysis in this exact format (one item per line):
PROJECT_TYPE: [website/api/cli/script/data-analysis/library]
KEY_FEATURES: [list main features, separated by semicolons]
ESTIMATED_COMPLEXITY: [simple/medium/complex]
TECH_STACK: [suggested technologies, separated by semicolons]
DEPENDENCIES: [external dependencies or integrations needed]
IS_PROJECT_DESCRIPTION: [yes/no - is this clearly a project description?]

Be concise and practical."""

            system_prompt = "You are a software project analyzer. Extract key information from project descriptions."

            response = await self.llm_client.generate(
                prompt=analysis_prompt,
                system_prompt=system_prompt,
                max_tokens=300,
                temperature=0.3
            )

            # Parse the response
            return self._parse_project_analysis(response.text)

        except Exception as e:
            logger.error(f"Error analyzing project description: {str(e)}")
            return {"error": str(e)}

    def _parse_project_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """
        Parse LLM's project analysis response
        
        Args:
            analysis_text: Raw analysis from LLM
            
        Returns:
            Structured project data
        """
        result = {
            "project_type": None,
            "key_features": [],
            "complexity": None,
            "tech_stack": [],
            "dependencies": [],
            "is_project_description": False
        }

        try:
            lines = analysis_text.strip().split('\n')
            
            for line in lines:
                if ':' not in line:
                    continue
                    
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()

                if key == "project_type":
                    result["project_type"] = value.lower()
                elif key == "key_features":
                    result["key_features"] = [f.strip() for f in value.split(';') if f.strip()]
                elif key == "estimated_complexity":
                    result["complexity"] = value.lower()
                elif key == "tech_stack":
                    result["tech_stack"] = [t.strip() for t in value.split(';') if t.strip()]
                elif key == "dependencies":
                    result["dependencies"] = [d.strip() for d in value.split(';') if d.strip()]
                elif key == "is_project_description":
                    result["is_project_description"] = value.lower() in ['yes', 'true', '1']

            return result

        except Exception as e:
            logger.error(f"Error parsing project analysis: {str(e)}")
            return result

    def should_create_project(self, user_message: str) -> bool:
        """
        Determine if user wants to create a project based on conversation
        
        Args:
            user_message: Latest user message
            
        Returns:
            True if user wants to create a project
        """
        project_keywords = [
            "creat", "build", "make", "develop", "generate", "website", "app",
            "api", "project", "bana", "develop", "application", "tool", "script",
            "ok let's go", "yes", "ha", "ji", "theek ha"
        ]
        
        user_lower = user_message.lower()
        return any(keyword in user_lower for keyword in project_keywords)

    def clear_history(self) -> None:
        """Clear conversation history"""
        self.conversation_history = []
        self.project_context = {}

    def get_context(self) -> Dict[str, Any]:
        """Get current project context"""
        return self.project_context.copy()

    def set_context(self, context: Dict[str, Any]) -> None:
        """Set project context"""
        self.project_context = context
