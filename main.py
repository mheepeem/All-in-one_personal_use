import sys
from PySide6.QtWidgets import QApplication
from all_widgets.main_window import MainWindow
from all_widgets.registry import load_apps_from_config
from config.logging_config import get_logger, LoggingManager, rotate_logs, create_logging_config, get_current_log_file
import resources.resources

def main():
    rotate_logs()
    log_file = get_current_log_file()
    logging_config = create_logging_config()
    log_manager = LoggingManager(logging_config, log_file)
    log_manager.log_start()

    logger = get_logger(__name__)

    try:
        app = QApplication(sys.argv)
        load_apps_from_config("config/apps_config.json")
        window = MainWindow(app)
        window.show()
        logger.info("Application is running...")
        sys.exit(app.exec())
    finally:
        log_manager.log_end()

if __name__ == "__main__":
    main()