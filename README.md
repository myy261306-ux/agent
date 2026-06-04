# 🤖 Autonomous Agent System

A professional multi-agent system that runs locally on your laptop. The system automatically manages project development from requirements gathering to testing and deployment.

## 🎯 Overview

This is a **local autonomous agent system** with:
- **Main Manager (Orchestrator)**: Central coordinator
- **Multiple Code Generator Agents**: Collaborative code generation
- **Debugger Agent**: Testing, debugging, and verification
- **Multi-LLM Support**: Groq → OpenRouter (with fallback)

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│          Main Manager                   │
│    (Orchestrator & Coordinator)         │
└──────────┬──────────────────────────────┘
           │
    ┌──────┴──────┐
    │             │
┌───▼──────┐   ┌──▼────────┐
│ LLM      │   │  Agent    │
│ Client   │   │  Pool     │
│(Fallback)│   │(Parallel) │
└──────────┘   └─────┬─────┘
                  ┌──┴──┐
                  │     │
            ┌─────▼─┐ ┌─▼─────┐
            │ Code  │ │Debug  │
            │ Gen   │ │Agent  │
            │Agents │ │       │
            └───────┘ └───────┘
```

## 🚀 Quick Start

### 1. Setup

```bash
cd agent-system
pip install -r requirements.txt
```

### 2. Configure API Keys

Edit `.env` file and add your API keys:

```env
# Primary LLM Provider (Groq)
# Get from: https://console.groq.com
GROQ_API_KEY=your_groq_key_here

# Fallback LLM Provider (OpenRouter)
# Get from: https://openrouter.ai/keys
OPENROUTER_API_KEY=your_openrouter_key_here
```

### 3. Run the System

```bash
python main.py
```

### 4. Create a Project

```
🤖 Enter command: new
Project name: My Website
Project type: website
Project description: A modern e-commerce website
```

The system will:
1. Ask detailed questions about your project
2. Generate a comprehensive specification
3. Plan execution tasks
4. Assign agents to build your project
5. Monitor and validate results

## 📋 Commands

| Command | Description |
|---------|-------------|
| `new` | Create a new project |
| `work` | Work on existing project |
| `list` | List all projects |
| `status` | Show system status |
| `help` | Show help message |
| `exit` | Shut down system |

## 📂 Project Structure

```
agent-system/
├── .env                          # Configuration (add your API keys here)
├── .env.example                  # Example configuration
├── main.py                       # CLI entry point
├── requirements.txt              # Python dependencies
│
├── main_manager/
│   ├── __init__.py
│   └── orchestrator.py          # Main orchestrator logic
│
├── agents/
│   ├── __init__.py
│   ├── base_agent.py            # Abstract base agent
│   ├── code_generator_agent.py  # Code generation agent
│   ├── debugger_agent.py        # Testing/debugging agent
│   └── agent_pool.py            # Agent pool management
│
├── llm/
│   ├── __init__.py
│   ├── provider_base.py         # Abstract LLM provider
│   ├── groq_provider.py         # Groq implementation
│   ├── openrouter_provider.py   # OpenRouter implementation
│   └── llm_client.py            # LLM orchestrator with fallback
│
├── project_manager/
│   ├── __init__.py
│   └── project.py               # Project management
│
├── utils/
│   ├── __init__.py
│   ├── config.py                # Configuration management
│   ├── logger.py                # Logging setup
│   └── helpers.py               # Utility functions
│
└── tests/
    └── (test files)
```

## 🔄 Workflow

### Step 1: Create New Project

```
🤖 Enter command: new
Project name: My App
Project type: website
```

### Step 2: Automatic Requirement Gathering

The system uses AI to ask intelligent questions:
- What is the purpose?
- Who are the target users?
- What features do you need?
- What technology do you prefer?
- etc.

### Step 3: Specification Generation

Automatically creates a detailed specification:
- Project Overview
- Functional Requirements
- Technical Architecture
- Technology Stack
- Database Schema
- API Endpoints
- Frontend Components
- Testing Strategy

### Step 4: Task Planning

Creates executable tasks:
```json
[
  {
    "task_id": "codegen_20240604_xyz",
    "name": "Create homepage component",
    "type": "code_generation",
    "priority": "high",
    "requirements": { ... }
  },
  ...
]
```

### Step 5: Agent Execution

- **Code Generator Agents** (3-5) work in parallel to create code
- **Debugger Agent** tests and verifies results
- Auto-fix attempts for issues
- Results saved to project directory

### Step 6: Results & Verification

Generated code saved in:
```
~/agent-projects/website_20240604_xyz/
├── src/                    # Generated source code
├── tests/                  # Generated tests
├── specification.md        # Project specification
├── requirements.md         # Requirements document
└── logs/                   # Execution logs
```

## 🔌 LLM Provider Fallback Strategy

The system uses intelligent fallback:

1. **Primary**: Groq (Fast, cost-effective)
2. **Fallback**: OpenRouter (Large model selection)

If primary provider fails or times out, automatically switches to fallback.

## ⚙️ Configuration

### Environment Variables

```env
# API Keys (required - at least one)
GROQ_API_KEY=...
OPENROUTER_API_KEY=...

# System Configuration
PROJECTS_DIR=~/agent-projects          # Where projects are saved
LOG_LEVEL=INFO                         # DEBUG, INFO, WARNING, ERROR
ENABLE_VERBOSE_MODE=False              # Detailed logging
MAX_CONCURRENT_AGENTS=5                # Number of parallel agents
REQUEST_TIMEOUT=60                     # API request timeout (seconds)
```

### Project Types Supported

- `website` - Web applications (React, Next.js, etc.)
- `api` - REST/GraphQL APIs
- `cli` - Command-line tools
- `script` - Automation scripts
- `data-analysis` - Data processing projects
- `library` - Reusable libraries

## 📊 Monitoring

View system status anytime:

```
🤖 Enter command: status
```

Shows:
- Current project
- Active agents
- Completed/failed tasks
- Total tokens used
- Available LLM providers

## 🛡️ Error Handling

The system includes:
- Automatic LLM provider fallback
- Task retry logic with exponential backoff
- Graceful degradation
- Comprehensive error logging
- User-friendly error messages

## 📝 Logging

Detailed logs for each project:
```
~/agent-projects/project_id/logs/project.log
```

View real-time logs while system is running.

## 🧪 Testing Generated Code

The Debugger Agent automatically:
1. Analyzes code for issues
2. Identifies potential bugs
3. Runs test cases
4. Generates quality reports
5. Auto-fixes safe issues
6. Reports remaining issues

## 🔐 Security

- API keys stored only in `.env` (never in code)
- All API calls use HTTPS
- No data sent to external services (code stays local)
- Secure file permissions on generated files

## 🚀 Advanced Features

### Custom Prompts

Modify agent behavior by editing system prompts in agent classes.

### Extending with New Agents

Create new agent types by extending `BaseAgent`:

```python
from agents.base_agent import BaseAgent, Task, TaskResult

class CustomAgent(BaseAgent):
    def __init__(self, agent_id: str, llm_client):
        super().__init__(agent_id, "custom_type")
        self.llm_client = llm_client
    
    async def process_task(self, task: Task) -> TaskResult:
        # Implement your logic
        pass
```

### Adding New LLM Providers

Create new provider by extending `BaseLLMProvider`:

```python
from llm.provider_base import BaseLLMProvider

class CustomProvider(BaseLLMProvider):
    @staticmethod
    def get_provider_name() -> str:
        return "CustomProvider"
    
    async def generate(self, ...):
        # Implement provider logic
        pass
```

## 📚 Project Metadata

Each project tracks:
- Creation date/time
- Update date/time
- Status (planning, development, testing, completed)
- Requirements snapshot
- Agent assignments
- Token usage
- Test results
- Execution history

## 🎯 Future Enhancements

- [ ] Web dashboard UI
- [ ] Real-time progress visualization
- [ ] Collaborative mode (multiple users)
- [ ] Version control integration
- [ ] Deployment automation
- [ ] Performance optimization
- [ ] Advanced analytics

## 📖 Examples

### Example 1: Create a Simple Blog

```
Project name: My Blog
Type: website
Description: A simple blog with posts and comments

# System will generate:
- Blog homepage with post list
- Individual post pages
- Comment system
- Admin panel
- Database schema
- Tests and documentation
```

### Example 2: Create an API

```
Project name: Weather API
Type: api
Description: RESTful API for weather data

# System will generate:
- API endpoints
- Database models
- Authentication
- Tests
- API documentation
- Deployment config
```

## 🤝 Contributing

To extend the system:
1. Create new agents by extending `BaseAgent`
2. Add LLM providers by extending `BaseLLMProvider`
3. Improve task planning logic in `MainManager`
4. Add test cases in `tests/` directory

## 📞 Support

For issues or questions:
1. Check logs: `~/agent-projects/<project_id>/logs/`
2. Review error messages
3. Ensure API keys are correctly configured
4. Try with different LLM provider

## 📄 License

Professional Multi-Agent System for Local Project Development

---

**Ready to automate your development workflow? Let's go! 🚀**
