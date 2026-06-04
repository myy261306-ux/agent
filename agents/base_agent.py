"""
Base Agent Class
Abstract base for all agent types
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class Task:
    """Task structure for agents"""

    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    task_type: str = ""
    requirements: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    priority: str = "medium"  # high, medium, low
    status: str = "pending"  # pending, in_progress, completed, failed
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class TaskResult:
    """Result structure from agent task execution"""

    task_id: str
    status: str  # completed, failed, in_progress
    output: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: list = field(default_factory=list)
    tokens_used: int = 0


class BaseAgent(ABC):
    """Abstract base class for all agents"""

    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.logger = setup_logger(f"Agent-{agent_type}")
        self.task_queue: asyncio.Queue = None
        self.is_running = False
        self.current_task: Optional[Task] = None
        self.total_tokens_used = 0
        self.tasks_completed = 0

        self.logger.info(f"✓ Agent initialized: {agent_id} (type: {agent_type})")

    @abstractmethod
    async def process_task(self, task: Task) -> TaskResult:
        """
        Process a task
        Must be implemented by subclasses

        Args:
            task: Task to process

        Returns:
            TaskResult with output or errors
        """
        pass

    async def start(self) -> None:
        """Start agent and listen for tasks"""
        if not self.task_queue:
            raise RuntimeError("Task queue not set")

        self.is_running = True
        self.logger.info(f"🚀 Agent started and listening for tasks")

        try:
            while self.is_running:
                try:
                    # Wait for task with timeout to allow graceful shutdown
                    task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                    await self.execute_task(task)
                except asyncio.TimeoutError:
                    # No task available, continue listening
                    continue
                except asyncio.CancelledError:
                    break
        finally:
            self.is_running = False
            self.logger.info(f"🛑 Agent stopped")

    async def execute_task(self, task: Task) -> None:
        """Execute a single task"""
        self.current_task = task
        task.status = "in_progress"
        task.started_at = datetime.now().isoformat()

        self.logger.debug(f"Processing task: {task.task_id} ({task.task_type})")

        try:
            result = await self.process_task(task)
            self.tasks_completed += 1
            self.total_tokens_used += result.tokens_used

            task.status = result.status
            task.completed_at = datetime.now().isoformat()

            if result.status == "completed":
                self.logger.info(
                    f"✓ Task completed: {task.task_id} ({result.tokens_used} tokens)"
                )
            else:
                self.logger.warning(f"⚠ Task failed: {task.task_id}")
                if result.errors:
                    for error in result.errors:
                        self.logger.error(f"  Error: {error}")

        except Exception as e:
            task.status = "failed"
            task.completed_at = datetime.now().isoformat()
            self.logger.error(f"✗ Exception during task execution: {str(e)}")

        self.current_task = None

    def stop(self) -> None:
        """Stop agent gracefully"""
        self.is_running = False
        self.logger.info("Stopping agent...")

    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "is_running": self.is_running,
            "tasks_completed": self.tasks_completed,
            "total_tokens_used": self.total_tokens_used,
            "current_task": self.current_task.task_id if self.current_task else None,
        }
