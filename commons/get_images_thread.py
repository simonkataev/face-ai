import pathlib

from PyQt5.QtCore import QThread, pyqtSignal

from commons.common import Common
from commons.get_image_metadata import GetImageMetadata
from commons.metadata_detail import MetadataDetail
from commons.processing_detail import ProcessingDetail


class GetImagesThread(QThread):
    finished_get_images_signal = pyqtSignal(object, object, object)

    def __init__(self, faceai, urls, parent=None):
        super().__init__(parent=parent)
        self.processing_details = []
        self.metadata = []
        self.urls = urls
        self.image_urls = []
        self.faceai = faceai
        self.direct = ""
        self.is_direct = False
        self.is_urls = False
        self.is_old_cases = False
        self.get_image_metadata = GetImageMetadata()

    def run(self):
        if self.is_urls:
            self.get_images_from_urls()
        if self.is_direct or self.is_old_cases:
            self.get_images_from_folder_path()
        self.finished_get_images_signal.emit(self.image_urls, self.processing_details, self.metadata)

    def get_images_from_urls(self):
        self.init_members()
        for url in self.urls:
            processing_detail = ProcessingDetail()
            metadata_detail = self.get_image_metadata.get_metadata(url)
            if Common.get_file_extension_from_path(url) == ".heic":
                url = Common.reformat_image(url)
                processing_detail.reformatted = True
            if self.faceai.is_face(url):
                url, processing_detail.resized = Common.resize_image(url, 500)
                self.image_urls.append(url)
                self.processing_details.append(processing_detail)
                self.metadata.append(metadata_detail)

    def get_images_from_folder_path(self):
        self.init_members()
        desktop = pathlib.Path(self.direct)
        for url in desktop.glob(r'**/*'):
            if Common.EXTENSIONS.count(url.suffix):
                meta_detail = self.get_image_metadata.get_metadata(url)
                processing_detail = ProcessingDetail()
                if Common.get_file_extension_from_path(url) == ".heic":
                    url = Common.reformat_image(url)
                    processing_detail.reformatted = True
                if self.faceai.is_face(url):
                    url, processing_detail.resized = Common.resize_image(url.__str__(), 500)
                    self.image_urls.append(url)
                    self.processing_details.append(processing_detail)
                    self.metadata.append(meta_detail)

    def init_flags(self, val):
        self.is_old_cases = val
        self.is_urls = val
        self.is_direct = val

    def init_members(self):
        self.image_urls.clear()
        self.processing_details.clear()
        self.metadata.clear()
