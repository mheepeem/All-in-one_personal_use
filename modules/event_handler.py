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

    def __init__(self, interval=5):  # Check every 1 second
        super().__init__()
        self.interval = interval
        self._isRunning = True

    def run(self):
        while self._isRunning:
            status = self.check_internet_connection()
            self.status_changed.emit(status)
            time.sleep(self.interval)

    def stop(self):
        self._isRunning = False

    def check_internet_connection(self):
        """Checks internet connectivity with a short timeout."""
        try:
            response = requests.get("https://www.google.com", timeout=2)  # 1 second timeout
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException:
            return False