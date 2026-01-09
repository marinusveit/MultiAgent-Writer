"""
Background worker threads for API calls
"""

from PyQt6.QtCore import QThread, pyqtSignal


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
