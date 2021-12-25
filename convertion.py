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