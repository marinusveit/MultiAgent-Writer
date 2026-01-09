# Contributing Guide

Thank you for your interest in contributing to MultiAgent-Writer! This guide will help you get started with development.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/multiagent-writer.git
cd multiagent-writer
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages**:
- PyQt6>=6.6.0 - GUI framework
- requests>=2.31.0 - HTTP client
- python-dotenv>=1.0.0 - Environment variable loading
- pyinstaller>=6.0.0 - (Optional) For building executables

### 4. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenRouter API key
nano .env  # or use your favorite editor
```

**In .env**:
```
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

Get your API key from: https://openrouter.ai/keys

### 5. Run Application

```bash
# Using the test launcher
python run_new.py

# Or directly
python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('src')))
from multiagent_writer.main import main
main()
"
```

---

## Project Structure

See `docs/ARCHITECTURE.md` for detailed architecture documentation.

```
MultiAgent-Writer/
├── src/
│   └── multiagent_writer/
│       ├── main.py              # Entry point
│       ├── ui/                  # PyQt6 UI components
│       │   ├── main_window.py
│       │   ├── dialogs.py
│       │   ├── workers.py
│       │   └── button_manager.py
│       ├── api/                 # OpenRouter API integration
│       │   ├── service.py
│       │   ├── client.py
│       │   └── errors.py
│       ├── core/                # Core business logic
│       │   └── text_processor.py
│       ├── prompts/             # LLM prompt templates
│       │   └── templates.py
│       └── config/              # Configuration
│           ├── config_manager.py
│           └── constants.py
├── docs/                        # Documentation
│   ├── ARCHITECTURE.md
│   └── API.md
├── tests/                       # Test files
├── .env                         # API key (git-ignored)
├── config.json                  # User settings (git-ignored)
└── requirements.txt             # Dependencies
```

---

## Development Workflow

### Making Changes

1. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** in the appropriate module:
   - UI changes: `src/multiagent_writer/ui/`
   - API changes: `src/multiagent_writer/api/`
   - Core logic: `src/multiagent_writer/core/`
   - Prompts: `src/multiagent_writer/prompts/`

3. **Test your changes**:
   ```bash
   python run_new.py
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: your feature description"
   ```

5. **Push and create pull request**:
   ```bash
   git push origin feature/your-feature-name
   ```

### Code Style

**Follow Python conventions**:
- PEP 8 style guide
- 4 spaces for indentation (not tabs)
- Max line length: 100 characters
- Descriptive variable names

**Docstrings**:
```python
def improve_text_ausformulieren(self, text: str, status_callback=None) -> dict:
    """
    3-step workflow for expanding bullet points into full text.

    Args:
        text: Input text (bullet points or short notes)
        status_callback: Optional progress callback function

    Returns:
        Dictionary with step1_kimi, step2_analysis, step3_final

    Raises:
        ValueError: If text is empty
        APIError: If API call fails
    """
    pass
```

**Type Hints**:
```python
from typing import Dict, Any, Optional, Callable

def load_config(self) -> Dict[str, Any]:
    """Load configuration"""
    pass

def improve_text(
    self,
    text: str,
    status_callback: Optional[Callable[[str], None]] = None
) -> Dict[str, str]:
    """Improve text"""
    pass
```

---

## Adding Features

### Adding a New Mode

See `docs/ARCHITECTURE.md` → "Adding New Features" section for detailed examples.

**Quick summary**:
1. Add prompts to `src/multiagent_writer/prompts/templates.py`
2. Add workflow to `src/multiagent_writer/api/service.py`
3. Update UI in `src/multiagent_writer/ui/main_window.py`

**Example**: Adding "summarize" mode

**1. Add prompt** (`prompts/templates.py`):
```python
def get_prompt_multi_agent(mode, agent_type, text, analysis=None, ...):
    # ... existing modes ...

    if mode == "zusammenfassen":
        if agent_type == "kimi_k2":
            return f"Fasse diesen Text zusammen:\n\n{text}"
        # ... other agents
```

**2. Add workflow** (`api/service.py`):
```python
def improve_text_zusammenfassen(self, text: str, status_callback=None) -> dict:
    """3-step workflow for summarizing text"""
    # Step 1: Kimi K2
    step1 = self.client.call_model(...)
    # Step 2: Claude Opus
    step2 = self.client.call_model(...)
    # Step 3: GPT-4o
    step3 = self.client.call_model(...)
    return {'step1': step1, 'step2': step2, 'step3': step3}
```

**3. Update UI** (`ui/main_window.py`):
```python
# Add to mode dropdown
self.mode_combo.addItems(["ausformulieren", "korrekturlesen", "zusammenfassen"])

# Handle in process_text()
if mode == "zusammenfassen":
    result = api_service.improve_text_zusammenfassen(text, status_callback)
```

### Adding a New AI Model

**1. Update config defaults** (`config/config_manager.py`):
```python
DEFAULT_MODELS = {
    'kimi_k2': 'openai/gpt-oss-120b',
    'claude_opus': 'anthropic/claude-3.5-sonnet',
    'gpt_52': 'openai/gpt-4o',
    'gemini': 'google/gemini-2.0-flash-001'  # New model
}
```

**2. Use in workflow**:
```python
result = self.client.call_model(text, self.config['models']['gemini'], prompt)
```

---

## Debugging

### Enable Verbose Logging

Add to `src/multiagent_writer/main.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test API Calls

Test API integration without running the full UI:

```bash
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('src')))

from multiagent_writer.api.service import TextImprovementService
from multiagent_writer.config.config_manager import ConfigManager

config = ConfigManager().load()
service = TextImprovementService(config)

text = '- KI ist wichtig'
result = service.improve_text_ausformulieren(text)
print(result['step3_final'])
"
```

### Test Module Imports

```bash
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('src')))

# Test imports
from multiagent_writer.ui.main_window import ThesisImproverWindow
from multiagent_writer.api.service import TextImprovementService
from multiagent_writer.core.text_processor import InteractiveDiff

print('✓ All imports successful!')
"
```

### Check Configuration Loading

```bash
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('src')))

from multiagent_writer.config.config_manager import ConfigManager

config = ConfigManager().load()
print('API key:', 'configured' if config.get('api_key') else 'missing')
print('Models:', config.get('models'))
"
```

---

## Common Issues

### ImportError after refactoring

**Problem**: `ModuleNotFoundError: No module named 'multiagent_writer'`

**Solution**: Make sure you're adding `src/` to Python path:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path('src')))
```

Or use the test launcher:
```bash
python run_new.py
```

### PyQt6 crashes

**Problem**: Segmentation fault or PyQt6 import errors

**Solution 1**: Check Python version (requires 3.9+)
```bash
python3 --version
```

**Solution 2**: Reinstall PyQt6
```bash
pip install --force-reinstall PyQt6
```

**Solution 3**: Check display server (Linux)
```bash
# If using Wayland, try X11
export QT_QPA_PLATFORM=xcb
python run_new.py
```

### API Key not found

**Problem**: "API-Key nicht konfiguriert" error

**Solution 1**: Check .env file exists and has correct format
```bash
cat .env
# Should contain:
# OPENROUTER_API_KEY=sk-or-v1-...
```

**Solution 2**: Verify environment loading
```python
from dotenv import load_dotenv
import os
load_dotenv()
print(os.getenv('OPENROUTER_API_KEY'))
```

**Solution 3**: Manually set in config.json (not recommended for security)
```json
{
    "api_key": "sk-or-v1-...",
    ...
}
```

### Config validation errors

**Problem**: KeyError when accessing config

**Solution**: Config is auto-validated on load. If you see KeyError, reload config:
```python
config = config_manager.load()  # Validates and fixes missing keys
```

---

## Testing

### Manual Testing Checklist

Before submitting a pull request, test these scenarios:

**1. Basic Functionality**:
- [ ] Application launches without errors
- [ ] Can enter text in input area
- [ ] Can select mode (ausformulieren/korrekturlesen)
- [ ] Process button works

**2. API Integration**:
- [ ] API call succeeds with valid API key
- [ ] Progress dialog shows step updates
- [ ] Error dialog shows on invalid API key
- [ ] Error dialog shows on network error

**3. Interactive Diff**:
- [ ] Diff view displays changes correctly
- [ ] Click on change toggles state (pending → accepted → rejected)
- [ ] "Accept all" accepts all changes
- [ ] "Reject all" rejects all changes
- [ ] Toggle view switches between diff and plain text

**4. Output Functions**:
- [ ] Copy button copies to clipboard
- [ ] Accept button moves text to input
- [ ] Export button saves to file
- [ ] Reset button clears output

**5. Settings**:
- [ ] Settings dialog opens
- [ ] Can update API key
- [ ] Can change model
- [ ] Can set system prompt
- [ ] Settings save correctly

**6. Analysis Dialog**:
- [ ] "Show analysis" button opens dialog
- [ ] Claude Opus analysis displays with Markdown
- [ ] Dialog closes properly

### Unit Testing (Future)

We plan to add pytest-based unit tests:

```bash
# Install test dependencies
pip install pytest pytest-qt pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=src/multiagent_writer --cov-report=html
```

**Test structure** (planned):
```
tests/
├── test_api_service.py
├── test_config_manager.py
├── test_text_processor.py
└── test_ui_components.py
```

---

## Pull Request Process

1. **Fork the repository**

2. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature
   ```

3. **Make changes and test**:
   - Follow code style guidelines
   - Add type hints
   - Update documentation if needed
   - Test manually

4. **Commit with descriptive message**:
   ```bash
   git commit -m "Add feature: brief description

   - More detailed explanation
   - Why this change is needed
   - How it was implemented"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature
   ```

6. **Create Pull Request**:
   - Describe what your PR does
   - Reference any related issues
   - List what you tested

## Code Review Guidelines

**For Reviewers**:
- Check code follows style guidelines
- Verify functionality works as described
- Look for potential bugs or edge cases
- Ensure documentation is updated

**For Contributors**:
- Respond to feedback promptly
- Make requested changes
- Keep PR scope focused (one feature per PR)
- Be patient and respectful

---

## Documentation

### Updating Documentation

If your changes affect public APIs or architecture:

1. **Update API.md** for new/changed methods
2. **Update ARCHITECTURE.md** for architectural changes
3. **Update README.md** for user-facing changes
4. **Add inline docstrings** for new functions

### Documentation Style

**Markdown formatting**:
```markdown
# Header 1
## Header 2
### Header 3

**Bold text**
*Italic text*

- Bullet point
- Another point

1. Numbered item
2. Another item

`inline code`

```python
# Code block
def example():
    pass
```
```

---

## Getting Help

**Questions about contributing**:
- Open an issue with label `question`
- Check existing issues for similar questions

**Bug reports**:
- Open an issue with label `bug`
- Include steps to reproduce
- Include error messages and logs

**Feature requests**:
- Open an issue with label `enhancement`
- Describe the feature
- Explain the use case

---

## Community Guidelines

- Be respectful and constructive
- Help others when possible
- Share knowledge and learnings
- Follow the code of conduct

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## Thank You!

Your contributions help make MultiAgent-Writer better for everyone. Thank you for taking the time to contribute! 🎉
