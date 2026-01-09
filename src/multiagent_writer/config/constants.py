"""
UI constants, colors, and styling
"""

from typing import Dict


class UIConstants:
    """UI layout and styling constants"""

    # Window geometry
    MAIN_WINDOW_WIDTH = 1200
    MAIN_WINDOW_HEIGHT = 800
    MAIN_WINDOW_X = 100
    MAIN_WINDOW_Y = 100

    # Dialog sizes
    SETTINGS_DIALOG_MIN_WIDTH = 500
    ANALYSIS_DIALOG_MIN_WIDTH = 900
    ANALYSIS_DIALOG_MIN_HEIGHT = 700

    # Splitter ratios
    SPLITTER_LEFT_SIZE = 600
    SPLITTER_RIGHT_SIZE = 600

    # Text field styling
    TEXT_FIELD_STYLE = """
        QPlainTextEdit, QTextBrowser {
            background-color: #FFFFFF;
            color: #000000;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 11pt;
            selection-background-color: #0078D7;
            selection-color: #FFFFFF;
        }
    """

    # Button styling
    PROCESS_BUTTON_STYLE = """
        QPushButton {
            background-color: #4CAF50;
            color: white;
            padding: 10px;
            font-size: 14px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
    """

    # Mode labels
    MODE_LABELS = {
        "ausformulieren": "Ausformulieren",
        "korrekturlesen": "Korrektur lesen"
    }


class DiffColors:
    """Diff styling colors"""
    ADDITION = "#c8e6c9"
    DELETION = "#ffcdd2"
    MODIFICATION = "#fff9c4"
    ACCEPTED_COLOR = "#2e7d32"
    REJECTED_COLOR = "#c62828"


class DiffStyle:
    """Diff rendering styles"""
    CURSOR = "cursor: pointer;"
    TOOLTIP = "title='Klicken um zu akzeptieren/ablehnen'"
    PADDING = "2px 4px;"
    LINE_HEIGHT = 1.8
    FONT_FAMILY = "Arial, sans-serif"
