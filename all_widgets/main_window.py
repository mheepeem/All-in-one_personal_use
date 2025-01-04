from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QLabel
from PySide6.QtGui import QPixmap, QFontDatabase, QFont, QIcon
from PySide6.QtCore import Qt
from all_widgets.sidebar import Sidebar
from modules.event_handler import InternetChecker
from all_widgets.registry import AppRegistry


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Mheepeem's Universal App")
        self.setWindowIcon(QIcon(":/images/icons/origami.png"))

        # State tracking
        self.is_first_load = True
        self.last_selected_main_app = 0  # Default to the first valid app index

        # Load fonts
        font_id = QFontDatabase.addApplicationFont(":/fonts/Kanit-Medium.ttf")
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            font_family = font_families[0]
            font = QFont(font_family, 10)
            self.app.setFont(font)

        # Menubar
        self.menubar = self.menuBar()
        self.menubar.setStyleSheet("""
            QMenuBar {
                background-color: #2D2D2D;
                color: white;
            }
            QMenuBar::item {
                background-color: transparent;
            }
            QMenuBar::item:selected {
                background-color: #3E3E3E;
            }
        """)

        # Internet status
        self.status_icon_label = QLabel()
        self.status_icon_label.setPixmap(
            QPixmap(":/images/components/red-dot.png").scaled(20, 20, Qt.KeepAspectRatio)
        )
        self.menubar.setCornerWidget(self.status_icon_label, Qt.TopRightCorner)

        # Sidebar and content area
        self.sidebar = Sidebar()
        self.content_area = QStackedWidget()
        self.blank_page = QWidget()  # Create a blank page
        self.content_area.addWidget(self.blank_page)  # Add blank page at index 0

        # Load apps dynamically
        self.load_apps()

        # Layout
        layout = QHBoxLayout()
        layout.addWidget(self.sidebar)
        layout.addWidget(self.content_area)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        central_widget = QWidget()
        central_widget.setLayout(layout)
        central_widget.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(central_widget)

        # InternetChecker for background internet status checking
        self.internet_checker = InternetChecker()
        self.internet_checker.status_changed.connect(self.update_status_icon)
        self.internet_checker.start()

        # Connect signals
        self.sidebar.page_changed.connect(self.switch_app)
        self.sidebar.sub_page_changed.connect(self.switch_sub_app)

    def load_apps(self):
        """Load apps dynamically from the AppRegistry."""
        for app_name, app_widget in AppRegistry.get_all_apps().items():
            app_widget.setObjectName(app_name)  # Set the object name for identification
            self.content_area.addWidget(app_widget)

            # Handle sub-apps
            sub_apps = AppRegistry.get_all_sub_apps().get(app_name, {})
            for sub_app_name, sub_app_widget in sub_apps.items():
                if isinstance(app_widget, QStackedWidget):  # Ensure parent app is a QStackedWidget
                    sub_app_widget.setObjectName(sub_app_name)
                    app_widget.addWidget(sub_app_widget)

    def switch_app(self, index):
        """Switch between main apps."""
        if self.is_first_load:
            # On first load, initialize and show the first app
            self.is_first_load = False
            self.content_area.setCurrentIndex(index + 1)  # Offset for blank page
            self.last_selected_main_app = index + 1
            print(f"First load, switched to main app: {index + 1}.")
            return

        adjusted_index = index + 1  # Offset for blank page
        if adjusted_index < self.content_area.count():
            selected_app = self.content_area.widget(adjusted_index)

            # Check if the selected app has sub-apps
            sub_apps = AppRegistry.get_all_sub_apps().get(selected_app.objectName(), {})
            if sub_apps:
                # If the app has sub-apps, retain the last selected app but update index
                print(f"Main app '{selected_app.objectName()}' has sub-apps. Retaining previous selection.")
                self.last_selected_main_app = adjusted_index  # Update index for sub-app switching
                return

            # For apps without sub-apps, switch directly
            self.content_area.setCurrentIndex(adjusted_index)
            self.last_selected_main_app = adjusted_index
            print(f"Switched to main app at index {index} (adjusted index {adjusted_index}).")
        else:
            print(f"Warning: No main app at index {index}.")

    def switch_sub_app(self, sub_app_name):
        """Switch between sub-apps."""
        current_app = self.content_area.currentWidget()

        # Ensure the current app is a QStackedWidget
        if not isinstance(current_app, QStackedWidget):
            # Adjust the content area to the main app with sub-apps (PDF in this case)
            if self.last_selected_main_app < self.content_area.count():
                self.content_area.setCurrentIndex(self.last_selected_main_app)
                current_app = self.content_area.currentWidget()
            else:
                print(f"Warning: Current app '{type(current_app).__name__}' does not support sub-app switching.")
                return

        # Find and switch to the correct sub-app
        for i in range(current_app.count()):
            widget = current_app.widget(i)
            if widget.objectName() == sub_app_name:
                current_app.setCurrentIndex(i)
                print(f"Switched to sub-app: {sub_app_name}")
                return

        print(f"Warning: Sub-app '{sub_app_name}' not found.")

    def update_status_icon(self, is_connected):
        """Update the internet status icon based on connectivity."""
        if is_connected:
            self.status_icon_label.setPixmap(
                QPixmap(":/images/components/green-dot.png").scaled(20, 20, Qt.KeepAspectRatio)
            )
        else:
            self.status_icon_label.setPixmap(
                QPixmap(":/images/components/red-dot.png").scaled(20, 20, Qt.KeepAspectRatio)
            )

    def closeEvent(self, event):
        """Stop the InternetChecker when closing the app."""
        self.internet_checker.stop()
        super().closeEvent(event)
