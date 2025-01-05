from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from PySide6.QtCore import QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
from config.logging_config import get_logger

logger = get_logger(__name__)

class Google(QWidget):
    icon_path = ":/images/icons/google.png"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Google")

        self.web_view = QWebEngineView()
        self.web_view.setPage(WebEnginePageWithHistory(self))
        self.web_view.load(QUrl('https://www.google.com/'))

        # Back and forward buttons
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.navigate_back)

        forward_button = QPushButton("Forward")
        forward_button.clicked.connect(self.navigate_forward)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(back_button)
        button_layout.addWidget(forward_button)

        # Main layout
        layout = QVBoxLayout(self)
        layout.addLayout(button_layout)
        layout.addWidget(self.web_view)
        self.setLayout(layout)

    def navigate_back(self):
        """Handle back navigation and log the event."""
        if self.web_view.history().canGoBack():
            self.web_view.back()
            logger.info("Navigated back in web view history.")
        else:
            logger.warning("Back navigation requested but no previous page available.")

    def navigate_forward(self):
        """Handle forward navigation and log the event."""
        if self.web_view.history().canGoForward():
            self.web_view.forward()
            logger.info("Navigated forward in web view history.")
        else:
            logger.warning("Forward navigation requested but no next page available.")

class WebEnginePageWithHistory(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)

    def canGoBack(self):
        """Override canGoBack to enable back navigation."""
        return True