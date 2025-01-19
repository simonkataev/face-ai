import json

from PyQt5 import uic, QtGui
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QPushButton, QLabel, QLineEdit, QVBoxLayout, QGridLayout, \
    QSizePolicy, QTextEdit, QWidget, QMessageBox, QHBoxLayout, QFormLayout

from commons.growing_text_edit import GrowingTextEdit
from commons.common import Common
from commons.db_connection import DBConnection
from commons.gen_report_thread import GenReportThread
from commons.probe_result_item_widget import ProbeResultItemWidget
from commons.probing_result import ProbingResult
from commons.target_items_container_generator import TargetItemsContainerGenerator


class LoaderProbeReportPreviewPage(QWidget):
    return_home_signal = pyqtSignal(str)
    go_back_signal = pyqtSignal(object)
    generate_report_signal = pyqtSignal(object, object)
    go_remaining_signal = pyqtSignal()
    start_splash_signal = pyqtSignal(str)
    stop_splash_signal = pyqtSignal(object)
    show_window_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(LoaderProbeReportPreviewPage, self).__init__(parent=parent)
        self.target_items_generator_thread = TargetItemsContainerGenerator()
        self.case_data_for_results = []
        self.probe_result = ProbingResult()
        self.generate_report_thread = GenReportThread()
        self.window = uic.loadUi("./forms/Page_5.ui", self)
        self.btnGoBack = self.findChild(QPushButton, "btnGoBack")
        self.btnGoRemaining = self.findChild(QPushButton, "btnGoRemaining")
        self.btnGenerateReport = self.findChild(QPushButton, "btnGenerateReport")
        self.btnReturnHome = self.findChild(QPushButton, "btnReturnHome")
        self.lblCaseNumber = self.findChild(QLabel, "lblCaseNumber")
        # self.lblPs = self.findChild(QTextEdit, "teditPS")
        self.lblExaminerNo = self.findChild(QLabel, "lblExaminerNo")
        # self.lblExaminerName = self.findChild(QTextEdit, "teditExaminerName")
        self.lblProbeId = self.findChild(QLabel, "lblProbeId")
        self.lblProbeResult = self.findChild(QLabel, "lblProbeResult")
        # self.teditRemarks = self.findChild(QTextEdit, "teditRemarks")
        self.lblTimeOfReportGeneration = self.findChild(QLabel, "lblTimeOfReportGeneration")

        self.flyCaseDetail = self.findChild(QFormLayout, "flyCaseDetail5")
        self.lblPs = GrowingTextEdit()
        self.lblPs.setReadOnly(True)
        self.lblPs.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.lblPs.setMinimumSize(Common.CASE_DETAIL_LINE_EDIT_WIDTH, Common.CASE_DETAIL_LINE_EDIT_HEIGHT)
        self.lblPs.setMaximumSize(Common.CASE_DETAIL_LINE_EDIT_WIDTH, Common.CASE_DETAIL_LINE_EDIT_HEIGHT)

        self.lblExaminerName = GrowingTextEdit()
        self.lblExaminerName.setReadOnly(True)
        self.lblExaminerName.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.lblExaminerName.setMinimumSize(Common.CASE_DETAIL_LINE_EDIT_WIDTH, Common.CASE_DETAIL_LINE_EDIT_HEIGHT)
        self.lblExaminerName.setMaximumSize(Common.CASE_DETAIL_LINE_EDIT_WIDTH, Common.CASE_DETAIL_LINE_EDIT_HEIGHT)

        self.teditRemarks = GrowingTextEdit()
        self.teditRemarks.setReadOnly(True)
        self.teditRemarks.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.teditRemarks.setMinimumSize(Common.CASE_DETAIL_LINE_EDIT_WIDTH, Common.CASE_DETAIL_LINE_EDIT_HEIGHT)
        self.teditRemarks.setMaximumSize(Common.CASE_DETAIL_LINE_EDIT_WIDTH, Common.CASE_DETAIL_LINE_EDIT_HEIGHT)

        self.lblPs.setStyleSheet(Common.GROWING_TEXT_EDIT_STYLE_PREVIEW_REPORT)
        self.lblExaminerName.setStyleSheet(Common.GROWING_TEXT_EDIT_STYLE_PREVIEW_REPORT)
        self.teditRemarks.setStyleSheet(Common.GROWING_TEXT_EDIT_STYLE_PREVIEW_REPORT)

        self.flyCaseDetail.setWidget(4, QFormLayout.FieldRole, self.lblPs)
        self.flyCaseDetail.setWidget(7, QFormLayout.FieldRole, self.lblExaminerName)
        self.flyCaseDetail.setWidget(8, QFormLayout.FieldRole, self.teditRemarks)

        self.lbeSubjectImage = self.findChild(QLabel, "lblSubjectImage")
        self.leditRemainingPhotoNumber = self.findChild(QLineEdit, "leditRemainingPhotoNumber")
        self.lblSubjectImage = self.findChild(QLabel, "lblSubjectImage")
        self.lblMatchedDescription = self.findChild(QLabel, "lblMatchedDescription")
        self.wdtProbingResult = self.findChild(QWidget, "wdtProbingResult")
        # self.etextJsonResult = self.findChild(QTextEdit, "teditJsonResult")

        self.vlyJsonResult = self.findChild(QVBoxLayout, "JsonResp_layout")
        # self.etextJsonResult = GrowingTextEdit()
        self.etextJsonResult = self.findChild(QTextEdit, "tedit_jsonRet")
        self.etextJsonResult.setStyleSheet(Common.JSON_RESULT_STYLE)
        self.etextJsonResult.setObjectName("teditJsonResult")
        self.etextJsonResult.setReadOnly(True)
        self.etextJsonResult.setAlignment(Qt.AlignHCenter)
        self.vlyJsonResult.addWidget(self.etextJsonResult)

        self.vlyReportResultLayout = self.findChild(QVBoxLayout, "vlyTargetResults")
        self.glyReportBuff = QGridLayout()
        self.vlyGoRemaining = self.findChild(QHBoxLayout, "hlyGoRemaining")
        self.init_actions()
        # self.init_input_values()
        # self.init_result_views()
        self.set_validate_input_data()
        self.lblStatus = self.findChild(QLabel, "lblStatus")

    def set_statusbar(self, status):
        self.lblStatus.setText(status)

    @pyqtSlot(ProbingResult)
    def finished_generate_report_slot(self, probe_result):
        self.probe_result = probe_result
        self.generate_report_signal.emit(self.probe_result, self.case_data_for_results)
        self.stop_splash_signal.emit(None)
        self.set_enabled(True)

    @pyqtSlot()
    def on_clicked_generate_report(self):
        if self.probe_result.probe_id == '':
            Common.show_message(QMessageBox.Warning, "The data for generating report is empty. You will go home.",
                                "", "Empty Data", "")
            self.return_home_signal.emit("")
        else:
            # check "Data Storage" folder exist. if not stop to run.
            is_exist, root_path = Common.check_exist_data_storage()
            if is_exist:
                self.start_splash_signal.emit("data")
                self.generate_report_thread.probe_result = self.probe_result
                self.set_enabled(False)
                self.generate_report_thread.start()
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
        case_info = self.probe_result.case_info
        self.init_views()
        # self.probe_result = ProbingResult()
        self.go_back_signal.emit(case_info)

    @pyqtSlot()
    def on_clicked_go_remaining(self):
        if self.leditRemainingPhotoNumber.text() == '':
            return
        remaining_number = int(self.leditRemainingPhotoNumber.text())
        self.leditRemainingPhotoNumber.setText("")
        if len(self.probe_result.json_result['results']) <= remaining_number:
            return
        if remaining_number > 0:
            self.set_enabled(False)
            self.start_splash_signal.emit("data")
            # remove some items from json results except remaining number
            result_images = \
                Common.remove_elements_from_list_tail(self.probe_result.json_result['results'], remaining_number)
            self.probe_result.json_result['results'].clear()
            self.probe_result.json_result['results'] = result_images
            result_faces = \
                Common.remove_elements_from_list_tail(self.probe_result.json_result['faces'], remaining_number)
            self.probe_result.json_result['faces'].clear()
            self.probe_result.json_result['faces'] = result_faces
            self.leditRemainingPhotoNumber.setText("")
            # repaint view
            # self.refresh_views()
            self.refresh_target_view()

    # set validator to input box
    def set_validate_input_data(self):
        remaining_number_validator = QIntValidator(self.leditRemainingPhotoNumber)
        self.leditRemainingPhotoNumber.setValidator(remaining_number_validator)

    def init_actions(self):
        self.btnGenerateReport.clicked.connect(self.on_clicked_generate_report)
        self.btnGoBack.clicked.connect(self.on_clicked_go_back)
        self.btnReturnHome.clicked.connect(self.on_clicked_return_home)
        self.btnGoRemaining.clicked.connect(self.on_clicked_go_remaining)
        self.target_items_generator_thread.finished_refreshing_target_items.connect(
            self.finished_refresh_target_widget_slot)
        self.generate_report_thread.finished_generate_report_signal.connect(self.finished_generate_report_slot)

    def refresh_views(self):
        # self.init_input_values()
        self.start_splash_signal.emit("data")
        self.set_enabled(False)
        self.init_target_images_view()
        # self.repaint()

    @pyqtSlot(list)
    def finished_refresh_target_widget_slot(self, case_data):
        self.glyReportBuff = QGridLayout(self)
        case_data_buff = []
        metadata_buff = []
        processing_buff = []
        results = self.probe_result.json_result['results']
        faces = self.probe_result.json_result['faces']

        index = 0
        
        if len(results) > 0 and len(case_data):
            results_ = results.copy()
            for result in results_:
                confidence = float(result['confidence'][:len(result['confidence']) - 2])
                if confidence < Common.MATCH_LEVEL:
                    self.probe_result.remove_json_item(result)
                    case_data_buff.append(case_data[index])
                    metadata_buff.append(self.probe_result.case_info.target_images_metadata[index])
                    processing_buff.append(self.probe_result.case_info.target_images_processing_details[index])
                index += 1

        # if there are cases that match level is lower than 70,
        # those will be removed from case data
        if len(case_data_buff) > 0:
            for case_buff in case_data_buff:
                case_data.remove(case_buff)
            for meta in metadata_buff:
                self.probe_result.case_info.target_images_metadata.remove(meta)
            for proc in processing_buff:
                self.probe_result.case_info.target_images_processing_details.remove(proc)
        index = 0
        self.case_data_for_results = case_data
        results = self.probe_result.json_result['results']
        faces = self.probe_result.json_result['faces']
        if len(results) > 0 and len(case_data):
            self.wdtProbingResult.show()
            for result in results:
                case_information = case_data[index]
                face = faces[index]
                # show the cross button on image
                result_view_item = ProbeResultItemWidget(result, face, True,
                                                         self.probe_result.case_info.is_used_old_cases,
                                                         case_information)
                # connect delete signal from delete button on target image.
                result_view_item.delete_item_signal.connect(self.delete_result_item)
                self.glyReportBuff.addWidget(result_view_item, index // 3, index % 3)

                index += 1
            wdtContainer = QWidget()  # container for bordering.
            wdtContainer.setLayout(self.glyReportBuff)
            wdtContainer.setStyleSheet(Common.TARGET_LIST_STYLE)
            self.vlyReportResultLayout.addWidget(wdtContainer)
            # js_result = json.dumps(self.probe_result.json_result, indent=4, sort_keys=True)
            self.etextJsonResult.setPlainText(Common.convert_json_for_page(self.probe_result))
        else:
            self.wdtProbingResult.hide()

        self.init_input_values()
        self.set_enabled(True)
        self.stop_splash_signal.emit(None)

    def init_input_values(self):
        if not self.probe_result:
            return
        if not Common.is_empty(self.probe_result.case_info):
            probe_id = Common.generate_probe_id()
            # check whether probe id exist on database
            db = DBConnection()
            while db.is_exist_value("cases", "probe_id", probe_id):
                probe_id = Common.generate_probe_id()
            self.probe_result.probe_id = probe_id
            # if self.probe_result.probe_id == '':
            #     probe_id = Common.generate_probe_id()
            #     # check whether probe id exist on database
            #     db = DBConnection()
            #     while db.is_exist_value("cases", "probe_id", probe_id):
            #         probe_id = Common.generate_probe_id()
            #     self.probe_result.probe_id = probe_id
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
            # image_style = "background:transparent;border: 1px solid rgb(53, 132, 228);"
            resized_image_path, resized = Common.resize_image(self.probe_result.case_info.subject_image_url,
                                                     self.lbeSubjectImage.size().width())
            self.probe_result.case_info.subject_image_url = resized_image_path
            image_style = "image:url('" + resized_image_path + \
                          "');background:transparent;border: 1px solid rgb(53, 132, 228);"
            self.lblSubjectImage.setStyleSheet(image_style)
            self.lblSubjectImage.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            # lbl_x, lbl_y, pixmap = Common.make_pixmap_from_image(self.probe_result.case_info.subject_image_url, self.lblSubjectImage)
            # self.lblSubjectImage.setPixmap(pixmap)
        else:
            self.lblProbeId.setText("")
            self.lblMatchedDescription.setText("")
            self.lblProbeResult.setText("")
            self.lblCaseNumber.setText("")
            self.lblPs.setText("")
            self.lblExaminerNo.setText("")
            self.lblExaminerName.setText("")
            self.teditRemarks.setText("")
            self.lblTimeOfReportGeneration.setText("")
            image_style = "background:transparent;border: 1px solid rgb(53, 132, 228);"
            self.lblSubjectImage.setStyleSheet(image_style)
            self.lblSubjectImage.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.etextJsonResult.setPlainText("")
            self.leditRemainingPhotoNumber.setText("")

    def init_target_images_view(self):
        # clear all child on result container layout
        self.clear_result_list()
        self.etextJsonResult.setPlainText("")
        if not self.probe_result:
            self.set_enabled(True)
            self.stop_splash_signal.emit(None)
            return
        if not Common.is_empty(self.probe_result.case_info):
            results = self.probe_result.json_result['results']

            self.target_items_generator_thread.set_data(self, results, True,
                                                        self.probe_result.case_info.is_used_old_cases)
            self.target_items_generator_thread.start()
        else:
            self.set_enabled(True)
            self.stop_splash_signal.emit(None)

    @pyqtSlot(object)
    def delete_result_item(self, item):
        self.start_splash_signal.emit("data")
        self.set_enabled(False)
        json_result = self.probe_result.json_result['results']
        if not len(json_result) > 1:
            self.set_enabled(True)
            self.stop_splash_signal.emit(None)
            return
        self.probe_result.remove_json_item(item)
        # self.init_target_images_view()
        self.refresh_target_view()

    def refresh_target_view(self):
        # clear all child on result container layout
        self.clear_result_list()
        self.etextJsonResult.setPlainText("")

        self.glyReportBuff = QGridLayout(self)
        results = self.probe_result.json_result['results']
        faces = self.probe_result.json_result['faces']
        case_data = self.case_data_for_results
        index = 0
        if len(results) > 0 and len(case_data):
            self.wdtProbingResult.show()
            for result in results:
                case_information = case_data[index]
                face = faces[index]
                # show the cross button on image
                result_view_item = ProbeResultItemWidget(result, face, True,
                                                         self.probe_result.case_info.is_used_old_cases,
                                                         case_information)
                # connect delete signal from delete button on target image.
                result_view_item.delete_item_signal.connect(self.delete_result_item)
                self.glyReportBuff.addWidget(result_view_item, index // 3, index % 3)
                index += 1
            wdtContainer = QWidget()  # container for bordering.
            wdtContainer.setLayout(self.glyReportBuff)
            wdtContainer.setStyleSheet(Common.TARGET_LIST_STYLE)
            self.vlyReportResultLayout.addWidget(wdtContainer)
            # js_result = json.dumps(self.probe_result.json_result, indent=4, sort_keys=True)
            self.etextJsonResult.setPlainText(Common.convert_json_for_page(self.probe_result.json_result))
        else:
            self.wdtProbingResult.hide()
        self.set_enabled(True)
        self.stop_splash_signal.emit(None)

    def clear_result_list(self):
        Common.clear_layout(self.vlyReportResultLayout)

    def showEvent(self, a0: QtGui.QShowEvent) -> None:
        super().showEvent(a0)
        self.show_window_signal.emit()

    def init_views(self):
        self.lblProbeId.setText("")
        self.lblMatchedDescription.setText("")
        self.lblProbeResult.setText("")
        self.lblCaseNumber.setText("")
        self.lblPs.setText("")
        self.lblExaminerNo.setText("")
        self.lblExaminerName.setText("")
        self.teditRemarks.setText("")
        self.lblTimeOfReportGeneration.setText("")
        image_style = "image:url('');background:transparent;border: 1px solid rgb(53, 132, 228);"
        self.lblSubjectImage.setStyleSheet(image_style)
        self.lblSubjectImage.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.etextJsonResult.setPlainText("")
        self.leditRemainingPhotoNumber.setText("")
        self.clear_result_list()
        self.probe_result = ProbingResult()
        self.wdtProbingResult.hide()

    def set_enabled(self, enabled):
        self.btnGoBack.setEnabled(enabled)
        self.btnReturnHome.setEnabled(enabled)
        self.btnGenerateReport.setEnabled(enabled)
        self.btnGoRemaining.setEnabled(enabled)

