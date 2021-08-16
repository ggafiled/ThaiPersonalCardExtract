import src.ThaiPersonalCardExtract as card
reader = card.ThaiGovernmentLottery(
    lang=card.MIX,
    provider=card.DEFAULT,
    tesseract_cmd="D:/Program Files/Tesseract-OCR/tesseract",
    save_extract_result=True,
    path_to_save="D:/dev/ThaiPersonalCardExtract/examples/extract/thai_government_lottery")
    # for windows need to pass tesseract_cmd parameter to setup your tesseract command path.

result = reader.extractInfo("../examples/card7.jpg")
print(result)