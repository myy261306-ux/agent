"""
Agent Pool Manager
Manages multiple agents and task distribution
"""

import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass

from agents.base_agent import BaseAgent, Task, TaskResult
from agents.code_generator_agent import CodeGeneratorAgent
from agents.debugger_agent import DebuggerAgent
from llm import LLMClient
from utils.logger import setup_logger
from utils.config import Config

logger = setup_logger(__name__)


@dataclass
class AgentPoolStats:
    """Statistics for agent pool"""

    total_agents: int
    active_agents: int
    completed_tasks: int
    failed_tasks: int
    total_tokens: int


class AgentPool:
    """Manages a pool of agents"""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.completed_tasks: List[TaskResult] = []
        self.failed_tasks: List[TaskResult] = []

        self._initialize_agents()

    def _initialize_agents(self) -> None:
        """Initialize the agent pool"""
        logger.info("🚀 Initializing Agent Pool...")

        # Create code generator agents
        num_generators = min(Config.MAX_CONCURRENT_AGENTS - 1, 3)
        for i in range(num_generators):
            agent_id = f"codegen-{i+1}"
            agent = CodeGeneratorAgent(agent_id, self.llm_client)
            agent.task_queue = self.task_queue
            self.agents[agent_id] = agent
            logger.info(f"  ✓ Code Generator Agent created: {agent_id}")

        # Create debugger agent
        debugger_id = "debugger-1"
        debugger = DebuggerAgent(debugger_id, self.llm_client)
        debugger.task_queue = self.task_queue
        self.agents[debugger_id] = debugger
        logger.info(f"  ✓ Debugger Agent created: {debugger_id}")

        logger.info(f"✓ Agent Pool initialized with {len(self.agents)} agents")

    async def start(self) -> None:
        """Start all agents"""
        logger.info("🚀 Starting Agent Pool...")
        tasks = [agent.start() for agent in self.agents.values()]
        await asyncio.gather(*tasks)

    def stop(self) -> None:
        """Stop all agents"""
        logger.info("🛑 Stopping Agent Pool...")
        for agent in self.agents.values():
            agent.stop()

    async def submit_task(self, task: Task) -> str:
        """
        Submit a task to the pool

        Args:
            task: Task to execute

        Returns:
            Task ID
        """
        await self.task_queue.put(task)
        logger.debug(f"Task submitted: {task.task_id} (type: {task.task_type})")
        return task.task_id

    async def submit_tasks(self, tasks: List[Task]) -> List[str]:
        """
        Submit multiple tasks

        Args:
            tasks: List of tasks to execute

        Returns:
            List of task IDs
        """
        task_ids = []
        for task in tasks:
            await self.submit_task(task)
            task_ids.append(task.task_id)
        return task_ids

    async def wait_for_task(self, task_id: str, timeout: int = 300) -> Optional[TaskResult]:
        """
        Wait for a specific task to complete

        Args:
            task_id: ID of task to wait for
            timeout: Max wait time in seconds

        Returns:
            TaskResult when completed, None if timed out
        """
        start_time = asyncio.get_event_loop().time()
        check_interval = 0.5  # Check every 500ms

        while True:
            # Check completed tasks
            for result in self.completed_tasks:
                if result.task_id == task_id:
                    return result

            # Check failed tasks
            for result in self.failed_tasks:
                if result.task_id == task_id:
                    return result

            # Check timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                logger.warning(f"Task {task_id} timed out after {timeout}s")
                return None

            await asyncio.sleep(check_interval)

    def get_agent_stats(self) -> Dict[str, any]:
        """Get statistics for all agents"""
        stats = {}
        for agent_id, agent in self.agents.items():
            stats[agent_id] = agent.get_stats()
        return stats

    def get_pool_stats(self) -> AgentPoolStats:
        """Get overall pool statistics"""
        total_completed = len(self.completed_tasks)
        total_failed = len(self.failed_tasks)
        total_tokens = sum(r.tokens_used for r in self.completed_tasks)
        active_agents = len([a for a in self.agents.values() if a.is_running])

        return AgentPoolStats(
            total_agents=len(self.agents),
            active_agents=active_agents,
            completed_tasks=total_completed,
            failed_tasks=total_failed,
            total_tokens=total_tokens,
        )

    async def record_result(self, result: TaskResult) -> None:
        """Record task result"""
        if result.status == "completed":
            self.completed_tasks.append(result)
            logger.debug(f"Task recorded as completed: {result.task_id}")
        else:
            self.failed_tasks.append(result)
            logger.warning(f"Task recorded as failed: {result.task_id}")
