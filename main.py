"""
Thesis Improver - Hauptanwendung
KI-gestütztes Text-Tool für Masterarbeiten
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QComboBox, QLabel, QSplitter, QMessageBox,
    QFileDialog, QMenuBar, QMenu, QDialog, QLineEdit, QFormLayout, QDialogButtonBox,
    QTextBrowser, QProgressDialog, QPlainTextEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence

from api_service import APIService, APIError, NetworkError, RateLimitError, AuthenticationError
from text_processor import TextProcessor, InteractiveDiff, ChangeState


class APIWorker(QThread):
    """Background worker for API calls"""
    progress = pyqtSignal(str)  # Status message
    finished = pyqtSignal(dict)  # Result
    error = pyqtSignal(Exception)  # Error

    def __init__(self, api_service, mode, text, parent=None):
        super().__init__(parent)
        self.api_service = api_service
        self.mode = mode
        self.text = text

    def run(self):
        """Execute API call in background thread"""
        try:
            if self.mode == "ausformulieren":
                result = self.api_service.improve_text_ausformulieren(
                    self.text,
                    status_callback=lambda msg: self.progress.emit(msg)
                )
            else:  # korrekturlesen
                result = self.api_service.improve_text_korrekturlesen(
                    self.text,
                    status_callback=lambda msg: self.progress.emit(msg)
                )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(e)


class AnalysisDialog(QDialog):
    """Dialog zur Anzeige der Claude Opus 4.5 Analyse"""

    def __init__(self, analysis_text: str, parent=None):
        super().__init__(parent)
        self.init_ui(analysis_text)

    def init_ui(self, analysis_text):
        """Initialisiert den Analyse-Dialog"""
        self.setWindowTitle("Claude Opus 4.5 - Detaillierte Textanalyse")
        self.setMinimumSize(900, 700)

        layout = QVBoxLayout(self)

        # Überschrift
        header_label = QLabel("<h2>📊 Analyse von Claude Opus 4.5</h2>")
        header_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout.addWidget(header_label)

        # Analyse-Text anzeigen (mit Markdown-Rendering)
        text_view = QTextEdit()
        text_view.setReadOnly(True)
        text_view.setMarkdown(analysis_text)
        text_view.setStyleSheet(
            "font-family: 'Segoe UI', Arial, sans-serif; "
            "font-size: 10pt; "
            "padding: 15px; "
            "background-color: #ffffff; "
            "border: 1px solid #dee2e6; "
            "border-radius: 4px;"
        )

        layout.addWidget(text_view)

        # Info-Text
        info_label = QLabel(
            "<i>💡 Diese Analyse wurde von Claude Opus 4.5 erstellt und dient als Grundlage "
            "für die Textverbesserung durch GPT-5.2.</i>"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #6c757d; padding: 5px;")
        layout.addWidget(info_label)

        # Schließen-Button
        close_button = QPushButton("Schließen")
        close_button.clicked.connect(self.accept)
        close_button.setStyleSheet(
            "QPushButton { padding: 8px 20px; font-size: 11pt; }"
        )
        layout.addWidget(close_button)


class SettingsDialog(QDialog):
    """Dialog für API-Einstellungen"""

    def __init__(self, api_service, parent=None):
        super().__init__(parent)
        self.api_service = api_service
        self.init_ui()

    def init_ui(self):
        """Initialisiert die Dialog-UI"""
        self.setWindowTitle("API-Einstellungen")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # Formular
        form_layout = QFormLayout()

        # API-Key Eingabe
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setText(self.api_service.config.get('api_key', ''))
        self.api_key_input.setPlaceholderText("sk-or-v1-...")
        form_layout.addRow("API-Key:", self.api_key_input)

        # "API-Key anzeigen" Checkbox
        self.show_key_button = QPushButton("API-Key anzeigen")
        self.show_key_button.setCheckable(True)
        self.show_key_button.toggled.connect(self.toggle_key_visibility)
        form_layout.addRow("", self.show_key_button)

        # Model-Auswahl
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "anthropic/claude-3.5-sonnet",
            "anthropic/claude-opus-4.5",
            "google/gemini-2.0-flash-001",
            "openai/gpt-4o",
            "meta-llama/llama-3.1-70b-instruct"
        ])

        current_model = self.api_service.config.get('model', 'anthropic/claude-3.5-sonnet')
        index = self.model_combo.findText(current_model)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)

        form_layout.addRow("Model:", self.model_combo)

        # System-Prompt (Leitfaden)
        self.system_prompt_label = QLabel("Schreibregeln (System-Prompt):")
        self.system_prompt_edit = QTextEdit()
        self.system_prompt_edit.setPlainText(self.api_service.config.get('system_prompt', ''))
        self.system_prompt_edit.setToolTip("Leitfaden für die Texterstellung (z.B. technische Dokumentation)")
        self.system_prompt_edit.setMinimumHeight(150)
        form_layout.addRow(self.system_prompt_label, self.system_prompt_edit)

        # Thema der Arbeit
        self.topic_label = QLabel("Thema der Arbeit:")
        self.topic_edit = QLineEdit()
        self.topic_edit.setText(self.api_service.config.get('thesis_topic', ''))
        self.topic_edit.setToolTip("Kontext für bessere Textgenerierung")
        self.topic_edit.setPlaceholderText("z.B. 'Künstliche Intelligenz in der Medizin'")
        form_layout.addRow(self.topic_label, self.topic_edit)

        # Hinweise
        hint_label = QLabel(
            "<p><b>Hinweise:</b></p>"
            "<ul>"
            "<li>OpenRouter API-Key erhältlich auf <a href='https://openrouter.ai'>openrouter.ai</a></li>"
            "<li><b>claude-3.5-sonnet</b>: Empfohlen (gute Balance)</li>"
            "<li><b>claude-opus-4.5</b>: Höchste Qualität (teuer)</li>"
            "<li><b>gemini-2.0-flash</b>: Schnell und günstig</li>"
            "</ul>"
        )
        hint_label.setOpenExternalLinks(True)
        hint_label.setWordWrap(True)

        layout.addLayout(form_layout)
        layout.addWidget(hint_label)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

    def toggle_key_visibility(self, checked):
        """Schaltet die Sichtbarkeit des API-Keys um"""
        if checked:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_key_button.setText("API-Key verbergen")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_key_button.setText("API-Key anzeigen")

    def save_settings(self):
        """Speichert die Einstellungen"""
        api_key = self.api_key_input.text().strip()
        model = self.model_combo.currentText()

        if not api_key:
            QMessageBox.warning(
                self,
                "Ungültige Eingabe",
                "Bitte gib einen API-Key ein."
            )
            return

        try:
            # Neue Config zusammenstellen
            config = {
                'api_key': api_key,
                'model': model,
                'timeout': self.api_service.config.get('timeout', 180),
                'models': self.api_service.config.get('models', {}),
                'system_prompt': self.system_prompt_edit.toPlainText(),
                'thesis_topic': self.topic_edit.text().strip()
            }

            # Einstellungen speichern
            self.api_service.save_config(config)

            QMessageBox.information(
                self,
                "Erfolg",
                "Einstellungen wurden gespeichert."
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler",
                f"Fehler beim Speichern der Einstellungen:\n{str(e)}"
            )


class ThesisImproverWindow(QMainWindow):
    """Hauptfenster der Anwendung"""

    def __init__(self):
        super().__init__()

        self.api_service = APIService()
        self.text_processor = TextProcessor()

        self.original_text = ""
        self.improved_text = ""
        self.current_analysis = ""  # Speichert die Opus 4.5 Analyse
        self.interactive_diff = None  # Speichert InteractiveDiff-Instanz

        self.init_ui()

    def init_ui(self):
        """Initialisiert die Benutzeroberfläche"""

        self.setWindowTitle("Thesis Improver - Text-Verbesserung für Masterarbeiten")
        self.setGeometry(100, 100, 1200, 800)

        # Zentrales Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Haupt-Layout
        main_layout = QVBoxLayout(central_widget)

        # === Obere Kontrollen ===
        controls_layout = QHBoxLayout()

        # Modus-Auswahl
        mode_label = QLabel("Modus:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["ausformulieren", "korrekturlesen"])
        self.mode_combo.setToolTip(
            "Ausformulieren: Kimi K2 → Opus 4.5 (Analyse) → GPT-5.2 (Umsetzung)\n"
            "Korrekturlesen: Opus 4.5 (Analyse) → GPT-5.2 (Umsetzung)\n\n"
            "⚠️ Nutzt mehrere Modelle - höhere Kosten!"
        )
        # Signal: Button-Text aktualisieren, wenn Modus geändert wird
        self.mode_combo.currentTextChanged.connect(self.update_process_button_text)

        controls_layout.addWidget(mode_label)
        controls_layout.addWidget(self.mode_combo)
        controls_layout.addStretch()

        main_layout.addLayout(controls_layout)

        # === Text-Bereiche ===
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Linker Bereich: Original-Text
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        left_label = QLabel("Original-Text:")
        left_label.setStyleSheet("font-weight: bold;")

        # Use QPlainTextEdit for input (doesn't support rich text, ignores clipboard formatting)
        self.input_text = QPlainTextEdit()
        self.input_text.setPlaceholderText(
            "Gib hier deinen Text ein...\n\n"
            "Beispiel für 'Ausformulieren':\n"
            "- KI wichtig\n"
            "- Einsatz in Medizin\n"
            "- Ethische Fragen\n\n"
            "Beispiel für 'Korrekturlesen':\n"
            "Die künstliche Inteligenz ist ein wichtiger Faktor für die zukunft."
        )

        # Apply explicit styling (white bg, black text, resistant to clipboard/dark mode)
        self.input_text.setStyleSheet("""
            QPlainTextEdit {
                background-color: #FFFFFF;
                color: #000000;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11pt;
                selection-background-color: #0078D7;
                selection-color: #FFFFFF;
            }
        """)

        left_layout.addWidget(left_label)
        left_layout.addWidget(self.input_text)

        # Rechter Bereich: Verbesserter Text
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Header mit Label und View-Toggle
        right_header_layout = QHBoxLayout()

        right_label = QLabel("Verbesserter Text:")
        right_label.setStyleSheet("font-weight: bold;")

        # View-Toggle Button (rechts ausgerichtet)
        self.toggle_view_button = QPushButton("Text anzeigen")
        self.toggle_view_button.setToolTip("Zwischen Diff-Ansicht und reinem Text umschalten")
        self.toggle_view_button.clicked.connect(self.toggle_view)
        self.toggle_view_button.setEnabled(False)
        self.toggle_view_button.setMaximumWidth(150)  # Nicht zu breit
        self.show_diff = True  # Zeigt an, ob Diff angezeigt wird (initial = Diff aktiv)

        right_header_layout.addWidget(right_label)
        right_header_layout.addStretch()  # Platz zwischen Label und Button
        right_header_layout.addWidget(self.toggle_view_button)

        right_layout.addLayout(right_header_layout)

        self.output_text = QTextBrowser()  # Changed from QTextEdit to QTextBrowser
        self.output_text.setReadOnly(True)
        self.output_text.setOpenExternalLinks(False)  # Handle clicks internally
        self.output_text.anchorClicked.connect(self.handle_change_click)
        self.output_text.setPlaceholderText("Hier erscheint der verbesserte Text...")

        # Apply minimal styling (white bg, but allow HTML colors for diff)
        self.output_text.setStyleSheet("""
            QTextBrowser {
                background-color: #FFFFFF;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11pt;
                selection-background-color: #0078D7;
                selection-color: #FFFFFF;
            }
        """)

        right_layout.addWidget(self.output_text)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([600, 600])

        main_layout.addWidget(splitter)

        # === Untere Buttons ===
        button_layout = QHBoxLayout()

        # Initial Text basierend auf aktuellem Modus
        initial_mode = self.mode_combo.currentText()
        button_text = "Ausformulieren" if initial_mode == "ausformulieren" else "Korrektur lesen"
        self.process_button = QPushButton(button_text)
        self.process_button.setToolTip(f"{button_text} (Ctrl+Enter)")
        self.process_button.clicked.connect(self.process_text)
        self.process_button.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; "
            "padding: 10px; font-size: 14px; font-weight: bold; }"
            "QPushButton:hover { background-color: #45a049; }"
        )

        self.copy_button = QPushButton("Kopieren")
        self.copy_button.setToolTip("Text in Zwischenablage kopieren (Ctrl+K)")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.copy_button.setEnabled(False)

        self.accept_button = QPushButton("← Übernehmen")
        self.accept_button.setToolTip("Verbesserten Text ins Eingabefeld übernehmen")
        self.accept_button.clicked.connect(self.accept_changes)
        self.accept_button.setEnabled(False)

        self.export_button = QPushButton("Speichern")
        self.export_button.setToolTip("Text als Datei speichern")
        self.export_button.clicked.connect(self.export_text)
        self.export_button.setEnabled(False)

        self.reset_button = QPushButton("Zurücksetzen")
        self.reset_button.setToolTip("Output-Feld leeren")
        self.reset_button.clicked.connect(self.reset_output)
        self.reset_button.setEnabled(False)

        self.show_analysis_button = QPushButton("📊 Analyse anzeigen")
        self.show_analysis_button.setToolTip("Zeigt die detaillierte Analyse von Claude Opus 4.5")
        self.show_analysis_button.clicked.connect(self.show_analysis_dialog)
        self.show_analysis_button.setEnabled(False)

        self.accept_all_button = QPushButton("✓ Alle akzeptieren")
        self.accept_all_button.setToolTip("Alle Änderungen akzeptieren")
        self.accept_all_button.clicked.connect(self.accept_all_changes)
        self.accept_all_button.setEnabled(False)

        self.reject_all_button = QPushButton("✗ Alle ablehnen")
        self.reject_all_button.setToolTip("Alle Änderungen ablehnen (Original beibehalten)")
        self.reject_all_button.clicked.connect(self.reject_all_changes)
        self.reject_all_button.setEnabled(False)

        button_layout.addWidget(self.process_button)
        button_layout.addWidget(self.show_analysis_button)
        button_layout.addWidget(self.accept_all_button)
        button_layout.addWidget(self.reject_all_button)
        button_layout.addWidget(self.accept_button)
        button_layout.addWidget(self.copy_button)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.reset_button)

        main_layout.addLayout(button_layout)

        # === Status-Leiste ===
        self.status_label = QLabel("Bereit")
        self.status_label.setStyleSheet("padding: 5px;")
        main_layout.addWidget(self.status_label)

        # === Menü-Leiste ===
        self.create_menu()

        # === Tastatur-Shortcuts ===
        self.create_shortcuts()

    def create_menu(self):
        """Erstellt die Menü-Leiste"""
        menubar = self.menuBar()

        # Datei-Menü
        file_menu = menubar.addMenu("Datei")

        export_action = QAction("Speichern...", self)
        export_action.setShortcut(QKeySequence("Ctrl+S"))
        export_action.triggered.connect(self.export_text)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("Beenden", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Einstellungen-Menü
        settings_menu = menubar.addMenu("Einstellungen")

        config_action = QAction("API-Konfiguration...", self)
        config_action.triggered.connect(self.show_settings)
        settings_menu.addAction(config_action)

        # Hilfe-Menü
        help_menu = menubar.addMenu("Hilfe")

        about_action = QAction("Über", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_shortcuts(self):
        """Erstellt Tastatur-Shortcuts"""
        # Ctrl+Enter: Verarbeiten
        process_shortcut = QKeySequence("Ctrl+Return")
        process_action = QAction(self)
        process_action.setShortcut(process_shortcut)
        process_action.triggered.connect(self.process_text)
        self.addAction(process_action)

        # Ctrl+K: In Zwischenablage kopieren
        copy_shortcut = QKeySequence("Ctrl+K")
        copy_action = QAction(self)
        copy_action.setShortcut(copy_shortcut)
        copy_action.triggered.connect(self.copy_to_clipboard)
        self.addAction(copy_action)

    def update_status(self, message):
        """Aktualisiert den Status-Text"""
        self.status_label.setText(message)
        QApplication.processEvents()

    def update_process_button_text(self, mode):
        """Aktualisiert den Text des Verarbeiten-Buttons basierend auf dem Modus"""
        button_text = "Ausformulieren" if mode == "ausformulieren" else "Korrektur lesen"
        self.process_button.setText(button_text)
        self.process_button.setToolTip(f"{button_text} (Ctrl+Enter)")

    def process_text(self):
        """Verarbeitet den Text mit Multi-Agent-Workflow"""
        # Input holen
        input_text = self.input_text.toPlainText().strip()

        if not input_text:
            QMessageBox.warning(
                self,
                "Leerer Text",
                "Bitte gib einen Text ein, der verarbeitet werden soll."
            )
            return

        # UI während Verarbeitung deaktivieren
        self.process_button.setEnabled(False)
        mode = self.mode_combo.currentText()

        # Create progress dialog
        self.progress_dialog = QProgressDialog(
            "Verarbeite Text...",
            "Abbrechen",
            0, 0,  # Indeterminate (no specific range)
            self
        )
        self.progress_dialog.setWindowTitle("Bitte warten")
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setMinimumDuration(0)  # Show immediately
        self.progress_dialog.setAutoClose(True)
        self.progress_dialog.setCancelButton(None)  # Disable cancel for now (API calls can't be canceled mid-flight)

        # Create worker thread
        self.worker = APIWorker(self.api_service, mode, input_text, self)

        # Connect signals
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_api_success)
        self.worker.error.connect(self.on_api_error)

        # Start processing
        self.status_label.setText("⏳ Starte Multi-Agent-Prozess...")
        self.worker.start()

    def update_progress(self, message):
        """Update progress dialog label"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.setLabelText(message)
        self.status_label.setText(message)
        QApplication.processEvents()

    def on_api_success(self, result):
        """Handle successful API response"""
        # Close progress dialog
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.close()

        mode = self.mode_combo.currentText()

        # Extract analysis and final text based on mode
        if mode == "ausformulieren":
            self.current_analysis = result['step2_analysis']
            self.improved_text = result['step3_final']
        else:  # korrekturlesen
            self.current_analysis = result['step1_analysis']
            self.improved_text = result['step2_final']

        # Original-Text speichern
        self.original_text = self.input_text.toPlainText().strip()

        # Create interactive diff and display
        self.interactive_diff = InteractiveDiff(self.original_text, self.improved_text)
        html_diff = self.interactive_diff.generate_interactive_html()
        self.output_text.setHtml(html_diff)

        # Buttons aktivieren
        self.show_analysis_button.setEnabled(True)
        self.copy_button.setEnabled(True)
        self.accept_button.setEnabled(True)
        self.export_button.setEnabled(True)
        self.reset_button.setEnabled(True)
        self.toggle_view_button.setEnabled(True)
        self.accept_all_button.setEnabled(True)
        self.reject_all_button.setEnabled(True)
        self.show_diff = True
        self.toggle_view_button.setText("Nur Text anzeigen")

        # Update status with statistics
        self.update_diff_statistics()

        # Re-enable process button
        self.process_button.setEnabled(True)

    def on_api_error(self, exception):
        """Handle API error"""
        # Close progress dialog
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.close()

        # Re-enable process button
        self.process_button.setEnabled(True)

        # Show appropriate error message
        if isinstance(exception, AuthenticationError):
            QMessageBox.critical(
                self,
                "Authentifizierungs-Fehler",
                f"{str(exception)}\n\nBitte gehe zu Einstellungen und trage einen gültigen API-Key ein."
            )
            self.status_label.setText("✗ Fehler: Ungültiger API-Key")

        elif isinstance(exception, NetworkError):
            QMessageBox.critical(
                self,
                "Netzwerk-Fehler",
                f"{str(exception)}\n\nBitte prüfe deine Internetverbindung."
            )
            self.status_label.setText("✗ Fehler: Keine Verbindung")

        elif isinstance(exception, RateLimitError):
            QMessageBox.warning(
                self,
                "Rate Limit",
                f"{str(exception)}\n\nBitte warte einen Moment und versuche es erneut."
            )
            self.status_label.setText("✗ Zu viele Anfragen")

        elif isinstance(exception, APIError):
            QMessageBox.critical(
                self,
                "API-Fehler",
                f"Ein Fehler ist aufgetreten:\n{str(exception)}"
            )
            self.status_label.setText("✗ API-Fehler")

        else:
            QMessageBox.critical(
                self,
                "Unbekannter Fehler",
                f"Ein unerwarteter Fehler ist aufgetreten:\n{str(exception)}"
            )
            self.status_label.setText("✗ Unbekannter Fehler")

    def copy_to_clipboard(self):
        """Kopiert den verbesserten Text in die Zwischenablage"""
        if not self.improved_text:
            return

        # Use final text from interactive diff (respects user's accept/reject choices)
        final_text = self.interactive_diff.get_final_text() if self.interactive_diff else self.improved_text
        clipboard = QApplication.clipboard()
        clipboard.setText(final_text)

        self.status_label.setText("✓ In Zwischenablage kopiert")

    def accept_changes(self):
        """Übernimmt den verbesserten Text in das Original-Feld"""
        if not self.improved_text:
            return

        # Use final text from interactive diff (respects user's accept/reject choices)
        final_text = self.interactive_diff.get_final_text() if self.interactive_diff else self.improved_text
        self.input_text.setPlainText(final_text)
        self.status_label.setText("✓ Änderungen übernommen")

    def toggle_view(self):
        """Schaltet zwischen Diff-Ansicht und reinem Text um"""
        if not self.original_text or not self.improved_text:
            return

        if self.show_diff:
            # Zeige nur den reinen Text (mit aktuellen Auswahlen)
            final_text = self.interactive_diff.get_final_text() if self.interactive_diff else self.improved_text
            self.output_text.setPlainText(final_text)
            self.toggle_view_button.setText("Unterschiede anzeigen")
            self.show_diff = False
        else:
            # Zeige Diff-Ansicht
            if self.interactive_diff:
                html_diff = self.interactive_diff.generate_interactive_html()
            else:
                # Fallback to creating interactive diff
                self.interactive_diff = InteractiveDiff(self.original_text, self.improved_text)
                html_diff = self.interactive_diff.generate_interactive_html()

            self.output_text.setHtml(html_diff)
            self.toggle_view_button.setText("Text anzeigen")
            self.show_diff = True

    def export_text(self):
        """Exportiert den verbesserten Text als .txt Datei"""
        if not self.improved_text:
            QMessageBox.warning(
                self,
                "Kein Text",
                "Es gibt keinen Text zum Exportieren."
            )
            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Text speichern",
            "verbesserter_text.txt",
            "Text-Dateien (*.txt);;Alle Dateien (*)"
        )

        if filename:
            try:
                # Use final text from interactive diff (respects user's accept/reject choices)
                final_text = self.interactive_diff.get_final_text() if self.interactive_diff else self.improved_text
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(final_text)

                self.status_label.setText(f"✓ Gespeichert: {filename}")
                QMessageBox.information(
                    self,
                    "Erfolg",
                    f"Text wurde gespeichert:\n{filename}"
                )

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Fehler beim Speichern",
                    f"Datei konnte nicht gespeichert werden:\n{str(e)}"
                )

    def reset_output(self):
        """Setzt den Output zurück"""
        self.output_text.clear()
        self.improved_text = ""
        self.original_text = ""
        self.current_analysis = ""
        self.interactive_diff = None
        self.copy_button.setEnabled(False)
        self.accept_button.setEnabled(False)
        self.export_button.setEnabled(False)
        self.reset_button.setEnabled(False)
        self.toggle_view_button.setEnabled(False)
        self.show_analysis_button.setEnabled(False)
        self.accept_all_button.setEnabled(False)
        self.reject_all_button.setEnabled(False)
        self.show_diff = True
        self.status_label.setText("Bereit")

    def handle_change_click(self, url):
        """Handle clicks on diff changes"""
        if not self.interactive_diff:
            return

        change_id = url.toString().lstrip('#')

        # Toggle the change state
        self.interactive_diff.toggle_change(change_id)

        # Re-render the diff
        html = self.interactive_diff.generate_interactive_html()
        self.output_text.setHtml(html)

        # Update the stored improved_text
        self.improved_text = self.interactive_diff.get_final_text()

        # Update status with statistics
        self.update_diff_statistics()

    def update_diff_statistics(self):
        """Update status bar with current diff statistics"""
        if not self.interactive_diff:
            return

        total_changes = sum(1 for c in self.interactive_diff.changes if c.operation != 'equal')
        accepted = sum(1 for c in self.interactive_diff.changes
                      if c.operation != 'equal' and c.state == ChangeState.ACCEPTED)
        rejected = sum(1 for c in self.interactive_diff.changes
                      if c.operation != 'equal' and c.state == ChangeState.REJECTED)
        pending = total_changes - accepted - rejected

        self.status_label.setText(
            f"Änderungen: {total_changes} gesamt | "
            f"{accepted} akzeptiert | {rejected} abgelehnt | {pending} ausstehend"
        )

    def accept_all_changes(self):
        """Accept all pending changes"""
        if not self.interactive_diff:
            return

        for change in self.interactive_diff.changes:
            if change.operation != 'equal':
                change.state = ChangeState.ACCEPTED

        html = self.interactive_diff.generate_interactive_html()
        self.output_text.setHtml(html)
        self.improved_text = self.interactive_diff.get_final_text()
        self.update_diff_statistics()

    def reject_all_changes(self):
        """Reject all pending changes"""
        if not self.interactive_diff:
            return

        for change in self.interactive_diff.changes:
            if change.operation != 'equal':
                change.state = ChangeState.REJECTED

        html = self.interactive_diff.generate_interactive_html()
        self.output_text.setHtml(html)
        self.improved_text = self.interactive_diff.get_final_text()
        self.update_diff_statistics()

    def show_analysis_dialog(self):
        """Zeigt die detaillierte Analyse von Claude Opus 4.5"""
        if not self.current_analysis:
            QMessageBox.information(
                self,
                "Keine Analyse verfügbar",
                "Es wurde noch keine Analyse durchgeführt.\n\n"
                "Bitte verarbeite zuerst einen Text."
            )
            return

        dialog = AnalysisDialog(self.current_analysis, self)
        dialog.exec()

    def show_settings(self):
        """Zeigt den Einstellungs-Dialog"""
        dialog = SettingsDialog(self.api_service, self)
        dialog.exec()

    def show_about(self):
        """Zeigt den Über-Dialog"""
        QMessageBox.about(
            self,
            "Über Thesis Improver",
            "<h2>Thesis Improver</h2>"
            "<p>Version 2.0 - Multi-Agent Edition</p>"
            "<p>KI-gestütztes Text-Tool für Masterarbeiten</p>"
            "<p><b>Multi-Agent-Workflows:</b></p>"
            "<ul>"
            "<li><b>Ausformulieren:</b> Kimi K2 → Opus 4.5 → GPT-5.2</li>"
            "<li><b>Korrekturlesen:</b> Opus 4.5 → GPT-5.2</li>"
            "</ul>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Diff-Ansicht mit farblichen Markierungen</li>"
            "<li>Detaillierte Analyse von Claude Opus 4.5</li>"
            "<li>Export-Funktion</li>"
            "</ul>"
            "<p><b>Powered by:</b> OpenRouter API</p>"
            "<p><b>Framework:</b> PyQt6</p>"
        )


def main():
    """Hauptfunktion"""
    app = QApplication(sys.argv)
    app.setApplicationName("Thesis Improver")

    window = ThesisImproverWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
