from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QToolButton,
                               QPushButton, QSizePolicy,  QComboBox,
                                QFormLayout, QFileDialog)
from PySide6.QtCore import Qt

from modules.event_handler import show_error_message, show_success_message
from modules.os import read_file, write_file, get_file_type
from all_widgets.drag_and_drop import DragAndDropArea
from modules.event_handler import *
import os
from config.logging_config import get_logger
from modules.utilities import extract_tables_from_pdfs
from all_widgets.fast_tool_tip_button import FastTooltipButton

logger = get_logger(__name__)

class PDFTableExtractor(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()

        self.dnd = DragAndDropArea()
        self.dnd.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Form layout
        form_layout = QFormLayout()

        self.combine_files_dropdown = self.create_dropdown_with_tooltip(
            "COMBINE FILES", ["Yes", "No"], "Combine all results into one Excel file."
        )
        form_layout.addRow(self.combine_files_dropdown[0], self.combine_files_dropdown[1])

        self.combine_tables_dropdown = self.create_dropdown_with_tooltip(
            "COMBINE TABLES", ["Yes", "No"], "Combine all tables on the same page into one sheet."
        )
        form_layout.addRow(self.combine_tables_dropdown[0], self.combine_tables_dropdown[1])

        self.mode_dropdown = self.create_dropdown_with_tooltip(
            "MODE", ["Normal"], "Select the mode for processing files."
        )
        form_layout.addRow(self.mode_dropdown[0], self.mode_dropdown[1])

        form_layout.setHorizontalSpacing(10)
        form_layout.setVerticalSpacing(0)
        form_layout.setContentsMargins(10, 0, 10, 0)

        form_layout_wid = QWidget()
        form_layout_wid.setLayout(form_layout)

        # Confirm Button
        self.confirm_button = QPushButton('Confirm')
        self.confirm_button.setFixedSize(100, 40)

        # MAIN LAYOUT
        main_layout.addWidget(self.dnd)
        main_layout.addWidget(form_layout_wid)
        main_layout.addWidget(self.confirm_button, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.setContentsMargins(0, 0, 0, 10)
        self.setLayout(main_layout)

        # SIGNAL
        self.dnd.filesDropped.connect(self.files_dropped_path)
        self.confirm_button.clicked.connect(self.process_all_files)

    def create_dropdown_with_tooltip(self, label_text, options, tooltip_text):
        """
        Creates a dropdown with a tooltip icon and label.
        :param label_text: The text label for the dropdown.
        :param options: The options for the dropdown.
        :param tooltip_text: The tooltip text for the info icon.
        :return: A tuple of QLabel and QWidget (with dropdown and info icon).
        """
        label = QLabel(label_text)

        # Info button (Circle with tooltip)
        info_button = FastTooltipButton()
        info_button.setText("?")
        info_button.setToolTip(tooltip_text)
        info_button.setStyleSheet("""
                    QToolButton {
                        border: 1px solid black;
                        border-radius: 10px;
                        min-width: 20px;
                        min-height: 20px;
                        text-align: center;
                        font-weight: bold;
                        background-color: lightgray;
                    }
                """)
        # Ensure the tooltip works properly
        info_button.setEnabled(True)
        info_button.setToolTipDuration(3000)  # Tooltip duration in milliseconds (optional)

        dropdown_layout = QHBoxLayout()

        # Dropdown
        dropdown = QComboBox()
        dropdown.addItems(options)
        dropdown.setStyleSheet("QComboBox { text-align: center; min-width: 150px; min-height: 25px; }")
        dropdown_layout.addWidget(info_button)
        dropdown_layout.addWidget(dropdown)

        # Container widget for dropdown and info
        dropdown_container = QWidget()
        dropdown_container.setLayout(dropdown_layout)

        return label, dropdown_container

    def files_dropped_path(self, path_list):
        self.path_list = path_list
        logger.info(f"Files dropped: {path_list}")

    def process_all_files(self):
        try:
            combine_files = self.combine_files_dropdown[1].layout().itemAt(1).widget().currentText() == "Yes"
            combine_tables = self.combine_tables_dropdown[1].layout().itemAt(1).widget().currentText() == "Yes"
            mode = self.mode_dropdown[1].layout().itemAt(1).widget().currentText()
            all_files_path = self.path_list

            if mode == "Normal":
                extract_tables_from_pdfs(all_files_path, None, combine_files, combine_tables)
            else:
                pass

            show_success_message(None, "SUCCEEDED","PDF table extraction process completed successfully.")
        except Exception as e:
            show_error_message(None,"ERROR", f"{e}")
            return





