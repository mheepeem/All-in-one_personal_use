from PySide6.QtWidgets import (QWidget, QVBoxLayout,
                               QPushButton, QSizePolicy,  QComboBox,
                               QLineEdit, QFormLayout, QFileDialog)
from PySide6.QtCore import Qt

from modules.event_handler import show_error_message, show_success_message
from modules.os import read_file, write_file, get_file_type
from modules.security import *
from all_widgets.drag_and_drop import DragAndDropArea
from modules.event_handler import *
import os
from config.logging_config import get_logger

logger = get_logger(__name__)

class CryptIt(QWidget):

    icon_path = ":/images/icons/cryptit.png"

    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()

        self.dnd = DragAndDropArea()
        self.dnd.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Form layout
        form_layout = QFormLayout()

        self.type_dropdown = QComboBox()
        self.type_dropdown.addItem("Encrypt")
        self.type_dropdown.addItem("Decrypt")
        self.type_dropdown.setStyleSheet("QComboBox { text-align: center; min-width: 150px; min-height: 25px;}")
        form_layout.addRow("TYPE", self.type_dropdown)

        self.key_input = QLineEdit()
        self.key_input.setStyleSheet("QLineEdit { text-align: center; min-width: 150px; min-height: 20px;}")
        form_layout.addRow("KEY", self.key_input)

        form_layout.setHorizontalSpacing(10)
        form_layout.setVerticalSpacing(10)
        form_layout.setContentsMargins(10,0,10,0)

        form_layout_wid = QWidget()
        form_layout_wid.setLayout(form_layout)

        # Confirm Button
        self.confirm_button = QPushButton('Confirm')
        self.confirm_button.setFixedSize(100,40)

        # MAIN LAYOUT
        main_layout.addWidget(self.dnd)
        main_layout.addWidget(form_layout_wid)
        # main_layout.addWidget(dir_layout_wid)
        main_layout.addWidget(self.confirm_button, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.setContentsMargins(0, 0, 0, 10)
        self.setLayout(main_layout)

        # SIGNAL
        self.dnd.filesDropped.connect(self.files_dropped_path)
        self.confirm_button.clicked.connect(self.process_all_files)

    def browse_files(self):
        logger.info("browse file.")
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.Directory)  # Set directory selection mode
        if file_dialog.exec():
            selected_dir = file_dialog.selectedFiles()[0]
            # Do something with the selected directory (e.g., display it)
            print(f"Selected directory: {selected_dir}")

    def files_dropped_path(self, path_list):
        self.path_list = path_list
        logger.info(f"Files dropped: {path_list}")

    def process_all_files(self):
        try:
            if not self.key_input.text() and not os.environ.get('CRYPTO_KEY'):
                raise ValueError("No encryption key provided. Please set CRYPTO_KEY or enter a key manually.")

            key = os.environ.get('CRYPTO_KEY') if not self.key_input.text() else self.key_input.text()
            cur_val_dropdown = self.type_dropdown.currentText()
            all_files_path = self.path_list

            for file_path in all_files_path:
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

                # write new file
                save_path = os.path.join(dir, new_filename)
                write_file(save_path, output_msg)
                logger.info(f"Processed file '{file_path}'. Saved as '{save_path}'.")

            show_success_message(None, "SUCCESS", 'Done!')
            logger.info("All files processed successfully.")

        except Exception as e:
            show_error_message(None,"ERROR", f"{e}")
            logger.error(f"Unexpected error during file processing: {e}")
            raise





