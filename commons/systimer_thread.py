from PyQt5.QtCore import QThread, pyqtSignal
from commons.systimer import SysTimer
from time import sleep
from commons.ntptime import ntp_get_time_from_string, ntp_get_time_from_object
from sys import exit


class SysTimerThread(QThread):
    expired_application_signal = pyqtSignal()

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.clock = None
        self.exp = ""
        self.expired = False

    def reset(self, clock):
        self.clock = clock

    def setexpire(self, exp_date):
        self.exp = exp_date
        self.expired = False

    def check_expire(self):   
        exp_date = ntp_get_time_from_string(self.exp)
        if exp_date == "": return 
        exp = exp_date - ntp_get_time_from_object(self.clock.now())
        print("check_expire: ", exp)
        if exp.total_seconds() <= 0 and self.expired == False:            
            self.expired_application_signal.emit()
            self.expired = True

    def run(self) -> None:
        self.timepick()

    def timepick(self):
        while True:
            self.clock.timepick() 
            self.check_expire()
            sleep(1)
