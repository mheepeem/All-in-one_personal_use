from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy, QComboBox, QLineEdit
)
from PySide6.QtCore import Qt
from modules.event_handler import show_error_message, show_success_message
from modules.os import read_file, write_file, get_file_type
from modules.security import *
from all_widgets.drag_and_drop import DragAndDropArea
from all_widgets.input_manager_area import InputManagerArea
from config.logging_config import get_logger
import os

logger = get_logger(__name__)

class CryptIt(QWidget):

    icon_path = ":/images/icons/cryptit.png"

    def __init__(self):
        super().__init__()

        # Drag-and-Drop Area
        self.dnd = DragAndDropArea()
        self.dnd.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Input Fields
        self.inputs = {
            "TYPE": {"type": QComboBox, "options": ["Encrypt", "Decrypt"]},
            "KEY": {"type": QLineEdit, "default": "Enter an encryption key or leave it blank to use the default key (configured by you)"},
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
            key = form_data.get("KEY")
            cur_val_dropdown = form_data.get("TYPE")

            if not key and not os.environ.get('CRYPTO_KEY'):
                raise ValueError("No encryption key provided. Please set CRYPTO_KEY or enter a key manually.")

            key = os.environ.get('CRYPTO_KEY') if not key else key

            if not self.path_list:
                raise ValueError("No files dropped for processing. Please drop files into the drop area.")

            for file_path in self.path_list:
                # Read data from file
                logger.info(f"Reading file: {file_path}")
                data = read_file(file_path)
                if not data:
                    logger.warning(f"No data found in file: {file_path}")
                    continue

                dir = os.path.dirname(file_path)
                filename = os.path.basename(file_path)
                file_type = get_file_type(file_path)

                # Encryption, Decryption
                if cur_val_dropdown == "Encrypt":
                    match file_type:
                        case 'application/json':
                            encrypt_kv_value_only(data, key)
                            output_msg = data
                        case _:
                            output_msg = encrypt_message(data, key)
                    new_filename = "encrypted_" + filename
                else:
                    match file_type:
                        case 'application/json':
                            decrypt_kv_value_only(data, key)
                            output_msg = data
                        case _:
                            output_msg = decrypt_message(data, key)
                    new_filename = "decrypted_" + filename.replace('encrypted_', '')

                # Write new file
                save_path = os.path.join(dir, new_filename)
                write_file(save_path, output_msg)
                logger.info(f"Processed file '{file_path}'. Saved as '{save_path}'.")

            show_success_message(None, "SUCCESS", 'Done!')
            logger.info("All files processed successfully.")

        except Exception as e:
            show_error_message(None, "ERROR", f"{e}")
            logger.error(f"Unexpected error during file processing: {e}")
            raise
