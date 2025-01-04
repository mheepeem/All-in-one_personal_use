from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from PySide6.QtCore import QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage

class Gemini(QWidget):
    icon_path = ":/images/icons/gemini.png"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gemini")

        self.web_view = QWebEngineView()
        self.web_view.setPage(WebEnginePageWithHistory(self))
        self.web_view.load(QUrl('https://gemini.google.com/'))
        # self.web_view.loadFinished.connect(self.on_load_finished)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.web_view.back)
        forward_button = QPushButton("Forward")
        forward_button.clicked.connect(self.web_view.forward)

        button_layout = QHBoxLayout()
        button_layout.addWidget(back_button)
        button_layout.addWidget(forward_button)

        layout = QVBoxLayout(self)
        layout.addLayout(button_layout)
        layout.addWidget(self.web_view)
        self.setLayout(layout)

    # def on_load_finished(self, success):
    #     if not success:
    #         print("Failed to load PDF.")

class WebEnginePageWithHistory(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)

    def canGoBack(self):
        """Override canGoBack to enable back navigation."""
        return True