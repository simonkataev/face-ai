from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox

from commons.common import Common
from commons.probing_result import ProbingResult
from commons.gen_report import export_report_pdf, gen_pdf_filename

import os, uuid
from zipfile import ZIP_DEFLATED, ZipFile
from pathlib import Path


class ThreadResult(object):
    def __init__(self):
        super().__init__()
        self.status = False
        self.message = ""


class ZipThread(QThread, ProbingResult):
    finished_zip_signal = pyqtSignal(ThreadResult)

    def __init__(self, probe_result, zip_location, parent=None):
        QThread.__init__(self, parent)
        self.reports = probe_result
        self.zip_location = zip_location
        self.res = ThreadResult()

    def run(self) -> None:
        self.zip_all_reports()

    def _itertarget(self, target: Path):
        if target.is_file():
            yield target
        elif target.is_dir():
            yield from (t for t in target.rglob('*') if t.is_file())

    def zip_all_reports(self):
        try:
            temp_path = Common.get_reg(Common.REG_KEY)
            if temp_path:
                temp_path = temp_path + "/" + Common.TEMP_PATH
            else:
                temp_path = Common.STORAGE_PATH + "/" + Common.TEMP_PATH
            Common.create_path(temp_path)
            temp_folder = temp_path + "/" + str(uuid.uuid4()) + "/"
            Common.create_path(temp_folder)

            for report in self.reports:
                filename = gen_pdf_filename(report.probe_id, report.case_info.case_number, report.case_info.case_PS)
                export_report_pdf(temp_folder, filename, filename)

            with ZipFile(self.zip_location, 'w', ZIP_DEFLATED) as allzip:
                for f in self._itertarget(Path(temp_folder)):
                    with f.open('rb') as b:
                        data = b.read()
                    filepath = str(f.relative_to(temp_folder))
                    allzip.writestr(filepath, data)
                    os.remove(temp_folder + filepath)
            os.rmdir(temp_folder)

            self.res.status = True
            self.res.message = ""
            self.finished_zip_signal.emit(self.res)
        except Exception as e:
            self.res.status = False
            self.res.message = e
            self.finished_zip_signal.emit(self.res)
