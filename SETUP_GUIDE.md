# Setup Guide - Conversational Agent System

## Prerequisites

### 1. Install Python Packages

The project requires several dependencies. Install them using:

```bash
pip install -r requirements.txt
```

Key dependencies:
- `python-dotenv` - Environment variable management
- `groq` - Groq LLM API
- `aiohttp` - Async HTTP client
- `asyncio-contextmanager` - Async utilities

### 2. Set Up Environment Variables

Create a `.env` file in the project root directory:

```bash
# .env file
GROQ_API_KEY=your_groq_api_key_here
OPENROUTER_API_KEY=your_openrouter_key_here  # Optional fallback
```

Get API keys from:
- **Groq**: https://console.groq.com/keys
- **OpenRouter**: https://openrouter.ai/keys

## Running the System

### Option 1: Direct Execution

```bash
python3 main.py
```

### Option 2: With Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the system
python3 main.py
```

## How to Use the Conversational Agent

Once running, you'll see:

```
Agent is ready to chat! Tell me about your project or type 'help' for options.

You:
```

### Example Workflow

#### 1. Simple Conversation

```
You: Hi! I want to build a website for my photography portfolio
Agent: That sounds like a great project! How many galleries or sections are you thinking of including? Will you need e-commerce functionality for selling prints?

You: Maybe 5 galleries with a contact form. No e-commerce needed
Agent: Perfect! A portfolio site with 5 galleries and contact form. Would you like a blog section for photography tips?
```

#### 2. Project Creation

When you describe a project in detail:

```
You: I need a shopping website with product catalog, shopping cart, checkout, and favourite page
Agent: [Asks clarifying questions...]
Agent: Creating plan for your e-commerce website...

[System generates comprehensive project plan]

Would you like to create this project? (yes/no): yes
Project created successfully!
```

#### 3. Traditional Commands (Still Work)

```
You: help
Agent: [Shows help information]

You: list
Agent: [Lists all projects]

You: status
Agent: [Shows system status]

You: exit
Agent: Goodbye! See you next time.
```

## Understanding Error Messages

### Error: `'LLMClient' object has no attribute 'generate_text'`

**Cause**: The agent code was outdated
**Fix**: Already applied in latest commit. System now uses correct `generate()` method

### Error: `ModuleNotFoundError: No module named 'dotenv'`

**Cause**: Dependencies not installed
**Fix**: Run `pip install -r requirements.txt`

### Error: `GROQ_API_KEY not configured`

**Cause**: API key not set in `.env` file
**Fix**: Add your Groq API key to `.env` file

## System Architecture

```
main.py
  ↓
run_conversational_loop()
  ↓
ConversationalAgent (agents/conversational_agent.py)
  ↓
LLMClient (llm/llm_client.py)
  ↓
GroqProvider or OpenRouterProvider
```

## Testing the Agent

```bash
# Test syntax
python3 -m py_compile agents/conversational_agent.py
python3 -m py_compile input_handlers/project_planner.py

# Run full system
python3 main.py
```

## Features

✓ **Natural Conversation** - Talk to the agent naturally in English or Urdu
✓ **Project Analysis** - Agent understands what you want to build
✓ **Plan Generation** - Automatically creates detailed project plans
✓ **Flexible Input** - Works with typos, mixed language, partial descriptions
✓ **Error Recovery** - Gracefully handles issues and asks for clarification
✓ **Traditional Commands** - Backward compatible with CLI commands

## Troubleshooting

### Agent Responses Are Slow

- Check your internet connection
- Verify API keys are valid
- Groq API might be under high load

### Agent Doesn't Understand Me

- Be more specific about your project
- Use technical terms when possible
- Describe key features and functionality

### System Crashes

- Check error logs in console output
- Verify all dependencies are installed: `pip list`
- Make sure API keys are correct

## Next Steps

1. Set up environment variables in `.env`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the system: `python3 main.py`
4. Start describing your project!

## Support

For detailed information about:
- **Conversational Agent**: See `CONVERSATIONAL_AGENT_GUIDE.md`
- **Quick Start Examples**: See `CONVERSATIONAL_AGENT_QUICKSTART.md`
- **NLI System**: See `NLI_DOCUMENTATION.md`

Enjoy building with the conversational agent!
