# Build-Anleitung für Thesis Improver

Diese Anleitung zeigt, wie du eine eigenständige Windows .exe Datei erstellst.

## Voraussetzungen

- Python 3.10 oder höher installiert
- Alle Dependencies installiert (siehe README.md)

## Windows Executable erstellen

### Option 1: Mit PyInstaller Spec-Datei (Empfohlen)

```bash
# Virtual Environment aktivieren
venv\Scripts\activate  # Windows
# oder
source venv/bin/activate  # Linux/Mac

# Mit Spec-Datei builden
pyinstaller build_windows.spec
```

Die fertige .exe befindet sich in `dist/ThesisImprover.exe`

### Option 2: Direkter PyInstaller-Befehl

```bash
pyinstaller --onefile --windowed --name ThesisImprover --add-data "config.json;." --add-data "prompts.py;." main.py
```

## Ausgabe

Nach erfolgreichem Build findest du:
- `dist/ThesisImprover.exe` - Die eigenständige Anwendung
- `build/` - Temporäre Build-Dateien (kann gelöscht werden)

## Die .exe verwenden

Die `ThesisImprover.exe` ist eine eigenständige Anwendung:

1. **Kopiere** die .exe auf einen beliebigen Windows-Rechner
2. **Doppelklick** auf die .exe
3. Beim ersten Start öffne die Einstellungen (Menü: Einstellungen → API-Konfiguration)
4. Trage deinen OpenRouter API-Key ein
5. Fertig!

## Wichtige Hinweise

### config.json

Die `config.json` wird beim ersten Start automatisch erstellt im gleichen Verzeichnis wie die .exe.

### Größe der .exe

Die .exe ist ca. 80-100 MB groß, da sie Python und alle Dependencies enthält. Das ist normal für PyInstaller-Anwendungen.

### Antivirus-Warnungen

Manche Antivirus-Programme warnen bei selbst-erstellten .exe Dateien. Das ist ein False Positive. Gründe:

- Die .exe ist nicht digital signiert (kostet Geld)
- PyInstaller-Executables werden manchmal als verdächtig eingestuft

**Lösung:** Die .exe als Ausnahme in deinem Antivirus-Programm hinzufügen.

### Digital Signieren (Optional, für Professionelle Verwendung)

Um Antivirus-Warnungen zu vermeiden, kannst du die .exe digital signieren:

1. Code-Signing-Zertifikat kaufen (z.B. von DigiCert, ca. 200€/Jahr)
2. Mit `signtool` (Windows SDK) signieren

Für persönliche/interne Verwendung nicht notwendig.

## Problembehebung

### "PyInstaller nicht gefunden"

```bash
pip install pyinstaller
```

### Build schlägt fehl

1. Stelle sicher, dass alle Dependencies installiert sind:
   ```bash
   pip install -r requirements.txt
   ```

2. Lösche `build/` und `dist/` Ordner und versuche es erneut:
   ```bash
   rmdir /s /q build dist  # Windows
   rm -rf build dist       # Linux/Mac
   ```

### .exe startet nicht

1. Teste, ob das Python-Script funktioniert:
   ```bash
   python main.py
   ```

2. Wenn das Script funktioniert, aber die .exe nicht, builded mit Debug-Modus:
   ```bash
   pyinstaller --onefile --windowed --debug all --name ThesisImprover main.py
   ```

3. Starte die .exe über die Kommandozeile, um Fehlermeldungen zu sehen:
   ```bash
   dist\ThesisImprover.exe
   ```

## Alternativen zu PyInstaller

Falls PyInstaller Probleme macht:

### cx_Freeze

```bash
pip install cx_Freeze
cxfreeze main.py --target-dir dist --target-name ThesisImprover.exe
```

### Nuitka

```bash
pip install nuitka
python -m nuitka --onefile --windows-disable-console --enable-plugin=pyqt6 main.py
```

Nuitka ist langsamer beim Builden, aber erstellt schnellere und kleinere Executables.

## Distribution

Zum Verteilen der Anwendung:

1. Erstelle einen Ordner mit:
   - `ThesisImprover.exe`
   - `README.md` (Nutzungsanleitung)

2. Erstelle eine ZIP-Datei

3. Teile die ZIP-Datei mit deiner Freundin

**Wichtig:** Der API-Key muss von jedem Nutzer selbst in den Einstellungen eingetragen werden!
