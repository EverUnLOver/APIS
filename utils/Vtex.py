from curses import has_key
from json.decoder import JSONDecodeError
from ntpath import join
import urllib3, json

class Vtex:
  def __init__(self, api_key: str, api_token: str, store_name: str):
    headers = {
      "Content-Type": "application/json",
      "X-VTEX-API-AppKey": api_key,
      "X-VTEX-API-AppToken": api_token
    }
    self.http = urllib3.HTTPSConnectionPool(
      headers=headers,
      host=f'{store_name}.vtexcommercestable.com.br'
    )
    self.base_url = f"https://{store_name}.vtexcommercestable.com.br/api"

  def _get_resources(self, uri, **kwargs):
    url = f"{self.base_url}/{uri}"
    r = self.http.request("GET", url)
    return r

  def _put_resource(self, uri, **kwargs):
    url = f"{self.base_url}/{uri}"
    data = kwargs.pop('data')
    encoded_data = json.dumps(data)
    r = self.http.request("PUT", url, body=encoded_data)
    return r

  def _get_json_resource(self, uri, **kwargs):
    try:
      response_json = {}
      method = kwargs.pop('method')
      if method == 'get':
        r = self._get_resources(uri, **kwargs)
        if r.status >= 200 and r.status < 400:
          response_json = json.loads(r.data.decode('utf-8'))
        else:
          response_json = {
            "status_code": r.status,
            "message": json.loads(r.data.decode('utf-8'))["Message"]
          }
      if method == 'put':
        r = self._put_resource(uri, **kwargs)
        if r.status >= 200 and r.status < 400:
          response_json = json.loads(r.data.decode('utf-8'))
        else:
          response_json = {
            "status_code": r.status,
            "message": json.loads(r.data.decode('utf-8'))["Message"]
          }
    # JSONDecodeError
    except urllib3.exceptions.ConnectTimeoutError as i:
      response_json = {
        "status_code": 504,
        "message": f'TIMEOUT: {str(i)}',
      }
    except urllib3.exceptions.RequestError as e:
      status_code = getattr(e.response, "status_code", 406)
      reason = getattr(e.response, "reason", str(e))
      response_json = {
        "status_code": status_code,
        "message": reason,
      }
    return response_json

  def put_file(self: "Vtex", file_data: dict, **kwargs):
    sku_id = file_data["_SkuId"]
    file_id = self.get_file_id(sku_id, file_data["Image Id"])
    uri = f"catalog/pvt/stockkeepingunit/{sku_id}/file/{file_id}"
    body_request = {
      "IsMain": self.is_main(sku_id, file_data["Image Id"]),
      "Label": file_data["Label"],
      "Name": file_data["Image Name"],
      "Text": file_data["Image Text"],
      "Url": file_data["Image URL"] if "https://" in file_data["Image URL"] else '://'.join(["https", file_data["Image URL"]]),
    }
    r = self._get_json_resource(uri, data=body_request, method='put', **kwargs)
    if not r or 'status_code' in r:
      print(f"Error with {file_data}")
      print(f"Reason {r}")

  def get_file_id(self: "Vtex", sku_id: int, archive_id: int):
    uri = f"catalog/pvt/stockkeepingunit/{sku_id}/file"
    vtex_files = self._get_json_resource(uri, method='get')
    if isinstance(vtex_files, list):
      for vtex_file in vtex_files:
        if vtex_file["ArchiveId"] == archive_id:
          print(vtex_file["Id"])
          return vtex_file["Id"]
    return False

  def is_main(self: "Vtex", sku_id: int, file_id: int):
    uri = f"catalog/pvt/stockkeepingunit/{sku_id}/file"
    vtex_files = self._get_json_resource(uri, method='get')
    if isinstance(vtex_files, list):
      for vtex_file in vtex_files:
        if vtex_file["ArchiveId"] == file_id:
          print(vtex_file["IsMain"])
          return vtex_file["IsMain"]
    return False