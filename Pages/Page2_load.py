import re

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QTextCursor, QShowEvent
from PyQt5.QtWidgets import QFileDialog, QFormLayout, QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QMessageBox, QSizePolicy, QWidget, QTextEdit
from PyQt5.QtWidgets import QPushButton

from commons.get_image_metadata import GetImageMetadata
from commons.growing_text_edit import GrowingTextEdit
from commons.case_info import CaseInfo
from commons.common import Common
from commons.metadata_detail import MetadataDetail
from commons.processing_detail import ProcessingDetail
from insightfaces.main import FaceAI


class LoaderCreateNewCasePage(QWidget):
    # when clicked 'return home' button, this will be emitted
    return_home_signal = pyqtSignal(str)
    # when clicked 'continue to probe' button, this will be emitted
    continue_probe_signal = pyqtSignal(object)

    def __init__(self, faceai, parent=None):
        super(LoaderCreateNewCasePage, self).__init__(parent)
        self.get_image_metadata = GetImageMetadata()
        self.image_metadata = MetadataDetail()
        self.processing_detail = ProcessingDetail()
        self.faceai = faceai
        self.window = uic.loadUi("./forms/Page_2.ui", self)
        # instance CaseInfo to save the case information
        self.case_info = CaseInfo()
        self.current_work_folder = ""
        # set button and line edit
        self.btnSelectPhoto = self.findChild(QPushButton, 'btnSelectTargetPhoto')
        self.btnReturnHome = self.findChild(QPushButton, 'btnReturnHome')
        self.btnContinueProbe = self.findChild(QPushButton, 'btnContinueProbe')
        self.btnGoBack = self.findChild(QPushButton, 'btnGoBack')
        self.leditCaseNumber = self.findChild(QLineEdit, 'leditCaseNumber')
        self.leditExaminerNo = self.findChild(QLineEdit, 'leditExaminerNo')

        self.flyCaseDetail = self.findChild(QFormLayout, "flyCaseDetail")
        # self.leditPS = self.findChild(QLineEdit, 'leditPS')
        self.leditPS = GrowingTextEdit()
        self.leditPS.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.leditPS.setMinimumSize(Common.CASE_DETAIL_LINE_EDIT_WIDTH, Common.CASE_DETAIL_LINE_EDIT_HEIGHT)
        self.leditPS.setMaximumSize(Common.CASE_DETAIL_LINE_EDIT_WIDTH, Common.CASE_DETAIL_LINE_EDIT_HEIGHT)

        # self.leditExaminerName = self.findChild(QLineEdit, 'leditExaminerName')
        self.leditExaminerName = GrowingTextEdit()
        self.leditExaminerName.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.leditExaminerName.setMinimumSize(Common.CASE_DETAIL_LINE_EDIT_WIDTH, Common.CASE_DETAIL_LINE_EDIT_HEIGHT)
        # self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # self.setMinimumSize(Common.CASE_DETAIL_LINE_EDIT_WIDTH, Common.CASE_DETAIL_LINE_EDIT_HEIGHT)
        self.leditExaminerName.setMaximumSize(Common.CASE_DETAIL_LINE_EDIT_WIDTH, Common.CASE_DETAIL_LINE_EDIT_HEIGHT)

        self.leditRemarks = GrowingTextEdit()
        self.leditRemarks.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.leditRemarks.setMinimumSize(Common.CASE_DETAIL_LINE_EDIT_WIDTH, Common.CASE_DETAIL_LINE_EDIT_HEIGHT)
        self.leditRemarks.setMaximumSize(Common.CASE_DETAIL_LINE_EDIT_WIDTH, Common.CASE_DETAIL_LINE_EDIT_HEIGHT)
        # self.leditRemarks = self.findChild(QTextEdit, 'teditRemarks')
        self.leditPS.setStyleSheet(Common.GROWING_TEXT_EDIT_STYLE_CREATE_CASE)
        self.leditExaminerName.setStyleSheet(Common.GROWING_TEXT_EDIT_STYLE_CREATE_CASE)
        self.leditRemarks.setStyleSheet(Common.GROWING_TEXT_EDIT_STYLE_CREATE_CASE)
        self.leditPS.setAlignment(Qt.AlignVCenter)

        self.flyCaseDetail.setWidget(1, QFormLayout.FieldRole, self.leditPS)
        self.flyCaseDetail.setWidget(2, QFormLayout.FieldRole, self.leditExaminerName)
        self.flyCaseDetail.setWidget(4, QFormLayout.FieldRole, self.leditRemarks)

        self.setTabOrder(self.leditCaseNumber, self.leditPS)
        self.setTabOrder(self.leditPS, self.leditExaminerName)
        self.setTabOrder(self.leditExaminerName, self.leditExaminerNo)
        self.setTabOrder(self.leditExaminerNo, self.leditRemarks)
        # set image url
        self.subject_photo_url = ''
        self.set_event_actions()
        self.set_regxs()
        self.lblStatus = self.findChild(QLabel, "lblStatus")

    def set_statusbar(self, status):
        self.lblStatus.setText(status)

    # set slots to each widget
    def set_event_actions(self):
        self.btnSelectPhoto.clicked.connect(self.get_subject_photo)
        self.btnReturnHome.clicked.connect(self.return_home)
        self.btnContinueProbe.clicked.connect(self.continue_probe_slot)
        self.btnGoBack.clicked.connect(self.return_home)

    # set regular expression for checking input data
    def set_regxs(self):
        self.set_regx_line_edit(self.leditCaseNumber, Common.CREATE_CASE_REGX_FOR_REMOVE, Common.CASE_NUMBER_LENGTH)
        self.set_regx_plain_text_edit(self.leditPS, Common.CREATE_CASE_REGX_FOR_REMOVE, Common.CASE_PS_LENGTH)
        self.set_regx_plain_text_edit(self.leditExaminerName, Common.CREATE_CASE_REGX_FOR_REMOVE, Common.CASE_EXAMINER_NAME_LENGTH)
        self.set_regx_line_edit(self.leditExaminerNo, Common.CREATE_CASE_REGX_FOR_REMOVE, Common.CASE_EXAMINER_NO_LENGTH)
        self.set_regx_plain_text_edit(self.leditRemarks, Common.CREATE_CASE_REGX_FOR_REMOVE, Common.CASE_REMARKS_LENGTH)

    # set regular expression for checking on line edit
    def set_regx_line_edit(self, line_edit, regx, length):
        line_edit.textChanged[str].connect(
            lambda txt: self.check_ledit_string_validation(line_edit, regx, txt, length))

    def set_regx_plain_text_edit(self, text_edit, regx, length):
        # text_edit.cursorPositionChanged.connect(lambda: self.check_ptedit_value_validation(text_edit, regx, length))
        text_edit.textChanged.connect(
            lambda: self.check_ptedit_string_validation(text_edit, regx, length))

    @pyqtSlot()
    # get subject photo from file dialog and set the gotten photo on button
    def get_subject_photo(self):
        photo_url, _ = QFileDialog.getOpenFileName(self, 'Open file', self.current_work_folder, Common.IMAGE_FILTER)
        if photo_url:
            self.current_work_folder = Common.get_folder_path(photo_url)
            self.image_metadata = self.get_image_metadata.get_metadata(photo_url)
            if Common.get_file_extension_from_path(photo_url) == ".heic":
                photo_url = Common.reformat_image(photo_url)
                self.processing_detail.reformatted = True
            if self.faceai.is_face(photo_url) == 0:
                Common.show_message(QMessageBox.Warning, "Please select an image with man", "",
                                    "Incorrect image selected.",
                                    "")
                self.subject_photo_url = ""
                self.get_subject_photo()
            elif self.faceai.is_face(photo_url) == 2:
                Common.show_message(QMessageBox.Warning, "Subject photo must be a single photo", "",
                                    "Incorrect image selected.",
                                    "")
                self.subject_photo_url = ""
                self.get_subject_photo()
            else:
                # check the "data storage" folder exist.
                is_exist, root_path = Common.check_exist_data_storage()
                if is_exist:
                    resized_image_path, self.processing_detail.resized = Common.resize_image(photo_url, self.btnSelectPhoto.size().width())
                    self.subject_photo_url = resized_image_path
                    btn_style = "image:url('" + resized_image_path + "');background:transparent;" \
                                 "border: 1px solid rgb(53, 132, 228);"
                    self.btnSelectPhoto.setStyleSheet(btn_style)
                    self.btnSelectPhoto.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
                else:
                    Common.show_message(QMessageBox.Warning, "\"" + root_path + "\" folder does not exist."
                                                             "\nPlease make it and then retry.",
                                        "", "Folder Not Exist", "")
        else:
            self.subject_photo_url = ""
            btn_style = "border:none;background:transparent;" \
                        "image:url(:/newPrefix/Group 68.png);border-radius: 30px;background:none;"
            self.btnSelectPhoto.setStyleSheet(btn_style)

    @pyqtSlot()
    def return_home(self):
        self.return_home_signal.emit("")

    @pyqtSlot()
    def continue_probe_slot(self):
        is_empty, ledit_name = self.is_empty_input_values()
        if is_empty == True:
            Common.show_message(QMessageBox.Warning, "Please fill all fields", "", "Empty Warning",
                                ledit_name + " is empty")
        else:
            self.case_info.case_number = self.leditCaseNumber.text()
            self.case_info.case_PS = self.leditPS.toPlainText()
            self.case_info.examiner_no = self.leditExaminerNo.text()
            self.case_info.examiner_name = self.leditExaminerName.toPlainText()
            self.case_info.remarks = self.leditRemarks.toPlainText()
            self.case_info.subject_image_url = self.subject_photo_url
            self.case_info.subject_image_processing_detail = self.processing_detail
            self.case_info.subject_image_metadata = self.image_metadata
            # emit continue probe signal
            self.continue_probe_signal.emit(self.case_info)

    # check whether all input value is empty or not
    # even if one value is empty, return False
    def is_empty_input_values(self):
        if self.leditCaseNumber.text() == '':
            self.leditCaseNumber.setFocus()
            return True, 'Case Number'
        if self.leditPS.toPlainText() == '':
            self.leditPS.setFocus()
            return True, 'PS'
        if self.leditExaminerNo.text() == '':
            self.leditExaminerNo.setFocus()
            return True, "Examiner's NO"
        if self.leditExaminerName.toPlainText() == '':
            self.leditExaminerName.setFocus()
            return True, "Examiner's Name"
        if self.leditRemarks.toPlainText() == '':
            self.leditRemarks.setFocus()
            return True, "Remarks"
        if self.subject_photo_url == '':
            self.btnSelectPhoto.setFocus()
            return True, "Subject Image Url"
        return False, "All Fields are filled."

    # remove all invalid substring according to regx
    @pyqtSlot(str)
    def check_ledit_string_validation(self, line_edit, regx, txt, max_length):
        sub_string = re.sub(regx, '', txt)
        len_text = len(txt)
        if not txt == sub_string:
            txt = sub_string
            line_edit.setText(txt)
        if len_text > max_length:
            txt = txt[:len_text - 1]
            line_edit.setText(txt)

    # remove all invalid substring according to regx
    @pyqtSlot(str)
    def check_ptedit_string_validation(self, text_edit, regx, max_length):
        txt = text_edit.toPlainText()
        len_txt = len(txt)
        if txt == '':
            return
        sub_string = re.sub(regx, '', txt)
        if not txt == sub_string:
            txt = sub_string
            text_edit.setPlainText(txt)
            return
        if len_txt > max_length:
            txt = txt[:len_txt - 1]
            text_edit.setPlainText(txt)
            return
        cursor = text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        text_edit.setTextCursor(cursor)

    # return page to initial status
    def refresh_view(self):
        btn_style = "border:none;background:transparent;" \
                    "image:url(:/newPrefix/Group 68.png);border-radius: 30px;background:none;"
        self.btnSelectPhoto.setStyleSheet(btn_style)
        self.leditCaseNumber.setText("")
        self.leditPS.setText("")
        self.leditExaminerName.setText("")
        self.leditExaminerNo.setText("")
        self.leditRemarks.setText("")
        self.case_info = CaseInfo()
        self.subject_photo_url = ""

    def showEvent(self, a0: QShowEvent) -> None:
        print("2.width:", self.btnSelectPhoto.size().width(), self.btnSelectPhoto.size().height())
