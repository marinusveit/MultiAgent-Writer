"""
OpenRouter API Client for low-level HTTP communication
"""

import json
import requests
from typing import Dict, Any

from .errors import APIError, NetworkError, RateLimitError, AuthenticationError


class OpenRouterClient:
    """Low-level OpenRouter API client"""

    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, api_key: str, timeout: int = 180):
        """
        Initialize the OpenRouter client.

        Args:
            api_key: OpenRouter API key
            timeout: Request timeout in seconds (default: 180)
        """
        self.api_key = api_key
        self.timeout = timeout

    def call_model(self, text: str, model: str, prompt: str) -> str:
        """
        Make API call to OpenRouter.

        Args:
            text: The text to process (for logging/tracking)
            model: Model name (e.g., 'anthropic/claude-opus-4.5')
            prompt: The complete prompt string

        Returns:
            The model's response as string

        Raises:
            APIError: Bei API-Fehlern
            NetworkError: Bei Netzwerkproblemen
            RateLimitError: Bei Rate-Limit-Überschreitung
            AuthenticationError: Bei ungültigem API-Key
        """
        if not self.api_key:
            raise AuthenticationError("API-Key nicht konfiguriert.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/thesis-improver",
            "X-Title": "Thesis Improver Multi-Agent"
        }

        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            response = requests.post(
                self.BASE_URL,
                headers=headers,
                json=data,
                timeout=self.timeout
            )

            if response.status_code == 401:
                raise AuthenticationError("API-Key ungültig.")
            elif response.status_code == 429:
                raise RateLimitError("Zu viele Anfragen. Bitte warten.")
            elif response.status_code == 400:
                # 400 Bad Request - lese den detaillierten Fehler aus der Response
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Unbekannter Fehler')
                    raise APIError(f"Ungültige Anfrage: {error_msg}")
                except json.JSONDecodeError:
                    raise APIError(f"Ungültige Anfrage (400): {response.text}")
            elif response.status_code >= 500:
                raise APIError(f"Server-Fehler: {response.status_code}")

            response.raise_for_status()
            response_data = response.json()

            if 'choices' not in response_data or not response_data['choices']:
                raise APIError("Ungültige API-Antwort")

            return response_data['choices'][0]['message']['content'].strip()

        except requests.exceptions.Timeout:
            raise NetworkError("Zeitüberschreitung bei der API-Anfrage.")
        except requests.exceptions.ConnectionError:
            raise NetworkError("Keine Internetverbindung.")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Netzwerkfehler: {str(e)}")
        except json.JSONDecodeError:
            raise APIError("Fehler beim Parsen der API-Antwort")
