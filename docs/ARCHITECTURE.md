# Architecture Documentation

## Overview

MultiAgent-Writer is a PyQt6 desktop application that improves text using multiple AI models in sequence through the OpenRouter API. The application uses a multi-agent workflow where different AI models perform specialized tasks: one model formulates text, another analyzes it, and a third implements improvements.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│                   (PyQt6 Main Window)                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ├─► Input Text Area (QPlainTextEdit)
                     ├─► Output Text Area (Interactive Diff)
                     └─► Control Buttons & Settings
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      UI Layer                                │
│  src/multiagent_writer/ui/                                   │
│  ├── main_window.py      - Main application window          │
│  ├── dialogs.py          - Settings & Analysis dialogs      │
│  ├── workers.py          - Background API worker threads    │
│  └── button_manager.py   - Button state management          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Service Layer                         │
│  src/multiagent_writer/api/                                  │
│  ├── service.py          - Multi-agent workflows            │
│  ├── client.py           - OpenRouter HTTP client           │
│  └── errors.py           - Custom exceptions                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Core Processing                           │
│  src/multiagent_writer/core/                                 │
│  └── text_processor.py   - Diff generation & rendering      │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Configuration & Prompts                    │
│  src/multiagent_writer/config/                               │
│  ├── config_manager.py   - Config loading/validation        │
│  └── constants.py        - UI constants & styling           │
│  src/multiagent_writer/prompts/                              │
│  └── templates.py        - LLM prompt templates             │
└─────────────────────────────────────────────────────────────┘
```

## Multi-Agent Workflow

### Ausformulieren (Formulate)
3-step process to expand bullet points into full text:

```
Input Text (Bullet Points)
    │
    ▼
┌────────────────────┐
│   Step 1: Kimi K2  │  Formulates bullet points into sentences
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ Step 2: Claude Opus│  Analyzes formulated text for improvements
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│  Step 3: GPT-4o    │  Implements improvements
└────────┬───────────┘
         │
         ▼
    Final Text
```

**Example**:
```
Input:
- KI wichtig
- Einsatz in Medizin
- Ethische Fragen

Output:
Künstliche Intelligenz spielt eine zunehmend wichtige Rolle in
der modernen Gesellschaft. Ihr Einsatz in der Medizin ermöglicht
präzisere Diagnosen und personalisierte Behandlungsansätze.
Gleichzeitig werfen diese Entwicklungen wichtige ethische Fragen auf.
```

### Korrekturlesen (Proofread)
2-step process to improve existing text:

```
Input Text (Full Text)
    │
    ▼
┌────────────────────┐
│ Step 1: Claude Opus│  Analyzes text for errors & improvements
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│  Step 2: GPT-4o    │  Applies corrections
└────────┬───────────┘
         │
         ▼
    Improved Text
```

**Example**:
```
Input:
Die künstliche Inteligenz ist ein wichtiger Faktor für die zukunft.

Output:
Die künstliche Intelligenz ist ein wichtiger Faktor für die Zukunft.
```

## Key Components

### 1. Interactive Diff View (`core/text_processor.py`)

**Purpose**: Show word-level differences between original and improved text with interactive accept/reject functionality.

**Features**:
- Word-level diff with additions (green), deletions (red)
- Click to accept/reject individual changes
- Three states: PENDING (default), ACCEPTED, REJECTED
- Statistics tracking (words added/removed, character changes)

**Key Classes**:
- `Change` - Represents a single diff change with ID, type, and state
- `ChangeState` - Enum for change states (PENDING, ACCEPTED, REJECTED)
- `InteractiveDiff` - Manages diff rendering and state

**Usage Example**:
```python
from multiagent_writer.core.text_processor import InteractiveDiff

diff = InteractiveDiff(original_text="KI wichtig", modified_text="KI ist wichtig")
html = diff.generate_interactive_html()
stats = diff.get_statistics()
# {'words_added': 1, 'words_removed': 0, 'chars_added': 4, 'chars_removed': 0}

# Toggle change state
diff.toggle_change_state(change_id=0)
final_text = diff.get_final_text()
```

### 2. API Service (`api/service.py`)

**Purpose**: Orchestrate multi-agent API calls through OpenRouter.

**Key Methods**:
- `improve_text_ausformulieren(text, status_callback)` - 3-step workflow
- `improve_text_korrekturlesen(text, status_callback)` - 2-step workflow

**Status Callbacks**: Update UI progress during multi-step processing.

**Workflow Orchestration**:
```python
# Step 1: Call first model
step1_result = self.client.call_model(text, model1, prompt1)

# Step 2: Call second model with step1 result
step2_result = self.client.call_model(step1_result, model2, prompt2)

# Step 3 (ausformulieren only): Call third model
step3_result = self.client.call_model(step1_result, model3, prompt3)

return {'step1': step1_result, 'step2': step2_result, 'step3': step3_result}
```

### 3. Configuration (`config/config_manager.py`)

**Config Sources** (priority order):
1. Environment variables (`.env` file) - highest priority for API key
2. `config.json` - user settings
3. Default values - fallback

**Key Settings**:
- `api_key` - OpenRouter API key (from .env)
- `models` - Model selection for each agent (kimi_k2, claude_opus, gpt_52)
- `system_prompt` - Custom instructions for AI (e.g., writing style guidelines)
- `thesis_topic` - Context for text improvement

**Configuration Loading**:
```python
from multiagent_writer.config.config_manager import ConfigManager

manager = ConfigManager()
config = manager.load()  # Loads from config.json + .env
# config = {
#     'api_key': 'sk-or-v1-...',  # from .env
#     'models': {'kimi_k2': 'openai/gpt-oss-120b', ...},
#     'system_prompt': '...',
#     'thesis_topic': '...'
# }
```

### 4. UI Components (`ui/`)

#### MainWindow (`main_window.py`)
- Main application window with split view (input/output)
- Button management using `OutputButtonManager`
- Helper methods: `_close_progress_dialog()`, `_get_final_text()`, `_show_error_dialog()`

#### Dialogs (`dialogs.py`)
- `AnalysisDialog` - Displays Claude Opus analysis with Markdown rendering
- `SettingsDialog` - API key, model selection, system prompt configuration

#### Workers (`workers.py`)
- `APIWorker` - Background QThread for API calls to prevent UI blocking

#### ButtonManager (`button_manager.py`)
- `OutputButtonManager` - Manages state of 8 output buttons (copy, accept, export, etc.)

## Threading Model

**Main Thread**: PyQt6 UI event loop
- Handles all UI updates and user interactions
- Must not be blocked by long-running operations

**Worker Thread** (`APIWorker`):
- Runs API calls in background (30-60s duration)
- Emits signals: `progress` (status updates), `finished` (result), `error` (exception)
- Prevents UI freezing during multi-agent processing

**Thread Safety**:
- Only main thread modifies widgets
- Worker thread uses Qt signals to communicate with main thread
- No direct widget access from worker thread

**Signal Flow**:
```python
# In main thread
worker = APIWorker(api_service, mode, text)
worker.progress.connect(self.update_progress)      # Update progress dialog
worker.finished.connect(self.on_api_success)       # Handle success
worker.error.connect(self.on_api_error)            # Handle error
worker.start()                                      # Start in background

# In worker thread
self.progress.emit("Step 1/3: Processing...")     # Signals to main thread
result = api_service.improve_text(...)
self.finished.emit(result)                         # Signals to main thread
```

## Adding New Features

### Adding a New Multi-Agent Workflow

**1. Add new mode to `prompts/templates.py`:**
```python
def get_prompt_multi_agent(mode, agent_type, text, ...):
    # ... existing modes ...

    # Add new mode
    if mode == "zusammenfassen":  # New mode: Summarize
        if agent_type == "kimi_k2":
            return f"Fasse diesen Text zusammen:\n\n{text}"
        elif agent_type == "opus_analyse":
            return f"Analysiere diese Zusammenfassung:\n\n{text}"
        elif agent_type == "gpt_umsetzung":
            return f"Verbessere diese Zusammenfassung:\n\n{text}\n\nAnalyse:\n{analysis}"
```

**2. Add method to `api/service.py`:**
```python
def improve_text_zusammenfassen(self, text: str, status_callback=None) -> dict:
    """3-step workflow for summarizing text"""
    if not text or not text.strip():
        raise ValueError("Text darf nicht leer sein")

    # Step 1: Kimi K2
    prompt_kimi = get_prompt_multi_agent("zusammenfassen", "kimi_k2", text, ...)
    step1_kimi = self.client.call_model(text, self.config['models']['kimi_k2'], prompt_kimi)

    # Step 2: Opus Analyse
    prompt_opus = get_prompt_multi_agent("zusammenfassen", "opus_analyse", step1_kimi, ...)
    step2_analysis = self.client.call_model(step1_kimi, self.config['models']['claude_opus'], prompt_opus)

    # Step 3: GPT Umsetzung
    prompt_gpt = get_prompt_multi_agent("zusammenfassen", "gpt_umsetzung", step1_kimi, step2_analysis, ...)
    step3_final = self.client.call_model(step1_kimi, self.config['models']['gpt_52'], prompt_gpt)

    return {
        'step1_kimi': step1_kimi,
        'step2_analysis': step2_analysis,
        'step3_final': step3_final
    }
```

**3. Update UI in `ui/main_window.py`:**
```python
# In init_ui()
self.mode_combo.addItems(["ausformulieren", "korrekturlesen", "zusammenfassen"])

# In process_text()
if mode == "ausformulieren":
    result = api_service.improve_text_ausformulieren(text, status_callback)
elif mode == "korrekturlesen":
    result = api_service.improve_text_korrekturlesen(text, status_callback)
elif mode == "zusammenfassen":
    result = api_service.improve_text_zusammenfassen(text, status_callback)

# In on_api_success()
if mode == "zusammenfassen":
    self.current_analysis = result['step2_analysis']
    self.improved_text = result['step3_final']
```

### Adding a New AI Model

**1. Update `config/config_manager.py`:**
```python
DEFAULT_MODELS = {
    'kimi_k2': 'openai/gpt-oss-120b',
    'claude_opus': 'anthropic/claude-3.5-sonnet',
    'gpt_52': 'openai/gpt-4o',
    'gemini': 'google/gemini-2.0-flash-001'  # New model
}
```

**2. Update `config.json` template:**
```json
{
    "models": {
        "kimi_k2": "openai/gpt-oss-120b",
        "claude_opus": "anthropic/claude-3.5-sonnet",
        "gpt_52": "openai/gpt-4o",
        "gemini": "google/gemini-2.0-flash-001"
    }
}
```

**3. Use in workflow:**
```python
# In api/service.py
step1_result = self.client.call_model(text, self.config['models']['gemini'], prompt)
```

## Dependencies

**Core**:
- PyQt6 - GUI framework
- requests - HTTP client for OpenRouter API
- python-dotenv - Environment variable loading

**Built-in**:
- difflib - Text diff generation
- json - Config parsing
- threading - Background workers (QThread)

## Configuration Files

- `.env` - API key (git-ignored, user-specific)
- `config.json` - User settings (git-ignored after first run)
- `src/multiagent_writer/compat_api_service.py` - Compatibility layer for old code
- `pyproject.toml` - Package metadata & dependencies (coming in Phase 4)

## Testing Strategy

**Unit Tests**: Test individual components
- Config loading and validation
- Diff generation logic
- Prompt template generation

**Integration Tests**: Test API service workflows
- Mock OpenRouter API responses
- Test multi-step workflows
- Verify error handling

**UI Tests**: Test PyQt6 interactions (with pytest-qt)
- Button state management
- Dialog opening/closing
- Text input/output

## Security Considerations

1. **API Key Storage**: Never commit API keys
   - Use `.env` file (git-ignored)
   - Override from environment variables
   - Never log API keys

2. **Input Validation**: Validate all user inputs
   - Check for empty text before API calls
   - Validate config structure on load
   - Handle malformed JSON gracefully

3. **Error Handling**: Don't leak sensitive information
   - Sanitize error messages before display
   - Don't include API keys in error messages
   - Log errors without exposing credentials

4. **Rate Limiting**: OpenRouter handles rate limiting
   - Show user-friendly errors on rate limit
   - Don't retry automatically (avoid cost escalation)
   - Let user decide when to retry

## Performance Considerations

**API Calls**: 30-60 seconds per workflow
- Use background threads to prevent UI blocking
- Show progress dialog during processing
- Allow user to see incremental progress (Step 1/3, 2/3, 3/3)

**Diff Rendering**: Fast for texts up to 10,000 words
- Uses Python's `difflib` for efficient diff generation
- HTML rendering is done once, cached in InteractiveDiff
- Click handling is O(1) lookup by change_id

**Memory Usage**: Minimal
- Stores only current text and diff in memory
- No persistent history or undo stack
- Config file is <10KB

## Project Structure

```
MultiAgent-Writer/
├── src/
│   └── multiagent_writer/
│       ├── __init__.py
│       ├── main.py                     # Entry point
│       ├── compat_api_service.py       # Compatibility layer
│       ├── api/
│       │   ├── __init__.py
│       │   ├── errors.py              # Custom exceptions
│       │   ├── client.py              # OpenRouter HTTP client
│       │   └── service.py             # Multi-agent workflows
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── main_window.py         # Main application window
│       │   ├── dialogs.py             # Settings & Analysis dialogs
│       │   ├── workers.py             # APIWorker background thread
│       │   └── button_manager.py      # Button state management
│       ├── core/
│       │   ├── __init__.py
│       │   └── text_processor.py      # Diff generation & rendering
│       ├── prompts/
│       │   ├── __init__.py
│       │   └── templates.py           # LLM prompt templates
│       └── config/
│           ├── __init__.py
│           ├── config_manager.py      # Configuration loading/validation
│           └── constants.py           # UI constants & styling
├── docs/
│   ├── ARCHITECTURE.md                 # This file
│   └── API.md                          # API documentation
├── .env                                # API key (git-ignored)
├── .env.example                        # Template for .env
├── config.json                         # User settings (git-ignored)
├── requirements.txt                    # Python dependencies
├── CONTRIBUTING.md                     # Development guide
└── README.md                           # Project overview
```

## Code Patterns

### Error Handling
```python
try:
    result = api_service.improve_text_ausformulieren(text)
except AuthenticationError as e:
    show_error_dialog("Ungültiger API-Key")
except NetworkError as e:
    show_error_dialog("Keine Internetverbindung")
except APIError as e:
    show_error_dialog(f"API-Fehler: {e}")
```

### Status Updates
```python
def status_callback(message: str):
    """Called by API service to update progress"""
    progress_dialog.setLabelText(message)
    QApplication.processEvents()  # Update UI immediately

result = api_service.improve_text_ausformulieren(
    text,
    status_callback=status_callback
)
```

### Button State Management
```python
# Instead of:
self.copy_button.setEnabled(True)
self.accept_button.setEnabled(True)
self.export_button.setEnabled(True)
# ... 5 more lines

# Use:
self.button_manager.enable_all()
```

## Common Pitfalls

**1. Blocking UI Thread**
❌ Bad:
```python
result = api_service.improve_text(text)  # Blocks for 60s
```

✅ Good:
```python
worker = APIWorker(api_service, mode, text)
worker.finished.connect(self.on_api_success)
worker.start()  # Runs in background
```

**2. Missing Config Validation**
❌ Bad:
```python
model = config['models']['kimi_k2']  # KeyError if missing
```

✅ Good:
```python
config = config_manager.load()  # Auto-validates and fixes
model = config['models']['kimi_k2']  # Guaranteed to exist
```

**3. Inconsistent Change States**
❌ Bad:
```python
if change_id in accepted_changes:
    state = "accepted"
elif change_id in rejected_changes:
    state = "rejected"
```

✅ Good:
```python
state = self.changes[change_id].state  # Use ChangeState enum
```
