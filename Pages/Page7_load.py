import os
import time
from datetime import datetime
from commons.systimer import SysTimer
from commons.ntptime import ntp_get_time_from_object

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QSize, Qt
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QTableWidget, QHBoxLayout, QLineEdit, QComboBox, QTableWidgetItem, \
    QFileDialog, QMessageBox, QWidget, QLabel

from commons.common import Common
from commons.export_pdf_button import ExportPdfButton
from commons.gen_report import export_report_pdf, gen_pdf_filename
from commons.get_reports_thread import GetReportsThread
from commons.pagination_layout import PaginationLayout
from commons.probing_result import ProbingResult
from commons.zip_thread import ZipThread, ThreadResult


class LoaderProbeReportListPage(QWidget):
    return_home_signal = pyqtSignal(str)
    go_back_signal = pyqtSignal(object)
    go_back_empty_signal = pyqtSignal()
    start_splash_signal = pyqtSignal(str)
    stop_splash_signal = pyqtSignal(object)

    def __init__(self, parent=None):
        super(LoaderProbeReportListPage, self).__init__(parent=parent)
        self.zip_thread = None
        self.probe_result = ProbingResult()
        self.current_page = 0
        self.current_search_page = 0
        self.number_per_page = 10
        self.search_string = '%'
        self.is_searching_result = False
        self.reports = []
        self.searched_reports = []
        self.shown_reports = []  # current shown reports on table
        self.get_reports_thread = GetReportsThread()

        self.window = uic.loadUi("./forms/Page_7.ui", self)
        self.btnReturnHome = self.findChild(QPushButton, "btnReturnHome")
        self.btnGoBack = self.findChild(QPushButton, "btnGoBack1")
        self.btnExportAllZip = self.findChild(QPushButton, "btnExportAllZip")
        self.btnGoRemainingPage = self.findChild(QPushButton, "btnGoRemainingPage")
        self.vlyTableContainer = self.findChild(QVBoxLayout, "vlyTableContainer")
        self.resultTable = self.findChild(QTableWidget, "resultTable")
        style = "::section {background-color: rgb(0, 90, 226);border: 1px solid rgb(53, 132, 228); }"
        self.setStyleSheet(style)
        self.resultTable.setMinimumHeight(0)
        self.hlyPaginationContainer = self.findChild(QHBoxLayout, "hlyPaginationContainer")
        self.combEntriesNumber = self.findChild(QComboBox, "combEntriesNumber")
        self.combEntriesNumber.setCurrentIndex(0)

        self.leditSearchString = self.findChild(QLineEdit, "leditSearchString")
        self.zip_time = time.time()
        self.init_actions()
        self.lblStatus = self.findChild(QLabel, "lblStatus")

    def set_statusbar(self, status):
        self.lblStatus.setText(status)

    @pyqtSlot()
    def on_clicked_go_back(self):
        pass

    @pyqtSlot()
    def on_clicked_return_home(self):
        Common.remove_target_images()
        self.return_home_signal.emit("")

    @pyqtSlot(int)
    def changed_entries_number(self, current_index):
        self.number_per_page = int(self.combEntriesNumber.currentText())
        self.current_page = 0
        self.current_search_page = 0
        self.init_views()

    @pyqtSlot(str)
    def changed_search_string(self, search_string):
        if not search_string == '':
            self.search_string = search_string
            self.is_searching_result = True
            self.current_search_page = 0
            self.current_page = 0
        else:
            self.is_searching_result = False
        self.init_views()

    def init_actions(self):
        # self.btnGoBack.clicked.connect(self.on_clicked_go_back)
        self.btnReturnHome.clicked.connect(self.on_clicked_return_home)
        self.combEntriesNumber.currentIndexChanged.connect(self.changed_entries_number)
        self.leditSearchString.textChanged.connect(self.changed_search_string)
        self.btnExportAllZip.clicked.connect(self.on_clicked_export_allzip)
        self.get_reports_thread.finished_reports_signal.connect(
            lambda reports: self.finished_get_reports_slot(reports)
        )

    @pyqtSlot(list)
    def finished_get_reports_slot(self, reports):
        self.reports = reports
        self.init_views()
        self.set_enabled(True)
        self.stop_splash_signal.emit(None)

    def refresh_view(self):
        self.get_reports_thread.start()
        self.set_enabled(False)
        self.init_empty()  # set all members and search box as empty
        self.start_splash_signal.emit("data")

    def init_views(self):
        Common.clear_layout(self.hlyPaginationContainer)
        if self.is_searching_result:
            self.shown_reports = self.get_search_results(self.search_string, self.current_search_page,
                                                         self.number_per_page)
            # if the number of data is more than showing number per page, show pagination layout.
            searched_len = len(self.searched_reports)
            if searched_len > self.number_per_page:
                self.set_pagination(searched_len, self.current_search_page, self.number_per_page)
            self.init_table(self.shown_reports, self.current_search_page, self.number_per_page)
        else:
            report_len = len(self.reports)
            self.shown_reports = self.get_pagination_results(report_len, self.current_page, self.number_per_page)
            # if the number of data is more than showing number per page, show pagination layout.
            if report_len > self.number_per_page:
                self.set_pagination(report_len, self.current_page, self.number_per_page)
            self.init_table(self.shown_reports, self.current_page, self.number_per_page)

    # set pagination layout with the number of shown data on table.
    def set_pagination(self, data_len, current_page, number_per_page):
        if data_len:
            hly_pagination = PaginationLayout(data_len, number_per_page, current_page)
            # connect signals
            hly_pagination.changed_page_signal.connect(self.refresh_table)
            self.hlyPaginationContainer.addLayout(hly_pagination)

    def get_search_results(self, search_string, current_page, number_per_page):
        self.searched_reports.clear()
        paginated = []
        for item in self.reports:
            case_info = item.case_info
            probe_id = item.probe_id
            created_date = item.created_date
            if case_info.case_number.count(search_string) > 0 \
                    or case_info.case_PS.count(search_string) > 0 \
                    or case_info.examiner_no.count(search_string) > 0 \
                    or case_info.examiner_name.count(search_string) > 0 \
                    or case_info.remarks.count(search_string) > 0 \
                    or probe_id.count(search_string) > 0 \
                    or created_date.count(search_string) > 0:
                self.searched_reports.append(item)
        start_index = current_page * number_per_page
        end_index = start_index + number_per_page
        report_len = len(self.searched_reports)
        if self.searched_reports:
            if start_index > report_len:
                dif = start_index - report_len
                start_index -= dif
                end_index = report_len
            else:
                if end_index > report_len:
                    end_index = report_len
            paginated = self.searched_reports[start_index:end_index]
        return paginated

    def get_pagination_results(self, report_len, current_page, number_per_page):
        results = []
        start_index = current_page * number_per_page
        end_index = start_index + number_per_page
        if start_index > report_len:
            dif = start_index - report_len
            start_index -= dif
            end_index = report_len
        else:
            if end_index > report_len:
                end_index = report_len
        results = self.reports[start_index:end_index]
        return results

    def init_table(self, reports, current_page, number_per_page):
        row_index = 0
        vheader_label_index = current_page * number_per_page + 1
        vheader_labels = []
        # set table row and column num
        self.resultTable.setRowCount(len(reports))
        self.resultTable.verticalHeader().setDefaultAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        for report in reports:
            case_info = report.case_info
            formated_date = Common.convert_string2datetime(report.created_date, '%Y-%m-%d %H-%M-%S')
            datetime_item = QTableWidgetItem(formated_date)
            datetime_item.setSizeHint(QSize(50, 50))
            case_no = QTableWidgetItem(case_info.case_number)
            ps = QTableWidgetItem(case_info.case_PS)
            probe_id = QTableWidgetItem(report.probe_id)
            exam_no = QTableWidgetItem(case_info.examiner_no)
            exam_name = QTableWidgetItem(case_info.examiner_name)
            export_btn = ExportPdfButton(report)
            export_btn.export_pdf_signal.connect(self.export_pdf)
            self.resultTable.setItem(row_index, 0, datetime_item)
            self.resultTable.setItem(row_index, 1, case_no)
            self.resultTable.setItem(row_index, 2, ps)
            self.resultTable.setItem(row_index, 3, probe_id)
            self.resultTable.setItem(row_index, 4, exam_name)
            self.resultTable.setItem(row_index, 5, exam_no)
            self.resultTable.setCellWidget(row_index, 6, export_btn)
            vheader_labels.append(str(vheader_label_index))
            vheader_label_index += 1
            row_index += 1
        self.resultTable.setVerticalHeaderLabels(vheader_labels)

    @pyqtSlot(int)
    def refresh_table(self, page):
        if self.is_searching_result:
            self.current_search_page = page
        else:
            self.current_page = page
        self.init_views()

    @pyqtSlot(str)
    def getAvailableFileName(self, path):
        is_exist, able_file = Common.get_available_appendix_num(path, ".pdf")
        if is_exist:
            path = able_file        
        self.available_filename = path
        print(self.available_filename)

    @pyqtSlot(ProbingResult)
    def export_pdf(self, probe_result):
        is_exist, root_path = Common.check_exist_data_storage()
        if is_exist:
            exfilename = gen_pdf_filename(probe_result.probe_id, probe_result.case_info.case_number,
                                        probe_result.case_info.case_PS)
            filename = os.path.join(Common.EXPORT_PATH, exfilename)
            # is_exist, able_file = Common.get_available_appendix_num(filename, ".pdf")
            # if is_exist:
            #     filename = able_file
            fdialog = QFileDialog(self)
            fdialog.setAcceptMode(QFileDialog.AcceptSave)
            fdialog.setDirectory(Common.EXPORT_PATH)
            fdialog.setNameFilter(Common.PDF_FILTER)
            fdialog.selectFile(filename)
            # fdialog.currentChanged.connect(self.getAvailableFileName)
            fdialog.setOption(QFileDialog.DontConfirmOverwrite, True) 
            if fdialog.exec_():
                file_location = fdialog.selectedFiles()
                if file_location[0] == "":
                    return
                filename = file_location[0].replace(".pdf", "")
                is_exist, able_file = Common.get_available_appendix_num(filename, ".pdf")
                if is_exist:
                    filename = able_file
                dirs = file_location[0].split("/")
                file_path = file_location[0].replace(dirs[len(dirs) - 1], "")
                
                exported = export_report_pdf(file_path, exfilename, filename)
                if exported:
                    Common.show_message(QMessageBox.Information, "Report has been exported to PDF.", "Report Generation", "Notice",
                                        "")
                else:
                    Common.show_message(QMessageBox.Information, "Report was not exported to PDF.", "Report Generation",
                                        "Notice",
                                        "")
        else:
            Common.show_message(QMessageBox.Warning, "\"" + root_path + "\" folder does not exist."
                                                                        "\nPlease make it and then retry.",
                                "", "Folder Not Exist", "")

    @pyqtSlot()
    def on_clicked_export_allzip(self):
        is_exist, root_path = Common.check_exist_data_storage()
        if is_exist:
            zip_call_interval = time.time() - self.zip_time
            if zip_call_interval < 3:
                return

            report_path = Common.get_reg(Common.REG_KEY)
            if report_path:
                report_path = report_path + "/" + Common.REPORTS_PATH
            else:
                report_path = Common.STORAGE_PATH + "/" + Common.REPORTS_PATH
            Common.create_path(report_path)

            datestr = datetime.strftime(ntp_get_time_from_object(SysTimer.now()), "%d_%m_%Y")
            zip_file = "%s/probe_reports_%s" % (Common.EXPORT_PATH, datestr)
            # is_exist, able_zip_file = Common.get_available_appendix_num(zip_file, ".zip")
            # if is_exist:
            #     zip_file = able_zip_file
            fdialog = QFileDialog(self)
            fdialog.setAcceptMode(QFileDialog.AcceptSave)
            fdialog.setDirectory(Common.EXPORT_PATH)
            fdialog.setNameFilter(Common.ZIP_FILTER)
            fdialog.selectFile(zip_file)
            fdialog.setOption(QFileDialog.DontConfirmOverwrite, True) 
            if fdialog.exec_():
                zip_location = fdialog.selectedFiles()
                # zip_location = QFileDialog.getSaveFileName(self, "Save report zip file", zip_file, ".zip")
                self.zip_time = time.time()

                if zip_location[0] == '':
                    return
                zip_file = zip_location[0].replace(".zip", "")
                is_exist, able_zip_file = Common.get_available_appendix_num(zip_file, ".zip")
                if is_exist:
                    zip_file = able_zip_file
                self.zip_thread = ZipThread(self.reports, zip_file + ".zip")
                self.zip_thread.finished_zip_signal.connect(self.finished_zip_slot)
                self.zip_thread.start()
                self.set_enabled(False)  # set screen to be unable to operate
        else:
            Common.show_message(QMessageBox.Warning, "\"" + root_path + "\" folder does not exist."
                                                                        "\nPlease make it and then retry.",
                                "", "Folder Not Exist", "")

    @pyqtSlot(ThreadResult)
    def finished_zip_slot(self, res):
        self.zip_thread.quit()
        self.set_enabled(True)
        if res.status:
            Common.show_message(QMessageBox.Information, "PDF reports have been exported to ZIP.", "",
                                "Notice", "")
        else:
            Common.show_message(QMessageBox.Information,
                                "PDF reports have not been exported to ZIP. Because %s" % res.message,
                                "", "Notice", "")

    def set_enabled(self, enabled):
        # self.btnGoBack.setEnabled(enabled)
        self.btnReturnHome.setEnabled(enabled)
        self.btnExportAllZip.setEnabled(enabled)

    def init_empty(self):
        self.current_search_page = 0
        self.current_page = 0
        self.searched_reports.clear()
        self.reports.clear()
        self.shown_reports.clear()
        self.search_string = ''
        self.leditSearchString.setText("")
