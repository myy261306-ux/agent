# 🚀 Setup Guide - Autonomous Agent System

## Prerequisites

- **Python 3.11+** (required)
- **pip** or **conda** (package manager)
- **API Keys** (at least one from: Groq, OpenRouter, or Google Gemini)

## Step 1: Environment Setup

### 1.1 Create Virtual Environment (Recommended)

```bash
# Navigate to agent-system directory
cd agent-system

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 1.2 Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Get API Keys

### Option A: Groq (Recommended - FREE, Fast)

1. Go to https://console.groq.com
2. Sign up for free account
3. Create API key in "API Keys" section
4. Copy the key

**Groq gives you:**
- ✅ Free tier (very generous)
- ✅ Fastest inference times
- ✅ Great for code generation
- ✅ 30+ requests per minute limit

### Option B: OpenRouter (Fallback)

1. Go to https://openrouter.ai
2. Sign up for account
3. Add payment method (if using paid models)
4. Generate API key in account settings
5. Copy the key

**OpenRouter gives you:**
- ✅ Access to many models
- ✅ Pay-as-you-go pricing
- ✅ No subscription required

### Option C: Google Gemini (Tertiary)

1. Go to https://aistudio.google.com
2. Sign in with Google account
3. Create new API key
4. Copy the key

**Gemini gives you:**
- ✅ Free tier available
- ✅ Advanced capabilities
- ✅ Multimodal support

## Step 3: Configure .env File

### 3.1 Copy example file

```bash
cp .env.example .env
```

### 3.2 Edit .env file

```bash
# On macOS/Linux:
nano .env

# On Windows:
notepad .env
```

### 3.3 Add your API keys

```env
# Groq API Key (Primary)
GROQ_API_KEY=gsk_your_groq_key_here

# OpenRouter API Key (Fallback)
OPENROUTER_API_KEY=sk_your_openrouter_key_here

# Google Gemini API Key (Tertiary)
GEMINI_API_KEY=your_gemini_key_here

# System Configuration
PROJECTS_DIR=~/agent-projects
LOG_LEVEL=INFO
ENABLE_VERBOSE_MODE=False
MAX_CONCURRENT_AGENTS=5
REQUEST_TIMEOUT=60
```

**⚠️ Important:**
- Never share these keys
- Never commit .env to git
- Keep at least ONE API key configured
- Keys are used in fallback order

## Step 4: Verify Installation

### 4.1 Run validation tests

```bash
python tests/test_system.py
```

Expected output:
```
✓ PASS: Configuration
✓ PASS: LLM Providers
✓ PASS: System Initialization
✓ PASS: Project Creation
```

### 4.2 Check system status

```bash
python main.py
# Then type: status
```

## Step 5: First Project

### 5.1 Start the system

```bash
python main.py
```

You should see:
```
============================================================
🤖 AUTONOMOUS AGENT SYSTEM
============================================================
Multi-LLM Agent System with Fallback Strategy
Providers: groq, openrouter, gemini
============================================================
```

### 5.2 Create new project

```
🤖 Enter command: new
Project name: My Website
Project type: website
Project description: A modern website
```

### 5.3 Answer requirements questions

System will ask questions like:
- What is the main purpose?
- Who are target users?
- What features do you need?
- What design style?
- etc.

### 5.4 Review specification

System generates detailed specification. Review and confirm to proceed.

### 5.5 Watch execution

Agents will:
- Generate code
- Run tests
- Debug issues
- Save results

## Troubleshooting

### Problem: "No LLM providers available"

**Solution:**
1. Check .env file exists in agent-system directory
2. Add at least one valid API key
3. Restart the system
4. Run: `python tests/test_system.py`

### Problem: "API key invalid"

**Solution:**
1. Verify API key is correct (copy from provider)
2. Check for extra spaces in .env
3. Ensure .env is in agent-system directory
4. Try with different provider

### Problem: "Connection timeout"

**Solution:**
1. Check internet connection
2. Verify API provider status (uptime status page)
3. Try increasing REQUEST_TIMEOUT in .env (e.g., 120)
4. System will automatically fallback to next provider

### Problem: "Module not found"

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Verify Python version
python --version  # Should be 3.11 or higher

# Check virtual environment is activated
which python  # Should show venv path
```

### Problem: "Permission denied" on macOS/Linux

**Solution:**
```bash
# Make main.py executable
chmod +x main.py

# Run with python
python main.py  # Instead of ./main.py
```

## File Locations

After setup, key locations are:

```
agent-system/
├── .env                    ← Your API keys go here
├── main.py                 ← Start system from here
├── requirements.txt        ← Dependencies
└── tests/test_system.py    ← Validation tests

~/agent-projects/          ← Generated projects
├── project_1/
│   ├── src/               ← Generated code
│   ├── tests/             ← Generated tests
│   ├── logs/              ← Execution logs
│   └── specification.md   ← Project specification
```

## Commands Reference

```bash
# Start system
python main.py

# Run validation tests
python tests/test_system.py

# Check Python version
python --version

# List projects
python main.py
# Then type: list

# View logs for a project
# Navigate to: ~/agent-projects/<project_id>/logs/
tail -f ~/agent-projects/website_20240604_xyz/logs/project.log
```

## System Requirements

| Requirement | Minimum | Recommended |
|------------|---------|------------|
| Python | 3.11 | 3.11+ |
| RAM | 4GB | 8GB+ |
| Disk Space | 2GB | 10GB+ |
| Internet | Required | Always on |
| API Keys | 1 | 2-3 (backup) |

## Performance Tips

1. **Use Groq first** - Fastest for code generation
2. **Configure multiple providers** - Automatic fallback
3. **Increase MAX_CONCURRENT_AGENTS** - For larger projects
4. **Monitor token usage** - Check project logs
5. **Use appropriate log level** - INFO for production, DEBUG for troubleshooting

## Security Best Practices

1. ✅ Never commit .env to git
2. ✅ Use .gitignore to exclude:
   ```
   .env
   agent-projects/
   __pycache__/
   venv/
   ```
3. ✅ Rotate API keys periodically
4. ✅ Monitor API usage on provider dashboards
5. ✅ Don't share .env file
6. ✅ Use strong passwords on API provider accounts

## Next Steps

After successful setup:

1. **Create your first project**
   ```
   python main.py
   type: new
   ```

2. **Explore generated code**
   ```
   ~/agent-projects/<project_id>/src/
   ```

3. **Review logs**
   ```
   ~/agent-projects/<project_id>/logs/project.log
   ```

4. **Extend agents** (optional)
   - Create custom agents by extending BaseAgent
   - Add new project types
   - Customize LLM providers

## Getting Help

1. Check README.md for comprehensive documentation
2. Review log files for error details
3. Run validation tests to diagnose issues
4. Check API provider status pages
5. Ensure API keys are valid and have credits

## Next Commands to Try

```
# After starting system (python main.py)
help          # Show all commands
new           # Create new project
status        # View system status
list          # List all projects
```

---

**Ready to build? Start with: `python main.py` then type `new`**

Happy coding! 🚀
