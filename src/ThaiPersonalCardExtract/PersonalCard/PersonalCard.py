from ..utils import *
import os
import cv2
import sys
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
        self.roi_extract = [
            [(258, 38), (543, 72), 'text', 'Identification_Number', 'eng,tha',
             '--oem 1 -c tessedit_char_whitelist=0123456789', 'tesseract'],
            [(165, 65), (545, 110), 'text', 'FullNameTH', 'tha', '--dpi 300 --psm 7 --oem 1', 'easyocr'],
            [(223, 105), (422, 130), 'text', 'NameEN', 'eng',
             '--dpi 300 --psm 13 --oem 1 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz. "',
             'tesseract'],
            [(264, 134), (449, 152), 'text', 'LastNameEN', 'eng',
             '--dpi 300 --psm 13 --oem 1 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
             'tesseract'],
            [(258, 154), (406, 182), 'text', 'BirthdayTH', 'tha', '--dpi 300', 'easyocr'],
            [(295, 179), (438, 207), 'text', 'BirthdayEN', 'eng', '--dpi 300 --psm 7 --oem 1', 'tesseract'],
            [(240, 208), (309, 233), 'text', 'Religion', 'tha,eng', '--dpi 300 --psm 7 --oem 1', 'easyocr'],
            [(60, 220), (410, 278), 'text', 'Address', 'tha,eng', '--dpi 300 --psm 13 --oem 1', 'easyocr'],
            [(50, 275), (140, 297), 'text', 'DateOfIssueTH', 'tha', '--dpi 300', 'easyocr'],
            [(50, 313), (147, 332), 'text', 'DateOfIssueEN', 'eng', '--dpi 300 --psm 7 --oem 1', 'tesseract'],
            [(332, 275), (436, 300), 'text', 'DateOfExpiryTH', 'tha', '--dpi 300', 'easyocr'],
            [(327, 312), (436, 333), 'text', 'DateOfExpiryEN', 'eng', '--dpi 300 --psm 7 --oem 1', 'tesseract']
        ]
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
        self.reader = easyocr.Reader(['th', 'en'], gpu=True) if str(provider) == str(Provider.EASYOCR) or str(
            Provider.DEFAULT) else None
        self.__loadSIFT()
        self.h, self.w = self.source_image_front_tempalte.shape

    def __loadSIFT(self):
        self.source_image_front_tempalte = self.__readImage(
            os.path.join(self.root_path, 'datasets', 'identity_card/personal-card-template.jpg'))
        self.source_image_back_tempalte = self.__readImage(os.path.join(
            self.root_path, 'datasets', 'identity_card/personal-card-back-template.jpg'))
        self.source_front_kp, self.source_front_des = self.sift.detectAndCompute(self.source_image_front_tempalte, None)
        self.source_back_kp, self.source_back_des = self.sift.detectAndCompute(self.source_image_back_tempalte, None)

    def __readImage(self, image=None):
        try:
            img = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
            img = cv2.convertScaleAbs(img)
            return img
        except cv2.error as e:
            raise ValueError(f"Can't read image from source. cause {e.msg}")

    def __compareTemplateSimilarity(self, queryDescriptors, trainDescriptors):
        matches = self.flann.knnMatch(queryDescriptors, trainDescriptors, k=2)
        for x, y in matches:
            if x.distance < self.template_threshold * y.distance:
                self.good.append(x)

    def __findAndWrapObject(self):
        if len(self.good) > 10:
            processPoints = np.float32([self.process_kp[m.queryIdx].pt for m in self.good]).reshape(-1, 1, 2)
            sourcePoints = np.float32([self.source_front_kp[m.trainIdx].pt for m in self.good]).reshape(-1, 1, 2)

            M, _ = cv2.findHomography(processPoints, sourcePoints, cv2.RANSAC, 5.0)
            self.image_scan = cv2.warpPerspective(self.image, M, (self.w, self.h))

        if self.save_extract_result:
            cv2.imwrite(os.path.join(self.path_to_save, 'image_scan.jpg'), self.image_scan)

    def __extractItems(self):
        for index, box in enumerate(
                self.roi_extract if str(self.lang) == str(Language.MIX) else filter(lambda item: str(self.lang) in item[4],
                                                                          self.roi_extract)):
            imgCrop = self.image_scan[box[0][1]:box[1][1], box[0][0]:box[1][0]]
            imgCrop = cv2.adaptiveThreshold(imgCrop, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 8)
            imgCrop = cv2.copyMakeBorder(imgCrop, 10, 10, 10, 10, cv2.BORDER_ISOLATED, value=[255, 255, 255])

            if str(self.provider) == Provider.DEFAULT.value:
                if str(box[6]) == str(str(Provider.EASYOCR)):
                    self.cardInfo[str(self.lang)][box[3]] = " ".join(str.strip("".join(self.reader.readtext(imgCrop, detail=0, paragraph=True, width_ths=1.0))).split())
                elif str(box[6]) == str(Provider.TESSERACT):
                    self.cardInfo[str(self.lang)][box[3]] = str.strip(
                        " ".join(pytesseract.image_to_string(imgCrop, lang=box[4].split(",")[0], config=box[5])
                            .replace('\n', '')
                            .replace('\x0c', '')
                            .replace('-', '')
                            .replace('"', '')
                            .replace("'", '')
                            .split()))
            elif str(self.provider) == str(Provider.EASYOCR):
                self.cardInfo[str(self.lang)][box[3]] = " ".join(str.strip(
                        "".join(self.reader.readtext(imgCrop, detail=0, paragraph=True, width_ths=1.0))).split())
            elif str(self.provider) == str(Provider.TESSERACT):
                self.cardInfo[str(self.lang)][box[3]] = str.strip(
                    " ".join(pytesseract.image_to_string(imgCrop, lang=box[4].split(",")[0], config=box[5])
                            .replace('\n', '')
                            .replace('\x0c', '')
                            .replace('-', '')
                            .replace('"', '')
                            .replace("'", '')
                            .split()))

            if self.save_extract_result:
                Image.fromarray(imgCrop).save(os.path.join(self.path_to_save, f'{box[3]}.jpg'), compress_level=3)

        if str(self.lang) == str(Language.MIX):
            extract_th = self.cardInfo[str(self.lang)]["FullNameTH"].split(' ')
            self.cardInfo[str(self.lang)]["PrefixTH"] = str("".join(extract_th[0]))
            self.cardInfo[str(self.lang)]["NameTH"] = str(
                "".join(extract_th[1] if len(extract_th) > 2 else extract_th[-1]))
            self.cardInfo[str(self.lang)]["LastNameTH"] = str("".join(extract_th[-1]))

            extract_en = self.cardInfo[str(self.lang)]["NameEN"].split(' ')
            self.cardInfo[str(self.lang)]["PrefixEN"] = str("".join(extract_en[0]))
            self.cardInfo[str(self.lang)]["NameEN"] = str("".join(extract_en[1:]))
        elif str(self.lang) == str(Language.THAI):
            extract_th = self.cardInfo[str(self.lang)]["FullNameTH"].split(' ')
            print(f"len {extract_th}")
            self.cardInfo[str(self.lang)]["PrefixTH"] = str("".join(extract_th[0]))
            self.cardInfo[str(self.lang)]["NameTH"] = str(
                "".join(extract_th[1] if len(extract_th) > 2 else extract_th[-1]))
            self.cardInfo[str(self.lang)]["LastNameTH"] = str("".join(extract_th[-1]))
        elif str(self.lang) == str(Language.ENGLISH):
            extract_en = self.cardInfo[str(self.lang)]["NameEN"].split(' ')
            self.cardInfo[str(self.lang)]["PrefixEN"] = str(extract_en[0])
            self.cardInfo[str(self.lang)]["NameEN"] = str(extract_en[1:])

        return self.cardInfo[str(self.lang)]

    def extractInfo(self, image):
        self.image = self.__readImage(image)
        self.process_kp, self.process_des = self.sift.detectAndCompute(self.image, None)
        self.__compareTemplateSimilarity(self.process_des, self.source_front_des)
        self.__findAndWrapObject()
        return self.__extractItems()
