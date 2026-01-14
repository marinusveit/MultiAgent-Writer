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
    # Base colors
    ADDITION = "#c8e6c9"
    DELETION = "#ffcdd2"
    MODIFICATION = "#fff9c4"
    ACCEPTED_COLOR = "#2e7d32"
    REJECTED_COLOR = "#c62828"

    # Hover colors
    ADDITION_HOVER = "#a5d6a7"          # Darker green on hover
    DELETION_HOVER = "#ef9a9a"          # Darker red on hover
    ACCEPTED_HOVER = "#1b5e20"          # Darker green for accepted
    REJECTED_HOVER = "#b71c1c"          # Darker red for rejected

    # Border colors
    BORDER_PENDING = "rgba(0,0,0,0.2)"
    BORDER_ACCEPTED = "rgba(46,125,50,0.3)"
    BORDER_REJECTED = "rgba(198,40,40,0.3)"
    BORDER_HOVER_PENDING = "rgba(0,0,0,0.4)"
    BORDER_HOVER_ACCEPTED = "rgba(46,125,50,0.6)"
    BORDER_HOVER_REJECTED = "rgba(198,40,40,0.6)"


class DiffStyle:
    """Diff rendering styles"""
    CURSOR = "cursor: pointer;"
    TOOLTIP = "title='Klicken um zu akzeptieren/ablehnen'"
    PADDING = "2px 4px"
    MARGIN = "0 1px"
    LINE_HEIGHT = 1.8
    FONT_FAMILY = "Arial, sans-serif"

    # Visual styling for borders and transitions
    BORDER_RADIUS = "3px"
    BORDER_WIDTH = "1px"
    BORDER_WIDTH_HOVER = "2px"
    BOX_SHADOW_HOVER = "0 2px 4px rgba(0,0,0,0.15)"
    TRANSITION = "all 0.2s ease"
