from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QComboBox, QHBoxLayout, QLineEdit, QSizePolicy
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QFontMetrics


class ModeManagerArea(QWidget):
    confirm_clicked = Signal(dict)  # Signal to emit the form data when confirmed
    mode_changed = Signal(str)     # Signal to emit the new mode when it changes

    def __init__(self, modes=None):
        """
        Initialize the ModeManagerArea with a dictionary of modes.
        Each mode should map to a dictionary of (label, widget_func) pairs.

        self.modes = {
            "Normal": {
                "Combine Files": {"type": QComboBox, "options": ["Yes", "No"]},
                "Combine Tables": {"type": QComboBox, "options": ["Yes", "No"]},
            },
            "Specific Case": {
                "Specific Case Option": {"type": QLineEdit},
            },
        }
        """
        super().__init__()

        self.modes = modes if modes else {}
        self.current_mode = None
        self.widget_map = {}  # Store widgets for each mode dynamically

        # Layouts
        self.main_layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()

        # Dynamic label width calculation
        self.max_label_width = self.calculate_max_label_width()

        # Mode Dropdown (label + dropdown in a horizontal layout)
        self.init_mode_selector()

        # Add form layout to main layout
        self.main_layout.addLayout(self.form_layout)

        # Initialize UI with the first mode
        self.on_mode_changed(self.mode_dropdown.currentText())

    def init_mode_selector(self):
        """Initialize the mode selector (label + dropdown)."""
        mode_row_layout = QHBoxLayout()

        # Mode Label
        mode_label = QLabel("MODE")
        mode_label.setFixedWidth(self.max_label_width)
        mode_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Mode Dropdown
        self.mode_dropdown = QComboBox()
        self.mode_dropdown.addItems(self.modes.keys())
        self.mode_dropdown.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.mode_dropdown.currentTextChanged.connect(self.on_mode_changed)

        # Add to layout
        mode_row_layout.addWidget(mode_label)
        mode_row_layout.addWidget(self.mode_dropdown)
        self.main_layout.addLayout(mode_row_layout)

    def calculate_max_label_width(self):
        """
        Dynamically calculate the maximum width for labels based on their content.
        """
        font_metrics = QFontMetrics(self.font())
        max_width = font_metrics.horizontalAdvance("MODE")  # Include "MODE" as a reference label
        for mode, fields in self.modes.items():
            for label, _ in fields.items():
                label_width = font_metrics.horizontalAdvance(label)
                max_width = max(max_width, label_width)
        return max_width + 10  # Add some padding for consistency

    def on_mode_changed(self, mode):
        """Update the UI when the mode changes."""
        self.current_mode = mode
        self.update_ui_based_on_mode(mode)
        self.mode_changed.emit(mode)

    def update_ui_based_on_mode(self, mode):
        """Dynamically update the form layout for the selected mode."""
        # Clear the form layout
        while self.form_layout.rowCount() > 0:
            self.form_layout.removeRow(0)

        self.widget_map = {}  # Reset the widget map for the current mode

        for label, widget_info in self.modes[mode].items():
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
            else:
                raise ValueError(f"Unsupported widget type: {widget_type}")

            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Ensure widgets adapt dynamically
            self.form_layout.addRow(label_widget, widget)
            self.widget_map[label] = widget

    def get_form_data(self):
        """Retrieve current input values."""
        data = {"mode": self.current_mode}
        for label, widget in self.widget_map.items():
            if isinstance(widget, QComboBox):
                data[label] = widget.currentText()
            elif isinstance(widget, QLineEdit):
                data[label] = widget.text()
        return data
