from PySide6.QtWidgets import (QWidget, QVBoxLayout,
                               QPushButton, QListWidget, QListWidgetItem, QLabel, QSizePolicy)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, Signal
from PySide6.QtGui import QIcon, QColor
from all_widgets.registry import AppRegistry

class Sidebar(QWidget):
    page_changed = Signal(int)  # Signal for main pages
    sub_page_changed = Signal(str)  # Signal for sub-pages

    def __init__(self):
        super().__init__()

        # Sidebar dimensions and styling
        self.sidebar_width = 80
        self.collapsed_width = 34
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#2D2D2D"))
        self.setPalette(palette)

        # Data structure to track sub-items
        self.parent_to_sub_items = {}  # Maps parent item text to a list of sub-items
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
        self.sidebar.setMaximumWidth(self.sidebar_width)
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

        # Connect signals
        self.sidebar.setIconSize(QSize(28, 28))
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

    def add_sidebar_item(self, text, icon_path, is_parent=False):
        """Add a parent item dynamically."""
        item = QListWidgetItem(self.sidebar)
        item.setText(text)
        item.setIcon(QIcon(icon_path))
        item.setData(Qt.UserRole, {"is_parent": is_parent, "sub_items": []})
        if is_parent:
            self.parent_to_sub_items[text] = []  # Initialize list for sub-items
        return item

    def add_sidebar_subitem(self, parent_text, text):
        """Add a sub-item dynamically."""
        sub_item = QListWidgetItem(f"    {text}")
        sub_item.setData(Qt.UserRole, {"is_parent": False, "parent_text": parent_text})
        self.parent_to_sub_items[parent_text].append(sub_item)  # Track sub-items for the parent

    def show_subitems(self, parent_text):
        """Show sub-items directly below the selected parent."""
        parent_row = None
        for i in range(self.sidebar.count()):
            if self.sidebar.item(i).text() == parent_text:
                parent_row = i
                break

        if parent_row is not None:
            for sub_item in self.parent_to_sub_items.get(parent_text, []):
                self.sidebar.insertItem(parent_row + 1, sub_item)
                parent_row += 1  # Adjust row position for subsequent sub-items

    def hide_all_subitems(self):
        """Remove all sub-items from the sidebar."""
        for sub_items in self.parent_to_sub_items.values():
            for sub_item in sub_items:
                if self.sidebar.row(sub_item) != -1:  # Check if the item is in the sidebar
                    self.sidebar.takeItem(self.sidebar.row(sub_item))

    def handle_item_clicked(self, item):
        """Handle clicks on parent and sub-items."""
        item_data = item.data(Qt.UserRole)
        if item_data["is_parent"]:
            # Parent item clicked
            self.hide_all_subitems()  # Hide all sub-items
            self.show_subitems(item.text())  # Show sub-items for the selected parent
            index = self.sidebar_items.index(item)
            self.page_changed.emit(index)
        else:
            # Sub-item clicked
            sub_app_name = item.text().strip()
            print(f"Sub-app clicked: {sub_app_name}")
            self.sub_page_changed.emit(sub_app_name)

    def toggle_sidebar(self):
        """Expand or collapse the sidebar with animation."""
        if self.sidebar.maximumWidth() == self.sidebar_width:
            # Collapse animation
            self.animation = QPropertyAnimation(self.sidebar, b"maximumWidth")
            self.animation.setDuration(200)
            self.animation.setStartValue(self.sidebar_width)
            self.animation.setEndValue(self.collapsed_width)
            self.animation.start()
            self.toggle_button.setText("▸")
        else:
            # Expand animation
            self.animation = QPropertyAnimation(self.sidebar, b"maximumWidth")
            self.animation.setDuration(200)
            self.animation.setStartValue(self.collapsed_width)
            self.animation.setEndValue(self.sidebar_width)
            self.animation.start()
            self.toggle_button.setText("▾")
