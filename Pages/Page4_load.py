from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QLabel

from commons.case_info import CaseInfo
from commons.probing_result import ProbingResult
from commons.probing_thread import ProbingThread
from insightfaces.main import FaceAI


class LoaderProbingPage(QWidget):
    completed_probing_signal = pyqtSignal(ProbingResult)
    start_splash_signal = pyqtSignal()

    def __init__(self, faceai, parent=None):
        super(LoaderProbingPage, self).__init__(parent=parent)
        self.faceai = faceai
        self.probing_result = ProbingResult()
        self.probing_thread = ProbingThread(CaseInfo, self.faceai)
        self.processing_gif = QMovie(":/newPrefix/AIFace_Processing.gif")
        self.current_gif = self.processing_gif
        self.failed_gif = QMovie(":/newPrefix/AIFace_Failed.gif")
        self.success_gif = QMovie(":/newPrefix/AIFace_Success.gif")
        self.window = uic.loadUi("./forms/Page_4.ui", self)
        self.lblFaceGif = self.findChild(QLabel, "lblFaceGif")
        self.lblProbeResult = self.findChild(QLabel, "lblProbeResult")
        self.probing_thread.failed_probing_signal.connect(self.failed_probing_slot)
        self.probing_thread.success_probing_signal.connect(self.success_probing_slot)
        self.timer = QTimer()
        self.lblStatus = self.findChild(QLabel, "lblStatus")

    def set_statusbar(self, status):
        self.lblStatus.setText(status)

    def start_gif(self):
        self.lblFaceGif.setMovie(self.current_gif)
        self.current_gif.start()

    def stop_gif(self):
        self.current_gif.stop()

    def start_probing(self, case_info):
        self.probing_result.case_info = case_info
        self.start_gif()
        # start to probe images
        self.probing_thread.probing_result.case_info = case_info
        self.probing_thread.finished_probing_signal.connect(self.finished_probing_slot)
        self.probing_thread.start()

    @pyqtSlot(ProbingResult)
    def finished_probing_slot(self, probing_result):
        self.stop_gif()
        self.probing_thread.quit()
        self.start_splash_signal.emit()
        self.completed_probing_signal.emit(probing_result)

    @pyqtSlot()
    # a slot to be run when timeout on probing page
    def timeout_gif(self):
        self.stop_gif()
        self.current_gif = self.processing_gif
        self.lblProbeResult.setText("Probing images...")
        self.start_gif()

    def failed_probing_slot(self):
        self.stop_gif()
        self.current_gif = self.failed_gif
        self.lblProbeResult.setText("Recognized as different person.")
        self.start_gif()
        self.timer.singleShot(800, self.timeout_gif)
        self.timer.start()

    def success_probing_slot(self):
        self.stop_gif()
        self.current_gif = self.success_gif
        self.lblProbeResult.setText("Recognized as same person.")
        self.start_gif()
        self.timer.singleShot(800, self.timeout_gif)
        self.timer.start()

