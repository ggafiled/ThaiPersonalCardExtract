from ..utils import Language, Provider, automatic_brightness_and_contrast
from collections import namedtuple
import os
import cv2
import sys
import yaml
import numpy as np
import pytesseract
import easyocr
from PIL import Image
from pathlib import Path

class DrivingLicense:
    def __init__(self,
                 lang: Language = Language.MIX,
                 provider: Provider = Provider.DEFAULT,
                 template_threshold: float = 0.7,
                 sift_rate: int = 25000,
                 tesseract_cmd: str = None,
                 save_extract_result: bool = False,
                 path_to_save: str = None):

        self.lang = lang
        self.provider = provider
        self.root_path = Path(__file__).parent.parent
        self.template_threshold = template_threshold
        self.image = None
        self.save_extract_result = save_extract_result
        self.path_to_save = path_to_save
        self.index_params = dict(algorithm=0, tree=5)
        self.search_params = dict()
        self.good = []
        self.cardInfo = {
            "mix": {
                "License_Number": "",
                "IssueDateTH": "",
                "ExpiryDateTH": "",
                "IssueDateEN": "",
                "ExpiryDateEN": "",
                "NameTH": "",
                "NameEN": "",
                "BirthDayTH": "",
                "BirthDayEN": "",
                "Identity_Number": "",
                "Province": "",
            },
            "tha": {
                "License_Number": "",
                "IssueDateTH": "",
                "ExpiryDateTH": "",
                "NameTH": "",
                "BirthDayTH": "",
                "Identity_Number": "",
                "Province": "",
            },
            "eng": {
                "License_Number": "",
                "IssueDateEN": "",
                "ExpiryDateEN": "",
                "NameEN": "",
                "BirthDayEN": "",
                "Identity_Number": "",
                "Province": "",
            }
        }

        if sys.platform.startswith("win"):
            if tesseract_cmd is None:
                raise ValueError("Please define your tesseract command path.")
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        if save_extract_result is True:
            if path_to_save is None or path_to_save is "":
                raise ValueError("Please define your path to save extracted images.")

        self.flann = cv2.FlannBasedMatcher(self.index_params, self.search_params)
        self.sift = cv2.SIFT_create(sift_rate)
        if str(provider) == str(Provider.EASYOCR) or str(provider) == str(Provider.DEFAULT):
            self.reader = easyocr.Reader(['th', 'en'], gpu=True)
        self.__loadSIFT()
        self.h, self.w = self.source_image_front_tempalte.shape

    def __loadSIFT(self):
        self.source_image_front_tempalte = self.__readImage(
            os.path.join(self.root_path, 'datasets', 'driving_license/thai-driving-license-template.jpg'))
        self.source_front_kp, self.source_front_des = self.sift.detectAndCompute(self.source_image_front_tempalte, None)
        with open(os.path.join(self.root_path, 'datasets', 'driving_license/config.yaml'), 'r') as f:
            try:
                self.roi_extract = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                raise ValueError(f"Can't load config file {exc}.")

    def __readImage(self, image=None):
        try:
            img = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
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
        for index, box in enumerate(
                self.roi_extract["roi_extract"] if str(self.lang) == str(Language.MIX) else filter(
                    lambda item: str(self.lang) in item["lang"],
                    self.roi_extract["roi_extract"])):
            imgCrop = self.image_scan[box["point"][1]:box["point"][3], box["point"][0]:box["point"][2]]
            imgCrop = cv2.convertScaleAbs(imgCrop)
            imgCrop = automatic_brightness_and_contrast(imgCrop)[0]

            if str(self.provider) == Provider.DEFAULT.value:
                if str(box["provider"]) == str(str(Provider.EASYOCR)):
                    self.cardInfo[str(self.lang)][box["name"]] = " ".join(str.strip("".join(self.reader.readtext(imgCrop, detail=0, paragraph=True, width_ths=1.0, blocklist=box["blocklist"]))).split())
                elif str(box["provider"]) == str(Provider.TESSERACT):
                    self.cardInfo[str(self.lang)][box["name"]] = str.strip(
                        " ".join(pytesseract.image_to_string(imgCrop, lang=box["lang"].split(",")[0], config=box["tesseract_config"])
                            .replace('\n', '')
                            .replace('\x0c', '')
                            .replace('-', '')
                            .replace('"', '')
                            .replace("'", '')
                            .split()))
            elif str(self.provider) == str(Provider.EASYOCR):
                self.cardInfo[str(self.lang)][box["name"]] = " ".join(str.strip(
                        "".join(self.reader.readtext(imgCrop, detail=0, paragraph=True, width_ths=1.0, blocklist=box["blocklist"]))).split())
            elif str(self.provider) == str(Provider.TESSERACT):
                self.cardInfo[str(self.lang)][box["name"]] = str.strip(
                    " ".join(pytesseract.image_to_string(imgCrop, lang=box["lang"].split(",")[0], config=box["tesseract_config"])
                            .replace('\n', '')
                            .replace('\x0c', '')
                            .replace('-', '')
                            .replace('"', '')
                            .replace("'", '')
                            .split()))

            if self.save_extract_result:
                Image.fromarray(imgCrop).save(os.path.join(self.path_to_save, f'{box["name"]}.jpg'), compress_level=3)

        _card = namedtuple('Card',self.cardInfo[str(self.lang)].keys())(*self.cardInfo[str(self.lang)].values())
        return _card

    def extractInfo(self, image):
        self.image = self.__readImage(image)
        self.process_kp, self.process_des = self.sift.detectAndCompute(self.image, None)
        self.__compareTemplateSimilarity(self.process_des, self.source_front_des)
        self.__findAndWrapObject()
        return self.__extractItems()
