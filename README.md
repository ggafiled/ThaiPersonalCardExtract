# ThaiPersonalCardExtract
[![PyPI Status](https://badge.fury.io/py/thai-personal-card-extract.svg)](https://badge.fury.io/py/thai-personal-card-extract)
[![license](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/JaidedAI/EasyOCR/blob/master/LICENSE)
[![Instragram](https://img.shields.io/badge/instragram-@ggafiled-blue.svg?style=flat)](https://www.instagram.com/ggafiled)

Library for extract infomation from thai personal identity card. 

## Examples
#### Real image file.
![Real image file](https://github.com/ggafiled/ThaiPersonalCardExtract/blob/main/examples/card.jpg?raw=true)

#### wrapPerpective image crop.
![wrapPerpective image crop](https://github.com/ggafiled/ThaiPersonalCardExtract/blob/main/examples/extract/image_scan.jpg?raw=true)

#### keypoint of image detected.
![keypoint of image detected](https://github.com/ggafiled/ThaiPersonalCardExtract/blob/main/examples/extract/image_keypoint.jpg?raw=true)

Resutls of library extract region of interest

| <p align="center"><kbd><img src="https://github.com/ggafiled/ThaiPersonalCardExtract/blob/main/examples/extract/Identification_Number.jpg?raw=true"/></kbd> </p>  <p align="center" class="image-caption">Identification Number</p> | <p align="center"><kbd><img src="https://github.com/ggafiled/ThaiPersonalCardExtract/blob/main/examples/extract/FullNameTH.jpg?raw=true"/></kbd></p>  <p align="center" class="image-caption">FullNameTH</p> |
|----------|------------|
| <p align="center"><kbd><img src="https://github.com/ggafiled/ThaiPersonalCardExtract/blob/main/examples/extract/NameEN.jpg?raw=true"/></kbd>  </p> <p align="center" class="image-caption">NameEN</p> | <p align="center"><kbd><img src="https://github.com/ggafiled/ThaiPersonalCardExtract/blob/main/examples/extract/LastNameEN.jpg?raw=true"/></kbd></p>  <p align="center" class="image-caption">LastNameEN</p> |
| <p align="center"><kbd><img src="https://github.com/ggafiled/ThaiPersonalCardExtract/blob/main/examples/extract/Birthday.jpg?raw=true"/></kbd>  </p> <p align="center" class="image-caption">Birthday</p> | <p align="center"><kbd><img src="https://github.com/ggafiled/ThaiPersonalCardExtract/blob/main/examples/extract/Address.jpg?raw=true"/></kbd></p>   <p align="center" class="image-caption">Address</p> |
| <p align="center"><kbd><img src="https://github.com/ggafiled/ThaiPersonalCardExtract/blob/main/examples/extract/Religion.jpg?raw=true"/></kbd> </p> <p align="center" class="image-caption">Religion</p>  |  |

## Installation
Install using `pip` for stable release,

``` bash
pip install thai-personal-card-extract
```

For latest development release,

``` bash
pip install git+git://github.com/ggafiled/ThaiPersonalCardExtrac.git
```

Note 1: for Windows, please install tesseract first by following the official instruction here https://medium.com/@navapat.tpb/734dae2fb4d3 On medium website, be sure to setup already.
Note 2: for Linux os, please install tesseract by following the official instruction https://github.com/tesseract-ocr/tesseract

## Usage
``` python
from ThaiPersonalCardExtract import PersonalCard
reader = PersonalCard(tesseract_cmd="D:/Program Files/Tesseract-OCR/tesseract") # for windows need to pass tesseract_cmd parameter to setup your tesseract command path.
result = reader.extractInfo('examples/card.jpg')
print(result)
```

Output will be in list format, each item represents result of library can extract, respectively.

``` bash
{
   "Identification_Number": "9999999999999",
   "FullNameTH": "นาย  อายุมฺมุราเสะ",
   "NameEN": "Me Shoys",
   "LastNameEN": "Hinata",
   "Birthday": "421 fun. 1998",
   "Religion": "พุทธ",
   "Address": "ท๒ 99/1 มิชีโฮะ เขตฮานามิกาวา อำเภอชิบ;"
}
```

# Config Options
you can set options to Instance by below keyword

| Parameter name | Value Type | Example
| ------------- | ------------- | ------------- |
| lang | Enum of PersonalCardLanguage Class | PersonalCardLanguage.THAI \n PersonalCardLanguage.ENGLISH *Default is 'th'
| template_threshold | Double | Rate to cals similarity of template *Default is 0.7
| sift_rate | Int | Feature Keypoint rate *Default is 25,000
| tesseract_cmd | String | Path of your tesseract command **For windows only.
| save_extract_result | Boolean | Set True if you want to save extracted image *Default is False
| path_to_save | String | Path that you given it save extracted image, relative with save_extract_result=True

# Donate Me ☕

![promptpay](https://github.com/ggafiled/ThaiPersonalCardExtract/blob/main/examples/promptpay.png?raw=true)
#### Mr.Nattapol Krobklang 