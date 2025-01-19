import cv2
import numpy as np
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QPushButton, QFormLayout, QLabel

from commons.common import Common
from insightfaces.main import FaceAI

class ProbeResultItemWidget(QWidget):
    delete_item_signal = pyqtSignal(object)

    def __init__(self, result_item, face_item, is_shown_delete_button, is_used_old_cases, case_information, parent=None):
        QWidget.__init__(self, parent=parent)
        self.result_item = result_item
        self.face_item = face_item
        self.is_used_old_cases = is_used_old_cases
        self.case_information = case_information
        # set whether to show cross button on image
        self.is_showed_cross_button = is_shown_delete_button

        self.vly_item_container = QVBoxLayout(self)

        self.vly_img_container = QVBoxLayout()
        self.vly_info_container = QVBoxLayout()

        self.wdt_image = QWidget()
        self.lbl_image = QLabel(self.wdt_image)

        if self.is_showed_cross_button:
            self.btn_delete = QPushButton(self.wdt_image)

        self.fly_info_container = QFormLayout()

        self.lbl_similarity_score_label = QLabel()
        self.lbl_similarity_score = QLabel()
        self.lbl_case_number_label = QLabel()
        self.lbl_case_number = QLabel()
        self.lbl_ps_label = QLabel()
        self.lbl_ps = QLabel()
        self.lbl_probe_id_label = QLabel()
        self.lbl_probe_id = QLabel()

        self.init_view()

    @pyqtSlot()
    def on_clicked_delete(self):
        self.delete_item_signal.emit(self.result_item)

    def resizeEvent(self, event):
        if self.is_showed_cross_button:
            image_geo = self.wdt_image.geometry()
            self.btn_delete.setGeometry(image_geo.width() - Common.CROSS_BUTTON_SIZE,
                                        0, Common.CROSS_BUTTON_SIZE, Common.CROSS_BUTTON_SIZE)

    def init_view(self):
        self.vly_item_container.setSpacing(6)
        self.wdt_image.setGeometry(0, 0, Common.RESULT_ITEM_WIDGET_SIZE, Common.RESULT_ITEM_WIDGET_SIZE)
        self.wdt_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.wdt_image.setMinimumSize(Common.RESULT_ITEM_WIDGET_SIZE, Common.RESULT_ITEM_WIDGET_SIZE)
        self.wdt_image.setMaximumSize(Common.RESULT_ITEM_WIDGET_SIZE, Common.RESULT_ITEM_WIDGET_SIZE)

        if self.is_showed_cross_button:
            image_geo = self.wdt_image.geometry()
            self.btn_delete.setGeometry(image_geo.width() - Common.CROSS_BUTTON_SIZE,
                                        0, Common.CROSS_BUTTON_SIZE, Common.CROSS_BUTTON_SIZE)
            self.btn_delete.setStyleSheet("image: url(:/newPrefix/error.png);background:transparent;border:none")
            self.btn_delete.clicked.connect(self.on_clicked_delete)

        self.vly_img_container.addWidget(self.wdt_image)

        self.lbl_similarity_score_label.setText("Similarity Score: ")
        self.lbl_similarity_score_label.setMaximumSize(Common.LABEL_MAX_WIDTH_IN_ITEM, Common.LABEL_MAX_HEIGHT_IN_ITEM)
        self.lbl_similarity_score.setMaximumSize(Common.VALUE_MAX_WIDTH_IN_ITEM, Common.VALUE_MAX_WIDTH_IN_ITEM)
        self.fly_info_container.addRow(self.lbl_similarity_score_label, self.lbl_similarity_score)

        self.lbl_case_number_label.setText("Old Case Number: ")
        self.lbl_ps_label.setText("PS: ")
        self.lbl_probe_id_label.setText("Probe ID: ")
        self.lbl_case_number.setStyleSheet(Common.TARGET_LIST_STYLE_LABEL)
        self.lbl_case_number_label.setStyleSheet(Common.TARGET_LIST_STYLE_LABEL)
        self.lbl_similarity_score.setStyleSheet(Common.TARGET_LIST_STYLE_LABEL)
        self.lbl_similarity_score_label.setStyleSheet(Common.TARGET_LIST_STYLE_LABEL)
        self.lbl_ps.setStyleSheet(Common.TARGET_LIST_STYLE_LABEL)
        self.lbl_ps_label.setStyleSheet(Common.TARGET_LIST_STYLE_LABEL)
        self.lbl_probe_id.setStyleSheet(Common.TARGET_LIST_STYLE_LABEL)
        self.lbl_probe_id_label.setStyleSheet(Common.TARGET_LIST_STYLE_LABEL)
        self.lbl_image.setStyleSheet(Common.TARGET_LIST_STYLE_LABEL)
        # self.wdt_image.setStyleSheet(Common.TARGET_LIST_STYLE_LABEL)

        if self.is_used_old_cases:

            self.lbl_case_number.setMaximumSize(Common.VALUE_MAX_WIDTH_IN_ITEM, Common.VALUE_MAX_WIDTH_IN_ITEM)
            self.lbl_case_number_label.setMaximumSize(Common.LABEL_MAX_WIDTH_IN_ITEM, Common.LABEL_MAX_HEIGHT_IN_ITEM)
            self.lbl_ps.setMaximumSize(Common.LABEL_MAX_WIDTH_IN_ITEM, Common.LABEL_MAX_HEIGHT_IN_ITEM)
            self.lbl_ps_label.setMaximumSize(Common.VALUE_MAX_WIDTH_IN_ITEM, Common.VALUE_MAX_WIDTH_IN_ITEM)
            self.lbl_probe_id.setMaximumSize(Common.LABEL_MAX_WIDTH_IN_ITEM, Common.LABEL_MAX_HEIGHT_IN_ITEM)
            self.lbl_probe_id_label.setMaximumSize(Common.VALUE_MAX_WIDTH_IN_ITEM, Common.VALUE_MAX_WIDTH_IN_ITEM)

            self.fly_info_container.addRow(self.lbl_case_number_label, self.lbl_case_number)
            self.fly_info_container.addRow(self.lbl_ps_label, self.lbl_ps)
            self.fly_info_container.addRow(self.lbl_probe_id_label, self.lbl_probe_id)
            if len(self.case_information):
                self.lbl_case_number.setText(self.case_information[0])
                self.lbl_ps.setText(self.case_information[1])
                self.lbl_probe_id.setText(self.case_information[2])

        self.vly_info_container.addLayout(self.fly_info_container)

        self.vly_item_container.addLayout(self.vly_img_container)
        self.vly_item_container.addLayout(self.vly_info_container)

        if not (self.result_item['confidence'] is None):
            # sim = abs(float(self.result_item['confidence'])) * 100
            # decimal_value = decimal.Decimal(sim)
            # # rounding the number upto 2 digits after the decimal point
            # rounded = decimal_value.quantize(decimal.Decimal('0.00'))
            fscore = float(self.result_item['confidence'][:len(self.result_item['confidence']) - 1])
            self.lbl_similarity_score.setText(self.result_item['confidence'] + " (" + FaceAI.get_similarity_str([], fscore, "", 100) + ")")
        img = cv2.imread(self.result_item['image_path'])
        img = np.array(img)

        size = Common.RESULT_ITEM_WIDGET_SIZE
        rate = 0.75
        width = img.shape[1]
        height = img.shape[0]
        if width > height:
            rate = size / width
        else:
            rate = size / height
        dim = (int(img.shape[1] * rate), int(img.shape[0] * rate))
        img = cv2.resize(img, dim)

        if float(self.result_item['confidence'][:len(self.result_item['confidence']) - 2]) >= 70.0:
            x1 = self.face_item['face_rectangle']['left'] * rate
            y1 = self.face_item['face_rectangle']['top'] * rate
            x2 = x1 + self.face_item['face_rectangle']['width'] * rate
            y2 = y1 + self.face_item['face_rectangle']['height'] * rate
            img = cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 1)

        height, width, channel = img.shape
        bytesPerLine = 3 * width
        qimage = QImage(img.tobytes(), width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap(qimage)
        lbl_x = 0
        lbl_y = 0
        if pixmap.size().width() > pixmap.size().height():
            lbl_y = (self.wdt_image.size().height() - pixmap.height()) / 2
            self.lbl_image.setGeometry(0, lbl_y, pixmap.width(), pixmap.height())
        else:
            lbl_x = (self.wdt_image.size().width() - pixmap.width()) / 2
            self.lbl_image.setGeometry(lbl_x, 0, pixmap.width(), pixmap.height())
        self.lbl_image.setPixmap(pixmap)
