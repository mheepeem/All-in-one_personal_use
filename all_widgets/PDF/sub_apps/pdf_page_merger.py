from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy, QLineEdit
)
from PySide6.QtCore import Qt
from modules.event_handler import show_error_message, show_success_message
from modules.utilities import create_dynamic_pages_per_sheet
from pathlib import Path
from config.logging_config import get_logger
from all_widgets.drag_and_drop import DragAndDropArea
from all_widgets.input_manager_area import InputManagerArea

logger = get_logger(__name__)


class PDFPageMerger(QWidget):
    def __init__(self):
        super().__init__()

        # Drag-and-Drop Area
        self.dnd = DragAndDropArea()
        self.dnd.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Input Fields
        self.inputs = {
            "PAGES PER SHEET": {"type": QLineEdit, "default": 4},
            "MARGIN": {"type": QLineEdit, "default": 5},
        }
        self.input_manager = InputManagerArea(self.inputs)

        # Confirm Button
        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.setFixedWidth(150)
        self.confirm_button.clicked.connect(self.process_all_files)

        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.dnd)
        main_layout.addWidget(self.input_manager)

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

    def files_dropped_path(self, path_list):
        """Callback for dropped files."""
        self.path_list = path_list
        logger.info(f"Files dropped: {path_list}")

    def process_all_files(self):
        """Process files based on the inputs."""
        try:
            # Retrieve input values
            form_data = self.input_manager.get_form_data()
            pages_per_sheet = int(form_data.get("PAGES PER SHEET", 4))
            margin = int(form_data.get("MARGIN", 5))

            if pages_per_sheet % 2 != 0:
                logger.error("Invalid pages per sheet: Only even numbers are allowed.")
                raise ValueError("Accept only even numbers!")

            if not self.path_list:
                logger.error("No files dropped for processing.")
                raise ValueError("No files to process. Please drop files into the drop area.")

            logger.info(f"Processing files with {pages_per_sheet} pages per sheet and {margin} margin.")
            for file_path in self.path_list:
                dir = Path(file_path).parent
                filename = Path(file_path).stem
                file_type = Path(file_path).suffix.lower()

                if file_type != ".pdf":
                    logger.error(f"Unsupported file type: {file_path}. Expected a .pdf file.")
                    raise TypeError(f"Unsupported file type: {file_path}. Expected a .pdf file.")

                save_path = dir / f"{filename}_{pages_per_sheet}pages_per_sheet.pdf"
                logger.info(f"Creating {pages_per_sheet}-page-per-sheet PDF for {file_path}. Output: {save_path}")
                create_dynamic_pages_per_sheet(file_path, str(save_path), pages_per_sheet, margin)

            logger.info("All files processed successfully. Output files created.")
            show_success_message(None, "SUCCESS", "Please check your output")

        except ValueError as ve:
            logger.error(f"Value error: {ve}")
            show_error_message(None, "ERROR", str(ve))
        except TypeError as te:
            logger.error(f"Type error: {te}")
            show_error_message(None, "ERROR", str(te))
        except Exception as e:
            logger.error(f"Unexpected error during processing: {e}")
            show_error_message(None, "ERROR", str(e))
