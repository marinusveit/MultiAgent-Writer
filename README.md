# Thesis Improver - Multi-Agent Edition

**Version 2.0** - KI-gestütztes Text-Tool für Masterarbeiten mit Multi-Agent-Workflow

Ein Desktop-Tool zur Unterstützung beim Schreiben wissenschaftlicher Arbeiten, das mehrere KI-Modelle koordiniert für bestmögliche Ergebnisse.

## ✨ Features

### Multi-Agent-Workflows

**Ausformulieren** (3-Schritt-Prozess):
1. **Kimi K2**: Formuliert Stichpunkte in akademischen Text aus
2. **Claude Opus 4.5**: Analysiert den Text kritisch (fachlich + grammatikalisch)
3. **GPT-5.2**: Setzt alle Verbesserungsvorschläge um

**Korrekturlesen** (2-Schritt-Prozess):
1. **Claude Opus 4.5**: Analysiert Fehler und Schwachstellen
2. **GPT-5.2**: Korrigiert den Text basierend auf der Analyse

### Weitere Features

- **Detaillierte Analyse-Ansicht**: Zeigt die vollständige Analyse von Claude Opus 4.5
- **Diff-Ansicht**: Farbliche Hervorhebung aller Änderungen
  - Grün = Hinzugefügt
  - Rot = Gelöscht
  - Gelb = Geändert
- **Umschaltbar**: Zwischen Diff-Ansicht und reinem Text
- **Export-Funktion**: Speichern als .txt Datei
- **Statistiken**: Wortanzahl-Änderungen, Anzahl der Modifikationen
- **Cross-Platform**: Läuft auf Windows und Linux

## 📋 Voraussetzungen

- Python 3.10 oder höher
- OpenRouter API-Key mit Zugriff auf:
  - Kimi K2 (`moonshot/kimi-k1.5`)
  - Claude Opus 4 (`anthropic/claude-opus-4`)
  - GPT-4o Latest (`openai/chatgpt-4o-latest`)

## 🚀 Installation

### 1. Repository klonen

```bash
git clone <repository-url>
cd MultiAgent-Writer
```

### 2. Virtual Environment erstellen

```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Dependencies installieren

```bash
pip install -r requirements.txt
```

### 4. API-Key konfigurieren

Öffne `config.json` und trage deinen OpenRouter API-Key ein:

```json
{
    "api_key": "sk-or-v1-dein_api_key_hier",
    "model": "anthropic/claude-3.5-sonnet",
    "timeout": 180,
    "models": {
        "kimi_k2": "moonshot/kimi-k1.5",
        "claude_opus": "anthropic/claude-opus-4",
        "gpt_52": "openai/chatgpt-4o-latest"
    }
}
```

**Oder:** Verwende die Einstellungen in der Anwendung (Menü → Einstellungen)

## 🎯 Verwendung

### Anwendung starten

```bash
python main.py
```

### Workflow

1. **Text eingeben** im linken Feld
   - Für Ausformulieren: Stichpunkte oder Rohtext
   - Für Korrekturlesen: Fertiger Text

2. **Modus wählen**
   - Ausformulieren (3 Agents)
   - Korrekturlesen (2 Agents)

3. **Verarbeiten klicken** (oder Ctrl+Enter)
   - Sehe Live-Status-Updates für jeden Schritt
   - Warte auf Fertigstellung (kann 1-3 Minuten dauern)

4. **Ergebnis prüfen**
   - Diff-Ansicht zeigt farblich alle Änderungen
   - Klicke "📊 Analyse anzeigen" für Details

5. **Aktionen**
   - "Übernehmen": Kopiert verbesserten Text zurück
   - "In Zwischenablage": Kopiert für andere Apps
   - "Als .txt speichern": Exportiert das Ergebnis

### Tastatur-Shortcuts

- `Ctrl+Enter`: Text verarbeiten
- `Ctrl+K`: In Zwischenablage kopieren
- `Ctrl+S`: Exportieren
- `Ctrl+Q`: Beenden

## 🔑 OpenRouter API-Key erhalten

1. Gehe zu **https://openrouter.ai**
2. Registriere einen Account
3. Navigiere zu **"Keys"** im Dashboard
4. Erstelle einen neuen API-Key
5. Lade Guthaben auf:
   - ~5-10€ reichen für viele Anfragen
   - Multi-Agent = höhere Kosten (3 bzw. 2 API-Calls pro Text)

## 💰 Kosten

**Wichtig:** Multi-Agent-Workflows verwenden mehrere Modelle!

### Ausformulieren
- 3 API-Calls: Kimi K2 + Opus 4 + GPT-4o
- Ca. 2-5 Cent pro 1000 Wörter (abhängig von Textlänge)

### Korrekturlesen
- 2 API-Calls: Opus 4 + GPT-4o
- Ca. 1-3 Cent pro 1000 Wörter

**Tipp:** Bei längeren Texten (> 2000 Wörter) in Absätze aufteilen.

## ⚙️ Konfiguration

### Modelle anpassen

In `config.json` kannst du die verwendeten Modelle ändern:

```json
{
    "models": {
        "kimi_k2": "moonshot/kimi-k1.5",
        "claude_opus": "anthropic/claude-opus-4",
        "gpt_52": "openai/chatgpt-4o-latest"
    }
}
```

Verfügbare Alternativen (OpenRouter):
- Kimi: `moonshot/kimi-k2`
- Claude: `anthropic/claude-3.5-sonnet`, `anthropic/claude-opus-4.5`
- GPT: `openai/gpt-4o`, `openai/o1`

### Timeout anpassen

Bei sehr langen Texten kann der Timeout erhöht werden:

```json
{
    "timeout": 300
}
```

## 📊 Analyse-Funktion

Die Analyse von Claude Opus 4.5 zeigt:

- **Fachliche Bewertung**: Korrektheit, Präzision, Argumentation
- **Grammatik & Rechtschreibung**: Liste aller Fehler
- **Stilistische Anmerkungen**: Bewertung des akademischen Stils
- **Struktur & Kohärenz**: Logische Struktur und Fluss
- **Konkrete Verbesserungsvorschläge**: Detaillierte Empfehlungen

Diese Analyse wird dann von GPT-5.2 verwendet, um den Text präzise zu verbessern.

## 🐛 Troubleshooting

### "API-Key ungültig"
- Prüfe deinen API-Key in `config.json`
- Stelle sicher, dass Guthaben vorhanden ist
- Verifiziere Zugriff auf alle 3 Modelle

### "Zeitüberschreitung"
- Erhöhe `timeout` in `config.json`
- Text evtl. kürzen (< 2000 Wörter)
- Internetverbindung prüfen

### "Model nicht verfügbar"
- Prüfe ob Model-Namen korrekt sind
- Bei OpenRouter prüfen ob Modelle verfügbar sind
- Alternative Modelle in config.json eintragen

### GUI friert ein
- Normal bei API-Calls (synchron im MVP)
- Status-Updates zeigen Fortschritt
- Nicht schließen während Verarbeitung

## 🔨 Entwicklung

### Requirements

Siehe `requirements.txt`:
- PyQt6 (GUI)
- requests (API-Calls)
- python-dotenv (Environment)

### Projektstruktur

```
MultiAgent-Writer/
├── main.py              # GUI & Hauptlogik
├── api_service.py       # Multi-Agent API-Integration
├── text_processor.py    # Diff-Generierung
├── prompts.py           # Multi-Agent Prompts
├── config.json          # Konfiguration
└── requirements.txt     # Dependencies
```

### Testing

```bash
# API-Service testen
python api_service.py

# Text-Processor testen
python text_processor.py
```

## 📦 Windows Executable erstellen

```bash
pyinstaller --onefile --windowed --name ThesisImprover main.py
```

Die .exe findet sich in `dist/ThesisImprover.exe`

## 🎓 Beispiel-Workflows

### Ausformulieren

**Input:**
```
- KI wichtig für Medizin
- Diagnose-Unterstützung
- Ethische Fragen
```

**Prozess:**
1. Kimi K2 → vollständige Absätze
2. Opus 4.5 → Analyse der Formulierung
3. GPT-5.2 → finaler polierter Text

**Output:**
Akademisch formulierter, fehlerfreier Text mit korrekter Terminologie.

### Korrekturlesen

**Input:**
```
Die künstliche Inteligenz ist ein wichtiger Faktor für die zukunft der Medizin.
```

**Prozess:**
1. Opus 4.5 → Fehleranalyse (Rechtschreibung, Grammatik, Stil)
2. GPT-5.2 → Korrigierter Text

**Output:**
```
Die künstliche Intelligenz ist ein wichtiger Faktor für die Zukunft der Medizin.
```

## 📄 Lizenz

MIT License

## 🙏 Support

Bei Problemen oder Fragen:
- GitHub Issues erstellen
- README durchlesen
- config.json überprüfen

## 🔄 Versionshistorie

**Version 2.0** (Multi-Agent Edition)
- Multi-Agent-Workflows (Kimi K2, Opus 4.5, GPT-5.2)
- Analyse-Ansicht
- Verbessertes Error Handling
- Timeout erhöht (180s)

**Version 1.0** (MVP)
- Single-Agent-Workflows
- Basis-Funktionalität
- Diff-Ansicht
- Export-Funktion
