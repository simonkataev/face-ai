import decimal
import json
import os.path
import os
import pathlib
import re
import shutil
import winreg
import time
from datetime import datetime

import cv2
import numpy as np
import pillow_heif
from PyQt5.QtCore import QFile
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMessageBox


class Common:
    JSON_RESULT_STYLE = "background:transparent; border-radius: 10px; " \
                        "border: 1px solid rgb(53, 132, 228); " \
                        "color: rgb(255,255,255); " \
                        "font-size: 10pt; font-family: Arial;"
    TARGET_LIST_STYLE = "background:transparent; border-radius: 10px; " \
                        "border: 1px solid rgb(53, 132, 228); "
    TARGET_LIST_STYLE_LABEL = "border:none"
    STATUS_BAR_HEIGHT = 20
    CASE_DETAIL_LINE_EDIT_HEIGHT = 40
    CASE_DETAIL_LINE_EDIT_WIDTH = 400
    REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\FaceAI\main.exe"
    STORAGE_PATH = "Data Storage"
    MEDIA_PATH = "Media"
    REPORTS_PATH = "Probe Reports"
    TEMP_PATH = "Temporary Data"
    REG_KEY = "DataFolder"
    EXPORT_PATH = r"C:\\Users\\" + os.getlogin() + r"\\Documents"
    MATCH_LEVEL = 70.00
    CASE_NUMBER_LENGTH = 14
    CASE_PS_LENGTH = 31
    CASE_EXAMINER_NAME_LENGTH = 63
    CASE_EXAMINER_NO_LENGTH = 20
    CASE_REMARKS_LENGTH = 139
    # CREATE_CASE_REGX = "\w"
    # CREATE_CASE_REGX = "[\u0020-\u007E]"
    # CREATE_CASE_REGX = r'[a-zA-Z0-9]+'
    # CREATE_CASE_REGX_FOR_REMOVE = r'[^a-zA-Z0-9]+'  #"/[ -~]/"
    # CREATE_CASE_REGX = r'/[ -~]/+'
    CREATE_CASE_REGX = r'[\u0020-\u007E]+'
    CREATE_CASE_REGX_FOR_REMOVE = r'[^\u0020-\u007E]+'  # "/[ -~]/"

    EXTENSIONS = ['.png', '.jpe?g', '.jpg', '.tif', '.jpeg', '.bmp']
    # IMAGE_FILTER = "Image Files (*.cur *.icns *.ico *.jpeg *.HEIF *.heif" \
    #                " *.jpg *.pbm *.pgm *.png *.ppm *.svg *.svgz *.tga" \
    #                " *.tif *.tiff *.wbmp" \
    #                " *.webp *.xbm *.xpm)"
    IMAGE_FILTER = "*.jpeg *.jpg *.png *.tif *.tiff *.bmp *.heic"
    PDF_FILTER = "PDF Files (*.pdf)"
    ZIP_FILTER = "ZIP Files (*.zip)"
    LABEL_MAX_HEIGHT_IN_ITEM = 30
    LABEL_MAX_WIDTH_IN_ITEM = 170
    VALUE_MAX_HEIGHT_IN_ITEM = 30
    VALUE_MAX_WIDTH_IN_ITEM = 230
    CROSS_BUTTON_SIZE = 30
    PAGINATION_BUTTON_SIZE = 40
    PAGINATION_GO_LABEL_SIZE = 90
    PAGINATION_NEXT_BUTTON_STYLE = "image: url(:/newPrefix/icon-next2.png); " \
                                   "border-radius: 10px;" \
                                   "background-repeat: no-repeat;" \
                                   "background-color: rgb(127, 0, 226);"
    PAGINATION_PREVIOUS_BUTTON_STYLE = "image: url(:/newPrefix/icon-back2.png); " \
                                       "border: 1px solid #7F00E2;" \
                                       "border-radius: 10px;" \
                                       "background-repeat: no-repeat;" \
                                       "background-color: rgb(127, 0, 226);"
    PAGINATION_BUTTON_STYLE = "border-radius: 10px;" \
                              "color: rgb(255, 255, 255);" \
                              "border: 1px solid white;" \
                              "background:transparent;"
    PAGINATION_BUTTON_ACTIVE_STYLE = "border-radius: 10px;" \
                                     "color: rgb(255, 255, 255);" \
                                     "border: 1px solid white;" \
                                     "background:transparent;" \
                                     "background-color:blue;"
    GO_BUTTON_STYLE = "border-radius: 10px;background: transparent;" \
                      "color: rgb(255, 255, 255);border: 1px solid white;"
    NUMBER_PER_PAGE = 5
    RESULT_ITEM_WIDGET_SIZE = 330
    REPORT_DESCRIPTION_MATCHED_FOR_SINGLE = "The subject photo has matched to the following target photo." \
                                            " Facial similarity score is attached herewith."
    REPORT_DESCRIPTION_MATCHED_FOR_MULTIPLE = "The subject photo has matched to the following target photos." \
                                              " Facial similarity scores are attached herewith."
    REPORT_DESCRIPTION_MATCHED_FOR_ENTIRE = "The subject photo has matched to the following target photos." \
                                            " Facial similarity scores are attached herewith."
    REPORT_DESCRIPTION_MATCHED_FOR_OLDCASE = "The subject photo has matched to the following old case photos." \
                                             " Facial similarity scores and old case details are attached herewith."
    REPORT_DESCRIPTION_NON_MATCHED = "The subject photo hasn't matched to any target photo."
    SELECTED_IMAGE_DESCRIPTION = " photos have been selected as target."
    GROWING_TEXT_EDIT_STYLE_PREVIEW_REPORT = "background:transparent;" \
                                             "border: 1px solid rgb(53, 132, 228);" \
                                             "color: rgb(255, 255, 255);font-size: 13pt;" \
                                             "font:bold;" \
                                             "font-family: Arial; "
    GROWING_TEXT_EDIT_STYLE_CREATE_CASE = "background:transparent;" \
                                          "border: 1px solid rgb(53, 132, 228);" \
                                          "color: rgb(255, 255, 255);font-size: 13pt;" \
                                          "font-family: Arial; "
    RASTER_IMAGE_ACCEPTED_NOTICE = "JPEG, PNG, TIF, BMP and HEIC files are accepted."

    PDF_NB_PARA1 = "The facial images were analyzed and compared using FaceAI, a facial recognition software incorporating advanced deep learning techniques, including convolutional neural networks (CNN). FaceAI utilizes CNN for facial feature extraction and facial landmark detection. This involves extracting high-level facial features such as the shape, texture, and spatial relationships of prominent facial components like the eyes, nose, and mouth."
    PDF_NB_PARA2 = "FaceAI generates a unique facial representation for each image based on these extracted features. The comparison process involves measuring the similarity between the reference image and the target image using cosine similarity, which produces a similarity score ranging from 0 to 1. A confidence threshold of 0.80 (80%) is applied to consider potential matches."
    PDF_NB_PARA3 = "The facial recognition report provided similarity scores represented in percentages. A similarity score of 80% or above indicates that the similarity scores are 0.80 or higher, which meets or exceeds the confidence threshold and is considered a match, as it indicates a high level of similarity between the facial images."
    PDF_NB_PARA4 = "It is important to note that while FaceAI provides accurate results in most cases, there are inherent limitations to automated facial recognition technology. False positives or false negatives can occur, and the software may require further manual verification by a trained human examiner. FaceAI's results should be interpreted as an aid to investigative analysis, and final conclusions should be based on a combination of automated results and human assessment."

    @staticmethod
    def clear_layout(layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                Common.clear_layout(child)

    @staticmethod
    def create_path(path_name):
        try:
            path = pathlib.Path(path_name)
            path.mkdir(parents=True, exist_ok=True)
        except Exception as ex:
            print(ex)

    @staticmethod
    def is_exist_folder(dir):
        return os.path.exists(os.path.join(dir))

    @staticmethod
    def check_exist_data_storage():
        root_path = Common.get_reg(Common.REG_KEY)
        is_exist = False
        if root_path:
            is_exist = Common.is_exist_folder(root_path)
        return is_exist, root_path

    @staticmethod
    def copy_file(from_path, to_path):
        Common.create_path(Common.get_folder_path(to_path))
        if not QFile.exists(to_path):
            QFile.copy(from_path, to_path)
        return to_path

    @staticmethod
    def get_file_name_from_path(url):
        pa = pathlib.Path(url)
        return pa.name

    @staticmethod
    def get_file_name_without_extension_from_path(url):
        fname = Common.get_file_name_from_path(url)
        return os.path.splitext(fname)[0]

    @staticmethod
    def get_file_extension_from_path(url):
        return os.path.splitext(url)[1]

    @staticmethod
    def remove_elements_from_list_tail(removing_list, start_index):
        ret_list = []
        list_len = len(removing_list)
        if start_index < list_len:
            for index in range(start_index):
                ret_list.append(removing_list[index])
        else:
            ret_list = removing_list.copy()
        return ret_list

    @staticmethod
    def resize_image(img_path, size):
        resized = False
        try:
            temp_path = Common.get_reg(Common.REG_KEY)
            if temp_path:
                temp_path = temp_path + "/" + Common.TEMP_PATH
            else:
                temp_path = Common.STORAGE_PATH + "/" + Common.TEMP_PATH
            Common.create_path(temp_path)
            temp_folder = temp_path + "/resize-temp/"
            Common.create_path(temp_folder)
            body_img = cv2.imread(img_path)
            fsize = os.stat(img_path).st_size
            if body_img is None:
                print('resize image: wrong path', img_path)
            else:
                img = np.array(body_img)
                rate = 1
                width = img.shape[0]
                height = img.shape[1]
                # if the size of image is larger than 6MB, the image will be resized.
                megasize = (fsize) / (1024 * 1024)
                if megasize > 6:
                    rate = (int)(megasize/6 + 1)
                    dim = (int(img.shape[1] / rate), int(img.shape[0] / rate))
                    img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
                    img_path = temp_folder + Common.get_file_name_from_path(img_path)
                    cv2.imwrite(img_path, img)
                    resized = True

                rate = 1
                if width > height:
                    rate = size / width
                else:
                    rate = size / height
                if rate > 1:
                    print("resized:", img_path)
                    dim = (int(img.shape[1] * rate), int(img.shape[0] * rate))
                    img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
                    img_path = temp_folder + Common.get_file_name_from_path(img_path)
                    cv2.imwrite(img_path, img)
                    # resized = True
        except IOError as e:
            print("resize image error:", e)
        return img_path, resized

    @staticmethod
    def reformat_image(img_path):
        try:
            temp_path = Common.get_reg(Common.REG_KEY)
            if temp_path:
                temp_path = temp_path + "/" + Common.TEMP_PATH
            else:
                temp_path = Common.STORAGE_PATH + "/" + Common.TEMP_PATH
            Common.create_path(temp_path)
            temp_folder = temp_path + "/reformat-temp/"
            Common.create_path(temp_folder)
            heif_file = pillow_heif.open_heif(img_path, convert_hdr_to_8bit=False, bgr_mode=True)
            np_array = np.asarray(heif_file)
            fname = Common.get_file_name_without_extension_from_path(img_path)
            img_path = temp_folder + fname + ".png"
            cv2.imwrite(img_path, np_array)
        except IOError as e:
            print("resize image error:", e)
        return img_path

    @staticmethod
    def remove_temp_folder(folder_name):
        temp_path = Common.get_reg(Common.REG_KEY)
        if temp_path:
            temp_path = temp_path + "/" + Common.TEMP_PATH
        else:
            temp_path = Common.STORAGE_PATH + "/" + Common.TEMP_PATH
        Common.create_path(temp_path)
        temp_folder = temp_path + "/" + folder_name
        Common.create_path(temp_folder)
        shutil.rmtree(temp_folder, ignore_errors=True)

    @staticmethod
    def remove_target_images():
        targets_path = Common.get_reg(Common.REG_KEY)
        if targets_path:
            targets_path = Common.get_reg(Common.REG_KEY) + "/" + Common.MEDIA_PATH + "/targets"
        else:
            # targets_path = Common.STORAGE_PATH + "/" + Common.MEDIA_PATH + "/targets"
            return

        desktop = pathlib.Path(targets_path)
        for url in desktop.glob(r'**/*'):
            os.remove(url)

    @staticmethod
    def make_pixmap_from_image(image_path, parent):
        img = cv2.imread(image_path)
        img = np.array(img)
        size = parent.size().width()
        rate = 0.75
        width = img.shape[1]
        height = img.shape[0]
        if width > height:
            rate = size / width
        else:
            rate = size / height
        dim = (int(img.shape[1] * rate), int(img.shape[0] * rate))
        img = cv2.resize(img, dim)
        height, width, channel = img.shape
        bytesPerLine = 3 * width
        qimage = QImage(img.tobytes(), width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap(qimage)
        lbl_x = 0
        lbl_y = 0
        if pixmap.size().width() > pixmap.size().height():
            lbl_y = (parent.size().height() - pixmap.height()) / 2
            # ret_label.setGeometry(0, lbl_y, pixmap.width(), pixmap.height())
        else:
            lbl_x = (parent.size().width() - pixmap.width()) / 2
            # ret_label.setGeometry(lbl_x, 0, pixmap.width(), pixmap.height())
        # ret_label.setPixmap(pixmap)
        return lbl_x, lbl_y, pixmap

    @staticmethod
    def is_empty(case_info):
        if case_info.case_number:
            return False
        return True

    @staticmethod
    def show_message(icon, text, information_text, title, detailed_text):
        msg = QMessageBox()
        msg.setStyleSheet("background-image: url(:/newPrefix/Background.png);")
        msg.setIcon(icon)
        msg.setText(text)
        msg.setInformativeText(information_text)
        msg.setWindowTitle(title)
        msg.setDetailedText(detailed_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    # this method make one integer with the number of integers,
    # each digit is between start and end
    @staticmethod
    def generate_digits(start, end, number):
        arr = np.random.uniform(start, end, number)
        arr = np.round(arr).astype(int)
        return "".join(str(x) for x in arr)

    @staticmethod
    def generate_probe_id():
        probe_id = str(Common.generate_digits(0, 9, 9))
        while Common.verify_probe_id(probe_id):
            return probe_id
        else:
            Common.generate_probe_id()

    # verify generated probe_id whether is already exist on database
    # if exist, return false
    @staticmethod
    def verify_probe_id(probe_id):
        return True

    @staticmethod
    def get_folder_path(absolute_file_path):
        return os.path.dirname(os.path.abspath(absolute_file_path))

    @staticmethod
    def get_reg(name):
        try:
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, Common.REG_PATH, 0,
                                          winreg.KEY_READ)
            value, regtype = winreg.QueryValueEx(registry_key, name)
            value = value.replace("\\", "/")
            winreg.CloseKey(registry_key)
            return value
        except WindowsError as wr:
            print(wr)
            return None

    @staticmethod
    def set_reg(name, value):
        try:
            winreg.CreateKey(winreg.HKEY_CURRENT_USER, Common.REG_PATH)
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, Common.REG_PATH, 0,
                                          winreg.KEY_WRITE)
            winreg.SetValueEx(registry_key, name, 0, winreg.REG_SZ, value)
            winreg.CloseKey(registry_key)
            return True
        except WindowsError:
            return False

    # sort list by attr.
    # if reverse is true, sorted by desc
    # sorting_list: list to be sorted,
    # attr: sort key
    # attr_type: attr type
    @staticmethod
    def sort_list_by_float_attribute(sorting_list, attr, attr_type, reverse):
        ret = []

        if len(sorting_list):
            if attr_type == 'string':
                for item in sorting_list:
                    item[attr] = float(item[attr])
            ret = sorted(sorting_list, key=lambda x: x[attr], reverse=reverse)
            for item in ret:
                item[attr] = Common.round_float_string_natural(item[attr]) + "%"
        return ret

    # round the float string up to 2 decimals
    @staticmethod
    def round_float_string(float_string):
        sim = float(float_string) * 100
        decimal_value = decimal.Decimal(sim)
        # rounding the number upto 2 digits after the decimal point
        rounded = decimal_value.quantize(decimal.Decimal('0.00'))
        return str(rounded)

    # round the float string up to 2 decimals
    @staticmethod
    def round_float_string_natural(value):
        decimal_value = decimal.Decimal(value)
        # rounding the number upto 2 digits after the decimal point
        rounded = decimal_value.quantize(decimal.Decimal('0.00'))
        return str(rounded)

    @staticmethod
    def get_available_appendix_num(name, ext):
        is_exist = os.path.isfile(name+ext)
        if not is_exist:
            return (is_exist, name)
        else:
            loop = True
            appendix = 1
            while loop:
                name_ = "%s (%d)" % (name, appendix)
                is_exist_ = os.path.isfile(name_+ext)
                if not is_exist_:
                    name = name_
                    loop = False
                time.sleep(0.01)
                appendix+=1
            return (is_exist, name)
    @staticmethod
    def convert_json_for_page(probing_result):

        faces = probing_result.json_result['faces']
        faces_buff = []
        ret_buff = ""
        if len(faces):
            face_index = 0
            ret_buff = "Subject photo metadata: \n"
            ret_buff += Common.convert_metadata2json(str(probing_result.json_result['time_used']),
                                                     probing_result.case_info.subject_image_metadata,
                                                     None,
                                                     probing_result.case_info.subject_image_processing_detail)
            for face in faces:
                ret_buff += "\nTarget photo " + str(face_index + 1) + " metadata:\n"
                roll = face['face_angle']
                roll_buff = re.sub('Roll: ', '', roll)
                roll_buff = re.sub(' degree', '', roll_buff)
                ret_buff += Common.convert_metadata2json(str(probing_result.json_result['time_used']),
                                                        probing_result.case_info.target_images_metadata[face_index],
                                                        roll_buff,
                                                        probing_result.case_info.target_images_processing_details[
                                                            face_index])                
                face_index += 1

        # js_result = json.dumps(ret_buff, indent=4, sort_keys=True)
        print(ret_buff)
        return ret_buff

    @staticmethod
    def convert_metadata2json(used_time, metadata, roll_data, processing):
        json_buff = {
            "Date and time: ": metadata.processed_time,
            "Source information": {
                "device": metadata.device
            },
            "Location": {
                "longitude": metadata.longitude,
                "latitude": metadata.latitude,
                "street": metadata.street
            },
            "Image quality and resolution": {
                "quality": "",
                "XResolution": metadata.XResolution,
                "YResolution": metadata.YResolution,
                "width": metadata.width,
                "height": metadata.height,
                "file size": metadata.fsize,
                "file type": metadata.type
                # "roll_angle": roll_data
            },
            "Processing detail": {
                "reformatted": processing.reformatted,
                "resized": processing.resized
            }
        }
        if roll_data is not None:
            json_buff.get("Image quality and resolution")["roll_angle"] = roll_data
        js_result = json.dumps(json_buff, indent=4, sort_keys=True)
        return js_result

    @staticmethod
    def convert_string2datetime(timestr, formatstr):
        # ddd = datetime.strptime("2023-04-29 13-59-02", '%Y-%m-%d %H-%M-%S')
        # print(ddd.strftime("%d/%m/%Y %I:%M %p"))
        formated_datetime = datetime.strptime(timestr, formatstr)
        return formated_datetime.strftime("%d/%m/%Y %I:%M %p")