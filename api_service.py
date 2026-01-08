"""
OpenRouter API Service für Text-Verbesserung
"""

import json
import requests
from typing import Dict, Any
from prompts import get_prompt, get_prompt_multi_agent


class APIError(Exception):
    """Basis-Fehlerklasse für API-Fehler"""
    pass


class NetworkError(APIError):
    """Fehler bei Netzwerkverbindung"""
    pass


class RateLimitError(APIError):
    """API Rate Limit überschritten"""
    pass


class AuthenticationError(APIError):
    """Ungültiger API-Key"""
    pass


class APIService:
    """Service für OpenRouter API-Aufrufe"""

    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, config_path: str = "config.json"):
        """
        Initialisiert den API Service.

        Args:
            config_path: Pfad zur config.json Datei
        """
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Lädt die Konfiguration aus der JSON-Datei"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Erstelle Standard-Config wenn nicht vorhanden
            default_config = {
                "api_key": "",
                "model": "anthropic/claude-3.5-sonnet",
                "timeout": 60
            }
            self.save_config(default_config)
            return default_config
        except json.JSONDecodeError as e:
            raise APIError(f"Fehler beim Lesen der Config: {e}")

    def save_config(self, config: Dict[str, Any]) -> None:
        """Speichert die Konfiguration in die JSON-Datei"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        self.config = config

    def update_api_key(self, api_key: str) -> None:
        """Aktualisiert den API-Key in der Config"""
        self.config['api_key'] = api_key
        self.save_config(self.config)

    def update_model(self, model: str) -> None:
        """Aktualisiert das Model in der Config"""
        self.config['model'] = model
        self.save_config(self.config)

    def call_model(self, text: str, model: str, prompt: str) -> str:
        """
        Generische Methode für einzelnen Model-Call.

        Args:
            text: Der zu verarbeitende Text (wird in prompt bereits eingefügt sein)
            model: Model-Name (z.B. 'anthropic/claude-opus-4.5')
            prompt: Der fertige Prompt-String

        Returns:
            Die Antwort des Models

        Raises:
            APIError: Bei API-Fehlern
            NetworkError: Bei Netzwerkproblemen
            RateLimitError: Bei Rate-Limit-Überschreitung
            AuthenticationError: Bei ungültigem API-Key
        """
        if not self.config.get('api_key'):
            raise AuthenticationError("API-Key nicht konfiguriert.")

        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
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
                timeout=self.config.get('timeout', 180)  # Erhöht auf 180s für Multi-Agent
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

    def improve_text_ausformulieren(self, text: str, status_callback=None) -> dict:
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
        """
        if not text or not text.strip():
            raise ValueError("Text darf nicht leer sein")

        # Schritt 1: Kimi K2 ausformulieren
        if status_callback:
            status_callback("Schritt 1/3: Kimi K2 formuliert aus...")

        prompt_kimi = get_prompt_multi_agent(
            "ausformulieren", "kimi_k2", text,
            system_prompt=self.config.get('system_prompt', ''),
            thesis_topic=self.config.get('thesis_topic', '')
        )
        step1_kimi = self.call_model(text, self.config['models']['kimi_k2'], prompt_kimi)

        # Schritt 2: Opus 4.5 Analyse
        if status_callback:
            status_callback("Schritt 2/3: Claude Opus 4.5 analysiert...")

        prompt_opus = get_prompt_multi_agent(
            "ausformulieren", "opus_analyse", step1_kimi,
            system_prompt=self.config.get('system_prompt', ''),
            thesis_topic=self.config.get('thesis_topic', '')
        )
        step2_analysis = self.call_model(step1_kimi, self.config['models']['claude_opus'], prompt_opus)

        # Schritt 3: GPT-5.2 Umsetzung
        if status_callback:
            status_callback("Schritt 3/3: GPT-5.2 setzt um...")

        prompt_gpt = get_prompt_multi_agent(
            "ausformulieren", "gpt_umsetzung", step1_kimi, step2_analysis,
            system_prompt=self.config.get('system_prompt', ''),
            thesis_topic=self.config.get('thesis_topic', '')
        )
        step3_final = self.call_model(step1_kimi, self.config['models']['gpt_52'], prompt_gpt)

        return {
            'step1_kimi': step1_kimi,
            'step2_analysis': step2_analysis,
            'step3_final': step3_final
        }

    def improve_text_korrekturlesen(self, text: str, status_callback=None) -> dict:
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
        """
        if not text or not text.strip():
            raise ValueError("Text darf nicht leer sein")

        # Schritt 1: Opus 4.5 Analyse
        if status_callback:
            status_callback("Schritt 1/2: Claude Opus 4.5 analysiert...")

        prompt_opus = get_prompt_multi_agent(
            "korrekturlesen", "opus_analyse", text,
            system_prompt=self.config.get('system_prompt', ''),
            thesis_topic=self.config.get('thesis_topic', '')
        )
        step1_analysis = self.call_model(text, self.config['models']['claude_opus'], prompt_opus)

        # Schritt 2: GPT-5.2 Umsetzung
        if status_callback:
            status_callback("Schritt 2/2: GPT-5.2 setzt um...")

        prompt_gpt = get_prompt_multi_agent(
            "korrekturlesen", "gpt_umsetzung", text, step1_analysis,
            system_prompt=self.config.get('system_prompt', ''),
            thesis_topic=self.config.get('thesis_topic', '')
        )
        step2_final = self.call_model(text, self.config['models']['gpt_52'], prompt_gpt)

        return {
            'step1_analysis': step1_analysis,
            'step2_final': step2_final
        }

    def improve_text(self, text: str, mode: str, variant: str) -> str:
        """
        Verbessert den Text mittels OpenRouter API.

        Args:
            text: Der zu verbessernde Text
            mode: 'ausformulieren' oder 'korrekturlesen'
            variant: 'formal' oder 'balanced'

        Returns:
            Der verbesserte Text

        Raises:
            APIError: Bei API-Fehlern
            NetworkError: Bei Netzwerkproblemen
            RateLimitError: Bei Rate-Limit-Überschreitung
            AuthenticationError: Bei ungültigem API-Key
        """
        # Validierung
        if not text or not text.strip():
            raise ValueError("Text darf nicht leer sein")

        if not self.config.get('api_key'):
            raise AuthenticationError("API-Key nicht konfiguriert. Bitte in den Einstellungen eintragen.")

        # Prompt generieren
        try:
            prompt = get_prompt(mode, variant, text)
        except ValueError as e:
            raise APIError(str(e))

        # API-Request vorbereiten
        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/thesis-improver",
            "X-Title": "Thesis Improver"
        }

        data = {
            "model": self.config.get('model', 'anthropic/claude-3.5-sonnet'),
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        # API-Request ausführen
        try:
            response = requests.post(
                self.BASE_URL,
                headers=headers,
                json=data,
                timeout=self.config.get('timeout', 60)
            )

            # Status-Code prüfen
            if response.status_code == 401:
                raise AuthenticationError("API-Key ungültig. Bitte in den Einstellungen prüfen.")
            elif response.status_code == 429:
                raise RateLimitError("Zu viele Anfragen. Bitte einen Moment warten.")
            elif response.status_code >= 500:
                raise APIError(f"Server-Fehler: {response.status_code}")

            response.raise_for_status()

            # Response parsen
            response_data = response.json()

            if 'choices' not in response_data or not response_data['choices']:
                raise APIError("Ungültige API-Antwort: Keine Choices gefunden")

            improved_text = response_data['choices'][0]['message']['content']
            return improved_text.strip()

        except requests.exceptions.Timeout:
            raise NetworkError("Zeitüberschreitung bei der API-Anfrage. Bitte erneut versuchen.")
        except requests.exceptions.ConnectionError:
            raise NetworkError("Keine Internetverbindung. Bitte Verbindung prüfen.")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Netzwerkfehler: {str(e)}")
        except json.JSONDecodeError:
            raise APIError("Fehler beim Parsen der API-Antwort")


def test_api():
    """Einfacher Test der API-Funktionalität"""
    service = APIService()

    test_text = "KI ist wichtig"

    print(f"Config geladen: {service.config}")
    print(f"\nTest-Text: {test_text}")

    if not service.config.get('api_key'):
        print("\n⚠️  API-Key nicht konfiguriert!")
        print("Bitte trage deinen OpenRouter API-Key in config.json ein.")
        return

    try:
        print("\nSende Anfrage an API...")
        result = service.improve_text(test_text, "ausformulieren", "formal")
        print(f"\n✓ Erfolg!")
        print(f"\nVerbesserter Text:\n{result}")
    except APIError as e:
        print(f"\n✗ Fehler: {e}")


if __name__ == "__main__":
    test_api()
