from ..utils import Language, Provider, Card, remove_dot_noise
from collections import namedtuple
import re
import os
import cv2
import sys
import yaml
import base64, binascii
import numpy as np
import pytesseract
import easyocr
from PIL import Image
from pathlib import Path


class PersonalCard:
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
                "Identification_Number": "",
                "FullNameTH": "",
                "PrefixTH": "",
                "NameTH": "",
                "LastNameTH": "",
                "PrefixEN": "",
                "NameEN": "",
                "LastNameEN": "",
                "BirthdayTH": "",
                "BirthdayEN": "",
                "Religion": "",
                "Address": "",
                "DateOfIssueTH": "",
                "DateOfIssueEN": "",
                "DateOfExpiryTH": "",
                "DateOfExpiryEN": "",
                "LaserCode": "",
            },
            "tha": {
                "Identification_Number": "",
                "FullNameTH": "",
                "PrefixTH": "",
                "NameTH": "",
                "LastNameTH": "",
                "BirthdayTH": "",
                "Religion": "",
                "Address": "",
                "DateOfIssueTH": "",
                "DateOfExpiryTH": "",
                "LaserCode": "",
            },
            "eng": {
                "Identification_Number": "",
                "PrefixEN": "",
                "NameEN": "",
                "LastNameEN": "",
                "BirthdayEN": "",
                "Religion": "",
                "Address": "",
                "DateOfIssueEN": "",
                "DateOfExpiryEN": "",
                "LaserCode": "",
            }
        }

        if sys.platform.startswith("win"):
            if tesseract_cmd == None:
                raise ValueError("Please define your tesseract command path.")
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        if save_extract_result == True:
            if path_to_save == None or path_to_save == "":
                raise ValueError("Please define your path to save extracted images.")

        self.flann = cv2.FlannBasedMatcher(self.index_params, self.search_params)
        self.sift = cv2.SIFT_create(sift_rate)

        if str(provider) == str(Provider.EASYOCR) or str(provider) == str(Provider.DEFAULT):
            self.reader = easyocr.Reader(['en', 'th'], gpu=True)
        self.__loadSIFT()
        self.h, self.w, *other = self.source_image_front_tempalte.shape

    def __loadSIFT(self):
        self.source_image_front_tempalte = self.__readImage(
            os.path.join(self.root_path, 'datasets', 'identity_card/personal-card-template.jpg'))
        self.source_image_back_tempalte = self.__readImage(os.path.join(
            self.root_path, 'datasets', 'identity_card/personal-card-back-template.jpg'))
        self.source_front_kp, self.source_front_des = self.sift.detectAndCompute(self.source_image_front_tempalte, None)
        self.source_back_kp, self.source_back_des = self.sift.detectAndCompute(self.source_image_back_tempalte, None)
        with open(os.path.join(self.root_path, 'datasets', 'identity_card/config.yaml'), 'r') as f:
            try:
                self.roi_extract = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                raise ValueError(f"Can't load config file {exc}.")

    def __readImage(self, image=None):
        try:
            try:
                # handler if image params is base64 encode.
                img = cv2.imdecode(np.fromstring(base64.b64decode(image, validate=True), np.uint8), cv2.IMREAD_COLOR)
            except binascii.Error:
                # handler if image params is string path.
                img = cv2.imread(image, cv2.IMREAD_COLOR)

            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            if img.shape[1] > 1280:
                scale_percent = 60  # percent of original size
                width = int(img.shape[1] * scale_percent / 100)
                height = int(img.shape[0] * scale_percent / 100)
                dim = (width, height)
                img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
            return img
        except cv2.error as e:
            raise ValueError(f"Can't read image from source. cause {e.msg}")

    def __compareTemplateSimilarity(self, queryDescriptors, trainDescriptors):
        self.good = []
        matches = self.flann.knnMatch(queryDescriptors, trainDescriptors, k=2)
        for x, y in matches:
            if x.distance < self.template_threshold * y.distance:
                self.good.append(x)

    def __findAndWrapObject(self, side: Card = Card.FRONT_TEMPLATE):
        if len(self.good) > 30:
            processPoints = np.float32([self.process_kp[m.queryIdx].pt for m in self.good]).reshape(-1, 1, 2)
            sourcePoints = None
            if str(side) == str(Card.FRONT_TEMPLATE):
                sourcePoints = np.float32([self.source_front_kp[m.trainIdx].pt for m in self.good]).reshape(-1, 1, 2)
            else:
                sourcePoints = np.float32([self.source_back_kp[m.trainIdx].pt for m in self.good]).reshape(-1, 1, 2)

            M, _ = cv2.findHomography(processPoints, sourcePoints, cv2.RANSAC, 5.0)
            self.image_scan = cv2.warpPerspective(self.image, M, (self.w, self.h))
        else:
            self.image_scan = self.image

        if self.save_extract_result:
            cv2.imwrite(os.path.join(self.path_to_save, 'image_scan.jpg'), self.image_scan)

    def __extractItems(self, side: Card = Card.FRONT_TEMPLATE):
        for index, box in enumerate(
                self.roi_extract["roi_extract"][str(side)] if str(self.lang) == str(Language.MIX) else filter(
                    lambda item: str(self.lang) in item["lang"],
                    self.roi_extract["roi_extract"])):
            imgCrop = self.image_scan[box["point"][1]:box["point"][3], box["point"][0]:box["point"][2]]
            imgCrop = cv2.adaptiveThreshold(imgCrop[:,:,0], 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 8) + cv2.adaptiveThreshold(imgCrop[:,:,1], 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 8) + cv2.adaptiveThreshold(imgCrop[:,:,2], 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 8)

            if str(side) == str(Card.BACK_TEMPLATE):
                imgCrop = remove_dot_noise(imgCrop)

            if str(self.provider) == Provider.DEFAULT.value:
                if str(box["provider"]) == str(str(Provider.EASYOCR)):
                    self.cardInfo[str(self.lang)][box["name"]] = " ".join(str.strip(
                        "".join(self.reader.readtext(imgCrop, batch_size=4 ,detail=0, paragraph=False , width_ths=1.0, blocklist=box["blocklist"]))).split())
                elif str(box["provider"]) == str(Provider.TESSERACT):
                    self.cardInfo[str(self.lang)][box["name"]] = str.strip(
                        " ".join(pytesseract.image_to_string(imgCrop, lang=box["lang"].split(",")[0],
                                                             config=box["tesseract_config"])
                                 .replace('\n', '')
                                 .replace('\x0c', '')
                                 .replace('-', '')
                                 .replace('"', '')
                                 .replace("'", '')
                                 .split()))
            elif str(self.provider) == str(Provider.EASYOCR):
                self.cardInfo[str(self.lang)][box["name"]] = " ".join(str.strip(
                    "".join(self.reader.readtext(imgCrop, batch_size=4 ,detail=0, paragraph=False , width_ths=1.0, blocklist=box["blocklist"]))).split())
            elif str(self.provider) == str(Provider.TESSERACT):
                self.cardInfo[str(self.lang)][box["name"]] = str.strip(
                    " ".join(pytesseract.image_to_string(imgCrop, lang=box["lang"].split(",")[0],
                                                         config=box["tesseract_config"])
                             .replace('\n', '')
                             .replace('\x0c', '')
                             .replace('-', '')
                             .replace('"', '')
                             .replace("'", '')
                             .split()))

            if self.save_extract_result:
                Image.fromarray(imgCrop).save(os.path.join(self.path_to_save, f'{box["name"]}.jpg'), compress_level=3)

        if str(self.lang) == str(Language.MIX) and str(side) == str(Card.FRONT_TEMPLATE):
            extract_th = self.cardInfo[str(self.lang)]["FullNameTH"].split(' ')
            self.cardInfo[str(self.lang)]["PrefixTH"] = str("".join(extract_th[0]))
            self.cardInfo[str(self.lang)]["NameTH"] = str(
                "".join(extract_th[1] if len(extract_th) > 2 else extract_th[-1]))
            self.cardInfo[str(self.lang)]["LastNameTH"] = str("".join(extract_th[-1]))

            extract_en = self.cardInfo[str(self.lang)]["NameEN"].split(' ')
            self.cardInfo[str(self.lang)]["PrefixEN"] = str("".join(extract_en[0]))
            self.cardInfo[str(self.lang)]["NameEN"] = str("".join(extract_en[1:]))
        elif str(self.lang) == str(Language.THAI) and str(side) == str(Card.FRONT_TEMPLATE):
            extract_th = self.cardInfo[str(self.lang)]["FullNameTH"].split(' ')
            self.cardInfo[str(self.lang)]["PrefixTH"] = str("".join(extract_th[0]))
            self.cardInfo[str(self.lang)]["NameTH"] = str(
                "".join(extract_th[1] if len(extract_th) > 2 else extract_th[-1]))
            self.cardInfo[str(self.lang)]["LastNameTH"] = str("".join(extract_th[-1]))
        elif str(self.lang) == str(Language.ENGLISH) and str(side) == str(Card.FRONT_TEMPLATE):
            extract_en = self.cardInfo[str(self.lang)]["NameEN"].split(' ')
            self.cardInfo[str(self.lang)]["PrefixEN"] = str(extract_en[0])
            self.cardInfo[str(self.lang)]["NameEN"] = str(extract_en[1:])

        if str(side) == str(Card.BACK_TEMPLATE):
            self.cardInfo[str(self.lang)]["LaserCode"] = "".join(re.findall("([a-zA-Z0-9])",self.cardInfo[str(self.lang)]["LaserCode"])).upper()

        _card = namedtuple('Card', self.cardInfo[str(self.lang)].keys())(*self.cardInfo[str(self.lang)].values())
        return _card

    def extract_front_info(self, image):
        self.image = self.__readImage(image)
        self.process_kp, self.process_des = self.sift.detectAndCompute(self.image, None)
        self.__compareTemplateSimilarity(self.process_des, self.source_front_des)
        self.__findAndWrapObject(Card.FRONT_TEMPLATE)
        return self.__extractItems()

    def extract_back_info(self, image):
        self.image = self.__readImage(image)
        self.process_kp, self.process_des = self.sift.detectAndCompute(self.image, None)
        self.__compareTemplateSimilarity(self.process_des, self.source_back_des)
        self.__findAndWrapObject(Card.BACK_TEMPLATE)
        return self.__extractItems(side = Card.BACK_TEMPLATE)
