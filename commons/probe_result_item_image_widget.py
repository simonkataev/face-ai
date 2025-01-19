from PyQt5.QtCore import QRect
from PyQt5.QtGui import QPaintEvent, QPainter, QColor, QPen
from PyQt5.QtWidgets import QWidget


class ProbeResultItemImageWidget(QWidget):
    def __init__(self, parent, face_item):
        super().__init__(parent)
        self.face_item = {"image_path":
                              "E:/freelancing/inpregress/faceAI-Team/New folder/FaceAI_App_Demo/student/2.jpg",
                          "face_token":
                              "b'cf8379921400fd731d7395f644d1781f'",
                          "face_rectangle": {"left": 192, "top": 96, "width": 215,
                                             "height": 275}, "face_angle": "Roll: 6 degree"}
        self.setGeometry(0, 0, 100, 100)
        self.setStyleSheet("background:red;")

    def paint_rect(self):
        face_rect_painter = QPainter(self)
        # "face_rectangle": { "left": 202, "top": 110, "width": 135,
        # "height": 169 }, "face_angle": "Roll: 14 degree" },
        face_rectangle = self.face_item['face_rectangle']
        rect_pen = QPen(QColor(255, 0, 0), 1)
        face_rect_painter.setPen(rect_pen)
        face_rect_painter.drawRect(QRect(face_rectangle['left'], face_rectangle['top'],
                                         face_rectangle['width'], face_rectangle['height']))

    def paintEvent(self, a0: QPaintEvent) -> None:
        super().paintEvent(a0)
        # opt = QStyleOption()
        # # opt.init(self)
        # p = QPainter(self)
        # raw_font = QRawFont()
        # raw_font.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)
        # style = "image:url('E:/freelancing/inpregress/faceAI-Team/New folder/FaceAI_App_Demo/student/2.jpg');"
        # self.setStyleSheet(style)
        face_rect_painter = QPainter(self)
        # "face_rectangle": { "left": 202, "top": 110, "width": 135,
        # "height": 169 }, "face_angle": "Roll: 14 degree" },
        face_rectangle = self.face_item['face_rectangle']
        rect_pen = QPen(QColor(255, 0, 0), 1)
        face_rect_painter.setPen(rect_pen)
        # face_rect_painter.drawRect(QRect(face_rectangle['left'], face_rectangle['top'],
        #                                  face_rectangle['width'], face_rectangle['height']))
        face_rect_painter.drawRect(QRect(0, 0, 20, 20))
