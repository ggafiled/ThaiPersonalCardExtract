import src.ThaiPersonalCardExtract as card
reader = card.DrivingLicense(
    lang=card.MIX,
    provider=card.DEFAULT,
    tesseract_cmd="D:/Program Files/Tesseract-OCR/tesseract",
    save_extract_result=True,
    path_to_save="D:/dev/ThaiPersonalCardExtract/examples/extract/driving_license")
    # for windows need to pass tesseract_cmd parameter to setup your tesseract command path.

result = reader.extractInfo("../examples/card3.jpg")
print(result)