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

        # Interactive loop
        while True:
            try:
                command = input("\n🤖 Enter command (help for options): ").strip().lower()

                if not command:
                    continue

                if command == "help":
                    print_help()

                elif command == "new":
                    await handle_new_project(manager)

                elif command == "work":
                    await handle_work(manager)

                elif command == "status":
                    manager.display_status()

                elif command == "list":
                    await handle_list_projects(manager)

                elif command == "exit" or command == "quit":
                    logger.info("Shutting down system...")
                    manager.agent_pool.stop()
                    break

                else:
                    logger.warning(f"Unknown command: {command}")
                    print("Type 'help' for available commands")

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
  new          - Create a new project
  work         - Work on existing project
  list         - List all projects
  status       - Show system status
  help         - Show this help message
  exit/quit    - Shut down system

WORKFLOW:
  1. 'new' to create a project
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
