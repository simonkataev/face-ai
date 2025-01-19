from PyQt5.QtCore import QThread, pyqtSignal
from cryptophic.main import encrypt

class EncThread(QThread):    
    finished_encrypting_signal = pyqtSignal()

    def __init__(self, parent=None):
        QThread.__init__(self, parent)

    def run(self) -> None:
        self.encrypting()

    def encrypting(self):
        res = encrypt(r".\test_model")
        print("Encrypting: ", res)
        self.finished_encrypting_signal.emit()