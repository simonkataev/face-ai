from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QPushButton

from commons.probing_result import ProbingResult


class ExportPdfButton(QPushButton):
    export_pdf_signal = pyqtSignal(ProbingResult)

    def __init__(self, probe_result):
        super().__init__()
        self.setStyleSheet("color:rgb(88,156,255);font:12pt 'Arial';max-height:50px")
        self.setText("Export")
        self.probe_result = probe_result
        self.clicked.connect(self.clicked_button)

    def clicked_button(self):
        self.export_pdf_signal.emit(self.probe_result)
