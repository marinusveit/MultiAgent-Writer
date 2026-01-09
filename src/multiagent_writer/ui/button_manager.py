"""
Button state management for output controls
"""

from typing import List
from PyQt6.QtWidgets import QPushButton


class OutputButtonManager:
    """Manages all output-related button states"""

    def __init__(self, buttons: List[QPushButton]):
        """
        Initialize button manager.

        Args:
            buttons: List of buttons to manage
        """
        self.buttons = buttons

    def enable_all(self):
        """Enable all managed buttons"""
        for button in self.buttons:
            button.setEnabled(True)

    def disable_all(self):
        """Disable all managed buttons"""
        for button in self.buttons:
            button.setEnabled(False)
