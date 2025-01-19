from sys import exit

import wmi
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QMessageBox

from commons.common import Common
from commons.verifying_license_thread import VerifyingLicenseThread
from cryptophic.license import write_infomation_db
from commons.systimer_thread import SysTimerThread


class LicenseBoxPage(QWidget):
    continue_app_signal = pyqtSignal(str)
    start_splash_signal = pyqtSignal(str)
    stop_splash_signal = pyqtSignal(object)

    def __init__(self, timerthread, parent=None):
        super(LicenseBoxPage, self).__init__(parent=parent)
        self.systimer_thread = timerthread
        self.window = uic.loadUi("./forms/Page_0.ui", self)
        self.btnConfirm = self.findChild(QPushButton, "btnConfirm")
        self.btnConfirm.clicked.connect(self.procLicenseConfirm)
        self.lblNotify = self.findChild(QLabel, "labelNotify")
        self.expired_date = ""
        self.verifying_license_thread = VerifyingLicenseThread()
        self.verifying_license_thread.finished_verifying_license_signal.connect(
            lambda ret, expire_flag: self.finished_verifying_license_slot(ret, expire_flag))

    @pyqtSlot(int, str)
    def finished_verifying_license_slot(self, ret, expire_dt):
        if ret is 0:
            self.lblNotify.setText("The license is not correct")
            self.stop_splash_signal.emit(None)  # stop splash
            self.setEnabled(True)  # once finished to process, can access to screen.
            return
        elif ret is -1:
            self.lblNotify.setText("The license is correct")
            self.stop_splash_signal.emit(None)  # stop splash
            self.setEnabled(True)  # once finished to process, can access to screen.
            Common.show_message(QMessageBox.Warning, "Please connect to internet to launch the software.", "",
                            "Internet connection failure",
                            "")
            return

        self.lblNotify.setText("The license is correct. One minutes...")
        #  getting processor batch number(FPO) and partial serial number(ATPO) date
        fpo_value = ""
        atpo_value = ""
        c = wmi.WMI()
        for s in c.Win32_Processor():
            fpo_value = s.ProcessorId
            atpo_value = s.Description
        self.expired_date = expire_dt
        self.systimer_thread.setexpire(self.expired_date)
        write_infomation_db(True, self.expired_date, fpo_value, atpo_value)
        # Goto homepage
        self.lblNotify.setText("Let's go to home page")
        self.stop_splash_signal.emit(None)  # stop splash
        self.setEnabled(True)  # once finished to process, can access to screen.
        self.continue_app_signal.emit(self.expired_date)  # start main

    # The function for license process confirm
    def procLicenseConfirm(self):
        # info = cpuinfo.get_cpu_info()
        # print(info)        

        lic = self.licenseBox.text()
        if len(lic) < 20:
            print("License length is not enough")
            self.lblNotify.setText("License length is not enough")
            return
        self.verifying_license_thread.license = lic
        self.setEnabled(False)  # once start to process, cannot access to screen.
        self.start_splash_signal.emit("data")  # start splash during verifying
        self.verifying_license_thread.start()  # start thread to verify license
        
