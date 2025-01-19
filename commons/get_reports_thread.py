from PyQt5.QtCore import QThread, pyqtSignal

from commons.db_connection import DBConnection


class GetReportsThread(QThread):
    finished_reports_signal = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self) -> None:
        results = []
        db = DBConnection()
        results = db.get_values()
        self.finished_reports_signal.emit(results)
