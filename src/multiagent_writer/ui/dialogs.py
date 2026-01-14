"""
Dialog windows for settings and analysis display
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton,
    QLineEdit, QFormLayout, QDialogButtonBox, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt


class AnalysisDialog(QDialog):
    """Dialog zur Anzeige der Analyse"""

    def __init__(self, analysis_text: str, model_name: str = "Claude Opus 4.5", parent=None):
        super().__init__(parent)
        self.model_name = model_name
        self.init_ui(analysis_text)

    def init_ui(self, analysis_text):
        """Initialisiert den Analyse-Dialog"""
        self.setWindowTitle(f"{self.model_name} - Detaillierte Textanalyse")
        self.setMinimumSize(900, 700)

        layout = QVBoxLayout(self)

        # Überschrift
        header_label = QLabel(f"<h2>📊 Analyse von {self.model_name}</h2>")
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
            f"<i>💡 Diese Analyse wurde von {self.model_name} erstellt und dient als Grundlage "
            "für die Textverbesserung.</i>"
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
