from PyQt5.QtCore import QThread, Qt, pyqtSignal, QTimer, pyqtSlot
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QSplashScreen, QApplication, QSizePolicy

splash_i = 0
splash_i_widget = 99
splash_stop = 0  # Stop indicator SplashScreen
max_i_widget = 199  # Max. SplashScreen frame
splash_i_data = 202
max_i_data = 295
max_i = 0
splash_i_buff = 0


# Creating indicators for Splash Screen animation
# SplashScreen current frame indicator
# Thread to determine the completion of the SplashScreen
class SplashThread(QThread):
    mysignal = pyqtSignal(int)  # create a signal that will inform about the stop of the timer
    stop_signal = pyqtSignal()
    started_signal = pyqtSignal()

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.splash_screen = QSplashScreen()
        self.splash_screen.setMinimumSize(0, 0)
        self.splash_screen.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.splash_screen.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.splash_screen.setEnabled(False)
        splash_pixmap = QPixmap(':/newPrefix/splash/splash_0.png')
        self.splash_screen.setPixmap(splash_pixmap)
        self.splash_screen.setStyleSheet("background:transparent;")
        self.timer = QTimer()
        self.splash_type = "widget"  # the splash whether while loading widget or data.
        self.timer.setInterval(0)
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self.update_splash_screen)
        self.mysignal.connect(self.stop_splash)

    def start_splash(self, data_type):
        global splash_i_widget, splash_i_data, max_i_data, max_i_widget, splash_stop, max_i, splash_i, splash_i_buff
        if data_type == "widget":
            splash_i_buff = splash_i_widget
            splash_i = splash_i_widget
            max_i = max_i_widget
        else:
            splash_i = splash_i_data
            splash_i_buff = splash_i_data
            max_i = max_i_data
        self.timer.start()
        self.splash_screen.show()

    # Update SplashScreen animation
    def update_splash_screen(self):
        global splash_i_widget, splash_i_data, max_i_data, max_i_widget, splash_stop, max_i, splash_i, splash_i_buff
        # if the current frame is equal to the maximum, then we slow down the animation timer
        self.timer.setInterval(50)
        if splash_i == 583:
            splash_i = 0
            splash_stop = 1
        else:  # otherwise update the frame to the next
            if splash_i < max_i:
                splash_i = splash_i + 1
            else:
                splash_i = splash_i_buff
        pixmap = QPixmap(':/newPrefix/splash/splash_' + str(splash_i) + '.png')
        # pixmap = QPixmap(':/newPrefix/Background.png')
        self.splash_screen.setPixmap(pixmap)

    def run(self):
        # Wait for the entire animation to complete
        while splash_stop == 0:
            QApplication.processEvents()
        if splash_stop == 1:
            self.mysignal.emit(1)  # # send signal from thread to stop SplashScreen

    # Function to stop the timer and close the SplashScreen window
    @pyqtSlot()
    def stop_splash(self, wdt):
        global splash_i, max_i, splash_i_buff
        splash_i = 0
        max_i = 0
        splash_i_buff = 0
        # self.timer.stop()  # stop the timer
        if wdt is not None:
            wdt.show()  # show form
            wdt.setFocus()
        self.splash_screen.hide()  # close SplashScreen
