from enum import Enum

class Language(Enum):
    THAI = 'tha'
    ENGLISH = 'eng'
    MIX = 'mix'

    def __str__(self):
        return self.value

class Provider(Enum):
    EASYOCR = 'easyocr'
    TESSERACT = 'tesseract'
    DEFAULT = 'default'

    def __str__(self):
        return self.value