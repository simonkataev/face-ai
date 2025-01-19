from PyQt5.QtCore import QThread, pyqtSignal
from cryptophic.main import decrypt

class DecThread(QThread):
    finished_decrypting_signal = pyqtSignal()

    def __init__(self, parent=None):
        QThread.__init__(self, parent)

    def run(self) -> None:
        self.decrypting()

    def decrypting(self):
        res = decrypt(r".\models")
        print("Decrypting: ", res)
        self.finished_decrypting_signal.emit()
