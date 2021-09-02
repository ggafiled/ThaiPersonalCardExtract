import src.ThaiPersonalCardExtract as card
reader = card.PersonalCard(
    lang=card.MIX,
    provider=card.DEFAULT,
    tesseract_cmd="D:/Program Files/Tesseract-OCR/tesseract",
    save_extract_result=True,
    path_to_save="D:/dev/ThaiPersonalCardExtract/examples/extract/personal_card")
    # for windows need to pass tesseract_cmd parameter to setup your tesseract command path.

result = reader.extract_front_info("../examples/card1.jpg")
print(result)

result = reader.extract_back_info("../examples/card5.jpg")
print(result)