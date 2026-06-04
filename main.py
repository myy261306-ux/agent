#!/usr/bin/env python3
"""
Agent System - Main Entry Point
Command-line interface for the autonomous agent system
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from main_manager import MainManager
from utils.logger import system_logger
from utils.config import Config
from input_handlers import CommandParser, NLPConverter, IntentType

logger = system_logger


async def main():
    """Main entry point"""
    try:
        # Initialize system
        manager = MainManager()

        # Initialize and validate
        if not await manager.initialize():
            logger.error("System initialization failed")
            return 1

        # Display available commands
        print_welcome_message()

        # Initialize NLI components
        command_parser = CommandParser(manager.llm_client)
        nlp_converter = NLPConverter(manager.llm_client)

        # Interactive loop
        while True:
            try:
                user_input = input("\n🤖 Enter command or natural language (help for options): ").strip()

                if not user_input:
                    continue

                # Parse input using NLI
                intent = command_parser.parse(user_input)

                # Handle based on detected intent
                await handle_intent(intent, manager, nlp_converter)

            except KeyboardInterrupt:
                logger.info("\nShutting down...")
                manager.agent_pool.stop()
                break
            except Exception as e:
                logger.error(f"Error: {str(e)}")

        logger.info("✓ System shutdown complete")
        return 0

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        return 1


async def handle_intent(intent, manager: MainManager, nlp_converter: NLPConverter) -> None:
    """
    Route user intent to appropriate handler

    Args:
        intent: Intent object from parser
        manager: MainManager instance
        nlp_converter: NLPConverter instance
    """
    if intent.intent_type == IntentType.HELP_REQUEST:
        print_help()

    elif intent.intent_type == IntentType.TASK_CREATION:
        # Ask for clarification if needed
        if intent.clarification_needed or intent.confidence < 0.9:
            logger.info("📝 Let me gather more details about your project...")
            await handle_new_project(manager)
        else:
            await handle_new_project(manager)

    elif intent.intent_type == IntentType.PROJECT_WORK:
        await handle_work(manager)

    elif intent.intent_type == IntentType.LIST_ITEMS:
        await handle_list_projects(manager)

    elif intent.intent_type == IntentType.STATUS:
        manager.display_status()

    elif intent.intent_type == IntentType.GREETING:
        print("👋 Hello! What would you like to do? Type 'help' for options or describe your project.")

    elif intent.intent_type == IntentType.EXIT:
        logger.info("Shutting down system...")
        manager.agent_pool.stop()
        raise KeyboardInterrupt()

    elif intent.intent_type == IntentType.UNCLEAR:
        # Ask for clarification
        if intent.clarification_message:
            print(f"🤔 {intent.clarification_message}")
        else:
            print("I didn't understand that. Try:")
            print("  - 'new' to create a project")
            print("  - 'work' to work on a project")
            print("  - 'list' to see your projects")
            print("  - 'help' for all commands")


async def handle_new_project(manager: MainManager) -> None:
    """Handle 'new' command to create new project"""
    print("\n" + "=" * 60)
    print("📋 CREATE NEW PROJECT")
    print("=" * 60)

    project_name = input("Project name: ").strip()
    if not project_name or len(project_name) < 3:
        logger.warning("Project name must be at least 3 characters")
        return

    print("\nProject types: website, api, cli, script, data-analysis, library")
    project_type = input("Project type: ").strip().lower()
    if not project_type:
        project_type = "website"

    description = input("Project description (optional): ").strip()

    # Create project
    project = await manager.start_new_project(project_name, project_type, description)

    # Gather requirements
    requirements = await manager.gather_requirements()

    # Generate specification
    specification = await manager.generate_specification(requirements)

    # Ask if user wants to proceed
    print("\n" + "=" * 60)
    print("📋 SPECIFICATION PREVIEW")
    print("=" * 60)
    print(specification[:500] + "..." if len(specification) > 500 else specification)
    print("=" * 60)

    proceed = input("\n✓ Proceed with execution? (yes/no): ").strip().lower()
    if proceed != "yes":
        logger.info("Project creation cancelled")
        return

    # Plan tasks
    tasks = await manager.plan_tasks()

    # Execute
    results = await manager.execute_project(tasks)

    logger.info(f"\n✓ Project execution complete!")
    logger.info(f"✓ Project saved at: {project.base_path}")


async def handle_work(manager: MainManager) -> None:
    """Handle 'work' command to work on existing project"""
    projects = manager.project_manager.list_projects()

    if not projects:
        logger.warning("No projects found")
        return

    print("\n📚 EXISTING PROJECTS:")
    for i, project in enumerate(projects, 1):
        print(f"{i}. {project['name']} ({project['type']}) - {project['status']}")

    try:
        choice = int(input("\nSelect project number: "))
        if 1 <= choice <= len(projects):
            project_id = projects[choice - 1]["id"]
            project = manager.project_manager.get_project(project_id)
            manager.current_project = project
            logger.info(f"✓ Loaded project: {project.name}")
        else:
            logger.warning("Invalid selection")
    except ValueError:
        logger.warning("Invalid input")


async def handle_list_projects(manager: MainManager) -> None:
    """Handle 'list' command to show all projects"""
    projects = manager.project_manager.list_projects()

    if not projects:
        logger.info("No projects found")
        return

    print("\n" + "=" * 60)
    print("📚 ALL PROJECTS")
    print("=" * 60)

    for project in projects:
        print(f"\n📁 {project['name']}")
        print(f"   ID: {project['id']}")
        print(f"   Type: {project['type']}")
        print(f"   Status: {project['status']}")
        print(f"   Created: {project['created_at']}")

    print("\n" + "=" * 60)


def print_welcome_message() -> None:
    """Print welcome message"""
    print("\n" + "=" * 60)
    print("🤖 AUTONOMOUS AGENT SYSTEM")
    print("=" * 60)
    print("Multi-LLM Agent System with Fallback Strategy")
    print(f"Providers: {', '.join(Config.get_available_providers())}")
    print("=" * 60)
    print("Type 'help' for available commands")
    print("=" * 60 + "\n")


def print_help() -> None:
    """Print help information"""
    print("\n" + "=" * 60)
    print("📖 AVAILABLE COMMANDS")
    print("=" * 60)
    print(
        """
COMMANDS (Traditional):
  new          - Create a new project
  work         - Work on existing project
  list         - List all projects
  status       - Show system status
  help         - Show this help message
  exit/quit    - Shut down system

NATURAL LANGUAGE (Supported):
  "build a website"            - Create a new project
  "mujhe app bana do"          - Create a new project (Urdu)
  "show my projects"           - List all projects
  "what's the status?"         - Show system status
  "hello"                      - Greet the system
  "help me"                    - Show this help

WORKFLOW:
  1. Type 'new' or 'build something' to create a project
  2. System will ask requirements interactively
  3. Specification will be generated automatically
  4. Agents will execute and build your project
  5. Results will be saved in ~/agent-projects/
"""
    )
    print("=" * 60 + "\n")


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
