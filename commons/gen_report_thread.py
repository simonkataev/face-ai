import json
import os

from PyQt5.QtCore import QThread, QDateTime, pyqtSignal

from commons.common import Common
from commons.db_connection import DBConnection
from commons.gen_report import create_pdf, gen_pdf_filename
from commons.probing_result import ProbingResult
from cryptophic.main import encrypt_file_to
from datetime import datetime
from commons.systimer import SysTimer
from commons.ntptime import ntp_get_time_from_object


# class to use generate report from probing result.
# this class will use the GenReport class to write pdf file.
class GenReportThread(QThread):
    finished_generate_report_signal = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.probe_result = ProbingResult()

    def run(self) -> None:
        self.generate_report()
        self.finished_generate_report_signal.emit(self.probe_result)

    # save probe result and make probe report file as pdf.
    def generate_report(self):
        report_path = Common.get_reg(Common.REG_KEY)
        if report_path:
            report_path = report_path + "/" + Common.REPORTS_PATH
        else:
            report_path = Common.STORAGE_PATH + "/" + Common.REPORTS_PATH
        Common.create_path(report_path)
        temp_path = Common.get_reg(Common.REG_KEY)
        if temp_path:
            temp_path = temp_path + "/" + Common.TEMP_PATH
        else:
            temp_path = Common.STORAGE_PATH + "/" + Common.TEMP_PATH
        Common.create_path(temp_path)

        filename = gen_pdf_filename(self.probe_result.probe_id, self.probe_result.case_info.case_number,
                                    self.probe_result.case_info.case_PS)

        if not (self.probe_result.case_info.subject_image_url == '') and \
                not (len(self.probe_result.case_info.target_image_urls) == 0):
            self.write_probe_results_to_database()

        create_pdf(self.probe_result.probe_id, self.probe_result, os.path.join(temp_path, filename))
        encrypt_file_to(os.path.join(temp_path, filename), os.path.join(report_path, filename))

    # write probe result to database
    def write_probe_results_to_database(self):
        self.update_json_data()
        # make data to be inserted to database and insert
        probe_result = self.probe_result
        case_info = self.probe_result.case_info
        cases_fields = ["probe_id", "matched", "report_generation_time", "case_no",
                        "PS", "examiner_no", "examiner_name", "remarks",
                        "subject_url", "json_result", "created_date"]
        cases_data = [(probe_result.probe_id, probe_result.matched, probe_result.json_result["time_used"],
                       case_info.case_number, case_info.case_PS, case_info.examiner_no, case_info.examiner_name,
                       case_info.remarks, case_info.subject_image_url, json.dumps(probe_result.json_result),
                       datetime.strftime(ntp_get_time_from_object(SysTimer.now()), "%Y-%m-%d %H-%M-%S"))]
        target_fields = ["target_url", "case_id"]
        target_data = []
        db = DBConnection()
        # check the case with the inserting probe id exists
        if not db.is_exist_value("cases", "probe_id", probe_result.probe_id):
            case_id = db.insert_values("cases", cases_fields, cases_data)
            for target in case_info.target_image_urls:
                target_tuple = (target, case_id)
                target_data.append(target_tuple)
        # db.insert_values("targets", target_fields, target_data)

    # update probe result with copied image urls
    def update_json_data(self):
        # create path "FaceAI Media" if not exists
        # so that subject and target images will be saved to that directory
        media_path = Common.get_reg(Common.REG_KEY)
        if media_path:
            media_path = media_path + "/" + Common.MEDIA_PATH
        else:
            media_path = Common.STORAGE_PATH + "/" + Common.MEDIA_PATH
        Common.create_path(media_path)

        # copy subject and target images to media directory, after that, replace urls with urls in media folder
        path_buff = self.probe_result.probe_id + "-" + \
                    self.probe_result.case_info.case_number + "-" + \
                    Common.get_file_name_from_path(self.probe_result.case_info.subject_image_url)

        path_buff = media_path + "/subjects/" + path_buff
        self.probe_result.case_info.subject_image_url = \
            Common.copy_file(self.probe_result.case_info.subject_image_url, path_buff)
        target_images = []
        index = 0
        if not self.probe_result.case_info.is_used_old_cases:
            for result in self.probe_result.json_result['results']:
                image_path = result['image_path']
                target_buff = self.probe_result.probe_id + "-" + \
                              "-" + self.probe_result.case_info.case_number + "-" + \
                              Common.get_file_name_from_path(image_path)
                target_buff = media_path + "/targets/" + target_buff
                modified_target = Common.copy_file(image_path, target_buff)
                target_images.append(modified_target)
                self.probe_result.json_result["results"][index]["image_path"] = modified_target
                self.probe_result.json_result["faces"][index]["image_path"] = modified_target
                self.probe_result.case_info.target_image_urls = target_images
                index += 1
