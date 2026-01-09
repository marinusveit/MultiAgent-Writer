# API Documentation

This document provides detailed API documentation for MultiAgent-Writer's public classes and methods.

## Table of Contents

- [Configuration](#configuration)
  - [ConfigManager](#configmanager)
- [API Service](#api-service)
  - [TextImprovementService](#textimprovementservice)
  - [OpenRouterClient](#openrouterclient)
- [Text Processing](#text-processing)
  - [InteractiveDiff](#interactivediff)
  - [TextProcessor](#textprocessor)
- [Custom Exceptions](#custom-exceptions)
- [UI Components](#ui-components)
  - [OutputButtonManager](#outputbuttonmanager)

---

## Configuration

### ConfigManager

Manages application configuration with environment variable support and automatic validation.

**Module**: `multiagent_writer.config.config_manager`

#### Constructor

```python
ConfigManager(config_path: str = "config.json")
```

**Parameters**:
- `config_path` (str, optional): Path to config.json file. Defaults to "config.json".

**Example**:
```python
from multiagent_writer.config.config_manager import ConfigManager

manager = ConfigManager()
config = manager.load()
```

#### Methods

##### `load() -> Dict[str, Any]`

Loads and validates configuration from config.json and .env file.

**Returns**: Complete configuration dictionary with validated structure.

**Raises**: `ValueError` if config.json contains invalid JSON.

**Behavior**:
1. Loads config.json if it exists, otherwise creates default config
2. Validates and fixes missing keys with defaults
3. Overrides API key from OPENROUTER_API_KEY environment variable (if set)

**Example**:
```python
config = manager.load()
# {
#     'api_key': 'sk-or-v1-...',  # from .env
#     'model': 'anthropic/claude-3.5-sonnet',
#     'timeout': 180,
#     'models': {
#         'kimi_k2': 'openai/gpt-oss-120b',
#         'claude_opus': 'anthropic/claude-3.5-sonnet',
#         'gpt_52': 'openai/gpt-4o'
#     },
#     'system_prompt': '...',
#     'thesis_topic': '...'
# }
```

##### `save(config: Dict[str, Any]) -> None`

Saves configuration to config.json file.

**Parameters**:
- `config` (Dict[str, Any]): Configuration dictionary to save

**Example**:
```python
config['system_prompt'] = "Write in formal academic style"
manager.save(config)
```

---

## API Service

### TextImprovementService

Multi-agent text improvement service that orchestrates API calls through OpenRouter.

**Module**: `multiagent_writer.api.service`

#### Constructor

```python
TextImprovementService(config: Dict[str, Any])
```

**Parameters**:
- `config` (Dict[str, Any]): Configuration dictionary from ConfigManager

**Example**:
```python
from multiagent_writer.api.service import TextImprovementService
from multiagent_writer.config.config_manager import ConfigManager

config = ConfigManager().load()
service = TextImprovementService(config)
```

#### Methods

##### `improve_text_ausformulieren(text: str, status_callback=None) -> dict`

3-step workflow for expanding bullet points into full text.

**Workflow**:
1. **Kimi K2**: Formulates bullet points into sentences
2. **Claude Opus**: Analyzes formulated text for improvements
3. **GPT-4o**: Implements improvements from analysis

**Parameters**:
- `text` (str): Input text (bullet points or short notes)
- `status_callback` (Optional[Callable[[str], None]]): Progress callback function

**Returns**: Dictionary with results from each step:
```python
{
    'step1_kimi': str,       # Kimi K2 formulated text
    'step2_analysis': str,   # Claude Opus analysis
    'step3_final': str       # GPT-4o final text
}
```

**Raises**:
- `ValueError`: Empty input text
- `AuthenticationError`: Invalid API key
- `NetworkError`: Connection issues
- `RateLimitError`: Too many requests
- `APIError`: Other API errors

**Example**:
```python
text = """
- KI ist wichtig
- Anwendungen in Medizin
- Ethische Fragen
"""

def update_status(message):
    print(f"Status: {message}")

result = service.improve_text_ausformulieren(
    text,
    status_callback=update_status
)

print(result['step3_final'])
# Output:
# Künstliche Intelligenz spielt eine zunehmend wichtige Rolle...
```

##### `improve_text_korrekturlesen(text: str, status_callback=None) -> dict`

2-step workflow for proofreading and improving existing text.

**Workflow**:
1. **Claude Opus**: Analyzes text for errors and improvements
2. **GPT-4o**: Applies corrections from analysis

**Parameters**:
- `text` (str): Input text (full sentences/paragraphs)
- `status_callback` (Optional[Callable[[str], None]]): Progress callback

**Returns**: Dictionary with results from each step:
```python
{
    'step1_analysis': str,   # Claude Opus analysis
    'step2_final': str       # GPT-4o corrected text
}
```

**Raises**: Same as `improve_text_ausformulieren()`

**Example**:
```python
text = "Die künstliche Inteligenz ist ein wichtiger Faktor für die zukunft."

result = service.improve_text_korrekturlesen(text)

print(result['step2_final'])
# Output:
# Die künstliche Intelligenz ist ein wichtiger Faktor für die Zukunft.
```

---

### OpenRouterClient

Low-level HTTP client for OpenRouter API communication.

**Module**: `multiagent_writer.api.client`

#### Constructor

```python
OpenRouterClient(api_key: str, timeout: int = 180)
```

**Parameters**:
- `api_key` (str): OpenRouter API key
- `timeout` (int, optional): Request timeout in seconds. Defaults to 180.

**Example**:
```python
from multiagent_writer.api.client import OpenRouterClient

client = OpenRouterClient(api_key="sk-or-v1-...", timeout=180)
```

#### Methods

##### `call_model(text: str, model: str, prompt: str) -> str`

Makes single API call to OpenRouter.

**Parameters**:
- `text` (str): The text to process (used for logging/tracking)
- `model` (str): Model identifier (e.g., "anthropic/claude-3.5-sonnet")
- `prompt` (str): Complete prompt string to send to the model

**Returns**: Model response as string

**Raises**:
- `AuthenticationError`: Invalid API key (HTTP 401)
- `RateLimitError`: Rate limit exceeded (HTTP 429)
- `APIError`: Server error (HTTP 400, 500+)
- `NetworkError`: Connection issues, timeouts

**Example**:
```python
prompt = "Verbessere diesen Text: KI ist wichtig"
response = client.call_model(
    text="KI ist wichtig",
    model="anthropic/claude-3.5-sonnet",
    prompt=prompt
)
print(response)
```

---

## Text Processing

### InteractiveDiff

Interactive word-level diff with accept/reject functionality.

**Module**: `multiagent_writer.core.text_processor`

#### Constructor

```python
InteractiveDiff(original_text: str, modified_text: str)
```

**Parameters**:
- `original_text` (str): Original text before improvements
- `modified_text` (str): Improved text after AI processing

**Example**:
```python
from multiagent_writer.core.text_processor import InteractiveDiff

diff = InteractiveDiff(
    original_text="KI wichtig",
    modified_text="KI ist wichtig"
)
```

#### Methods

##### `get_statistics() -> Dict[str, int]`

Returns statistics about the diff.

**Returns**: Dictionary with diff statistics:
```python
{
    'words_added': int,      # Number of words added
    'words_removed': int,    # Number of words removed
    'chars_added': int,      # Number of characters added
    'chars_removed': int,    # Number of characters removed
    'changes': int           # Total number of changes
}
```

**Example**:
```python
stats = diff.get_statistics()
print(f"Added: {stats['words_added']} words, Removed: {stats['words_removed']} words")
# Output: Added: 1 words, Removed: 0 words
```

##### `generate_interactive_html() -> str`

Returns HTML representation with clickable changes.

**Returns**: HTML string with styled diff

**Example**:
```python
html = diff.generate_interactive_html()
# HTML contains:
# - Green background for additions
# - Red background for deletions
# - Clickable spans with change IDs
# - Title attributes for tooltips
```

##### `toggle_change_state(change_id: int) -> None`

Toggles change between ACCEPTED and REJECTED states.

**Parameters**:
- `change_id` (int): ID of the change to toggle

**Behavior**:
- PENDING → ACCEPTED (first click)
- ACCEPTED → REJECTED (second click)
- REJECTED → PENDING (third click)

**Example**:
```python
diff.toggle_change_state(0)  # Accept first change
diff.toggle_change_state(0)  # Reject first change
diff.toggle_change_state(0)  # Reset to pending
```

##### `accept_all() -> None`

Accepts all pending changes.

**Example**:
```python
diff.accept_all()
final_text = diff.get_final_text()  # All changes applied
```

##### `reject_all() -> None`

Rejects all pending changes (keeps original).

**Example**:
```python
diff.reject_all()
final_text = diff.get_final_text()  # Original text unchanged
```

##### `get_final_text() -> str`

Gets final text based on accepted/rejected changes.

**Returns**: Final text with accepted changes applied and rejected changes reverted

**Example**:
```python
# Accept some changes, reject others
diff.toggle_change_state(0)  # Accept
diff.toggle_change_state(1)  # Accept
diff.toggle_change_state(1)  # Reject (toggle again)

final_text = diff.get_final_text()
# Returns text with only change 0 applied
```

---

### TextProcessor

Helper class for text processing operations.

**Module**: `multiagent_writer.core.text_processor`

#### Methods

##### `clean_text(text: str) -> str`

Cleans text by normalizing whitespace and removing control characters.

**Parameters**:
- `text` (str): Text to clean

**Returns**: Cleaned text

**Example**:
```python
from multiagent_writer.core.text_processor import TextProcessor

processor = TextProcessor()
cleaned = processor.clean_text("Text  with   extra   spaces")
# Returns: "Text with extra spaces"
```

---

## Custom Exceptions

All exceptions are in `multiagent_writer.api.errors`.

### APIError

Base class for all API-related errors.

**Usage**:
```python
from multiagent_writer.api.errors import APIError

try:
    result = service.improve_text(text)
except APIError as e:
    print(f"API error: {e}")
```

### NetworkError(APIError)

Raised for network connection issues.

**Common Causes**:
- No internet connection
- Request timeout
- DNS resolution failure

**Usage**:
```python
from multiagent_writer.api.errors import NetworkError

try:
    result = client.call_model(...)
except NetworkError as e:
    print("Check your internet connection")
```

### RateLimitError(APIError)

Raised when OpenRouter rate limit is exceeded.

**Usage**:
```python
from multiagent_writer.api.errors import RateLimitError

try:
    result = service.improve_text(text)
except RateLimitError as e:
    print("Too many requests. Wait and try again.")
```

### AuthenticationError(APIError)

Raised for invalid API key.

**Usage**:
```python
from multiagent_writer.api.errors import AuthenticationError

try:
    result = service.improve_text(text)
except AuthenticationError as e:
    print("Invalid API key. Check settings.")
```

---

## UI Components

### OutputButtonManager

Manages state of multiple output buttons collectively.

**Module**: `multiagent_writer.ui.button_manager`

#### Constructor

```python
OutputButtonManager(buttons: List[QPushButton])
```

**Parameters**:
- `buttons` (List[QPushButton]): List of buttons to manage

**Example**:
```python
from multiagent_writer.ui.button_manager import OutputButtonManager

button_manager = OutputButtonManager([
    self.copy_button,
    self.accept_button,
    self.export_button,
    self.reset_button
])
```

#### Methods

##### `enable_all() -> None`

Enables all managed buttons.

**Example**:
```python
button_manager.enable_all()
# All 4 buttons are now enabled
```

##### `disable_all() -> None`

Disables all managed buttons.

**Example**:
```python
button_manager.disable_all()
# All 4 buttons are now disabled
```

---

## Status Callbacks

Progress callbacks are used to update UI during multi-step workflows.

**Signature**:
```python
def status_callback(message: str) -> None:
    """Called by API service to report progress"""
    pass
```

**Example in PyQt6**:
```python
def update_progress(self, message: str):
    """Update progress dialog"""
    if hasattr(self, 'progress_dialog') and self.progress_dialog:
        self.progress_dialog.setLabelText(message)
    QApplication.processEvents()  # Update UI immediately

# Use in API call
worker = APIWorker(api_service, mode, text)
worker.progress.connect(self.update_progress)
worker.start()
```

**Example messages**:
- "Schritt 1/3: Kimi K2 formuliert aus..."
- "Schritt 2/3: Claude Opus 4.5 analysiert..."
- "Schritt 3/3: GPT-5.2 setzt um..."

---

## Complete Usage Example

```python
from multiagent_writer.config.config_manager import ConfigManager
from multiagent_writer.api.service import TextImprovementService
from multiagent_writer.api.errors import APIError, AuthenticationError
from multiagent_writer.core.text_processor import InteractiveDiff

# 1. Load configuration
config_manager = ConfigManager()
config = config_manager.load()

# 2. Create service
service = TextImprovementService(config)

# 3. Improve text
text = """
- KI ist wichtig
- Anwendungen in Medizin
- Ethische Fragen
"""

try:
    # Progress callback
    def show_progress(msg):
        print(f"Progress: {msg}")

    # Call API
    result = service.improve_text_ausformulieren(
        text,
        status_callback=show_progress
    )

    # 4. Create interactive diff
    diff = InteractiveDiff(
        original_text=text,
        modified_text=result['step3_final']
    )

    # 5. Get statistics
    stats = diff.get_statistics()
    print(f"Changes: {stats['changes']}")
    print(f"Words added: {stats['words_added']}")

    # 6. Toggle some changes
    diff.toggle_change_state(0)  # Accept first change
    diff.toggle_change_state(1)  # Accept second change

    # 7. Get final text
    final_text = diff.get_final_text()
    print(final_text)

except AuthenticationError:
    print("Error: Invalid API key")
except APIError as e:
    print(f"Error: {e}")
```

---

## Type Hints

All public methods include type hints for better IDE support:

```python
from typing import Dict, Any, Optional, Callable, List

def improve_text_ausformulieren(
    self,
    text: str,
    status_callback: Optional[Callable[[str], None]] = None
) -> Dict[str, str]:
    """..."""
    pass

def get_statistics(self) -> Dict[str, int]:
    """..."""
    pass

def enable_all(self) -> None:
    """..."""
    pass
```

---

## Error Handling Best Practices

**1. Catch specific exceptions**:
```python
try:
    result = service.improve_text(text)
except AuthenticationError:
    show_error("Invalid API key")
except NetworkError:
    show_error("No internet connection")
except RateLimitError:
    show_error("Too many requests")
except APIError as e:
    show_error(f"API error: {e}")
```

**2. Use status callbacks for progress**:
```python
def status_callback(message: str):
    progress_dialog.setLabelText(message)
    QApplication.processEvents()

result = service.improve_text_ausformulieren(
    text,
    status_callback=status_callback
)
```

**3. Validate input before API calls**:
```python
if not text or not text.strip():
    show_error("Please enter text")
    return

result = service.improve_text(text)
```

---

## API Rate Limits

OpenRouter enforces rate limits based on your account tier. The application handles rate limit errors gracefully:

- **429 Response**: RateLimitError is raised
- **User Action**: Wait and retry manually
- **No Automatic Retry**: Prevents unexpected cost escalation

**Best Practices**:
- Wait 60 seconds after rate limit error
- Don't implement automatic retry without user confirmation
- Monitor costs through OpenRouter dashboard
