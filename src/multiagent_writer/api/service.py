"""
Multi-agent text improvement service
"""

from typing import Dict, Any, Optional, Callable

from .client import OpenRouterClient
from .errors import APIError, NetworkError, RateLimitError, AuthenticationError


class TextImprovementService:
    """Multi-agent text improvement service"""

    # Default models for multi-agent workflows
    DEFAULT_MODELS = {
        'kimi_k2': 'openai/gpt-oss-120b',
        'claude_opus': 'anthropic/claude-3.5-sonnet',
        'gpt_52': 'openai/gpt-4o'
    }

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the text improvement service.

        Args:
            config: Configuration dictionary with api_key, models, etc.
        """
        self.config = config
        self.client = OpenRouterClient(
            api_key=config['api_key'],
            timeout=config.get('timeout', 180)
        )

    def improve_text_ausformulieren(
        self,
        text: str,
        status_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, str]:
        """
        3-Schritt-Prozess für Ausformulieren.

        Workflow:
        1. Kimi K2: Formuliert Stichpunkte aus
        2. Claude Opus 4.5: Analysiert den ausformulierten Text
        3. GPT-5.2: Setzt die Verbesserungsvorschläge um

        Args:
            text: Die Stichpunkte/Rohtext
            status_callback: Optional - Funktion für Status-Updates

        Returns:
            {
                'step1_kimi': str,      # Von Kimi K2 ausformuliert
                'step2_analysis': str,  # Opus 4.5 Analyse
                'step3_final': str      # GPT-5.2 finaler Text
            }

        Raises:
            ValueError: Text darf nicht leer sein
            AuthenticationError: Ungültiger API-Key
            NetworkError: Netzwerkprobleme
            RateLimitError: Rate-Limit-Überschreitung
            APIError: API-Fehler
        """
        if not text or not text.strip():
            raise ValueError("Text darf nicht leer sein")

        # Import here to avoid circular dependency
        from ..prompts.templates import get_prompt_multi_agent

        # Schritt 1: Kimi K2 ausformulieren
        if status_callback:
            status_callback("Schritt 1/3: Kimi K2 formuliert aus...")

        prompt_kimi = get_prompt_multi_agent(
            "ausformulieren", "kimi_k2", text,
            system_prompt=self.config.get('system_prompt', ''),
            thesis_topic=self.config.get('thesis_topic', '')
        )
        step1_kimi = self.client.call_model(text, self.config['models']['kimi_k2'], prompt_kimi)

        # Schritt 2: Opus 4.5 Analyse
        if status_callback:
            status_callback("Schritt 2/3: Claude Opus 4.5 analysiert...")

        prompt_opus = get_prompt_multi_agent(
            "ausformulieren", "opus_analyse", step1_kimi,
            system_prompt=self.config.get('system_prompt', ''),
            thesis_topic=self.config.get('thesis_topic', '')
        )
        step2_analysis = self.client.call_model(step1_kimi, self.config['models']['claude_opus'], prompt_opus)

        # Schritt 3: GPT-5.2 Umsetzung
        if status_callback:
            status_callback("Schritt 3/3: GPT-5.2 setzt um...")

        prompt_gpt = get_prompt_multi_agent(
            "ausformulieren", "gpt_umsetzung", step1_kimi, step2_analysis,
            system_prompt=self.config.get('system_prompt', ''),
            thesis_topic=self.config.get('thesis_topic', '')
        )
        step3_final = self.client.call_model(step1_kimi, self.config['models']['gpt_52'], prompt_gpt)

        return {
            'step1_kimi': step1_kimi,
            'step2_analysis': step2_analysis,
            'step3_final': step3_final
        }

    def improve_text_korrekturlesen(
        self,
        text: str,
        status_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, str]:
        """
        2-Schritt-Prozess für Korrekturlesen.

        Workflow:
        1. Claude Opus 4.5: Analysiert den Text
        2. GPT-5.2: Setzt die Korrekturvorschläge um

        Args:
            text: Der zu korrigierende Text
            status_callback: Optional - Funktion für Status-Updates

        Returns:
            {
                'step1_analysis': str,  # Opus 4.5 Analyse
                'step2_final': str      # GPT-5.2 korrigierter Text
            }

        Raises:
            ValueError: Text darf nicht leer sein
            AuthenticationError: Ungültiger API-Key
            NetworkError: Netzwerkprobleme
            RateLimitError: Rate-Limit-Überschreitung
            APIError: API-Fehler
        """
        if not text or not text.strip():
            raise ValueError("Text darf nicht leer sein")

        # Import here to avoid circular dependency
        from ..prompts.templates import get_prompt_multi_agent

        # Schritt 1: Opus 4.5 Analyse
        if status_callback:
            status_callback("Schritt 1/2: Claude Opus 4.5 analysiert...")

        prompt_opus = get_prompt_multi_agent(
            "korrekturlesen", "opus_analyse", text,
            system_prompt=self.config.get('system_prompt', ''),
            thesis_topic=self.config.get('thesis_topic', '')
        )
        step1_analysis = self.client.call_model(text, self.config['models']['claude_opus'], prompt_opus)

        # Schritt 2: GPT-5.2 Umsetzung
        if status_callback:
            status_callback("Schritt 2/2: GPT-5.2 setzt um...")

        prompt_gpt = get_prompt_multi_agent(
            "korrekturlesen", "gpt_umsetzung", text, step1_analysis,
            system_prompt=self.config.get('system_prompt', ''),
            thesis_topic=self.config.get('thesis_topic', '')
        )
        step2_final = self.client.call_model(text, self.config['models']['gpt_52'], prompt_gpt)

        return {
            'step1_analysis': step1_analysis,
            'step2_final': step2_final
        }
