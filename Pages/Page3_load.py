from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QShowEvent
from PyQt5.QtWidgets import QPushButton, QRadioButton, QStackedWidget, QFileDialog, QMessageBox, QLabel, \
    QSizePolicy, QWidget

from commons.case_info import CaseInfo
from commons.common import Common
from commons.get_image_metadata import GetImageMetadata
from commons.get_images_thread import GetImagesThread
from commons.metadata_detail import MetadataDetail
from commons.processing_detail import ProcessingDetail


class LoaderSelectTargetPhotoPage(QWidget):
    go_back_signal = pyqtSignal()
    start_probe_signal = pyqtSignal(object)
    return_home_signal = pyqtSignal(str)
    start_splash_signal = pyqtSignal(str)
    stop_splash_signal = pyqtSignal(object)

    def __init__(self, faceai, parent=None):
        super(LoaderSelectTargetPhotoPage, self).__init__(parent=parent)

        self.target_images_metadata = []
        self.processing_details = []
        self.window = uic.loadUi("./forms/Page3-test.ui", self)
        self.case_info = CaseInfo()
        self.faceai = faceai
        self.image_urls = []
        self.get_images_thread = GetImagesThread(faceai, [])
        self.current_work_folder = ""
        self.cmdbtnGoBack = self.findChild(QPushButton, "btnGoBack")
        self.btnStartProbe = self.findChild(QPushButton, "btnStartProbe")
        self.btnReturnHome = self.findChild(QPushButton, "btnReturnHome")
        self.rdobtnSinglePhoto = self.findChild(QRadioButton, "rdobtnSinglePhoto")
        self.rdobtnMultiPhoto = self.findChild(QRadioButton, "rdobtnMultiPhoto")
        self.rdobtnEntireFolder = self.findChild(QRadioButton, "rdobtnEntireFolder")
        self.rdobtnOldCasePhoto = self.findChild(QRadioButton, "rdobtnOldCasePhoto")
        self.btnSinglePhoto = self.findChild(QPushButton, "btnSinglePhoto")
        self.btnMultiPhoto = self.findChild(QPushButton, "btnMultiPhoto")
        self.btnMultiPhoto2 = self.findChild(QPushButton, "btnMultiPhoto2")
        self.lblMultiPhotoResult = self.findChild(QLabel, "lblMultiResult")
        self.btnEntireFolder = self.findChild(QPushButton, "btnEntireFolder")
        self.btnEntireFolder2 = self.findChild(QPushButton, "btnEntireFolder2")
        self.lblEntireResult = self.findChild(QLabel, "lblEntireFolderResult")
        self.lblOldCaseResult = self.findChild(QLabel, "lblOldCaseResult")
        self.lblOldCaseSelectedNumber = self.findChild(QLabel, "lblOldCaseSelectedNumber")
        self.stkwdtSelectPhotos = self.findChild(QStackedWidget, "stkwdtSelectPhotos")
        self.stkwdtSelectPhotos.setCurrentIndex(0)
        self.init_actions()
        self.lblStatus = self.findChild(QLabel, "lblStatus")

    def set_statusbar(self, status):
        self.lblStatus.setText(status)

    @pyqtSlot()
    def start_probe_slot(self):
        is_exist, root_path = Common.check_exist_data_storage()
        if is_exist:
            if self.case_info.subject_image_url == '':
                Common.show_message(QMessageBox.Warning, "Please select subject image.", "", "Empty Warning", "")
                self.go_back_signal.emit()
            else:
                if len(self.image_urls) == 0:
                    Common.show_message(QMessageBox.Warning, "Please select target images.", "", "Empty Warning", "")
                else:
                    self.case_info.target_image_urls = self.image_urls
                    self.case_info.target_images_processing_details = self.processing_details
                    self.case_info.target_images_metadata = self.target_images_metadata
                    self.start_probe_signal.emit(self.case_info)
        else:
            Common.show_message(QMessageBox.Warning, "\"" + root_path + "\" folder does not exist."
                                                                        "\nPlease make it and then retry.",
                                "", "Folder Not Exist", "")

    @pyqtSlot()
    def return_home_slot(self):
        self.return_home_signal.emit("")

    @pyqtSlot()
    def go_back_slot(self):
        self.image_urls.clear()  # clear image urls before back to the "create case page"
        self.go_back_signal.emit()

    @pyqtSlot()
    def select_photo_mode_slot(self, checked, index):
        if checked:
            self.get_images_thread.init_flags(False)
            self.stkwdtSelectPhotos.setCurrentIndex(index)
            # if selected old cases, select images from that folder
            if index == 3:
                self.select_from_old_cases()

    @pyqtSlot(list, list, list)
    def finished_get_images_slot(self, urls, processing_details, metadata):
        self.setEnabled(True)
        self.image_urls = urls
        self.processing_details = processing_details
        self.target_images_metadata = metadata
        if self.get_images_thread.is_urls:
            self.get_images_thread.is_urls = False
            if len(self.image_urls) == 0:
                self.lblMultiPhotoResult.setText("There are no raster images in this folder.")
            else:
                self.btnMultiPhoto2.setText(str(len(self.image_urls)) + Common.SELECTED_IMAGE_DESCRIPTION)
        if self.get_images_thread.is_direct:
            self.get_images_thread.is_direct = False
            if len(self.image_urls) == 0:
                self.lblEntireResult.setText("There are no raster images in this folder.")
            else:
                self.btnEntireFolder2.setText(str(len(self.image_urls)) + Common.SELECTED_IMAGE_DESCRIPTION)
        if self.get_images_thread.is_old_cases:
            self.get_images_thread.is_old_cases = False
            if not len(self.image_urls):
                self.lblOldCaseSelectedNumber.setText("")
                self.lblOldCaseResult.setText("There are no old cases images. Please select manually on other tab.")
            else:
                self.lblOldCaseResult.setText(
                    "Click on the \"Start probe\" button below to continue the further process.")
                self.lblOldCaseSelectedNumber.setText(str(len(self.image_urls)) + Common.SELECTED_IMAGE_DESCRIPTION)
        self.stop_splash_signal.emit(None)

    @pyqtSlot()
    def select_single_photo_slot(self):
        self.refresh_view()
        url, _ = QFileDialog.getOpenFileName(self, 'Open File', self.current_work_folder, Common.IMAGE_FILTER)
        if url:
            processing_detail = ProcessingDetail()
            metadata = GetImageMetadata()
            metadata_detail = metadata.get_metadata(url)
            if Common.get_file_extension_from_path(url) == ".heic":
                url = Common.reformat_image(url)
                processing_detail.reformatted = True
            if not self.faceai.is_face(url):
                Common.show_message(QMessageBox.Warning, "Please select an image with man", "",
                                    "Incorrect image selected.",
                                    "")
            else:
                # check "data storage" folder exist or not
                is_exist, root_path = Common.check_exist_data_storage()
                if is_exist:
                    self.current_work_folder = Common.get_folder_path(url)
                    resized_image_path, processing_detail.resized = Common.resize_image(url, self.btnSinglePhoto.size().width())
                    btn_style = "image:url('" + resized_image_path + "');height: auto;border: 1px solid rgb(53, 132, 228);"
                    self.btnSinglePhoto.setStyleSheet(btn_style)
                    self.btnSinglePhoto.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                    self.image_urls.append(resized_image_path)
                    self.processing_details.append(processing_detail)
                    self.target_images_metadata.append(metadata_detail)
                    self.case_info.target_type = 1
                else:
                    Common.show_message(QMessageBox.Warning, "\"" + root_path + "\" folder does not exist."
                                                                                "\nPlease make it and then retry.",
                                        "", "Folder Not Exist", "")
        else:
            btn_style = "border: none;image:url(:/newPrefix/Group 67.png);"
            self.btnSinglePhoto.setStyleSheet(btn_style)

    @pyqtSlot()
    def select_multi_photo_slot(self):
        self.refresh_view()
        urls, _ = QFileDialog.getOpenFileNames(self, 'Open Files', self.current_work_folder, Common.IMAGE_FILTER)
        length = len(urls)
        if length:
            # check "data storage" folder exist or not
            is_exist, root_path = Common.check_exist_data_storage()
            if is_exist:
                self.btnMultiPhoto2.setText("")
                self.setEnabled(False)
                self.current_work_folder = Common.get_folder_path(urls[0])
                self.get_images_thread.urls = urls
                self.get_images_thread.is_urls = True
                self.case_info.target_type = 2
                self.start_splash_signal.emit("data")
                self.get_images_thread.start()
            else:
                Common.show_message(QMessageBox.Warning, "\"" + root_path + "\" folder does not exist."
                                                                            "\nPlease make it and then retry.",
                                    "", "Folder Not Exist", "")
        else:
            self.btnMultiPhoto2.setText("Select target images.")
            self.lblMultiPhotoResult.setText(Common.RASTER_IMAGE_ACCEPTED_NOTICE)

    @pyqtSlot()
    def select_entire_folder_slot(self):
        self.refresh_view()
        direct = QFileDialog.getExistingDirectory(self, 'Entire Folder')

        if direct:
            # check "data storage" folder exist or not
            is_exist, root_path = Common.check_exist_data_storage()
            if is_exist:
                self.current_work_folder = direct
                self.get_images_thread.direct = direct
                self.get_images_thread.is_direct = True
                self.case_info.target_type = 3
                self.setEnabled(False)
                self.start_splash_signal.emit("data")
                self.get_images_thread.start()
            else:
                Common.show_message(QMessageBox.Warning, "\"" + root_path + "\" folder does not exist."
                                                                            "\nPlease make it and then retry.",
                                    "", "Folder Not Exist", "")

        else:
            self.btnEntireFolder2.setText("Select target folder.")
            self.lblEntireResult.setText(Common.RASTER_IMAGE_ACCEPTED_NOTICE)

    # get all images from old cases
    def select_from_old_cases(self):
        # check "data storage" folder exist or not
        is_exist, root_path = Common.check_exist_data_storage()
        if is_exist:
            self.refresh_view()
            self.lblOldCaseResult.setText("Loading images from old cases.... ")
            self.setEnabled(False)
            # start splash
            self.start_splash_signal.emit("data")
            self.image_urls.clear()
            self.case_info.is_used_old_cases = True

            reg_val = Common.get_reg(Common.REG_KEY)
            targets_path = ""
            if reg_val:
                targets_path = Common.get_reg(Common.REG_KEY) + "/" + Common.MEDIA_PATH + "/subjects"
            else:
                targets_path = Common.STORAGE_PATH + "/" + Common.MEDIA_PATH + "/subjects"
            self.get_images_thread.is_old_cases = True
            self.get_images_thread.direct = targets_path
            self.case_info.target_type = 4
            self.get_images_thread.start()
        else:
            Common.show_message(QMessageBox.Warning, "\"" + root_path + "\" folder does not exist."
                                                                        "\nPlease make it and then retry.",
                                "", "Folder Not Exist", "")

    # make file filter for QFileDialog from Common.EXTENSIONS
    def make_file_filter(self):
        file_filter = ' *.'.join([str(a) for a in Common.EXTENSIONS])
        file_filter = '"Images (*.' + file_filter + ')"'
        return file_filter

    # initiate actions for window
    def init_actions(self):
        self.btnStartProbe.clicked.connect(self.start_probe_slot)
        self.btnReturnHome.clicked.connect(self.return_home_slot)
        self.cmdbtnGoBack.clicked.connect(self.go_back_slot)
        self.btnSinglePhoto.clicked.connect(self.select_single_photo_slot)
        self.btnMultiPhoto.clicked.connect(self.select_multi_photo_slot)
        self.btnMultiPhoto2.clicked.connect(self.select_multi_photo_slot)
        self.btnEntireFolder.clicked.connect(self.select_entire_folder_slot)
        self.btnEntireFolder2.clicked.connect(self.select_entire_folder_slot)
        self.get_images_thread.finished_get_images_signal.connect(
            lambda urls, processing_details, metadata: self.finished_get_images_slot(urls, processing_details, metadata))

        self.rdobtnSinglePhoto.toggled[bool].connect(
            lambda checked:
            self.select_photo_mode_slot(checked, 0)
        )
        self.rdobtnMultiPhoto.toggled[bool].connect(
            lambda checked:
            self.select_photo_mode_slot(checked, 1)
        )
        self.rdobtnEntireFolder.toggled[bool].connect(
            lambda checked:
            self.select_photo_mode_slot(checked, 2)
        )
        self.rdobtnOldCasePhoto.toggled[bool].connect(
            lambda checked:
            self.select_photo_mode_slot(checked, 3)
        )

    def refresh_view(self):
        self.image_urls.clear()
        self.processing_details.clear()
        self.case_info.target_image_urls.clear()
        self.case_info.target_images_metadata.clear()
        self.case_info.is_used_old_cases = False
        btn_style = "background:transparent;border:0px;image:url(:/newPrefix/Group 67.png);"
        self.btnSinglePhoto.setStyleSheet(btn_style)
        self.btnMultiPhoto2.setText("Select target images.")
        self.lblMultiPhotoResult.setText(Common.RASTER_IMAGE_ACCEPTED_NOTICE)
        self.btnEntireFolder2.setText("Select target folder.")
        self.lblEntireResult.setText(Common.RASTER_IMAGE_ACCEPTED_NOTICE)
        self.lblOldCaseSelectedNumber.setText("")
        self.lblOldCaseResult.setText("Click on the \"Start probe\" button below to continue the further process.")
        self.repaint()

    def init_views(self):
        self.refresh_view()
        self.stkwdtSelectPhotos.setCurrentIndex(0)
        self.rdobtnSinglePhoto.setChecked(True)

    def showEvent(self, a0: QShowEvent) -> None:
        print("3.width:", self.btnSinglePhoto.size().width(), self.btnSinglePhoto.size().height())