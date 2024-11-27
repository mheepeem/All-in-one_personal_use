from PySide6.QtWidgets import QMainWindow, QWidget,QHBoxLayout, QVBoxLayout, QStackedWidget, QLabel, QApplication
from PySide6.QtGui import  QPixmap, QFontDatabase, QFont
from PySide6.QtCore import Qt
from all_widgets.widgets import Sidebar, PDFViewer
from all_widgets.cryptit import CryptIt
from modules.event_handler import InternetChecker
from all_widgets.google import Google
import resources

class MainWindow(QMainWindow):
    def __init__(self,app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Mheepeem's Universal App")

        # Load Fonts
        font_id = QFontDatabase.addApplicationFont(":/fonts/Kanit-Medium.ttf")  # Replace with your font file path
        font_families = QFontDatabase.applicationFontFamilies(font_id)

        if font_families:
            font_family = font_families[0]  # Get the first font family from the loaded font
            font = QFont(font_family, 10)  # Create a QFont object with the desired size
            self.app.setFont(font)

        # Get and set screen size
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        self.setMinimumSize(screen_width * 0.2, screen_height * 0.2)

        self.menubar = self.menuBar()
        self.menubar.setStyleSheet("""
            QMenuBar {
                background-color: #2D2D2D; /* Replace with your sidebar's background color */
                color: white; /* Optional: Set text color */
            }
            QMenuBar::item {
                background-color: transparent;
            }
            QMenuBar::item:selected {
                background-color: #3E3E3E; /* Optional: Highlight color when hovering */
            }
        """)

        # Internet Status Icon
        self.status_icon_label = QLabel()
        self.status_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.initial_pixmap = QPixmap(":/images/components/red-dot.png").scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Replace with your image path
        self.status_icon_label.setPixmap(self.initial_pixmap)
        self.menubar.setCornerWidget(self.status_icon_label, Qt.TopRightCorner)
        self.status_icon_label.setContentsMargins(0,2,5,2)

        self.sidebar = Sidebar()

        self.content_area = QStackedWidget()
        self.content_area.addWidget(CryptIt())
        self.content_area.addWidget(Google())

        # self.content_area.addWidget(QLabel("Settings Page"))
        # self.content_area.addWidget(QLabel("About Page"))

        # Connect the sidebar's page_changed signal to switch_page
        self.sidebar.page_changed.connect(self.switch_page)

        # Create the main layout
        All_content_layout = QHBoxLayout()
        All_content_layout.addWidget(self.sidebar)
        All_content_layout.addWidget(self.content_area)
        All_content_layout.setContentsMargins(0, 0, 0, 0)
        All_content_layout.setSpacing(0)# Set margins to 0

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.menubar)
        main_layout.addLayout(All_content_layout)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Set the central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        central_widget.setContentsMargins(0,0,0,0)
        self.setCentralWidget(central_widget)

        # Background Execution
        self.checker_thread = InternetChecker()
        self.checker_thread.status_changed.connect(self.update_status)
        self.checker_thread.start()

    def switch_page(self, index):  # Now in MainWindow
        self.content_area.setCurrentIndex(index)

    def update_status(self, is_connected):
        if is_connected:
            pixmap = QPixmap(":/images/components/green-dot.png").scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Replace with your image path
        else:
            pixmap = QPixmap(":/images/components/red-dot.png").scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Replace with your image path
        self.status_icon_label.setPixmap(pixmap)

    def closeEvent(self, event):
        self.checker_thread.stop()  # Stop the thread when the window is closed
        event.accept()









