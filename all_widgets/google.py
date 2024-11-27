from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings

class Google(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Viewer")

        self.web_view = QWebEngineView()
        self.web_view.load(QUrl('https://www.google.com/'))
        self.web_view.loadFinished.connect(self.on_load_finished)

        layout = QVBoxLayout(self)
        layout.addWidget(self.web_view)
        self.setLayout(layout)

    def on_load_finished(self, success):
        if not success:
            print("Failed to load PDF.")