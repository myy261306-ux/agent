"""
Main Manager - System Orchestrator
Central coordinator for the entire agent system
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from llm import LLMClient
from agents import AgentPool, Task, TaskResult
from project_manager import ProjectManager, Project, ProjectMetadata
from utils.logger import setup_logger
from utils.helpers import generate_task_id, format_timestamp
from utils.config import Config

logger = setup_logger(__name__)


class MainManager:
    """
    Main orchestrator for the agent system
    Coordinates requirements gathering, planning, task assignment, and execution
    """

    def __init__(self):
        logger.info("=" * 60)
        logger.info("🤖 AUTONOMOUS AGENT SYSTEM - INITIALIZING")
        logger.info("=" * 60)

        # Initialize core components
        self.llm_client = LLMClient()
        self.agent_pool = AgentPool(self.llm_client)
        self.project_manager = ProjectManager()

        self.current_project: Optional[Project] = None
        self.current_specification: Optional[str] = None
        self.execution_log: List[Dict[str, Any]] = []

        logger.info("✓ Main Manager initialized successfully")

    async def initialize(self) -> bool:
        """
        Initialize and validate all systems

        Returns:
            True if initialization successful
        """
        logger.info("\n🔍 Validating system configuration...")

        # Validate LLM connections
        provider_status = await self.llm_client.validate_all_connections()
        available_providers = [p for p, s in provider_status.items() if s]

        if not available_providers:
            logger.error("❌ No LLM providers available!")
            return False

        logger.info(f"✓ LLM System ready ({len(available_providers)} providers)")

        # Validate project storage
        try:
            test_projects = self.project_manager.list_projects()
            logger.info(f"✓ Project storage ready ({len(test_projects)} existing projects)")
        except Exception as e:
            logger.error(f"❌ Project storage error: {str(e)}")
            return False

        logger.info("\n✓ System initialization complete!\n")
        return True

    async def start_new_project(
        self, project_name: str, project_type: str, description: str = ""
    ) -> Project:
        """
        Start a new project

        Args:
            project_name: Name of the project
            project_type: Type of project (website, api, script, etc.)
            description: Project description

        Returns:
            Created Project object
        """
        logger.info(f"\n📋 Starting new project: {project_name}")

        project = self.project_manager.create_project(project_name, project_type, description)
        self.current_project = project

        # Initialize metadata
        metadata = ProjectMetadata(
            project_id=project.project_id,
            name=project_name,
            type=project_type,
            status="planning",
            created_at=format_timestamp(),
            updated_at=format_timestamp(),
            description=description,
        )

        project.save_metadata(metadata)
        project.add_log(f"Project started: {project_name}")

        logger.info(f"✓ Project created: {project.project_id}")
        return project

    async def gather_requirements(self) -> str:
        """
        Gather requirements interactively using LLM

        Returns:
            Requirements document
        """
        if not self.current_project:
            raise RuntimeError("No project selected")

        logger.info("\n❓ Gathering requirements using AI...")

        system_prompt = """You are an expert requirements gatherer. Your job is to ask detailed 
        questions to understand the user's project needs. Be thorough but concise. Format your 
        response with clear questions separated by newlines."""

        project_info = f"""Project Name: {self.current_project.name}
Project Type: {self.current_project.type}
Description: {self.current_project}"""

        prompt = f"""I'm starting a new {self.current_project.type} project called "{self.current_project.name}".

{self.current_project}

Please generate a comprehensive list of questions to understand all requirements for this project. 
Focus on:
1. Project goals and objectives
2. Target users and use cases
3. Key features needed
4. Technical requirements
5. Design preferences
6. Timeline and priorities

Generate questions in a numbered list format."""

        try:
            response = await self.llm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=2000,
            )

            requirements = response.content
            self.current_project.save_requirements(requirements)
            self.current_project.add_log("Requirements gathered")

            logger.info("✓ Requirements gathered from AI")
            return requirements

        except Exception as e:
            logger.error(f"✗ Requirements gathering failed: {str(e)}")
            raise

    async def generate_specification(self, requirements: str, user_answers: str = "") -> str:
        """
        Generate detailed specification from requirements

        Args:
            requirements: Requirements document
            user_answers: User's answers to questions

        Returns:
            Specification document
        """
        if not self.current_project:
            raise RuntimeError("No project selected")

        logger.info("\n📐 Generating specification...")

        system_prompt = """You are an expert technical architect. Convert requirements and answers 
        into a detailed, structured technical specification. Include all necessary implementation details."""

        prompt = f"""Based on the following requirements and answers, generate a comprehensive 
technical specification for a {self.current_project.type} project.

Project: {self.current_project.name}

Requirements:
{requirements}

User Answers:
{user_answers if user_answers else "Not provided yet"}

Generate a detailed specification including:
1. Project Overview
2. Functional Requirements
3. Technical Architecture
4. Technology Stack
5. Database Schema (if applicable)
6. API Endpoints (if applicable)
7. Frontend Components (if applicable)
8. Security Requirements
9. Performance Requirements
10. Testing Strategy
11. Deployment Plan

Format as a markdown document."""

        try:
            response = await self.llm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=4000,
            )

            specification = response.content
            self.current_specification = specification
            self.current_project.save_specification(specification)
            self.current_project.add_log("Specification generated")

            logger.info("✓ Specification generated")
            return specification

        except Exception as e:
            logger.error(f"✗ Specification generation failed: {str(e)}")
            raise

    async def plan_tasks(self) -> List[Task]:
        """
        Create execution plan from specification

        Returns:
            List of tasks for agents
        """
        if not self.current_project or not self.current_specification:
            raise RuntimeError("Project or specification not set")

        logger.info("\n🎯 Planning execution tasks...")

        system_prompt = """You are an expert project planner. Break down the specification 
        into concrete, actionable development tasks."""

        prompt = f"""Based on this specification, create a detailed task plan for development.

Specification:
{self.current_specification}

Create a detailed task breakdown in JSON format with the following structure:
[
  {{
    "task_id": "string",
    "name": "string",
    "type": "code_generation|testing|integration",
    "priority": "high|medium|low",
    "description": "string",
    "requirements": {{}},
    "dependencies": []
  }}
]

Generate 5-10 concrete, executable tasks."""

        try:
            response = await self.llm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=3000,
            )

            # Parse tasks from response
            tasks = self._parse_tasks_from_response(response.content)
            self.current_project.add_log(f"Execution plan created: {len(tasks)} tasks")

            logger.info(f"✓ Created execution plan with {len(tasks)} tasks")
            return tasks

        except Exception as e:
            logger.error(f"✗ Task planning failed: {str(e)}")
            raise

    def _parse_tasks_from_response(self, response: str) -> List[Task]:
        """Parse tasks from LLM response"""
        # Simplified parsing - in production this would be more robust
        tasks = []

        # Extract JSON if present
        import json
        import re

        json_match = re.search(r"\[.*\]", response, re.DOTALL)
        if json_match:
            try:
                task_data = json.loads(json_match.group())
                for item in task_data:
                    task = Task(
                        task_id=generate_task_id(item.get("type", "task")),
                        task_type=item.get("type", "code_generation"),
                        requirements=item.get("requirements", {}),
                        priority=item.get("priority", "medium"),
                    )
                    tasks.append(task)
            except json.JSONDecodeError:
                logger.warning("Failed to parse tasks as JSON, creating default tasks")

        # Create default task if parsing failed
        if not tasks:
            task = Task(
                task_id=generate_task_id("default"),
                task_type="code_generation",
                requirements={"description": response},
                priority="high",
            )
            tasks.append(task)

        return tasks

    async def execute_project(self, tasks: List[Task]) -> Dict[str, TaskResult]:
        """
        Execute project tasks using agent pool

        Args:
            tasks: List of tasks to execute

        Returns:
            Dictionary of results
        """
        if not self.current_project:
            raise RuntimeError("No project selected")

        logger.info(f"\n🚀 Executing {len(tasks)} tasks...")

        results = {}

        # Submit all tasks
        task_ids = await self.agent_pool.submit_tasks(tasks)
        logger.info(f"Submitted {len(task_ids)} tasks to agent pool")

        # Wait for all tasks to complete
        for task_id in task_ids:
            result = await self.agent_pool.wait_for_task(task_id, timeout=300)
            if result:
                results[task_id] = result
                status = "✓" if result.status == "completed" else "✗"
                logger.info(f"{status} Task completed: {task_id}")
            else:
                logger.warning(f"⏱ Task timed out: {task_id}")

        # Record completion
        self.current_project.add_log(f"Project execution completed: {len(results)} tasks")

        logger.info(f"\n✓ Project execution complete ({len(results)}/{len(tasks)} tasks)")
        return results

    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        pool_stats = self.agent_pool.get_pool_stats()

        return {
            "timestamp": format_timestamp(),
            "current_project": self.current_project.name if self.current_project else None,
            "agent_pool": {
                "total_agents": pool_stats.total_agents,
                "active_agents": pool_stats.active_agents,
                "completed_tasks": pool_stats.completed_tasks,
                "failed_tasks": pool_stats.failed_tasks,
                "total_tokens": pool_stats.total_tokens,
            },
            "llm_providers": self.llm_client.get_provider_info(),
        }

    def display_status(self) -> None:
        """Display formatted status"""
        status = self.get_status()

        print("\n" + "=" * 60)
        print("📊 SYSTEM STATUS")
        print("=" * 60)

        if status["current_project"]:
            print(f"Current Project: {status['current_project']}")

        print(f"\nAgent Pool:")
        print(f"  Total Agents: {status['agent_pool']['total_agents']}")
        print(f"  Active Agents: {status['agent_pool']['active_agents']}")
        print(f"  Completed Tasks: {status['agent_pool']['completed_tasks']}")
        print(f"  Failed Tasks: {status['agent_pool']['failed_tasks']}")
        print(f"  Total Tokens Used: {status['agent_pool']['total_tokens']}")

        print(f"\nLLM Providers ({status['llm_providers']['total_providers']}):")
        for provider in status["llm_providers"]["providers"]:
            print(f"  - {provider['name']} ({provider['model']})")

        print("=" * 60 + "\n")
