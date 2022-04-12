from json.decoder import JSONDecodeError
import urllib3, json, requests
from time import sleep
# import logging


class Shopify:
    def __init__(self, store_name: str, password: str, api_version: str):
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": password
        }
        self.api_version = api_version
        self.http = urllib3.HTTPSConnectionPool(
            headers=headers, host=f'{store_name}.myshopify.com')
        self.base_url = "https://{}.myshopify.com/admin".format(store_name)

    def _get_resources(self, uri, **kwargs):
        url = "{}/{}".format(self.base_url, uri)
        lr = list()
        while 1:
            print(url)
            r = self.http.request("GET", url)
            lr.append(r)
            link = r.headers.get('Link')
            if link and 'rel="next"' in link:
                link = link.split(',')[-1].strip()
                url = link[1:link.find('>')]
            else:
                break
        return lr

    def _put_resource(self, uri, **kwargs):
        url = "{}/{}".format(self.base_url, uri)
        data = kwargs.pop('data')
        encoded_data = json.dumps(data)
        r = self.http.request("PUT", url, body=encoded_data)
        return r

    def _post_resource(self, uri, **kwargs):
        url = "{}/{}".format(self.base_url, uri)
        data = kwargs.pop('data')
        encoded_data = json.dumps(data)
        r = self.http.request("POST", url, body=encoded_data)
        return r

    def _delete_resource(self, uri, **kwargs):
        url = "{}/{}".format(self.base_url, uri)
        r = self.http.request("DELETE", url)
        return r

    def _get_json_resource(self, uri, **kwargs):
        try:
            response_json = {}
            method = kwargs.pop('method')
            if method == 'get':
                list_response = self._get_resources(uri, **kwargs)
                response_json = list()
                for response in list_response:
                    if response.status in [requests.codes.ok]:
                        try:
                            response_json += list(json.loads(
                                response.data.decode('utf-8')).values())[0]
                        except ValueError as e:
                            response_json = {
                                "status_code": response.status,
                                "message": e,
                            }
                            break
            elif method == 'put':
                response = self._put_resource(uri, **kwargs)
                if response.status in [requests.codes.ok]:
                    try:
                        response_body = response.data.decode('utf-8')
                        response_json = json.loads(response_body)
                    except ValueError as e:
                        response_json = {
                            "status_code": response.status,
                            "message": e,
                        }
            elif method == 'post':
                response = self._post_resource(uri, **kwargs)
                if response.status in [requests.codes.ok, requests.codes.created, requests.codes.accepted]:
                    try:
                        response_body = response.data.decode('utf-8')
                        response_json = json.loads(response_body) | {'status_code': response.status}
                    except ValueError as e:
                        response_json = {
                            "status_code": response.status,
                            "message": e,
                        }
                else:
                    metafield = kwargs['data']['metafield']
                    try:
                        errors = json.loads(response.data.decode('utf-8')).get('errors')
                        response_json = {
                            "status_code": response.status,
                            'errors': errors,
                            'owner_id': metafield['owner_id'],
                            'owner_resource': metafield['owner_resource'],
                            'key': metafield['key'],
                        } | {key: metafield.get(key) for key in errors if errors not in ['Not Found']}
                    except (ValueError, JSONDecodeError) as e:
                        response_json = {
                            "status_code": response.status,
                            "message": e,
                            'owner_id': metafield['owner_id'],
                            'owner_resource': metafield['owner_resource'],
                            'key': metafield['key'],
                            'value': metafield['value']
                        }
                    print(response_json)
            elif method == 'delete':
                response = self._delete_resource(uri, **kwargs)
                if response.status in [requests.codes.ok]:
                    try:
                        response_body = response.data.decode('utf-8')
                        response_json = json.loads(response_body)
                    except ValueError as e:
                        response_json = {
                            "status_code": response.status,
                            "message": e,
                        }
            sleep(0.5)
            return response_json
        except urllib3.exceptions.ConnectTimeoutError as i:
            response_json = {
                "status_code": 504,
                "message": f'TIMEOUT: {str(i)}',
            }
        except urllib3.exceptions.RequestError as e:
            status_code = getattr(e.response, "status_code", 406)
            reason = getattr(e.response, "reason", str(e))
            response_json.append(
                {
                    "status_code": status_code,
                    "message": reason,
                }
            )
        sleep(0.5)
        return response_json

    def get_month_orders(self, datetime, **kwargs):
        uri = 'api/{}/orders.json?status=any&limit=250&created_at_min={}'.format(
            self.api_version,
            datetime.strftime('%Y-%m-%dT%H:%M:%S%z')
        )
        method = 'get'
        return self._get_json_resource(uri, method=method, **kwargs)

    def get_products(self: "Shopify", fields: str = None, **kwargs):
        """
        This function will return a list of products that have the metafield
        passed in as an argument.
        """
        uri = 'api/{}/products.json'.format(self.api_version)
        if fields:
            uri = "api/{}/products.json?limit=250&fields={}".format(
                self.api_version, fields)
        # else:api_version
        #     uri = "product_listings.json?limit=250"
        method = 'get'
        array_dicts = self._get_json_resource(
            uri, method=method, **kwargs)
        return array_dicts

    def get_metafields_product(self: "Shopify", product_id: int, **kwargs):
        if product_id:
            uri = "api/{}/products/{}/metafields.json".format(
                self.api_version, product_id)
            method = 'get'
            result = tuple(map(lambda x: x | {'product_id': product_id}, filter(lambda x: x and x.get(
                "status_code") == None, self._get_json_resource(uri, method=method, **kwargs))))
            return result
        return None

    def get_metafields_variant(self: "Shopify", args, **kwargs):
        product_id = args[0]
        variant_id = args[1]
        if product_id and variant_id:
            uri = "products/{}/variants/{}/metafields.json".format(
                product_id, variant_id)
            method = 'get'
            result = tuple(map(lambda x: x | {'product_id': product_id}, filter(lambda x: x and x.get(
                "status_code") == None, self._get_json_resource(uri, method=method, **kwargs))))
            return result
        return None

    def put_product(self: "Shopify", product: dict, **kwargs):
        """{"id":632910392,"title":"New product title"}"""

        uri = "api/{}/products/{}.json".format(
            self.api_version, product.get('id'))
        product.pop('indexed') if product.get('indexed') else None
        data = {
            "product": product
        }
        method = 'put'
        return self._get_json_resource(uri, method=method, data=data, **kwargs)


    def put_metafield(self: "Shopify", metafield: dict, **kwargs):
        """{"id":721389482,"value":"something new","type":"single_line_text_field"}"""

        metafield.pop('product_id') if metafield.get('product_id') else None
        metafield.pop('indexed') if metafield.get('indexed') else None
        # metafield['value'] = json.dumps(metafield.get('value'))
        uri = "api/{}/metafields/{}.json".format(self.api_version, metafield.get('id'))
        data = {
            "metafield": metafield
        }
        method = 'put'
        return self._get_json_resource(uri, method=method, data=data, **kwargs)

    def post_product(self: "Shopify", product: dict, **kwargs):
        """{"title":"Burton Custom Freestyle 151","body_html":"\u003cstrong\u003eGood snowboard!\u003c\/strong\u003e","vendor":"Burton","product_type":"Snowboard","tags":["Barnes \u0026 Noble","Big Air","John's Fav"]}"""

        uri = "api/{}/products.json".format(self.api_version)
        data = {
            "product": product
        }
        method = 'post'
        return self._get_json_resource(uri, method=method, data=data, **kwargs)

    def post_metafield(self: "Shopify", metafield: dict, **kwargs):
        """{"namespace":"inventory","key":"warehouse","value":25,"type":"number_integer"}"""

        metafield.pop('product_id') if metafield.get('product_id') else None
        # metafield['value'] = json.dumps(metafield.get('value'))
        uri = "api/{}/metafields.json".format(self.api_version)
        data = {
            "metafield": metafield
        }
        method = 'post'
        return self._get_json_resource(uri, method=method, data=data, **kwargs)

    def delete_metafield(self: "Shopify", metafield_id: int, **kwargs):
        uri = "api/{}/metafields/{}.json".format(self.api_version, metafield_id)
        method = 'delete'
        return self._get_json_resource(uri, method=method, **kwargs)
