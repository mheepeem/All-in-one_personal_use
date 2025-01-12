from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QComboBox, QLineEdit, QSizePolicy
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QFontMetrics


class InputManagerArea(QWidget):
    def __init__(self, inputs=None):
        """
        Initialize the InputManagerArea with a dictionary of inputs.
        Each input should map to a dictionary with the type and options (if applicable).

        Example:
        self.inputs = {
            "TYPE": {"type": QComboBox, "options": ["Encrypt", "Decrypt"]},
            "KEY": {"type": QLineEdit, "default": "Enter an encryption key or leave it blank to use the default key (configured by you)"},
        }
        """
        super().__init__()

        self.inputs = inputs if inputs else {}
        self.widget_map = {}  # Store widgets for each input dynamically

        # Layouts
        self.main_layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()

        # Dynamic label width calculation
        self.max_label_width = self.calculate_max_label_width()

        # Add form layout to main layout
        self.main_layout.addLayout(self.form_layout)

        # Initialize UI with provided inputs
        self.initialize_inputs()

    def calculate_max_label_width(self):
        """
        Dynamically calculate the maximum width for labels based on their content.
        """
        font_metrics = QFontMetrics(self.font())
        max_width = 0
        for label in self.inputs.keys():
            label_width = font_metrics.horizontalAdvance(label)
            max_width = max(max_width, label_width)
        return max_width + 10  # Add some padding for consistency

    def initialize_inputs(self):
        """
        Dynamically create the input fields based on the provided configuration.
        """
        for label, widget_info in self.inputs.items():
            label_widget = QLabel(label)
            label_widget.setFixedWidth(self.max_label_width)  # Ensure consistent label width
            label_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

            # Create widget based on the type and options provided
            widget_type = widget_info.get("type")
            if widget_type == QComboBox:
                widget = QComboBox()
                widget.addItems(widget_info.get("options", []))  # Add dropdown options
            elif widget_type == QLineEdit:
                widget = QLineEdit()
                placeholder = widget_info.get("default", "")
                widget.setPlaceholderText(str(placeholder))  # Set placeholder text instead of actual value
            else:
                raise ValueError(f"Unsupported widget type: {widget_type}")

            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Ensure widgets adapt dynamically
            self.form_layout.addRow(label_widget, widget)
            self.widget_map[label] = widget

    def get_form_data(self):
        """
        Retrieve current input values.
        """
        data = {}
        for label, widget in self.widget_map.items():
            if isinstance(widget, QComboBox):
                data[label] = widget.currentText()
            elif isinstance(widget, QLineEdit):
                data[label] = widget.text() if widget.text() else widget.placeholderText()  # Fallback to placeholder
        return data
