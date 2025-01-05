from PySide6.QtWidgets import QMessageBox
import time
from PySide6.QtCore import  QThread, Signal
import requests

def show_error_message(parent, title, message):
    QMessageBox.critical(parent, title, message, QMessageBox.Ok)

def show_success_message(parent, title, message):
    QMessageBox.information(parent, title, message, QMessageBox.Ok)

class InternetChecker(QThread):
    """
    A thread to check internet connectivity periodically.
    """
    status_changed = Signal(bool)

    def __init__(self, interval=10):  # Check every 10 seconds
        super().__init__()
        self.interval = interval
        self._isRunning = True
        self._last_status = None  # Track the last known status

    def run(self):
        while self._isRunning:
            current_status = self.check_internet_connection()
            if current_status != self._last_status:  # Log and emit only on status change
                self.status_changed.emit(current_status)
                self._last_status = current_status
            time.sleep(self.interval)

    def stop(self):
        self._isRunning = False

    def check_internet_connection(self):
        """Check internet connectivity with a short timeout."""
        try:
            response = requests.get("https://www.google.com", timeout=2)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException:
            return False