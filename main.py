import sys
from PySide6.QtWidgets import QApplication
from all_widgets.main_window import MainWindow
from all_widgets.registry import load_apps_from_config
import resources.resources

if __name__ == "__main__":
    app = QApplication(sys.argv)
    load_apps_from_config("config/apps_config.json")
    window = MainWindow(app)
    window.show()
    sys.exit(app.exec())