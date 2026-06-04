"""
Project Management Module
Handles project storage, metadata, and tracking
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from utils.helpers import (
    generate_id,
    ensure_directory,
    save_json,
    load_json,
    format_timestamp,
)
from utils.logger import setup_logger
from utils.config import Config

logger = setup_logger(__name__)


@dataclass
class ProjectMetadata:
    """Project metadata structure"""

    project_id: str
    name: str
    type: str  # "website", "api", "cli", "script", etc.
    status: str  # "planning", "development", "testing", "completed"
    created_at: str
    updated_at: str
    description: str = ""
    target_users: str = ""
    requirements_count: int = 0
    agents_assigned: List[str] = None
    estimated_tokens: int = 0
    actual_tokens: int = 0
    test_results: Dict[str, Any] = None

    def __post_init__(self):
        if self.agents_assigned is None:
            self.agents_assigned = []
        if self.test_results is None:
            self.test_results = {}

    def to_dict(self):
        return asdict(self)


class Project:
    """Project management class"""

    def __init__(self, project_id: str, name: str, project_type: str):
        self.project_id = project_id
        self.name = name
        self.type = project_type
        self.base_path = Path(Config.PROJECTS_DIR) / project_id
        self.src_path = self.base_path / "src"
        self.tests_path = self.base_path / "tests"
        self.logs_path = self.base_path / "logs"
        self.docs_path = self.base_path / "docs"

        # Create directories
        ensure_directory(str(self.base_path))
        ensure_directory(str(self.src_path))
        ensure_directory(str(self.tests_path))
        ensure_directory(str(self.logs_path))
        ensure_directory(str(self.docs_path))

        self.metadata_file = self.base_path / ".agent-metadata.json"
        self.requirements_file = self.base_path / "requirements.md"
        self.specification_file = self.base_path / "specification.md"
        self.log_file = self.logs_path / "project.log"

        logger.info(f"✓ Project initialized: {name} ({project_id})")

    def save_metadata(self, metadata: ProjectMetadata) -> None:
        """Save project metadata"""
        save_json(metadata.to_dict(), str(self.metadata_file))
        logger.debug(f"Metadata saved for project {self.project_id}")

    def load_metadata(self) -> Optional[ProjectMetadata]:
        """Load project metadata"""
        data = load_json(str(self.metadata_file))
        if data:
            return ProjectMetadata(**data)
        return None

    def save_requirements(self, content: str) -> None:
        """Save requirements document"""
        with open(self.requirements_file, "w") as f:
            f.write(content)
        logger.info(f"Requirements saved for project {self.project_id}")

    def load_requirements(self) -> str:
        """Load requirements document"""
        if self.requirements_file.exists():
            with open(self.requirements_file, "r") as f:
                return f.read()
        return ""

    def save_specification(self, content: str) -> None:
        """Save specification document"""
        with open(self.specification_file, "w") as f:
            f.write(content)
        logger.info(f"Specification saved for project {self.project_id}")

    def load_specification(self) -> str:
        """Load specification document"""
        if self.specification_file.exists():
            with open(self.specification_file, "r") as f:
                return f.read()
        return ""

    def add_log(self, message: str, level: str = "INFO") -> None:
        """Add message to project log"""
        timestamp = format_timestamp()
        log_entry = f"[{timestamp}] {level}: {message}\n"
        with open(self.log_file, "a") as f:
            f.write(log_entry)

    def save_source_file(self, filename: str, content: str) -> None:
        """Save source code file"""
        file_path = self.src_path / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content)
        self.add_log(f"Source file created: {filename}")

    def get_all_files(self) -> Dict[str, str]:
        """Get all project files with content"""
        files = {}
        for file_path in self.src_path.rglob("*"):
            if file_path.is_file():
                relative = file_path.relative_to(self.src_path)
                with open(file_path, "r", errors="ignore") as f:
                    files[str(relative)] = f.read()
        return files

    def get_project_info(self) -> Dict[str, Any]:
        """Get comprehensive project information"""
        metadata = self.load_metadata()
        return {
            "id": self.project_id,
            "name": self.name,
            "type": self.type,
            "path": str(self.base_path),
            "created_at": metadata.created_at if metadata else None,
            "status": metadata.status if metadata else "new",
            "src_files": len(list(self.src_path.rglob("*"))),
            "test_files": len(list(self.tests_path.rglob("*"))),
        }


class ProjectManager:
    """Project manager - handles all projects"""

    def __init__(self):
        self.projects_dir = Path(Config.PROJECTS_DIR)
        ensure_directory(str(self.projects_dir))
        self.projects: Dict[str, Project] = {}
        logger.info(f"ProjectManager initialized. Projects directory: {self.projects_dir}")

    def create_project(self, name: str, project_type: str, description: str = "") -> Project:
        """Create a new project"""
        if not name or len(name) < 3:
            raise ValueError("Project name must be at least 3 characters")

        project_id = generate_id(project_type)
        project = Project(project_id, name, project_type)

        # Create metadata
        metadata = ProjectMetadata(
            project_id=project_id,
            name=name,
            type=project_type,
            status="planning",
            created_at=format_timestamp(),
            updated_at=format_timestamp(),
            description=description,
        )

        project.save_metadata(metadata)
        self.projects[project_id] = project

        logger.info(f"✓ Project created: {name} (ID: {project_id})")
        return project

    def get_project(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        if project_id in self.projects:
            return self.projects[project_id]

        # Try to load from disk
        project_path = self.projects_dir / project_id
        if project_path.exists():
            metadata_file = project_path / ".agent-metadata.json"
            if metadata_file.exists():
                metadata = load_json(str(metadata_file))
                project = Project(project_id, metadata["name"], metadata["type"])
                self.projects[project_id] = project
                return project

        return None

    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects"""
        projects_list = []
        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_dir():
                metadata_file = project_dir / ".agent-metadata.json"
                if metadata_file.exists():
                    metadata = load_json(str(metadata_file))
                    projects_list.append(
                        {
                            "id": metadata["project_id"],
                            "name": metadata["name"],
                            "type": metadata["type"],
                            "status": metadata["status"],
                            "created_at": metadata["created_at"],
                        }
                    )
        return projects_list

    def delete_project(self, project_id: str) -> bool:
        """Delete a project"""
        project = self.get_project(project_id)
        if project:
            import shutil

            shutil.rmtree(project.base_path)
            if project_id in self.projects:
                del self.projects[project_id]
            logger.info(f"✓ Project deleted: {project_id}")
            return True
        return False
