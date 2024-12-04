# from encodings.punycode import selective_find

from PySide6.QtWidgets import (QWidget, QVBoxLayout,
                               QPushButton, QSizePolicy,  QComboBox,
                               QLineEdit, QFormLayout, QFileDialog)
from PySide6.QtCore import Qt

from modules.event_handler import show_error_message, show_success_message
from all_widgets.widgets import DragAndDropArea
from modules.event_handler import *
from modules.utilities import create_dynamic_pages_per_sheet
from pathlib import Path
import os

class PDFPageMerger(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()

        self.dnd = DragAndDropArea()
        self.dnd.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Form layout
        form_layout = QFormLayout()

        self.pages_input = QLineEdit()
        self.pages_input.setStyleSheet("QLineEdit { text-align: center; min-width: 150px; min-height: 20px;}")
        form_layout.addRow("PAGES PER SHEET", self.pages_input)

        self.margin_input = QLineEdit()
        self.margin_input.setStyleSheet("QLineEdit { text-align: center; min-width: 150px; min-height: 20px;}")
        form_layout.addRow("MARGIN", self.margin_input)

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
        main_layout.addWidget(self.confirm_button, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.setContentsMargins(0, 0, 0, 10)
        self.setLayout(main_layout)

        # SIGNAL
        self.dnd.filesDropped.connect(self.files_dropped_path)
        self.confirm_button.clicked.connect(self.process_all_files)


    def browse_files(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.Directory)  # Set directory selection mode
        if file_dialog.exec():
            selected_dir = file_dialog.selectedFiles()[0]
            # Do something with the selected directory (e.g., display it)
            print(f"Selected directory: {selected_dir}")

    def files_dropped_path(self, path_list):
        self.path_list = path_list
        print(self.path_list)

    def process_all_files(self):
        try:
            pages_per_sheet = 4 if self.pages_input.text() == "" else int(self.pages_input.text())
            margin = 5 if self.margin_input.text() == "" else int(self.margin_input.text())

            all_files_path = self.path_list

            if pages_per_sheet % 2 != 0:
                raise ValueError("Accept only even number!")

            for file_path in all_files_path:
                dir = os.path.dirname(file_path)
                filename = os.path.basename(file_path)
                file_type = Path(filename).suffix.replace('.', '')

                if file_type != 'pdf':
                    raise TypeError(f"Unsupported file type: {file_path}. Expected a .pdf file.")

                save_path = os.path.join(dir, filename + f"_{pages_per_sheet}pages_per_sheet.pdf")
                create_dynamic_pages_per_sheet(file_path, save_path, pages_per_sheet, margin)

            show_success_message(None, 'SUCCESS', 'Please check your output')

        except Exception as e:
            show_error_message(None,"ERROR", f"{e}")





