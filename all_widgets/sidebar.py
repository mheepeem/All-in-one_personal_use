from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem, QSizePolicy
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, Signal
from PySide6.QtGui import QIcon, QColor, QFontMetrics
from all_widgets.registry import AppRegistry
from config.logging_config import get_logger

logger = get_logger(__name__)

class Sidebar(QWidget):
    page_changed = Signal(int)  # Signal for main pages
    sub_page_changed = Signal(str)  # Signal for sub-pages
    expanded = Signal()  # Signal emitted when the sidebar is expanded

    def __init__(self):
        super().__init__()

        # Sidebar dimensions and styling
        self.collapsed_width = 34  # Width when collapsed
        self.expanded_width = 150  # Initial expanded width
        self.icon_size = 28  # Fixed icon size
        self.is_collapsed = False  # Track if the sidebar is collapsed
        self.indent_width = 20  # Indentation width for sub-items

        # Sidebar appearance
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#2D2D2D"))
        self.setPalette(palette)

        # Data structures
        self.parent_to_sub_items = {}  # Maps parent item text to sub-items
        self.sidebar_items = []  # Track parent items

        # Toggle button
        self.toggle_button = QPushButton("▾")
        self.toggle_button.setFixedSize(34, 34)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #2D2D2D;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #3E3E3E;
            }
        """)
        self.toggle_button.clicked.connect(self.toggle_sidebar)

        # Sidebar list widget
        self.sidebar = QListWidget()
        self.sidebar.setIconSize(QSize(self.icon_size, self.icon_size))
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.sidebar.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                color: white;
            }
        """)

        # Sidebar layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Populate sidebar dynamically
        self.populate_sidebar()

        # Adjust sidebar width on initialization
        self.adjust_sidebar_width()

        # Connect signals
        self.sidebar.itemClicked.connect(self.handle_item_clicked)

    def populate_sidebar(self):
        """Populate the sidebar dynamically."""
        default_icon_path = ":/images/icons/default.png"  # Default icon path
        for app_name, app_widget in AppRegistry.get_all_apps().items():
            icon_path = getattr(app_widget, "icon_path", default_icon_path)  # Use default if icon_path is missing
            parent_item = self.add_sidebar_item(app_name, icon_path, is_parent=True)
            self.sidebar_items.append(parent_item)

            # Add sub-apps
            sub_apps = AppRegistry.get_all_sub_apps().get(app_name, {})
            for sub_app_name in sub_apps.keys():
                self.add_sidebar_subitem(app_name, sub_app_name)

    def adjust_sidebar_width(self):
        """Adjust the sidebar width dynamically based on the longest text, including sub-items."""
        font_metrics = QFontMetrics(self.sidebar.font())
        max_text_width = 0

        for i in range(self.sidebar.count()):
            item = self.sidebar.item(i)
            text = item.text().strip()
            text_width = font_metrics.horizontalAdvance(text)

            # Add indentation for sub-items
            if item.data(Qt.UserRole).get("is_parent") is False:
                text_width += self.indent_width

            max_text_width = max(max_text_width, text_width)

        # Update the expanded width with padding
        padding = 10  # Reduce padding to avoid unnecessary extra space
        self.expanded_width = max(self.collapsed_width + padding, max_text_width + padding)
        self.sidebar.setMaximumWidth(self.expanded_width)

    def add_sidebar_item(self, text, icon_path, is_parent=False):
        """Add a parent item."""
        item = QListWidgetItem(self.sidebar)
        item.setText(text)
        item.setIcon(QIcon(icon_path))
        item.setData(Qt.UserRole, {"is_parent": is_parent, "sub_items": []})

        if is_parent:
            self.parent_to_sub_items[text] = []  # Initialize list for sub-items
        return item

    def add_sidebar_subitem(self, parent_text, text):
        """Add a sub-item."""
        sub_item = QListWidgetItem(f"    {text}")  # Indentation for sub-items
        sub_item.setData(Qt.UserRole, {"is_parent": False, "parent_text": parent_text})
        self.sidebar.addItem(sub_item)  # Add to sidebar directly
        self.parent_to_sub_items[parent_text].append(sub_item)

    def toggle_sidebar(self):
        """Expand or collapse the sidebar."""
        if self.is_collapsed:
            # Expand sidebar
            self.animation = QPropertyAnimation(self.sidebar, b"maximumWidth")
            self.animation.setDuration(200)
            self.animation.setStartValue(self.collapsed_width)
            self.animation.setEndValue(self.expanded_width)
            self.animation.start()
            self.toggle_button.setText("▾")
            self.is_collapsed = False

            # Emit expanded signal
            logger.info("Sidebar expanded.")
            self.expanded.emit()
        else:
            # Collapse sidebar
            self.animation = QPropertyAnimation(self.sidebar, b"maximumWidth")
            self.animation.setDuration(200)
            self.animation.setStartValue(self.expanded_width)
            self.animation.setEndValue(self.collapsed_width)
            self.animation.start()
            self.toggle_button.setText("▸")
            self.is_collapsed = True

            # Log sidebar collapse
            logger.info("Sidebar collapsed.")

    def handle_item_clicked(self, item):
        """Handle clicks on parent and sub-items."""
        item_data = item.data(Qt.UserRole)
        if item_data["is_parent"]:
            # Hide all sub-items first
            self.hide_all_subitems()

            # Show sub-items for the newly selected parent
            self.show_subitems(item.text())

            # Emit index for the selected main app
            self.page_changed.emit(self.sidebar.row(item))
        else:
            # Emit sub-app name
            self.sub_page_changed.emit(item.text().strip())

    def hide_all_subitems(self):
        """Hide all sub-items from the sidebar."""
        for sub_items in self.parent_to_sub_items.values():
            for sub_item in sub_items:
                # Remove sub-items from the sidebar
                if sub_item in [self.sidebar.item(i) for i in range(self.sidebar.count())]:
                    self.sidebar.takeItem(self.sidebar.row(sub_item))

    def show_subitems(self, parent_text):
        """Show sub-items for a given parent in the correct order."""
        if parent_text in self.parent_to_sub_items:
            parent_index = self.get_parent_index(parent_text)
            if parent_index is not None:
                # Insert sub-items immediately after the parent
                for i, sub_item in enumerate(self.parent_to_sub_items[parent_text]):
                    self.sidebar.insertItem(parent_index + 1 + i, sub_item)
        else:
            logger.warning(f"No sub-items found for parent: {parent_text}")

    def get_parent_index(self, parent_text):
        """Get the index of the parent item in the sidebar."""
        for i in range(self.sidebar.count()):
            item = self.sidebar.item(i)
            if item.text() == parent_text and item.data(Qt.UserRole)["is_parent"]:
                return i
        return None


