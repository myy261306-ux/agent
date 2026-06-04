"""
Utility Helper Functions
Common utility functions used across the system
"""

import uuid
import json
import asyncio
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime
import hashlib


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix"""
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}_{unique_id}" if prefix else unique_id


def generate_task_id(task_type: str = "task") -> str:
    """Generate a unique task ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique = str(uuid.uuid4())[:6]
    return f"{task_type}_{timestamp}_{unique}"


def ensure_directory(path: str) -> Path:
    """Ensure directory exists, create if needed"""
    p = Path(path).expanduser()
    p.mkdir(parents=True, exist_ok=True)
    return p


def save_json(data: Dict[str, Any], file_path: str) -> None:
    """Save data as JSON file"""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def load_json(file_path: str) -> Dict[str, Any]:
    """Load JSON file"""
    path = Path(file_path)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def read_file(file_path: str) -> str:
    """Read text file"""
    with open(Path(file_path), "r") as f:
        return f.read()


def write_file(file_path: str, content: str) -> None:
    """Write text file"""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def append_file(file_path: str, content: str) -> None:
    """Append to text file"""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(content)


def hash_text(text: str) -> str:
    """Generate SHA256 hash of text"""
    return hashlib.sha256(text.encode()).hexdigest()[:12]


def format_timestamp() -> str:
    """Get formatted current timestamp"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


async def run_async_tasks(tasks: List, max_concurrent: int = 5) -> List[Any]:
    """
    Run multiple async tasks with concurrency limit

    Args:
        tasks: List of coroutines to run
        max_concurrent: Maximum concurrent tasks

    Returns:
        List of results
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def bounded_task(task):
        async with semaphore:
            return await task

    return await asyncio.gather(*[bounded_task(task) for task in tasks])


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def format_file_size(size_bytes: int) -> str:
    """Format bytes to human readable size"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def validate_project_name(name: str) -> bool:
    """Validate project name"""
    if not name or len(name) < 3:
        return False
    if not name.replace("-", "").replace("_", "").isalnum():
        return False
    return True
