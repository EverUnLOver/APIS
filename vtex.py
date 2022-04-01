import pandas as pd
import json
from utils import Vtex

vtex = Vtex(api_key=input("API Key: "), api_token=input(
    "API Token: "), store_name=input("Store Name: "))

while 1:
  type_request = input("Type of request (PUT): ")

  if type_request == "PUT":
    name_file = input("File name: ")

    while 1:
      action = input("Action (PUT_IMAGES): ")
      if action == "PUT_IMAGES":
        df_json = pd.read_excel('{}.xlsx'.format(name_file))
        for index, row in df_json.iterrows():
          vtex.put_file(file_data=row.to_dict())
          break
        break
    break