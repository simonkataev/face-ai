from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QSizePolicy

from commons.common import Common


class CustomStatusBarLayout(QHBoxLayout):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.container = QHBoxLayout()
        self.lblexpired_status = QLabel()
        self.lblexpired_status.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.lblexpired_status.setAlignment(Qt.AlignLeft)
        self.lblexpired_status.setMinimumSize(300, Common.STATUS_BAR_HEIGHT)
        self.lblexpired_status.setMaximumSize(700, Common.STATUS_BAR_HEIGHT)

        self.container.addWidget(self.lblexpired_status)

    def set_message(self, mes):
        self.lblexpired_status.setText(mes)


