"""
Code Generator Agent
Generates code based on specifications and requirements
"""

import asyncio
from typing import Dict, Any

from agents.base_agent import BaseAgent, Task, TaskResult
from llm import LLMClient
from utils.logger import setup_logger

logger = setup_logger(__name__)


class CodeGeneratorAgent(BaseAgent):
    """Agent responsible for code generation"""

    def __init__(self, agent_id: str, llm_client: LLMClient):
        super().__init__(agent_id, "code_generator")
        self.llm_client = llm_client

    async def process_task(self, task: Task) -> TaskResult:
        """
        Process a code generation task

        Args:
            task: Task containing requirements and specifications

        Returns:
            TaskResult with generated code
        """
        try:
            requirements = task.requirements
            specification = task.context.get("specification", "")

            # Prepare prompt
            system_prompt = """You are an expert code generator. Generate clean, well-structured, 
            professional code that follows best practices. Include proper error handling, 
            type hints (if applicable), and documentation."""

            prompt = self._build_prompt(requirements, specification, task.task_type)

            logger.debug(f"Generating code for: {requirements.get('feature', 'unknown')}")

            # Generate code using LLM
            response = await self.llm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,  # Lower temperature for code generation
                max_tokens=4000,
            )

            # Parse response and extract code
            generated_code = response.content

            result = TaskResult(
                task_id=task.task_id,
                status="completed",
                output={
                    "code": generated_code,
                    "language": requirements.get("language", "python"),
                    "filename": requirements.get("filename", "generated.py"),
                    "description": requirements.get("description", ""),
                },
                metadata={
                    "provider": response.provider,
                    "model": response.model,
                    "finish_reason": response.finish_reason,
                },
                tokens_used=response.tokens_used,
            )

            logger.info(
                f"✓ Code generated for {requirements.get('feature', 'unknown')} ({response.tokens_used} tokens)"
            )
            return result

        except Exception as e:
            logger.error(f"✗ Code generation failed: {str(e)}")
            return TaskResult(
                task_id=task.task_id,
                status="failed",
                errors=[str(e)],
            )

    def _build_prompt(
        self, requirements: Dict[str, Any], specification: str, task_type: str
    ) -> str:
        """Build prompt for code generation"""

        feature = requirements.get("feature", "")
        description = requirements.get("description", "")
        language = requirements.get("language", "python")
        framework = requirements.get("framework", "")
        constraints = requirements.get("constraints", [])

        prompt = f"""Generate {language} code for the following requirement:

Feature: {feature}
Description: {description}
Framework: {framework if framework else "None"}

Specification:
{specification}

Constraints:
{chr(10).join([f"- {c}" for c in constraints]) if constraints else "- No specific constraints"}

Requirements:
1. Write clean, readable, well-documented code
2. Include type hints if applicable
3. Include proper error handling
4. Follow {language} best practices
5. Include docstrings for functions

Generate the complete code:"""

        return prompt
