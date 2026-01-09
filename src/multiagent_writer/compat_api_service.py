"""
Compatibility layer for old API Service interface
This allows existing code to work while we migrate to the new structure
"""

from typing import Dict, Any
from .api.service import TextImprovementService
from .api.errors import APIError, NetworkError, RateLimitError, AuthenticationError
from .config.config_manager import ConfigManager


class APIService:
    """
    Compatibility wrapper for the old APIService interface.
    Uses the new modular structure underneath.
    """

    def __init__(self, config_path: str = "config.json"):
        """Initialize the API service"""
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.load()
        self.service = TextImprovementService(self.config)

    def load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        self.config = self.config_manager.load()
        return self.config

    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration"""
        self.config_manager.save(config)
        self.config = config
        # Reinitialize service with new config
        self.service = TextImprovementService(config)

    def update_api_key(self, api_key: str) -> None:
        """Update API key in config"""
        self.config['api_key'] = api_key
        self.save_config(self.config)

    def update_model(self, model: str) -> None:
        """Update model in config"""
        self.config['model'] = model
        self.save_config(self.config)

    def improve_text_ausformulieren(self, text: str, status_callback=None) -> dict:
        """3-step workflow for expanding bullet points"""
        return self.service.improve_text_ausformulieren(text, status_callback)

    def improve_text_korrekturlesen(self, text: str, status_callback=None) -> dict:
        """2-step workflow for proofreading"""
        return self.service.improve_text_korrekturlesen(text, status_callback)
