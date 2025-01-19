from PyQt5.QtCore import QThread, pyqtSignal
from insightfaces.main import FaceAI
from time import sleep
from cryptophic.main import exit_process


class FaceAIInitThread(QThread, FaceAI):
    finished_initializing_signal = pyqtSignal()

    def __init__(self, faceai, parent=None):
        QThread.__init__(self, parent)
        self.faceai = faceai

    def run(self) -> None:
        self.initializing()

    def initializing(self):
        res = False
        while not res:
            res = self.faceai.is_models_exist()
            sleep(0.01)

        self.faceai.initialize()
        exit_process()
        self.finished_initializing_signal.emit()
