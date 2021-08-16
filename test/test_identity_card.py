import src.ThaiPersonalCardExtract as card
reader = card.PersonalCard(
    lang=card.MIX,
    provider=card.DEFAULT,
    tesseract_cmd="D:/Program Files/Tesseract-OCR/tesseract",
    save_extract_result=True,
    path_to_save="D:/dev/ThaiPersonalCardExtract/examples/extract")
    # for windows need to pass tesseract_cmd parameter to setup your tesseract command path.

result = reader.extractInfo("../examples/card1.jpg")
print(result)