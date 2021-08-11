import enum
import os
import cv2
import numpy as np
import pytesseract
import easyocr


class PersonalCardLanguage(enum.Enum):
    THAI = 'th'
    ENGLISH = 'en'


class PersonalCard:
    def __init__(self,
                 lang: PersonalCardLanguage = PersonalCardLanguage.THAI,
                 template_threshold=0.7,
                 sift_rate=25000,
                 tesseract_cmd=None,
                 save_extract_result=False,
                 path_to_save=None):

        self.lang = lang
        self.root_path = os.path.split(__file__)[0]
        self.template_threshold = template_threshold
        self.image = None
        self.save_extract_result = save_extract_result
        self.path_to_save = path_to_save
        self.index_params = dict(algorithm=0, tree=5)
        self.search_params = dict()
        self.flann = cv2.FlannBasedMatcher(self.index_params, self.search_params)
        self.sift = cv2.SIFT_create(sift_rate)
        self.reader = easyocr.Reader(['th', 'en'], gpu=True)
        self.loadSIFT()
        self.h, self.w = self.source_image_front_tempalte.shape
        self.roi_extract = [
            [(258, 38), (543, 72), 'text', 'Identification_Number', 'eng',
             '--oem 1 -c tessedit_char_whitelist=0123456789', 'tesseract'],
            [(165, 65), (545, 110), 'text', 'FullNameTH', 'tha', '--dpi 300', 'easyocr'],
            [(223, 105), (422, 130), 'text', 'NameEN', 'eng',
             '--dpi 300 --psm 13 --oem 1 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz. "',
             'tesseract'],
            [(264, 134), (449, 152), 'text', 'LastNameEN', 'eng',
             '--dpi 300 --psm 13 --oem 1 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
             'tesseract'],
            [(291, 179), (438, 207), 'text', 'Birthday', 'eng', '--dpi 300 --psm 13 --oem 1', 'tesseract'],
            [(240, 208), (309, 233), 'text', 'Religion', 'tha', '--dpi 300 --psm 13 --oem 1', 'easyocr'],
            [(60, 220), (410, 278), 'text', 'Address', 'tha', '--dpi 300 --psm 13 --oem 1', 'easyocr'],
        ]
        if os.name is 'nt':
            if tesseract_cmd is None:
                raise ValueError("Please define your tesseract command path.")
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        if save_extract_result is True:
            if path_to_save is None or path_to_save is "":
                raise ValueError("Please define your path to save extracted images.")

    def loadSIFT(self):
        self.source_image_front_tempalte = self.readImage(
            os.path.join(self.root_path, 'datasets', 'personal-card-template.jpg'))
        self.source_image_back_tempalte = self.readImage(os.path.join(
            self.root_path, 'datasets', 'personal-card-back-template.jpg'))
        self.source_front_kp, self.source_front_des = self.sift.detectAndCompute(self.source_image_front_tempalte, None)
        self.source_back_kp, self.source_back_des = self.sift.detectAndCompute(self.source_image_back_tempalte, None)

    def readImage(self, image=None):
        try:
            img = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
            img = cv2.convertScaleAbs(img)
            return img
        except cv2.error as e:
            raise ValueError(f"Can't read image from source. cause {e.msg}")

    def compareTemplateSimilarity(self, queryDescriptors, trainDescriptors):
        matches = self.flann.knnMatch(queryDescriptors, trainDescriptors, k=2)
        self.good = []
        for x, y in matches:
            if x.distance < self.template_threshold * y.distance:
                self.good.append(x)

    def findAndWrapObject(self):
        if len(self.good) > 10:
            processPoints = np.float32([self.process_kp[m.queryIdx].pt for m in self.good]).reshape(-1, 1, 2)
            sourcePoints = np.float32([self.source_front_kp[m.trainIdx].pt for m in self.good]).reshape(-1, 1, 2)

            M, _ = cv2.findHomography(processPoints, sourcePoints, cv2.RANSAC, 5.0)
            self.image_scan = cv2.warpPerspective(self.image, M, (self.w, self.h))

        if self.save_extract_result:
            cv2.imwrite(os.path.join(self.path_to_save, 'image_scan.jpg'),  self.image_scan)

    def _extractItems(self):
        cardInfo = {
            "Identification_Number": "",
            "FullNameTH": "",
            "NameEN": "",
            "LastNameEN": "",
            "Birthday": "",
            "Religion": "",
            "Address": "",
        }
        for index, box in enumerate(self.roi_extract):
            imgCrop = self.image_scan[box[0][1]:box[1][1], box[0][0]:box[1][0]]
            imgCrop = cv2.adaptiveThreshold(imgCrop, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 8)
            imgCrop = cv2.copyMakeBorder(imgCrop, 10, 10, 10, 10, cv2.BORDER_ISOLATED, value=[255, 255, 255])

            if box[6] == 'easyocr':
                if len(box) == 8:
                    cardInfo[box[3]] = ''.join(
                        self.reader.readtext(imgCrop, detail=0, paragraph=True, width_ths=1.0, allowlist=box[7]))
                else:
                    cardInfo[box[3]] = ''.join(self.reader.readtext(imgCrop, detail=0, paragraph=True, width_ths=1.0))
            else:
                cardInfo[box[3]] = str.strip(
                    pytesseract.image_to_string(imgCrop, lang=box[4], config=box[5]).replace('\n', '').replace('\x0c',
                                                                                                               '').replace(
                        '-', '').replace('"', '').replace("'", ''))
            if self.save_extract_result:
                cv2.imwrite(os.path.join(self.path_to_save, f'{box[3]}.jpg'), imgCrop)
        return cardInfo

    def extractInfo(self, image):
        self.image = self.readImage(image)
        self.process_kp, self.process_des = self.sift.detectAndCompute(self.image, None)
        self.compareTemplateSimilarity(self.process_des, self.source_front_des)
        self.findAndWrapObject()
        return self._extractItems()
