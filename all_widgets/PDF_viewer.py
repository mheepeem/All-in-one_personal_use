from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import  QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings

class PDFViewer(QWidget):
    def __init__(self, filepath):
        super().__init__()
        self.setWindowTitle("PDF Viewer")

        self.web_view = QWebEngineView()
        # Set PDF Viewer to True, if not you can't load and view a pdf.
        self.web_view.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.PdfViewerEnabled, True)
        self.web_view.load(QUrl.fromLocalFile(filepath))
        self.web_view.loadFinished.connect(self.on_load_finished)

        layout = QVBoxLayout(self)
        layout.addWidget(self.web_view)
        self.setLayout(layout)

    def on_load_finished(self, success):
        if not success:
            print("Failed to load PDF.")