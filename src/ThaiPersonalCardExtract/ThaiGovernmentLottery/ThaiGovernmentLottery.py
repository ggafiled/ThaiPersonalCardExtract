from collections import namedtuple
from pylibdmtx.pylibdmtx import decode
from pathlib import Path
import os
import cv2
import yaml
import numpy as np
from PIL import Image

Lottery = namedtuple('Lottery',['LotteryNumber','LessonNumber','SetNumber','Year'])

class ThaiGovernmentLottery:
    def __init__(self,
                 template_threshold: float = 0.7,
                 sift_rate: int = 25000,
                 save_extract_result: bool = False,
                 path_to_save: str = None):

        self.root_path = Path(__file__).parent.parent
        self.template_threshold = template_threshold
        self.image = None
        self.save_extract_result = save_extract_result
        self.path_to_save = path_to_save
        self.index_params = dict(algorithm=0, tree=5)
        self.search_params = dict()
        self.good = []

        if save_extract_result is True:
            if path_to_save is None or path_to_save is "":
                raise ValueError("Please define your path to save extracted images.")

        self.flann = cv2.FlannBasedMatcher(self.index_params, self.search_params)
        self.sift = cv2.SIFT_create(sift_rate)
        self.__loadSIFT()
        self.h, self.w, *other = self.source_image_front_tempalte.shape

    def __loadSIFT(self):
        self.source_image_front_tempalte = self.__readImage(
            os.path.join(self.root_path, 'datasets', 'thai_government_lottery/thai-government-lottery-tamplate.jpg'))
        self.source_front_kp, self.source_front_des = self.sift.detectAndCompute(self.source_image_front_tempalte, None)
        with open(os.path.join(self.root_path, 'datasets', 'thai_government_lottery/config.yaml'), 'r') as f:
            try:
                self.roi_extract = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                raise ValueError(f"Can't load config file {exc}.")

    def __readImage(self, image=None):
        try:
            img = cv2.imread(image)
            return img
        except cv2.error as e:
            raise ValueError(f"Can't read image from source. cause {e.msg}")

    def __compareTemplateSimilarity(self, queryDescriptors, trainDescriptors):
        matches = self.flann.knnMatch(queryDescriptors, trainDescriptors, k=2)
        for x, y in matches:
            if x.distance < self.template_threshold * y.distance:
                self.good.append(x)

    def __findAndWrapObject(self):
        if len(self.good) > 30:
            processPoints = np.float32([self.process_kp[m.queryIdx].pt for m in self.good]).reshape(-1, 1, 2)
            sourcePoints = np.float32([self.source_front_kp[m.trainIdx].pt for m in self.good]).reshape(-1, 1, 2)

            M, _ = cv2.findHomography(processPoints, sourcePoints, cv2.RANSAC, 5.0)
            self.image_scan = cv2.warpPerspective(self.image, M, (self.w, self.h))
        else:
            self.image_scan = self.image

        if self.save_extract_result:
            cv2.imwrite(os.path.join(self.path_to_save, 'image_scan.jpg'), self.image_scan)

    def __extractItems(self):
        for index, box in enumerate(self.roi_extract["roi_extract"]):
            imgCrop = self.image_scan[box["point"][1]:box["point"][3], box["point"][0]:box["point"][2]]
            imgCrop = cv2.convertScaleAbs(imgCrop)

            if str(box["provider"]) == "qrcode":
                self.result = decode((imgCrop.tobytes(), imgCrop.shape[1], imgCrop.shape[0]))[0].data.decode("ascii")

            if self.save_extract_result:
                Image.fromarray(imgCrop).save(os.path.join(self.path_to_save, f'{box["name"]}.jpg'), compress_level=3)

        Year, LessonNumber, SetNumber, LotteryNumber = self.result.split("-",4)

        _lottery = Lottery(Year=Year, LotteryNumber=LotteryNumber, LessonNumber=LessonNumber, SetNumber=SetNumber)

        return _lottery

    def extractInfo(self, image):
        self.image = self.__readImage(image)
        self.process_kp, self.process_des = self.sift.detectAndCompute(self.image, None)
        self.__compareTemplateSimilarity(self.process_des, self.source_front_des)
        self.__findAndWrapObject()
        return self.__extractItems()
