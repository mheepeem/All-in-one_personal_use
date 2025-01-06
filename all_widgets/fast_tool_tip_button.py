from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QToolButton, QToolTip

class FastTooltipButton(QToolButton):
    def __init__(self):
        super().__init__()
        self._tooltip_timer = QTimer(self)
        self._tooltip_timer.setSingleShot(True)
        self._tooltip_timer.timeout.connect(self.show_tooltip)

    def enterEvent(self, event):
        self._tooltip_timer.start(0)  # Set delay in milliseconds (e.g., 0 for no delay)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._tooltip_timer.stop()
        QToolTip.hideText()
        super().leaveEvent(event)

    def show_tooltip(self):
        QToolTip.showText(self.mapToGlobal(self.rect().center()), self.toolTip(), self)
