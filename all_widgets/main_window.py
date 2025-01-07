from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QLabel
from PySide6.QtGui import QPixmap, QFontDatabase, QFont, QIcon
from PySide6.QtCore import Qt
from all_widgets.sidebar import Sidebar
from modules.event_handler import InternetChecker
from all_widgets.registry import AppRegistry
from config.logging_config import get_logger

logger = get_logger(__name__)


class MainWindow(QMainWindow):

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Mheepeem's Universal App")
        self.setWindowIcon(QIcon(":/images/icons/origami.png"))

        # State tracking
        self.is_first_load = True
        self.last_selected_main_app = 0  # Default to the first valid app index
        self.last_selected_sub_app = {}

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
        self.internet_checker = InternetChecker(interval=10)
        self.internet_checker.status_changed.connect(self.update_status_icon)
        self.internet_checker.start()
        logger.info("InternetChecker initialized and started.")

        # Connect signals
        self.sidebar.page_changed.connect(self.switch_app)
        self.sidebar.sub_page_changed.connect(self.switch_sub_app)
        self.sidebar.expanded.connect(self.handle_sidebar_expanded)

    def load_apps(self):
        """Load apps dynamically from the AppRegistry."""
        for app_name, app_widget in AppRegistry.get_all_apps().items():
            try:
                app_widget.setObjectName(app_name)
                self.content_area.addWidget(app_widget)
                logger.info(f"Main app '{app_name}' loaded successfully.")

                # Handle sub-apps
                sub_apps = AppRegistry.get_all_sub_apps().get(app_name, {})
                for sub_app_name, sub_app_widget in sub_apps.items():
                    if isinstance(app_widget, QStackedWidget):
                        sub_app_widget.setObjectName(sub_app_name)
                        app_widget.addWidget(sub_app_widget)
                        logger.info(f"Sub-app '{sub_app_name}' added under '{app_name}'.")
                    else:
                        logger.warning(
                            f"Main app '{app_name}' is not a QStackedWidget. Skipping sub-app '{sub_app_name}'.")
            except Exception as e:
                logger.error(f"Failed to load app '{app_name}': {e}", exc_info=True)

    def switch_app(self, index):
        """Switch between main apps."""
        adjusted_index = index + 1  # Offset for blank page
        selected_app = self.content_area.widget(adjusted_index)

        # Check if the main app is already the current app
        if self.content_area.currentIndex() == adjusted_index:
            logger.info(
                f"Main app '{selected_app.objectName()}' is already displayed (index {index}). No action taken.")
            return

        # Hide all sub-apps of the previously selected main app
        previous_app = self.content_area.currentWidget()
        if isinstance(previous_app, QStackedWidget):
            previous_app.setCurrentIndex(0)  # Reset to the default page (e.g., the first sub-app or main app view)

        # Switch to the selected app
        if adjusted_index < self.content_area.count():
            self.last_selected_main_app = adjusted_index
            logger.info(f"Switched to main app: {selected_app.objectName()} (index {index}).")
            self.content_area.setCurrentIndex(adjusted_index)
        else:
            logger.warning(f"Invalid main app index: {index}. No app found.")

    def switch_sub_app(self, sub_app_name):
        """Switch between sub-apps."""
        if not sub_app_name:  # Check for empty sub-app name
            logger.warning("Attempted to switch to a sub-app with an empty name.")
            return

        current_app = self.content_area.currentWidget()

        # If the current app is not a QStackedWidget, locate and switch to the parent main app
        if not isinstance(current_app, QStackedWidget):
            for main_app_name, sub_apps in AppRegistry.get_all_sub_apps().items():
                if sub_app_name in sub_apps:
                    for index in range(1, self.content_area.count()):  # Skip blank page
                        widget = self.content_area.widget(index)
                        if widget.objectName() == main_app_name:
                            self.content_area.setCurrentIndex(index)
                            current_app = widget
                            self.last_selected_main_app = index  # Update the last selected main app

                            # Log the parent main app switch
                            logger.info(f"Switched to main app: {main_app_name} (index {index - 1}, with sub-apps).")
                            break
                    break

        # Ensure the current app is now a QStackedWidget (parent app with sub-apps)
        if not isinstance(current_app, QStackedWidget):
            logger.warning(f"Current app '{type(current_app).__name__}' does not support sub-app switching.")
            return

        # Switch to the correct sub-app
        for i in range(current_app.count()):
            widget = current_app.widget(i)
            if widget.objectName() == sub_app_name:
                current_app.setCurrentIndex(i)

                # Update the last selected sub-app for the current main app
                self.last_selected_sub_app[current_app.objectName()] = sub_app_name

                # Log the sub-app switch
                logger.info(f"Switched to sub-app: {sub_app_name}.")
                self.is_first_load = False
                return

        # Log a warning if the sub-app is not found
        logger.warning(f"Sub-app '{sub_app_name}' not found in the current app.")

    def handle_sidebar_expanded(self):
        """Handle actions when the sidebar is expanded."""
        current_app = self.content_area.currentWidget()

        if current_app:
            if isinstance(current_app, QStackedWidget):
                last_sub_app = self.last_selected_sub_app.get(current_app.objectName())

                if last_sub_app:
                    # Check if the last selected sub-app is already active
                    current_sub_app_index = current_app.currentIndex()
                    sub_app_widget = current_app.widget(current_sub_app_index)

                    if sub_app_widget and sub_app_widget.objectName() != last_sub_app:
                        logger.info(f"Restoring sub-app: {last_sub_app}.")
                        self.switch_sub_app(last_sub_app)
                    else:
                        logger.debug(f"Sub-app {last_sub_app} is already active. No action taken.")
                else:
                    logger.debug(f"No previous sub-app to restore for main app: {current_app.objectName()}.")
            else:
                # Log for main apps without sub-apps
                logger.debug(f"No sub-app handling required for main app: {current_app.objectName()}.")
        else:
            logger.warning("No current app found during sidebar expansion. Ignoring action.")

    def update_status_icon(self, is_connected):
        """Update the internet status icon based on connectivity."""
        if is_connected:
            self.status_icon_label.setPixmap(
                QPixmap(":/images/components/green-dot.png").scaled(20, 20, Qt.KeepAspectRatio)
            )
            logger.info("Internet connection detected. Status icon updated to green.")
        else:
            self.status_icon_label.setPixmap(
                QPixmap(":/images/components/red-dot.png").scaled(20, 20, Qt.KeepAspectRatio)
            )
            logger.warning("No internet connection detected. Status icon updated to red.")

    def closeEvent(self, event):
        """Stop the InternetChecker when closing the app."""
        self.internet_checker.stop()
        logger.info("Application is closing. Stopping InternetChecker.")
        super().closeEvent(event)
