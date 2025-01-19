import json
import os

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt
from PyQt5.QtWidgets import QPushButton, QLabel, QVBoxLayout, QGridLayout, QTextEdit, \
    QSizePolicy, QFileDialog, QWidget, QMessageBox, QFormLayout

from commons.growing_text_edit import GrowingTextEdit
from commons.common import Common
from commons.gen_report import export_report_pdf, gen_pdf_filename
from commons.probe_result_item_widget import ProbeResultItemWidget
from commons.probing_result import ProbingResult
from commons.target_items_container_generator import TargetItemsContainerGenerator


class LoaderProbeReportPage(QWidget):
    return_home_signal = pyqtSignal(str)
    go_back_signal = pyqtSignal(object, bool)  # bool is true, if go back
    export_pdf_signal = pyqtSignal(object)
    go_remaining_signal = pyqtSignal()
    start_splash_signal = pyqtSignal(str)
    stop_splash_signal = pyqtSignal(object)

    def __init__(self, parent=None):
        super(LoaderProbeReportPage, self).__init__(parent=parent)

        self.target_items_generator_thread = TargetItemsContainerGenerator()
        self.window = uic.loadUi("./forms/Page_6.ui", self)
        self.probe_result = ProbingResult()
        self.case_data_for_results = []
        self.btnGoBack = self.findChild(QPushButton, "btnGoBack")
        self.btnExportPdf = self.findChild(QPushButton, "btnExportPdf")
        self.btnReturnHome = self.findChild(QPushButton, "btnReturnHome")
        self.lblCaseNumber = self.findChild(QLabel, "lblCaseNumber")
        self.lblExaminerNo = self.findChild(QLabel, "lblExaminerNo")
        self.lblProbeId = self.findChild(QLabel, "lblProbeId")
        self.lblProbeResult = self.findChild(QLabel, "lblProbeResult")

        # self.lblPs = self.findChild(QTextEdit, "teditPS")
        # self.lblExaminerName = self.findChild(QTextEdit, "teditExaminerName")
        # self.teditRemarks = self.findChild(QTextEdit, "teditRemarks")

        self.lblTimeOfReportGeneration = self.findChild(QLabel, "lblTimeOfReportGeneration")
        self.lblSubjectImage = self.findChild(QLabel, "lblSubjectImage")
        self.lblMatchedDescription = self.findChild(QLabel, "lblMatchedDescription")

        self.flyCaseDetail = self.findChild(QFormLayout, "flyCaseDetail6")

        self.lblPs = GrowingTextEdit()
        self.lblPs.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.lblPs.setMinimumSize(Common.CASE_DETAIL_LINE_EDIT_WIDTH, Common.CASE_DETAIL_LINE_EDIT_HEIGHT)

        self.lblExaminerName = GrowingTextEdit()
        self.lblExaminerName.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.lblExaminerName.setMinimumSize(Common.CASE_DETAIL_LINE_EDIT_WIDTH, Common.CASE_DETAIL_LINE_EDIT_HEIGHT)

        self.teditRemarks = GrowingTextEdit()
        self.teditRemarks.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.teditRemarks.setMinimumSize(Common.CASE_DETAIL_LINE_EDIT_WIDTH, Common.CASE_DETAIL_LINE_EDIT_HEIGHT)

        self.lblPs.setStyleSheet(Common.GROWING_TEXT_EDIT_STYLE_PREVIEW_REPORT)
        self.lblExaminerName.setStyleSheet(Common.GROWING_TEXT_EDIT_STYLE_PREVIEW_REPORT)
        self.teditRemarks.setStyleSheet(Common.GROWING_TEXT_EDIT_STYLE_PREVIEW_REPORT)

        self.flyCaseDetail.setWidget(4, QFormLayout.FieldRole, self.lblPs)
        self.flyCaseDetail.setWidget(7, QFormLayout.FieldRole, self.lblExaminerName)
        self.flyCaseDetail.setWidget(8, QFormLayout.FieldRole, self.teditRemarks)

        # self.teditJsonResult = GrowingTextEdit()
        self.teditJsonResult = self.findChild(QTextEdit, "tedit_jsonRet")
        self.teditJsonResult.setObjectName("teditJsonResult")
        self.teditJsonResult.setStyleSheet(Common.JSON_RESULT_STYLE)
        self.teditJsonResult.setReadOnly(True)
        self.teditJsonResult.setAlignment(Qt.AlignHCenter)
        self.vlyJsonResp = self.findChild(QVBoxLayout, "vlyJsonResp")
        self.vlyJsonResp.addWidget(self.teditJsonResult)

        self.vlyReportResult = self.findChild(QVBoxLayout, "vlyTargetResults")
        self.glyReportBuff = QGridLayout()

        self.init_actions()
        self.lblStatus = self.findChild(QLabel, "lblStatus")

    def set_statusbar(self, status):
        self.lblStatus.setText(status)

    @pyqtSlot()
    def on_clicked_export_pdf(self):
        if self.probe_result.probe_id == '':
            Common.show_message(QMessageBox.Warning, "The data for generating report is empty. You will go home.",
                                "", "Empty Data", "")
            self.return_home_signal.emit("")
        else:
            is_exist, root_path = Common.check_exist_data_storage()
            if is_exist:
                exfilename = gen_pdf_filename(self.probe_result.probe_id, self.probe_result.case_info.case_number, self.probe_result.case_info.case_PS)
                filename = os.path.join(Common.EXPORT_PATH, exfilename)
                # is_exist, able_file = Common.get_available_appendix_num(filename, ".pdf")
                # if is_exist:
                #     filename = able_file
                fdialog = QFileDialog(self)
                fdialog.setAcceptMode(QFileDialog.AcceptSave)
                fdialog.setDirectory(Common.EXPORT_PATH)        
                fdialog.setNameFilter(Common.PDF_FILTER)
                fdialog.selectFile(filename)
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
                        Common.show_message(QMessageBox.Information, "Report has been exported to PDF.", "Report Generation", "Notice", "")
                        self.probe_result = ProbingResult()
                        self.refresh_views()
                        self.init_input_values()
                        self.return_home_signal.emit("")  # return to home page so that can start new case.
                        # self.export_pdf_signal.emit(self.probe_result)
                    else:
                        Common.show_message(QMessageBox.Information, "Report was not exported to PDF.", "Report Generation", "Notice",
                                            "")
            else:
                Common.show_message(QMessageBox.Warning, "\"" + root_path + "\" folder does not exist."
                                                                            "\nPlease make it and then retry.",
                                    "", "Folder Not Exist", "")

    @pyqtSlot()
    def on_clicked_return_home(self):
        Common.remove_target_images()
        self.return_home_signal.emit("")

    @pyqtSlot()
    def on_clicked_go_back(self):
        # self.probe_result = ProbingResult()
        self.go_back_signal.emit(self.probe_result, True)

    def init_actions(self):
        self.btnExportPdf.clicked.connect(self.on_clicked_export_pdf)
        self.btnGoBack.clicked.connect(self.on_clicked_go_back)
        self.btnReturnHome.clicked.connect(self.on_clicked_return_home)
        self.target_items_generator_thread.finished_refreshing_target_items.connect(
            lambda case_data: self.finished_refresh_target_items_slot(case_data))

    @pyqtSlot(list)
    def finished_refresh_target_items_slot(self, case_data):
        results = self.probe_result.json_result['results']
        faces = self.probe_result.json_result['faces']
        index = 0
        if len(results) > 0 and len(self.case_data_for_results):
            for result in results:
                # if float(result['confidence'][:len(result['confidence']) - 1]) < Common.MATCH_LEVEL:
                #     continue
                face = faces[index]
                case_info = self.case_data_for_results[index]
                # set unable the cross button on image
                result_view_item = ProbeResultItemWidget(result, face, False, self.probe_result.case_info.is_used_old_cases,
                                                         case_info)
                self.glyReportBuff.addWidget(result_view_item, index // 3, index % 3)
                index += 1
        wdtContainer = QWidget()  # container for bordering.
        wdtContainer.setLayout(self.glyReportBuff)
        wdtContainer.setStyleSheet(Common.TARGET_LIST_STYLE)
        self.vlyReportResult.addWidget(wdtContainer)
        # js_result = json.dumps(self.probe_result.json_result, indent=4, sort_keys=True)
        self.teditJsonResult.setPlainText(Common.convert_json_for_page(self.probe_result))
        self.init_input_values()
        self.set_enabled(True)
        self.stop_splash_signal.emit(None)

    def refresh_views(self):
        # self.init_input_values()
        self.init_target_images_view()

    def init_input_values(self):
        if not self.probe_result:
            return
        if not Common.is_empty(self.probe_result.case_info):
            self.lblProbeId.setText(self.probe_result.probe_id)
            matched = self.probe_result.is_matched()
            target_type = self.probe_result.case_info.target_type
            if matched == 'Matched':
                if target_type == 1:
                    self.lblMatchedDescription.setText(Common.REPORT_DESCRIPTION_MATCHED_FOR_SINGLE)
                elif target_type == 2:
                    self.lblMatchedDescription.setText(Common.REPORT_DESCRIPTION_MATCHED_FOR_MULTIPLE)
                elif target_type == 3:
                    self.lblMatchedDescription.setText(Common.REPORT_DESCRIPTION_MATCHED_FOR_ENTIRE)
                elif target_type == 4:
                    self.lblMatchedDescription.setText(Common.REPORT_DESCRIPTION_MATCHED_FOR_OLDCASE)
            else:
                self.lblMatchedDescription.setText(Common.REPORT_DESCRIPTION_NON_MATCHED)
            self.lblProbeResult.setText(matched)
            self.lblCaseNumber.setText(self.probe_result.case_info.case_number)
            self.lblPs.setText(self.probe_result.case_info.case_PS)
            self.lblExaminerNo.setText(self.probe_result.case_info.examiner_no)
            self.lblExaminerName.setText(self.probe_result.case_info.examiner_name)
            self.teditRemarks.setText(self.probe_result.case_info.remarks)
            self.lblTimeOfReportGeneration.setText(str(self.probe_result.json_result['time_used']))
            image_style = "image:url('" + self.probe_result.case_info.subject_image_url + \
                          "');background:transparent;border: 1px solid rgb(53, 132, 228);"
            # image_style = "background:transparent;border: 1px solid rgb(53, 132, 228);"
            self.lblSubjectImage.setStyleSheet(image_style)
            self.lblSubjectImage.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            # js_result = json.dumps(self.probe_result.json_result, indent=4, sort_keys=True)
            self.teditJsonResult.setPlainText(Common.convert_json_for_page(self.probe_result))
        else:
            self.lblProbeId.setText("")
            self.lblMatchedDescription.setText("The subject photo hasn't matched to any target photo.")
            self.lblProbeResult.setText("")
            self.lblCaseNumber.setText("")
            self.lblPs.setText("")
            self.lblExaminerNo.setText("")
            self.lblExaminerName.setText("")
            self.teditRemarks.setText("")
            self.lblTimeOfReportGeneration.setText("")
            image_style = "image:url('" + self.probe_result.case_info.subject_image_url + \
                          "');background:transparent;border: 1px solid rgb(53, 132, 228);"
            self.lblSubjectImage.setStyleSheet(image_style)
            self.lblSubjectImage.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.teditJsonResult.setPlainText("")

    def init_target_images_view(self):
        # clear all child on result container layout
        self.clear_result_list()
        # add items to result container layout
        self.glyReportBuff = QGridLayout(self)
        if not self.probe_result:
            return
        if not Common.is_empty(self.probe_result.case_info):
            self.set_enabled(False)
            self.start_splash_signal.emit("data")
            self.target_items_generator_thread.start()

    def clear_result_list(self):
        Common.clear_layout(self.vlyReportResult)

    def init_views(self):
        self.lblProbeId.setText("")
        self.lblMatchedDescription.setText(Common.REPORT_DESCRIPTION_NON_MATCHED)
        self.lblProbeResult.setText("")
        self.lblCaseNumber.setText("")
        self.lblPs.setText("")
        self.lblExaminerNo.setText("")
        self.lblExaminerName.setText("")
        self.teditRemarks.setText("")
        self.lblTimeOfReportGeneration.setText("")
        resized_image_path, resized = Common.resize_image(self.probe_result.case_info.subject_image_url,
                                                 self.lblSubjectImage.size().width())
        self.probe_result.case_info.subject_image_url = resized_image_path
        image_style = "image:url('" + resized_image_path + \
                      "');background:transparent;border: 1px solid rgb(53, 132, 228);"
        self.lblSubjectImage.setStyleSheet(image_style)
        self.lblSubjectImage.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.clear_result_list()
        self.probe_result = ProbingResult()

    def set_enabled(self, enabled):
        self.btnGoBack.setEnabled(enabled)
        self.btnReturnHome.setEnabled(enabled)
        self.btnExportPdf.setEnabled(enabled)
