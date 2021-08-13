from ThaiPersonalCardExtract import PersonalCard
reader = PersonalCard(
    tesseract_cmd="D:/Program Files/Tesseract-OCR/tesseract",
    save_extract_result=True,
    path_to_save="D:/dev/ThaiPersonalCardExtract/examples/extract")
    # for windows need to pass tesseract_cmd parameter to setup your tesseract command path.

result = reader.extractInfo("../examples/card.jpg")
print(result)