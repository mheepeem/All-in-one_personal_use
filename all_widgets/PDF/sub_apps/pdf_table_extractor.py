from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLineEdit, QSizePolicy
)
from PySide6.QtCore import Qt
from all_widgets.drag_and_drop import DragAndDropArea
from modules.utilities import extract_tables_from_pdfs
from config.logging_config import get_logger
from modules.event_handler import show_success_message, show_error_message
from all_widgets.mode_manager_area import ModeManagerArea

logger = get_logger(__name__)

class PDFTableExtractor(QWidget):
    def __init__(self):
        super().__init__()

        # Drag-and-Drop Area
        self.dnd = DragAndDropArea()
        self.dnd.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Modes and Widgets
        self.modes = {
            "Normal": {
                "Combine Files": {"type": QComboBox, "options": ["Yes", "No"]},
                "Combine Tables": {"type": QComboBox, "options": ["Yes", "No"]},
            }
        }

        # ModeManagerArea
        self.mode_manager = ModeManagerArea(modes=self.modes)
        self.mode_manager.mode_changed.connect(self.on_mode_changed)

        # Confirm Button
        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.setFixedWidth(150)
        self.confirm_button.clicked.connect(self.process_all_files)

        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.dnd)
        main_layout.addWidget(self.mode_manager)

        # Confirm Button Layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.confirm_button, alignment=Qt.AlignmentFlag.AlignCenter)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # Signal for dropped files
        self.dnd.filesDropped.connect(self.files_dropped_path)
        self.path_list = []

    def on_mode_changed(self, mode):
        """Callback for mode changes."""
        logger.info(f"Mode changed to: {mode}")

    def files_dropped_path(self, path_list):
        """Callback for file drops."""
        self.path_list = path_list
        logger.info(f"Files dropped: {path_list}")

    def process_all_files(self):
        """Process files based on the selected mode."""
        try:
            form_data = self.mode_manager.get_form_data()
            mode = form_data["mode"]
            logger.info(f"Processing mode: {mode}")

            if not self.path_list:
                raise ValueError("No files dropped into the area.")

            if mode == "Normal":
                combine_files = form_data["Combine Files"] == "Yes"
                combine_tables = form_data["Combine Tables"] == "Yes"
                extract_tables_from_pdfs(self.path_list, None, combine_files, combine_tables)

            elif mode == "Specific Case":
                specific_option = form_data["Specific Case Option"]
                logger.info(f"Processing Specific Case with option: {specific_option}")
                # Specific case logic

            show_success_message(None, "SUCCEEDED", "PDF table extraction completed successfully.")
        except Exception as e:
            logger.error(f"Error processing files: {e}")
            show_error_message(None, "ERROR", f"{e}")
            return
