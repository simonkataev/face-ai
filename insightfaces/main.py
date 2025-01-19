import math
import os
import os.path as osp
import time

import cv2
import onnxruntime
from PyQt5.QtCore import pyqtSignal, QObject

from cryptophic.main import generate_token
from insightfaces.arcface_onnx import ArcFaceONNX
from insightfaces.scrfd import SCRFD
from commons.ntptime import ntp_get_time_from_object
from commons.systimer import SysTimer
from datetime import datetime

THRESHOLDS = [0.7, 0.8, 0.9]


class FaceAI(QObject):
    failed_probing_signal = pyqtSignal()
    success_probing_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.DETECT_ONNX_MODEL = "231658a02e26b60e629bfddd7067b3"
        self.RECOG_ONNX_MODEL = "8e9068219eb663d67500912dd0ce1f"
        self.onnxruntime = onnxruntime.set_default_logger_severity(3)
        self.assets_dir = osp.expanduser(r"C:\\Users\\" + os.getlogin() + r"\\.secure\\.encfiles")
        self.detector = None
        self.rec = None

    # Line slope given two points:
    def slope(self, x1, y1, x2, y2):  # Line slope given two points:
        return (y2 - y1) / (x2 - x1)

    def angle(self, s1, s2):
        return math.degrees(math.atan((s2 - s1) / (1 + (s2 * s1))))

    def init_json_data(self, data):
        data['time_used'] = {}
        data['thresholds'] = {}
        data['faces'] = []
        data['results'] = []
        data['image_id'] = "image id"
        data['request_id'] = "reques id"

        return data

    @staticmethod
    def get_similarity_str(data, similarity, path, unit=1):
        conclu = ""

        if similarity < THRESHOLDS[0] * unit:
            conclu = 'NOT SIMILAR PERSON'
        elif similarity >= THRESHOLDS[0] * unit and similarity < THRESHOLDS[1] * unit:
            conclu = 'Low match'
        elif similarity >= THRESHOLDS[1] * unit and similarity < THRESHOLDS[2] * unit:
            conclu = 'High match'
        else:
            conclu = 'Highest match'

        return conclu

    def append_json_data(self, data, x1, y1, x2, y2, angle, sim, path):
        _, token = generate_token()
        facedata = {
            'image_path': path,
            'face_token': str(token),
            'face_rectangle': {
                'left': int(x1),
                'top': int(y1),
                'width': int(x2 - x1),
                'height': int(y2 - y1),
            },
            'face_angle': "Roll: %d degree" % int(angle)
        }
        result = {
            'image_path': path,
            'face_token': str(token),
            'confidence': "%.4f" % sim,
            'user_id': "",
        }

        data['faces'].append(facedata)
        data['results'].append(result)

        return data

    def append_failed_json_data(self, data, path):
        _, token = generate_token()
        facedata = {
            'image_path': path,
            'face_token': str(token),
            'face_rectangle': {
                'left': -1,
                'top': -1,
                'width': -1,
                'height': -1,
            },
            'face_angle': -1
        }
        result = {
            'image_path': path,
            'face_token': str(token),
            'confidence': -1,
            'user_id': "",
        }

        data['faces'].append(facedata)
        data['results'].append(result)

        return data

    def append_empty_json_data(self, data):
        data['faces'].append([])
        data['results'].append([])

        return data

    def build_json_data(self, data, time):
        # data['time_used'] = int(time)
        data['time_used'] = datetime.strftime(ntp_get_time_from_object(SysTimer.now()), "%d/%m/%Y %I:%M %p")
        data['thresholds'] = {
            'Low match': "%d%%" % int(THRESHOLDS[0] * 100),
            'High match': "%d%%" % int(THRESHOLDS[1] * 100),
            'Highest match': "%d%%" % int(THRESHOLDS[2] * 100),
        }
        data['request_id'] = "request"
        # data = json.dumps(data, indent=4)

        return data

    def draw_results(self, bboxes, kpss, image, angles):
        bboxes = bboxes
        kpsses = kpss
        img = image
        color = (0, 255, 0)
        for i in range(bboxes.shape[0]):
            bbox = bboxes[i]
            kpss = kpsses[i]
            x1, y1, x2, y2, x3 = bbox
            cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), color, 1)
            # img = cv2.putText(img, 'sim: %f'%sim[i, 0], (int(x1), int(y1)), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 1, cv2.LINE_AA)
            img = cv2.putText(img, 'angle: %f' % angles[i], (int(x1), int(y1)), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 1,
                              cv2.LINE_AA)
            for kps in kpss:
                x, y = kps
                cv2.circle(img, (int(x), int(y)), 1, color, 2)
        cv2.imshow('Test', img)
        cv2.waitKey(0)

    # Takes as input image path and return True if it has face, or False if it has not face
    # "path" is image path.
    def is_face(self, path):
        image = cv2.imread(path.__str__())
        bboxes, kpss = self.detector.autodetect(image)
        if bboxes.shape[0] == 0:
            return 0
        if bboxes.shape[0] > 1:
            return 2
        return 1

    def is_models_exist(self):
        if (os.path.isfile(os.path.join(self.assets_dir, self.DETECT_ONNX_MODEL))) & (
        os.path.isfile(os.path.join(self.assets_dir, self.RECOG_ONNX_MODEL))):
            return (os.stat(os.path.join(self.assets_dir, self.DETECT_ONNX_MODEL)).st_size > 10000000) & (
                        os.stat(os.path.join(self.assets_dir, self.RECOG_ONNX_MODEL)).st_size > 10000000)
        return False

    def initialize(self):
        self.detector = SCRFD(os.path.join(self.assets_dir, self.DETECT_ONNX_MODEL))
        self.detector.prepare(0)
        model_path = os.path.join(self.assets_dir, self.RECOG_ONNX_MODEL)
        self.rec = ArcFaceONNX(model_path)
        self.rec.prepare(0)

    # Takes as input subject and target image paths and return json formated data
    # pair (path1, path2). "path1" is subject image path. "path2" is target image paths.
    def recognition(self, path1, paths2):
        jsondata = {}
        angles1 = {}
        angles2 = {}
        image2 = {}
        sim = {}
        feat2 = []

        jsondata = self.init_json_data(jsondata)

        start_time = time.time()

        image1 = cv2.imread(path1.__str__())
        bboxes1, kpss1 = self.detector.autodetect(image1, max_num=1)
        if bboxes1.shape[0] == 0:
            jsondata = self.append_empty_json_data(jsondata)
            jsondata = self.build_json_data(jsondata, 0)
            return -1.0, "Face not found in Image-1"

        for idx, bbox1 in enumerate(bboxes1):
            x1, y1, x2, y2, z2 = bboxes1[idx]
            pt1, pt2, pt3, pt4, pt5 = kpss1[idx]
            angles1[idx] = self.angle(self.slope(x1, y1, x2, y1), self.slope(pt1[0], pt1[1], pt2[0], pt2[1]))

        feat1 = self.rec.get(image1, kpss1[0])

        for index, path2 in enumerate(paths2):
            image2[index] = cv2.imread(path2.__str__())
            bboxes2, kpss2 = self.detector.autodetect(image2[index])
            if bboxes2.shape[0] == 0:
                jsondata = self.append_failed_json_data(jsondata, path2.__str__())
                # return -1.0, "Face not found in Image-2"
                self.failed_probing_signal.emit()
                continue

            for idx, bbox2 in enumerate(bboxes2):
                x1, y1, x2, y2, z2 = bbox2
                pt1, pt2, pt3, pt4, pt5 = kpss2[idx]
                angles2[index] = self.angle(self.slope(x1, y1, x2, y1), self.slope(pt1[0], pt1[1], pt2[0], pt2[1]))
                feat2 = self.rec.get(image2[index], kpss2[idx])
                sim[index] = self.rec.compute_sim(feat1, feat2)
                print("sim: ", sim[index])
                if sim[index] >= 0.7:
                    break
            if sim[index] >= 0.7:
                self.success_probing_signal.emit()  # emit success signal for updating gif.
            else:
                self.failed_probing_signal.emit()  # emit failed signal for updating gif

            res = self.get_similarity_str(jsondata, sim[index], path2.__str__())
            jsondata = self.append_json_data(jsondata, x1, y1, x2, y2, angles2[index], sim[index], path2.__str__())

        end_time = time.time()
        time_used = end_time - start_time

        jsondata = self.build_json_data(jsondata, time_used)

        # self.draw_results(bboxes1, kpss1, image1, angles1)

        return jsondata
