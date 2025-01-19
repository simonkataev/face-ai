from sys import exit

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtGui import QShowEvent, QCloseEvent
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QStatusBar, QMessageBox, QHBoxLayout

from Pages.Page0_load import LicenseBoxPage
from Pages.Page1_load import StartHome
from Pages.Page2_load import LoaderCreateNewCasePage
from Pages.Page3_load import LoaderSelectTargetPhotoPage
from Pages.Page4_load import LoaderProbingPage
from Pages.Page5_load import LoaderProbeReportPreviewPage
from Pages.Page6_load import LoaderProbeReportPage
from Pages.Page7_load import LoaderProbeReportListPage
from commons.case_info import CaseInfo
from commons.common import Common
from commons.ntptime import ntp_get_time, ntp_get_time_from_string
from commons.systimer import SysTimer
from commons.systimer_thread import SysTimerThread
from commons.probing_result import ProbingResult
from commons.target_items_container_generator import TargetItemsContainerGenerator
from cryptophic.dec_thread import DecThread
from cryptophic.license import read_information_db, get_cpu_info
from insightfaces.faceai_init_thread import FaceAIInitThread
from insightfaces.main import FaceAI
import images


# start home page for probing
class StartMain(QMainWindow):
    finished_initiating_widget_signal = pyqtSignal(object)
    update_progress_signal = pyqtSignal(int)
    start_splash_signal = pyqtSignal(str)
    stop_splash_signal = pyqtSignal()

    def __init__(self, splash):
        super().__init__()
        ntptime = ntp_get_time()
        if ntptime is None:
            Common.show_message(QMessageBox.Warning, "Please connect to internet to launch the software.", "",
                                "Internet connection failure",
                                "")
            exit()
        self.app_unlocked, self.app_expire_date, self.app_fpo_info, self.app_atpo_info = read_information_db()
        self.check_device_info(self.app_fpo_info, self.app_atpo_info)

        self.systimer = SysTimer(ntptime)
        self.systimer_thread = SysTimerThread()
        self.systimer_thread.reset(self.systimer)
        self.systimer_thread.expired_application_signal.connect(self.expired_application_slot)
        self.systimer_thread.start()

        self.faceai = FaceAI()
        self.splash = splash
        # self.splash.start_splash(self)
        self.dec_thread = DecThread()
        self.dec_thread.finished_decrypting_signal.connect(self.finished_decrypting_slot)
        self.dec_thread.start()

        self.faceai_init_thread = FaceAIInitThread(self.faceai)
        self.faceai_init_thread.finished_initializing_signal.connect(self.finished_initializing_slot)

        self.window = uic.loadUi("./forms/main_window.ui", self)
        self.centralLayout = self.findChild(QVBoxLayout, "centralLayout")
        self.ui_0_license = LicenseBoxPage(self.systimer_thread, self)
        self.ui_1_home = StartHome(self)
        self.ui_2_create_new_case = LoaderCreateNewCasePage(self.faceai, self)
        self.ui_3_select_target_photo = LoaderSelectTargetPhotoPage(self.faceai, self)
        self.ui_4_probing = LoaderProbingPage(self.faceai, self)
        self.ui_5_probe_report_preview = LoaderProbeReportPreviewPage(self)
        self.ui_6_probe_report = LoaderProbeReportPage(self)
        self.ui_7_prove_report_list = LoaderProbeReportListPage(self)
        self.status_bar = self.findChild(QStatusBar, "statusBar")
        self.refresh_views_thread = TargetItemsContainerGenerator()  # the thread to be used to refresh some page
        self.refresh_views_thread.finished_refreshing_target_items.connect(
            lambda wdt: self.finished_refreshing_slot(wdt)
        )

        self.set_page_transition()
        self.set_splash_signal_slot()
        self.init_widgets()
        self.init_status_bar("start")

    # def start_main(self):
    #     self.show_p1_home()

    @pyqtSlot()
    def finished_decrypting_slot(self):
        self.dec_thread.quit()
        self.faceai_init_thread.start()
    
    @pyqtSlot()
    def expired_application_slot(self):
        self.show_p0_license()

    # when main window finished to be initiated or refreshed, the widget emit finished signal.
    # then, this slot will be called.
    @pyqtSlot()
    def finished_initializing_slot(self):
        self.faceai_init_thread.quit()        
        
        self.systimer_thread.setexpire(self.app_expire_date)
        if self.check_license(self.app_unlocked, self.app_expire_date):
            self.finished_initiating_widget_signal.emit(self)
            self.showMaximized()
            self.show_p1_home(self.app_expire_date)
        else:
            self.finished_initiating_widget_signal.emit(self)
            self.showMaximized()
            self.show_p0_license()

    # when some widget finished to be initiated or refreshed, the widget emit finished signal.
    # then, this slot will be called.
    @pyqtSlot(object)
    def finished_refreshing_slot(self, wdt):
        self.finished_initiating_widget_signal.emit(wdt)

    @pyqtSlot()
    def start_splash_for_subwidgets_slot(self, data_type):
        self.start_splash_signal.emit(data_type)

    def set_splash_signal_slot(self):
        self.ui_0_license.start_splash_signal.connect(
            lambda data_type: self.start_splash_for_subwidgets_slot(data_type)
        )
        self.ui_0_license.stop_splash_signal.connect(self.finished_refreshing_slot)

        self.ui_3_select_target_photo.start_splash_signal.connect(
            lambda data_type: self.start_splash_for_subwidgets_slot(data_type))
        self.ui_3_select_target_photo.stop_splash_signal.connect(self.finished_refreshing_slot)

        self.ui_5_probe_report_preview.start_splash_signal.connect(
            lambda data_type: self.start_splash_for_subwidgets_slot(data_type)
        )
        self.ui_5_probe_report_preview.stop_splash_signal.connect(self.finished_refreshing_slot)

        self.ui_6_probe_report.start_splash_signal.connect(
            lambda data_type: self.start_splash_for_subwidgets_slot(data_type)
        )
        self.ui_6_probe_report.stop_splash_signal.connect(self.finished_refreshing_slot)

        self.ui_7_prove_report_list.start_splash_signal.connect(
            lambda data_type: self.start_splash_for_subwidgets_slot(data_type)
        )
        self.ui_7_prove_report_list.stop_splash_signal.connect(self.finished_refreshing_slot)

    # set the connection between signal and slot for page transitions
    def set_page_transition(self):
        # Click to go page2 from page 1 button
        self.ui_1_home.btnCreateCase.clicked.connect(self.init_child_widgets)
        # Click to go to page 7 from page 1 button
        self.ui_1_home.btnGo2ProbeReport.clicked.connect(self.show_p7_probe_report_list_without_param)
        self.ui_0_license.continue_app_signal.connect(self.show_p1_home)
        self.ui_2_create_new_case.return_home_signal.connect(self.show_p1_home)
        # transit the case information 'create case page' to 'select target page'
        self.ui_2_create_new_case.continue_probe_signal.connect(
            lambda case_info:
            self.show_p3_select_target_photos(case_info)
        )
        # transit the case information 'select target page' to 'probing' page
        self.ui_3_select_target_photo.start_probe_signal.connect(
            lambda case_info:
            self.show_p4_probing(case_info)
        )
        self.ui_3_select_target_photo.go_back_signal.connect(self.show_p2_create_new_case)
        self.ui_3_select_target_photo.return_home_signal.connect(self.show_p1_home)

        # after completed probing, go to report preview page with probing_result object
        self.ui_4_probing.completed_probing_signal.connect(
            lambda probe_result: self.show_p5_probe_report_preview(probe_result, False))

        # once clicked "return home" button, return home page
        self.ui_5_probe_report_preview.return_home_signal.connect(self.show_p1_home)
        # once clicked "generate report" button on preview page, go to report page
        self.ui_5_probe_report_preview.generate_report_signal.connect(
            lambda probe_result, case_data:
            self.show_p6_probe_report(probe_result, case_data))
        # when clicked "go back" button on preview page, go to "select target photo" page
        self.ui_5_probe_report_preview.go_back_signal.connect(self.show_p3_select_target_photos)

        # when clicked "return home" button , return home page
        self.ui_6_probe_report.return_home_signal.connect(self.show_p1_home)
        # when clicked "export pdf" button, export result to pdf and go to report list page
        # self.ui_6_probe_report.export_pdf_signal.connect(self.show_p7_probe_report_list)

        # when clicked "go back" button on report page, go to "report preview page
        self.ui_6_probe_report.go_back_signal.connect(
            lambda probe_result, is_go_back: self.show_p5_probe_report_preview(probe_result, is_go_back))

        # when clicked "return home" button, return home page
        self.ui_7_prove_report_list.return_home_signal.connect(self.show_p1_home)
        # when clicked "go back" button, go back to "Probe report" page
        self.ui_7_prove_report_list.go_back_signal.connect(self.show_p6_probe_report_without_param)
        self.ui_7_prove_report_list.go_back_empty_signal.connect(self.show_p6_probe_report_without_param)

    @pyqtSlot(CaseInfo)
    def show_p3_select_target_photos(self, case_info):
        self.setWindowTitle("Select Target(s)")
        # hide other window
        self.ui_1_home.hide()
        self.ui_2_create_new_case.hide()
        self.ui_5_probe_report_preview.hide()
        # return page to initial status.
        self.ui_3_select_target_photo.init_views()
        # set case information to page
        self.ui_3_select_target_photo.case_info = case_info
        self.ui_3_select_target_photo.showMaximized()

    def show_p0_license(self):
        self.setWindowTitle("License")
        self.ui_1_home.hide()
        self.ui_2_create_new_case.hide()
        self.ui_3_select_target_photo.hide()
        self.ui_6_probe_report.hide()
        self.ui_7_prove_report_list.hide()
        self.ui_5_probe_report_preview.hide()
        self.ui_0_license.showMaximized()

    @pyqtSlot(str)
    def show_p1_home(self, expire_date):
        self.setWindowTitle("Home")
        self.init_child_widgets()
        if expire_date:
            self.init_status_bar("The license will be expired by " + expire_date + ".")
            self.systimer_thread.setexpire(expire_date)
        self.ui_0_license.hide()
        self.ui_2_create_new_case.hide()
        self.ui_3_select_target_photo.hide()
        self.ui_6_probe_report.hide()
        self.ui_7_prove_report_list.hide()
        self.ui_5_probe_report_preview.hide()
        self.ui_1_home.showMaximized()
        self.ui_1_home.setFocus()
        # if len(expire_date) > 0:
        #     self.init_status_bar("The license will be expired by "
        #                                 + expire_date)

    @pyqtSlot()
    def show_p2_create_new_case(self):
        self.setWindowTitle("Create a Case")
        Common.remove_target_images()
        self.ui_1_home.hide()
        self.ui_3_select_target_photo.hide()
        self.ui_2_create_new_case.showMaximized()

    @pyqtSlot(CaseInfo)
    def show_p4_probing(self, case_info):
        self.setWindowTitle("Probing...")
        self.ui_3_select_target_photo.hide()
        # start probing
        self.ui_4_probing.showMaximized()
        self.ui_4_probing.start_probing(case_info)

    @pyqtSlot(ProbingResult)
    def show_p5_probe_report_preview(self, probe_result, is_go_back):
        is_exist, root_path = Common.check_exist_data_storage()
        if is_exist:
            self.setWindowTitle("Probe Report Preview")
            # init views
            self.ui_4_probing.hide()
            self.ui_6_probe_report.hide()
            if not is_go_back:
                # show probe report preview page
                self.ui_5_probe_report_preview.probe_result = probe_result
                self.ui_5_probe_report_preview.refresh_views()
            self.ui_5_probe_report_preview.showMaximized()
        else:
            Common.show_message(QMessageBox.Warning, "\"" + root_path + "\" folder does not exist."
                                                                        "\nPlease make it and then retry.",
                                "", "Folder Not Exist", "")

    @pyqtSlot(ProbingResult, list)
    def show_p6_probe_report(self, probe_result, case_data):
        self.setWindowTitle("Probe Report")
        # init views
        self.ui_5_probe_report_preview.hide()
        self.ui_7_prove_report_list.hide()
        # return page to initial status
        self.ui_6_probe_report.probe_result = probe_result
        self.ui_6_probe_report.case_data_for_results = case_data
        # self.ui_2_create_new_case.refresh_view()
        # self.ui_3_select_target_photo.refresh_view()
        self.ui_6_probe_report.refresh_views()
        self.ui_6_probe_report.showMaximized()

    @pyqtSlot()
    def show_p6_probe_report_without_param(self):
        self.setWindowTitle("Probe Report")
        self.ui_7_prove_report_list.hide()
        self.ui_6_probe_report.probe_result = ProbingResult()
        self.ui_6_probe_report.init_input_values()
        self.ui_6_probe_report.init_target_images_view()
        self.ui_6_probe_report.showMaximized()

    @pyqtSlot(ProbingResult)
    def show_p7_probe_report_list(self, probe_result):
        self.setWindowTitle("Probe Reports")
        # init views
        self.ui_6_probe_report.hide()
        self.ui_7_prove_report_list.probe_result = probe_result
        self.ui_7_prove_report_list.refresh_view()
        # stop splashing
        # self.splash.stop_splash()
        # show probe report list page
        self.ui_7_prove_report_list.showMaximized()

    @pyqtSlot()
    def show_p7_probe_report_list_without_param(self):
        is_exist, root_path = Common.check_exist_data_storage()
        if is_exist:
            self.setWindowTitle("Probe Reports")
            self.ui_1_home.hide()
            self.ui_4_probing.hide()
            self.ui_7_prove_report_list.refresh_view()
            # show probe report list page
            self.ui_7_prove_report_list.showMaximized()
        else:
            Common.show_message(QMessageBox.Warning, "\"" + root_path + "\" folder does not exist."
                                                                        "\nPlease make it and then retry.",
                                "", "Folder Not Exist", "")

    def init_widgets(self):
        self.centralLayout.addWidget(self.ui_0_license)
        self.centralLayout.addWidget(self.ui_1_home)
        self.centralLayout.addWidget(self.ui_2_create_new_case)
        self.centralLayout.addWidget(self.ui_3_select_target_photo)
        self.centralLayout.addWidget(self.ui_4_probing)
        self.centralLayout.addWidget(self.ui_5_probe_report_preview)
        self.centralLayout.addWidget(self.ui_6_probe_report)
        self.centralLayout.addWidget(self.ui_7_prove_report_list)
        self.ui_0_license.hide()
        self.ui_1_home.hide()
        self.ui_2_create_new_case.hide()
        self.ui_3_select_target_photo.hide()
        self.ui_4_probing.hide()
        self.ui_5_probe_report_preview.hide()
        self.ui_6_probe_report.hide()
        self.ui_7_prove_report_list.hide()

    def showEvent(self, a0: QShowEvent) -> None:
        super().showEvent(a0)
        # self.showMaximized()
        # self.start_main()

    def closeEvent(self, a0: QCloseEvent) -> None:
        super().closeEvent(a0)
        self.refresh_views_thread.quit()
        self.splash.quit()

    def check_license(self, app_unlocked, app_expire_date):
        if not app_unlocked:
            self.init_status_bar("The license is not available.")
            self.show_p0_license()
        else:            
            ntptime = ntp_get_time()
            if ntptime is None:
                Common.show_message(QMessageBox.Warning, "Please connect to internet to launch the software.", "",
                                "Internet connection failure",
                                "")
                exit()
            
            app_expire = ntp_get_time_from_string(app_expire_date) - ntptime
            # self.status_bar.showMessage("The license will be expired by "
            #                             + app_expire_date + ". You can use more this application for "
            #                             + str(app_expire) + ".")

            if app_expire.total_seconds() > 0:
                self.init_status_bar("The license will be expired by "
                                            + Common.convert_string2datetime(app_expire_date, "%d/%m/%Y %H:%M:%S"))
                return True
            else:
                self.init_status_bar("The license was expired by "
                                            + Common.convert_string2datetime(app_expire_date, "%d/%m/%Y %H:%M:%S"))
                return False

    def check_device_info(self, app_fpo_info, app_atpo_info):
        fpo_info, atpo_info = get_cpu_info()
        if (app_fpo_info != fpo_info) & (app_atpo_info != atpo_info):
            Common.show_message(QMessageBox.Warning, "You are an invalid user or working on the other machine.", "",
                                "Invalid selected.",
                                "")
            exit()

    # when select create new case, refresh all child pages and then go to the create new case page
    def init_child_widgets(self):
        # check "data storage" folder exist or not
        is_exist, root_path = Common.check_exist_data_storage()
        if is_exist:
            self.ui_2_create_new_case.refresh_view()
            self.ui_3_select_target_photo.init_views()
            self.ui_5_probe_report_preview.init_views()
            self.ui_6_probe_report.init_views()
            self.ui_7_prove_report_list.init_empty()
            self.show_p2_create_new_case()
            Common.remove_temp_folder("resize-temp")
            Common.remove_temp_folder("reformat-temp")
        else:
            if root_path is not None:
                Common.show_message(QMessageBox.Warning, "\"" + root_path + "\" folder does not exist."
                                                                            "\nPlease make it and then retry.",
                                    "", "Folder Not Exist", "")
            else:
                Common.show_message(QMessageBox.Warning, "Root path does not exist."
                                                                            "\nPlease make it and then retry.",
                                    "", "Folder Not Exist", "")

    def init_status_bar(self, mes):
        self.ui_1_home.set_statusbar(mes)
        self.ui_2_create_new_case.set_statusbar(mes)
        self.ui_3_select_target_photo.set_statusbar(mes)
        self.ui_4_probing.set_statusbar(mes)
        self.ui_5_probe_report_preview.set_statusbar(mes)
        self.ui_6_probe_report.set_statusbar(mes)
        self.ui_7_prove_report_list.set_statusbar(mes)