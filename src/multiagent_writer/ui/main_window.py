"""
Main application window for MultiAgent-Writer
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QComboBox, QLabel, QSplitter, QMessageBox,
    QFileDialog, QMenuBar, QMenu, QDialog, QLineEdit, QFormLayout, QDialogButtonBox,
    QTextBrowser, QProgressDialog, QPlainTextEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QAction, QKeySequence

# Import from new structure
from ..compat_api_service import APIService
from ..api.errors import APIError, NetworkError, RateLimitError, AuthenticationError
from ..api.service import TextImprovementService
from ..core.text_processor import TextProcessor, InteractiveDiff, ChangeState

# Import UI components from new structure
from .workers import APIWorker
from .dialogs import AnalysisDialog, SettingsDialog
from .button_manager import OutputButtonManager


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

        # Set initial quality selection from config
        quality = self.api_service.config.get('model_quality', 'guenstig')
        index = self.quality_combo.findData(quality)
        if index >= 0:
            self.quality_combo.setCurrentIndex(index)

        # Update mode tooltip with current model names
        self._update_mode_tooltip()

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
        # Tooltip will be set dynamically after config is loaded
        # Signal: Button-Text aktualisieren, wenn Modus geändert wird
        self.mode_combo.currentTextChanged.connect(self.update_process_button_text)

        # Model quality selection
        quality_label = QLabel("Modell-Qualität:")
        self.quality_combo = QComboBox()
        self.quality_combo.addItem("Günstig", "guenstig")
        self.quality_combo.addItem("High-End", "high_end")
        self.quality_combo.setToolTip(
            "Günstig: Schneller und kostengünstiger (GPT-OSS-120B)\n"
            "High-End: Bessere Qualität, höhere Kosten (Claude Opus 4.5, GPT-5.2)"
        )
        self.quality_combo.currentIndexChanged.connect(self.on_quality_changed)

        controls_layout.addWidget(mode_label)
        controls_layout.addWidget(self.mode_combo)
        controls_layout.addWidget(quality_label)
        controls_layout.addWidget(self.quality_combo)
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
        # Tooltip will be set dynamically after config is loaded
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

        # Initialize button manager for output controls
        self.button_manager = OutputButtonManager([
            self.copy_button,
            self.accept_button,
            self.export_button,
            self.reset_button,
            self.toggle_view_button,
            self.show_analysis_button,
            self.accept_all_button,
            self.reject_all_button
        ])

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

    # === Helper Methods ===

    def _close_progress_dialog(self):
        """Closes progress dialog if it exists"""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None

    def _get_model_display_name(self, model_key: str) -> str:
        """Get user-friendly display name for model"""
        from ..config.constants import ModelQuality
        model_id = self.api_service.config['models'].get(model_key, '')
        return ModelQuality.MODEL_DISPLAY_NAMES.get(model_id, model_id)

    def _update_mode_tooltip(self):
        """Update mode combo tooltip with current model names"""
        kimi = self._get_model_display_name('kimi_k2')
        opus = self._get_model_display_name('claude_opus')
        gpt = self._get_model_display_name('gpt_52')

        self.mode_combo.setToolTip(
            f"Ausformulieren: {kimi} → {opus} (Analyse) → {gpt} (Umsetzung)\n"
            f"Korrekturlesen: {opus} (Analyse) → {gpt} (Umsetzung)\n\n"
            "⚠️ Nutzt mehrere Modelle - höhere Kosten!"
        )

        # Also update analysis button tooltip
        self.show_analysis_button.setToolTip(
            f"Zeigt die detaillierte Analyse von {opus}"
        )

    def _get_final_text(self) -> str:
        """Gets final text respecting user's accept/reject choices"""
        if self.interactive_diff:
            return self.interactive_diff.get_final_text()
        return self.improved_text

    def _show_error_dialog(self, exception: Exception):
        """Unified error handling"""
        # Error message mappings
        ERROR_MESSAGES = {
            AuthenticationError: (
                "Authentifizierungs-Fehler",
                "{}\n\nBitte gehe zu Einstellungen und trage einen gültigen API-Key ein.",
                "✗ Fehler: Ungültiger API-Key"
            ),
            NetworkError: (
                "Netzwerk-Fehler",
                "{}\n\nBitte prüfe deine Internetverbindung.",
                "✗ Fehler: Keine Verbindung"
            ),
            RateLimitError: (
                "Rate Limit",
                "{}\n\nBitte warte einen Moment und versuche es erneut.",
                "✗ Zu viele Anfragen"
            ),
            APIError: (
                "API-Fehler",
                "Ein Fehler ist aufgetreten:\n{}",
                "✗ API-Fehler"
            )
        }

        error_type = type(exception)

        if error_type in ERROR_MESSAGES:
            title, message_template, status = ERROR_MESSAGES[error_type]
            QMessageBox.critical(self, title, message_template.format(str(exception)))
            self.status_label.setText(status)
        else:
            # Unknown error
            QMessageBox.critical(
                self,
                "Unbekannter Fehler",
                f"Ein unerwarteter Fehler ist aufgetreten:\n{str(exception)}"
            )
            self.status_label.setText("✗ Unbekannter Fehler")

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

    def on_quality_changed(self, index):
        """Handle model quality selection change"""
        from ..config.constants import ModelQuality

        quality = self.quality_combo.currentData()

        # Update config
        self.api_service.config['model_quality'] = quality
        self.api_service.config_manager.save(self.api_service.config)

        # Reload config to apply new models
        self.api_service.config = self.api_service.config_manager.load()

        # Reinitialize service with new config
        self.api_service.service = TextImprovementService(self.api_service.config)

        # Update mode tooltip with new model names
        self._update_mode_tooltip()

        # Update status
        quality_name = ModelQuality.DISPLAY_NAMES.get(quality, quality)
        self.update_status(f"Modell-Qualität: {quality_name}")

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

        # Check if worker is already running
        if hasattr(self, 'worker') and self.worker.isRunning():
            QMessageBox.warning(
                self,
                "Verarbeitung läuft",
                "Bitte warte, bis die aktuelle Verarbeitung abgeschlossen ist."
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
        self._close_progress_dialog()

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

        # Enable all output buttons
        self.button_manager.enable_all()
        self.show_diff = True
        self.toggle_view_button.setText("Nur Text anzeigen")

        # Update status with statistics
        self.update_diff_statistics()

        # Re-enable process button
        self.process_button.setEnabled(True)

    def on_api_error(self, exception):
        """Handle API error"""
        # Close progress dialog
        self._close_progress_dialog()

        # Re-enable process button
        self.process_button.setEnabled(True)

        # Show error dialog with unified error handling
        self._show_error_dialog(exception)

    def copy_to_clipboard(self):
        """Kopiert den verbesserten Text in die Zwischenablage"""
        if not self.improved_text:
            return

        # Use final text from interactive diff (respects user's accept/reject choices)
        final_text = self._get_final_text()
        clipboard = QApplication.clipboard()
        clipboard.setText(final_text)

        self.status_label.setText("✓ In Zwischenablage kopiert")

    def accept_changes(self):
        """Übernimmt den verbesserten Text in das Original-Feld"""
        if not self.improved_text:
            return

        # Use final text from interactive diff (respects user's accept/reject choices)
        final_text = self._get_final_text()
        self.input_text.setPlainText(final_text)
        self.status_label.setText("✓ Änderungen übernommen")

    def toggle_view(self):
        """Schaltet zwischen Diff-Ansicht und reinem Text um"""
        if not self.original_text or not self.improved_text:
            return

        if self.show_diff:
            # Zeige nur den reinen Text (mit aktuellen Auswahlen)
            final_text = self._get_final_text()
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
                final_text = self._get_final_text()
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
        # Disable all output buttons
        self.button_manager.disable_all()
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
        """Zeigt die detaillierte Analyse"""
        if not self.current_analysis:
            QMessageBox.information(
                self,
                "Keine Analyse verfügbar",
                "Es wurde noch keine Analyse durchgeführt.\n\n"
                "Bitte verarbeite zuerst einen Text."
            )
            return

        opus_name = self._get_model_display_name('claude_opus')
        dialog = AnalysisDialog(self.current_analysis, opus_name, self)
        dialog.exec()

    def show_settings(self):
        """Zeigt den Einstellungs-Dialog"""
        dialog = SettingsDialog(self.api_service, self)
        dialog.exec()

    def show_about(self):
        """Zeigt den Über-Dialog"""
        # Get dynamic model names
        kimi = self._get_model_display_name('kimi_k2')
        opus = self._get_model_display_name('claude_opus')
        gpt = self._get_model_display_name('gpt_52')

        QMessageBox.about(
            self,
            "Über Thesis Improver",
            "<h2>Thesis Improver</h2>"
            "<p>Version 2.0 - Multi-Agent Edition</p>"
            "<p>KI-gestütztes Text-Tool für Masterarbeiten</p>"
            "<p><b>Multi-Agent-Workflows:</b></p>"
            "<ul>"
            f"<li><b>Ausformulieren:</b> {kimi} → {opus} → {gpt}</li>"
            f"<li><b>Korrekturlesen:</b> {opus} → {gpt}</li>"
            "</ul>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Diff-Ansicht mit farblichen Markierungen</li>"
            f"<li>Detaillierte Analyse von {opus}</li>"
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
