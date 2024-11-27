from PySide6.QtWidgets import (QWidget, QVBoxLayout,
                               QPushButton, QListWidget, QStackedWidget, QHBoxLayout,
                               QListWidgetItem, QLabel, QSizePolicy, QFrame, QGridLayout, QComboBox,
                               QStyledItemDelegate, QLineEdit, QFormLayout, QFileDialog)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, Signal, QUrl
from PySide6.QtGui import QIcon
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
import resources

class Sidebar(QWidget):
    page_changed = Signal(int)

    def __init__(self):
        super().__init__()

        # Create the sidebar with a specific width
        self.sidebar = QListWidget()
        self.sidebar_width = 80  # Set your desired sidebar width
        self.sidebar.setMaximumWidth(self.sidebar_width)
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.sidebar.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sidebar.setStyleSheet("QListWidget { border-radius: 0px; }")

        # Create a toggle button
        self.toggle_button = QPushButton("▾")
        self.toggle_button.setFixedSize(34, 34)
        self.toggle_button.clicked.connect(self.toggle_sidebar)

        # Create a custom widget to hold the button in the sidebar
        toggle_widget = QWidget()
        toggle_layout = QHBoxLayout(toggle_widget)
        toggle_layout.addWidget(self.toggle_button, alignment=Qt.AlignmentFlag.AlignLeft)
        toggle_layout.setContentsMargins(0, 0, 0, 0)

        # Create a custom list widget item for the button
        toggle_item = QListWidgetItem(self.sidebar)
        toggle_item.setSizeHint(toggle_widget.sizeHint())
        self.sidebar.addItem(toggle_item)
        self.sidebar.setItemWidget(toggle_item, toggle_widget)

        # Store references to the items in a list
        self.sidebar_items = []

        # Add the buttons to the sidebar with icons
        self.add_sidebar_item("CryptIt", ":/images/icons/cryptit.png")
        self.add_sidebar_item("Google", ":/images/icons/google.png")
        # self.add_sidebar_item("Home", "./images/icons/cryptit.png")
        # self.add_sidebar_item("About", "./images/icons/cryptit.png")

        # Connect itemClicked signal to emit_page_changed using a loop
        self.sidebar.setIconSize(QSize(28, 28))
        self.sidebar.itemClicked.connect(self.handle_item_clicked)

        # Create the layout for the sidebar
        layout = QVBoxLayout(self)
        layout.addWidget(self.sidebar)
        layout.setContentsMargins(0,0,0,0)  # Set margins to 0
        self.sidebar.setStyleSheet("QListWidget { border-radius: 0px; }")
        self.setLayout(layout)

    def add_sidebar_item(self, text, icon_path):
        item = QListWidgetItem(self.sidebar)
        item.setText(text)
        item.setIcon(QIcon(icon_path))
        self.sidebar.addItem(item)
        self.sidebar_items.append(item)  # Add the item to the list

    def handle_item_clicked(self, item):
        if item in self.sidebar_items:
            index = self.sidebar_items.index(item)
            self.emit_page_changed(index)

    def emit_page_changed(self, index):
        self.page_changed.emit(index)

    def toggle_sidebar(self):
        if self.sidebar.maximumWidth() == self.sidebar_width:
            # Create animation to collapse the sidebar
            self.animation = QPropertyAnimation(self.sidebar, b"maximumWidth")
            self.animation.setDuration(200)
            self.animation.setStartValue(self.sidebar_width)
            self.animation.setEndValue(34)
            self.animation.start()
            self.toggle_button.setText("▸")
        else:
            # Create animation to expand the sidebar
            self.animation = QPropertyAnimation(self.sidebar, b"maximumWidth")
            self.animation.setDuration(200)
            self.animation.setStartValue(34)
            self.animation.setEndValue(self.sidebar_width)
            self.animation.start()
            self.toggle_button.setText("▾")

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








