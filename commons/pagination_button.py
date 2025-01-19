from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QPushButton

from commons.common import Common


class PaginationButton(QPushButton):
    button_clicked_signal = pyqtSignal(int)

    def __init__(self, current_page, parent=None):
        super().__init__(parent=parent)
        self.current_page = current_page
        self.setText(str(current_page + 1))
        self.setMinimumSize(Common.PAGINATION_BUTTON_SIZE, Common.PAGINATION_BUTTON_SIZE)
        self.setMaximumSize(Common.PAGINATION_BUTTON_SIZE, Common.PAGINATION_BUTTON_SIZE)
        self.setStyleSheet(Common.PAGINATION_BUTTON_STYLE)
        self.clicked.connect(self.button_clicked_slot)

    def button_clicked_slot(self):
        self.button_clicked_signal.emit(self.current_page)

