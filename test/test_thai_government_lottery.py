import src.ThaiPersonalCardExtract as card
import pandas as pd
from glob import glob

excels = {}
paths = glob('../examples/lottery/*.jpg') + glob('../examples/lottery/*.jpeg') + glob('../examples/lottery/*.png')
reader = card.ThaiGovernmentLottery(
        save_extract_result=True,
        path_to_save="../examples/extract/thai_government_lottery")

for i,p in enumerate(paths):
    result = reader.extractInfo(p)
    _tmp = {"File_Name": p, "LotteryNumber": result.LotteryNumber, "LessonNumber": result.LessonNumber, "SetNumber": result.SetNumber, "Year": result.Year}
    excels[i] = _tmp

df = pd.DataFrame.from_dict(excels, orient='index')
df.to_csv ('../examples/export_dataframe.csv', index = False, header=True)
