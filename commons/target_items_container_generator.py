from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QGridLayout

from commons.db_connection import DBConnection


class TargetItemsContainerGenerator(QThread):
    finished_refreshing_target_items = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_old_cases = False
        self.is_shown_delete_button = False
        self.case_data_for_results = []
        self.results = []  # the widget to be refreshed.
        self.glyReportBuff = None
        self.widget = None

    def set_data(self, wdt, results, is_shown_delete_button, is_old_cases):
        self.widget = wdt
        self.results = results
        self.glyReportBuff = QGridLayout(wdt)
        self.is_shown_delete_button = is_shown_delete_button
        self.is_old_cases = is_old_cases

    def run(self) -> None:
        self.refresh_views()

    def refresh_views(self):
        if len(self.results):
            db = DBConnection()
            self.case_data_for_results = db.get_case_data(self.results)
        self.finished_refreshing_target_items.emit(self.case_data_for_results)


