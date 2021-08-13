# ThaiPersonalCardExtract
[![Downloads](http://pepy.tech/badge/thai-personal-card-extract)](http://pepy.tech/project/thai-personal-card-extract)
[![PyPI Status](https://badge.fury.io/py/thai-personal-card-extract.svg)](https://badge.fury.io/py/thai-personal-card-extract)
[![license](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/ggafiled/ThaiPersonalCardExtract/blob/master/LICENSE)
[![Instragram](https://img.shields.io/badge/instragram-@ggafiled-blue.svg?style=flat)](https://www.instagram.com/ggafiled)

Library for extract infomation from thai personal identity card. imprement from easyocr and tesseract

## New Feature 🎁
* More arae extract.
* lang : attribute : get only area of given language.
* provider : attribute : set ocr provider now support easyocr and tesseract.
 
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
| <p align="center"><kbd><img src="https://github.com/ggafiled/ThaiPersonalCardExtract/blob/main/examples/extract/BirthdayTH.jpg?raw=true"/></kbd>  </p> <p align="center" class="image-caption">BirthdayTH</p> | <p align="center"><kbd><img src="https://github.com/ggafiled/ThaiPersonalCardExtract/blob/main/examples/extract/BirthdayEN.jpg?raw=true"/></kbd>  </p> <p align="center" class="image-caption">BirthdayEN</p> |
| <p align="center"><kbd><img src="https://github.com/ggafiled/ThaiPersonalCardExtract/blob/main/examples/extract/Religion.jpg?raw=true"/></kbd> </p> <p align="center" class="image-caption">Religion</p>  | <p align="center"><kbd><img src="https://github.com/ggafiled/ThaiPersonalCardExtract/blob/main/examples/extract/Address.jpg?raw=true"/></kbd></p>   <p align="center" class="image-caption">Address</p> |
| <p align="center"><kbd><img src="https://github.com/ggafiled/ThaiPersonalCardExtract/blob/main/examples/extract/DateOfIssueTH.jpg?raw=true"/></kbd>  </p> <p align="center" class="image-caption">DateOfIssueTH</p> | <p align="center"><kbd><img src="https://github.com/ggafiled/ThaiPersonalCardExtract/blob/main/examples/extract/DateOfIssueEN.jpg?raw=true"/></kbd>  </p> <p align="center" class="image-caption">DateOfIssueEN</p> |
| <p align="center"><kbd><img src="https://github.com/ggafiled/ThaiPersonalCardExtract/blob/main/examples/extract/DateOfExpiryTH.jpg?raw=true"/></kbd>  </p> <p align="center" class="image-caption">DateOfExpiryTH</p> | <p align="center"><kbd><img src="https://github.com/ggafiled/ThaiPersonalCardExtract/blob/main/examples/extract/DateOfExpiryEN.jpg?raw=true"/></kbd>  </p> <p align="center" class="image-caption">DateOfExpiryEN</p> |


## Recommend ⚠
* Image quality lowest should be 600x350
* Images with minimal reflections should be used. for good results
* Identity Card should be size in the image about 75%, if the image doesn't cropped that to be left only Identity Card  area.
* <b> For faster, please resize image and usage CUDA GPU. </b>

## Installation
Install using `pip` for stable release,

``` bash
pip install thai-personal-card-extract
```

For latest development release,

``` bash
pip install git+git://github.com/ggafiled/ThaiPersonalCardExtrac.git
```

<b>Note 1:</b> for Windows, please install tesseract first by following the official instruction here https://medium.com/@navapat.tpb/734dae2fb4d3 On medium website, be sure to setup already.

<b>Note 2:</b> for Linux os, please install tesseract by following the official instruction https://github.com/tesseract-ocr/tesseract

## Usage

[![Watch the video](https://www.youtube.com/watch?v=FmPN667DTmE&t=5s/0.jpg)](https://www.youtube.com/watch?v=FmPN667DTmE&t=5s)

``` python
# With build-in Config Options.
import ThaiPersonalCardExtract as card
reader = card.PersonalCard(
    lang=card.THAI,
    provider=card.DEFAULT,
    tesseract_cmd="D:/Program Files/Tesseract-OCR/tesseract",
    save_extract_result=True,
    path_to_save="D:/dev/ThaiPersonalCardExtract/examples/extract")
result = reader.extractInfo('examples/card.jpg')
print(result)


# With free-style 
from ThaiPersonalCardExtract import PersonalCard
reader = PersonalCard(lang="mix", tesseract_cmd="D:/Program Files/Tesseract-OCR/tesseract") # for windows need to pass tesseract_cmd parameter to setup your tesseract command path.
result = reader.extractInfo('examples/card.jpg')
print(result)
```

Output will be in list format, each item represents result of library can extract, respectively.

``` bash
{
   "Identification_Number": "9999999999999",
   "FullNameTH": "นาย อายุมฺมุราเสะ",
   "PrefixTH": "นาย",
   "NameTH": "อายุมฺมุราเสะ",
   "LastNameTH": "อายุมฺมุราเสะ",
   "PrefixEN": "Me",
   "NameEN": "Shoys",
   "LastNameEN": "Hinata",
   "BirthdayTH": "21 มี.ย. 2539",
   "BirthdayEN": "21 Jun..1996",
   "Religion": "พุทธ",
   "Address": "ท๒ 99/1 มิชีโฮะ เขตฮานามิกาวา อำเภอชิบ;",
   "DateOfIssueTH": "11 ส.ค. 2554",
   "DateOfIssueEN": "~11 Ang. 2021",
   "DateOfExpiryTH": "11 ส.ค. 2574",
   "DateOfExpiryEN": "21 ug. 2092"
}
```

For set ``` lang ``` attribute to ``` tha ```
``` python
from ThaiPersonalCardExtract import PersonalCard
reader = PersonalCard(lang="tha", tesseract_cmd="D:/Program Files/Tesseract-OCR/tesseract") # for windows need to pass tesseract_cmd parameter to setup your tesseract command path.
result = reader.extractInfo('examples/card.jpg')
print(result)
```
Output will be in list format, each item represents result of library can extract, respectively.

``` bash
{
   "Identification_Number": "9999999999999",
   "FullNameTH": "นาย อายุมฺมุราเสะ",
   "PrefixTH": "นาย",
   "NameTH": "อายุมฺมุราเสะ",
   "LastNameTH": "อายุมฺมุราเสะ",
   "BirthdayTH": "21 มี.ย. 2539",
   "Religion": "พุทธ",
   "Address": "ท๒ 99/1 มิชีโฮะ เขตฮานามิกาวา อำเภอชิบ;",
   "DateOfIssueTH": "11 ส.ค. 2554",
   "DateOfExpiryTH": "11 ส.ค. 2574"
}
```

And you can set ocr provider following below ``` default  #used both easyocr and tesseract **Recommend ``` Or ``` easyocr ``` Or ``` tesseract ```
``` python
from ThaiPersonalCardExtract import PersonalCard
reader = PersonalCard(lang="tha", provider="default", tesseract_cmd="D:/Program Files/Tesseract-OCR/tesseract") # for windows need to pass tesseract_cmd parameter to setup your tesseract command path.
result = reader.extractInfo('examples/card.jpg')
print(result)
```

# Config Options
you can set options to Instance by below keyword

| Parameter name | Value Type | Example
| ------------- | ------------- | ------------- |
| lang | String | Expected Results Language ``` bash mix  #get all area both tha and eng ``` Or ``` bash tha ``` Or ``` bash eng ``` *Default is 'mix'
| provider | String | OCR Provider have ``` bash default  #used both easyocr and tesseract **Recommend ``` Or ``` bash easyocr ``` Or ``` bash tesseract ``` *Default is 'default'
| template_threshold | Double | Rate to cals similarity of template *Default is 0.7
| sift_rate | Int | Feature Keypoint rate *Default is 25,000
| tesseract_cmd | String | Path of your tesseract command **For windows only.
| save_extract_result | Boolean | Set True if you want to save extracted image *Default is False
| path_to_save | String | Path that you given it save extracted image, relative with save_extract_result=True

# Donate Me ☕

![promptpay](https://github.com/ggafiled/ThaiPersonalCardExtract/blob/main/examples/promptpay.png?raw=true)
#### Mr.Nattapol Krobklang 
