from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel)
from PySide6.QtCore import Qt, Signal


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
        if event.mimeData().hasUrls():
            event.accept()
            self.label.setStyleSheet("background-color: lightblue;")
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        # Reset the background color when the drag leaves the area
        self.label.setStyleSheet("""
                        QLabel {
                            border: 2px dashed #FFFFFF; /* Red dashed border */
                            border-radius: 10px; /* Rounded corners */
                            padding: 10px; /* Add some padding */
                        }
                    """)

    def dropEvent(self,event):
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
                                border: 2px dashed #FFFFFF; /* Red dashed border */
                                border-radius: 10px; /* Rounded corners */
                                padding: 10px; /* Add some padding */
                            }
                        """)
            self.filesDropped.emit(all_filepaths)
        else:
            event.ignore()