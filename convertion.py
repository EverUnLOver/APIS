import pandas as pd
import json

def excel_to_json(file_path):
    file_path = file_path.removesuffix('.xlsx')
    df = pd.read_excel("{}.xlsx".format(file_path))
    data = []
    for _, row in df.iterrows():
        data.append(row.to_dict())
    json_data = json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False)
    with open("{}.json".format(file_path), "w", encoding="utf-8") as f:
        f.write(json_data)

def json_to_excel(file_path):
    file_path = file_path.removesuffix('.json')
    with open("{}.json".format(file_path), "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    writer = pd.ExcelWriter("{}.xlsx".format(file_path),
                        engine='xlsxwriter',
                        date_format='m/d/yyyy')
    df.to_excel(writer, index=False)

def json_to_csv(file_path):
    file_path = file_path.removesuffix('.json')
    with open("{}.json".format(file_path), "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df.to_csv("{}.csv".format(file_path), index=False)

excel_to_json("códigosciudades.xlsx")