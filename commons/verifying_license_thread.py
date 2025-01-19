from PyQt5.QtCore import QThread, pyqtSignal
from cryptophic.license import access_license_list


class VerifyingLicenseThread(QThread):
    finished_verifying_license_signal = pyqtSignal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.license = ""

    def run(self) -> None:
        # Read license list file
        ret, expire_flag = access_license_list(self.license)
        self.finished_verifying_license_signal.emit(ret, expire_flag)
