"""
Configuration management for the application
"""

import json
import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv


class ConfigManager:
    """Manages application configuration"""

    CONFIG_FILE = "config.json"

    # Default models for multi-agent workflows
    DEFAULT_MODELS = {
        'kimi_k2': 'openai/gpt-oss-120b',
        'claude_opus': 'anthropic/claude-3.5-sonnet',
        'gpt_52': 'openai/gpt-4o'
    }

    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the config manager.

        Args:
            config_path: Path to config.json file
        """
        self.config_path = Path(config_path)
        load_dotenv()  # Load .env file

    def load(self) -> Dict[str, Any]:
        """
        Load and validate configuration.

        Returns:
            Complete configuration dictionary

        Raises:
            ValueError: If config.json has invalid JSON
        """
        if not self.config_path.exists():
            return self._create_default_config()

        config = self._load_json()
        config = self._validate_and_fix(config)

        # Apply model quality tier
        quality = config.get('model_quality', 'guenstig')
        config['models'] = self.get_models_for_quality(quality)

        # Override API key from environment if present
        env_key = os.getenv('OPENROUTER_API_KEY')
        if env_key:
            config['api_key'] = env_key

        return config

    def save(self, config: Dict[str, Any]) -> None:
        """
        Save configuration to file.

        Args:
            config: Configuration dictionary to save
        """
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

    def get_models_for_quality(self, quality: str) -> Dict[str, str]:
        """
        Get model configuration for specified quality tier.

        Args:
            quality: Quality tier identifier (e.g., "guenstig", "high_end")

        Returns:
            Dictionary mapping model keys to model IDs
        """
        from .constants import ModelQuality
        return ModelQuality.CONFIGURATIONS.get(
            quality,
            ModelQuality.CONFIGURATIONS[ModelQuality.CHEAP]
        )

    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration"""
        default = {
            "api_key": "",
            "model": "anthropic/claude-3.5-sonnet",
            "timeout": 180,
            "model_quality": "guenstig",  # Default to cheap tier
            "models": self.DEFAULT_MODELS.copy(),
            "system_prompt": "",
            "thesis_topic": ""
        }
        self.save(default)
        return default

    def _load_json(self) -> Dict[str, Any]:
        """Load JSON from file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config.json: {e}")

    def _validate_and_fix(self, config: dict) -> dict:
        """
        Validate config and add missing keys with defaults.

        Args:
            config: Configuration dictionary to validate

        Returns:
            Validated and fixed configuration
        """
        # Ensure 'models' exists
        if 'models' not in config or not isinstance(config['models'], dict):
            config['models'] = self.DEFAULT_MODELS.copy()

        # Ensure required model keys exist
        for key, default_model in self.DEFAULT_MODELS.items():
            if key not in config['models']:
                config['models'][key] = default_model

        # Ensure other required keys
        if 'system_prompt' not in config:
            config['system_prompt'] = ""
        if 'thesis_topic' not in config:
            config['thesis_topic'] = ""
        if 'timeout' not in config:
            config['timeout'] = 180
        if 'model' not in config:
            config['model'] = "anthropic/claude-3.5-sonnet"
        if 'api_key' not in config:
            config['api_key'] = ""
        if 'model_quality' not in config:
            config['model_quality'] = "guenstig"

        return config
