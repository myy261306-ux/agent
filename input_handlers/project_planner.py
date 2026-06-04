"""
Project Planner
Generates detailed project plans from project descriptions
"""

import logging
import json
from typing import Dict, Any, Optional
from llm.llm_client import LLMClient

logger = logging.getLogger(__name__)


class ProjectPlanner:
    """
    Generates structured project plans from descriptions.
    Breaks down projects into components, tasks, and requirements.
    """

    def __init__(self, llm_client: LLMClient):
        """
        Initialize project planner
        
        Args:
            llm_client: LLMClient instance
        """
        self.llm_client = llm_client

    def generate_plan(self, project_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate detailed project plan from project information
        
        Args:
            project_info: Project details from analysis
            
        Returns:
            Structured project plan
        """
        try:
            plan_prompt = self._build_plan_prompt(project_info)
            
            messages = [
                {"role": "system", "content": "You are an expert project manager. Create detailed, practical project plans."},
                {"role": "user", "content": plan_prompt}
            ]

            response = self.llm_client.generate_text(
                messages=messages,
                max_tokens=800,
                temperature=0.5
            )

            return self._parse_plan_response(response, project_info)

        except Exception as e:
            logger.error(f"Error generating plan: {str(e)}")
            return {"error": str(e)}

    def _build_plan_prompt(self, project_info: Dict[str, Any]) -> str:
        """Build prompt for plan generation"""
        prompt = f"""Create a detailed project plan for this software project:

PROJECT TYPE: {project_info.get('project_type', 'unspecified')}
KEY FEATURES: {', '.join(project_info.get('key_features', []))}
COMPLEXITY: {project_info.get('complexity', 'medium')}
TECH STACK: {', '.join(project_info.get('tech_stack', []))}

Provide the plan in this exact format:

PROJECT_NAME: [short project name]
DESCRIPTION: [1-2 sentence description]

COMPONENTS:
- [Component 1]: [brief description]
- [Component 2]: [brief description]
- [Component 3]: [brief description]
(list 3-5 main components)

TASKS:
1. [Setup/Foundation task]
2. [Core feature task]
3. [Additional features task]
4. [Testing and optimization]
5. [Deployment/finalization]

REQUIREMENTS:
- [Technical requirement 1]
- [Technical requirement 2]
- [Technical requirement 3]

TIMELINE_ESTIMATE: [hours/days estimate]

Be practical and actionable."""
        return prompt

    def _parse_plan_response(self, response: str, project_info: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM plan response into structured format"""
        plan = {
            "project_name": project_info.get('project_type', 'New Project'),
            "project_type": project_info.get('project_type'),
            "description": "",
            "components": [],
            "tasks": [],
            "requirements": [],
            "timeline_estimate": "",
            "original_response": response
        }

        try:
            lines = response.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Parse sections
                if line.startswith("PROJECT_NAME:"):
                    plan["project_name"] = line.replace("PROJECT_NAME:", "").strip()
                    current_section = "header"
                    
                elif line.startswith("DESCRIPTION:"):
                    plan["description"] = line.replace("DESCRIPTION:", "").strip()
                    
                elif line.startswith("COMPONENTS:"):
                    current_section = "components"
                    
                elif line.startswith("TASKS:"):
                    current_section = "tasks"
                    
                elif line.startswith("REQUIREMENTS:"):
                    current_section = "requirements"
                    
                elif line.startswith("TIMELINE_ESTIMATE:"):
                    plan["timeline_estimate"] = line.replace("TIMELINE_ESTIMATE:", "").strip()
                    
                elif line.startswith("- ") and current_section == "components":
                    component = line[2:].strip()
                    if component:
                        plan["components"].append(component)
                        
                elif line and line[0].isdigit() and "." in line and current_section == "tasks":
                    task = line.split(".", 1)[1].strip() if "." in line else line
                    if task:
                        plan["tasks"].append(task)
                        
                elif line.startswith("- ") and current_section == "requirements":
                    req = line[2:].strip()
                    if req:
                        plan["requirements"].append(req)

            return plan

        except Exception as e:
            logger.error(f"Error parsing plan: {str(e)}")
            plan["error"] = str(e)
            return plan

    def display_plan(self, plan: Dict[str, Any]) -> str:
        """Format plan for display"""
        if "error" in plan:
            return f"Error generating plan: {plan['error']}"

        output = []
        output.append("\n" + "=" * 70)
        output.append("PROJECT PLAN")
        output.append("=" * 70)
        output.append(f"\nProject: {plan.get('project_name', 'New Project')}")
        output.append(f"Type: {plan.get('project_type', 'unknown').upper()}")
        output.append(f"\nDescription:\n{plan.get('description', 'No description')}")

        if plan.get("components"):
            output.append("\n\nCOMPONENTS:")
            for component in plan["components"]:
                output.append(f"  • {component}")

        if plan.get("tasks"):
            output.append("\n\nTASKS:")
            for i, task in enumerate(plan["tasks"], 1):
                output.append(f"  {i}. {task}")

        if plan.get("requirements"):
            output.append("\n\nREQUIREMENTS:")
            for req in plan["requirements"]:
                output.append(f"  • {req}")

        if plan.get("timeline_estimate"):
            output.append(f"\n\nEstimated Time: {plan['timeline_estimate']}")

        output.append("\n" + "=" * 70 + "\n")

        return "\n".join(output)
