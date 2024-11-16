from PySide6.QtWidgets import QMainWindow, QWidget,QHBoxLayout, QVBoxLayout, QStackedWidget, QLabel, QApplication
from widgets import Sidebar
from cryptit import CryptIt

class MainWindow(QMainWindow):
    def __init__(self,app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Mheepeem's Universal App")

        # Get and set screen size
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        self.setMinimumSize(screen_width * 0.2, screen_height * 0.2)

        self.sidebar = Sidebar()

        self.content_area = QStackedWidget()
        self.content_area.addWidget(CryptIt())
        # self.content_area.addWidget(QLabel("Settings Page"))
        # self.content_area.addWidget(QLabel("About Page"))

        # Connect the sidebar's page_changed signal to switch_page
        self.sidebar.page_changed.connect(self.switch_page)

        # Create the main layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_area)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Set margins to 0

        # Set the central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        central_widget.setContentsMargins(0,0,0,0)
        self.setCentralWidget(central_widget)

    def switch_page(self, index):  # Now in MainWindow
        self.content_area.setCurrentIndex(index)









