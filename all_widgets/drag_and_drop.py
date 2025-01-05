from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel)
from PySide6.QtCore import Qt, Signal
from config.logging_config import get_logger

logger = get_logger(__name__)

class DragAndDropArea(QWidget):

    filesDropped = Signal(list)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.initUI()

    def initUI(self):

        self.label = QLabel('Drag and Drop here!')
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
                QLabel {
                    border: 2px dashed #FFFFFF; /* Red dashed border */
                    border-radius: 10px; /* Rounded corners */
                    padding: 10px; /* Add some padding */
                }
            """)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def dragEnterEvent(self, event):
        logger.info("Drag event detected: file dragged into drop area.")
        if event.mimeData().hasUrls():
            event.accept()
            self.label.setStyleSheet("background-color: lightblue;")
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            show_filepaths = ''
            all_filepaths = []
            for url in event.mimeData().urls():
                filepath = url.toLocalFile()
                all_filepaths.append(filepath)
                show_filepaths += f"{filepath}\n"
                self.label.setText(f"Dropped file\n {show_filepaths}")
            self.label.setStyleSheet("""
                            QLabel {
                                border: 2px dashed #FFFFFF; /* White dashed border */
                                border-radius: 10px; /* Rounded corners */
                                padding: 10px; /* Add some padding */
                            }
                        """)
            self.filesDropped.emit(all_filepaths)
            logger.info("Drop operation succeeded: File(s) dropped into the upload area.")
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        logger.info("Drop operation canceled: User dragged item outside the valid area.")
        # Reset the background color when the drag leaves the area
        self.label.setStyleSheet("""
                        QLabel {
                            border: 2px dashed #FFFFFF; /* White dashed border */
                            border-radius: 10px; /* Rounded corners */
                            padding: 10px; /* Add some padding */
                        }
                    """)