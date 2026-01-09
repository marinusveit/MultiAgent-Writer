"""
Entry point for MultiAgent-Writer application
"""

import sys
from PyQt6.QtWidgets import QApplication

from .ui.main_window import ThesisImproverWindow


def main():
    """Main entry point for the application"""
    app = QApplication(sys.argv)
    app.setApplicationName("MultiAgent-Writer")

    window = ThesisImproverWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
