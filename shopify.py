from numpy import product
import pandas as pd
import json
from utils import Shopify
from datetime import datetime, timedelta

shopify = Shopify(store_name=input('Ingrese la tienda : '), password=input(
    'Ingrese el password or access_token : '), api_version=input('ingrese la version del api : '))


metafields = {'color': {'namespace': 'my_fields', 'type': 'single_line_text_field'}, 'familia_color': {'namespace': 'my_field', 'type': 'single_line_text_field'}, 'peso': {'namespace': 'my_fields', 'type': 'single_line_text_field'}, 'modo_de_uso': {'namespace': 'my_fields', 'type': 'single_line_text_field'}, 'lavado': {'namespace': 'my_fields', 'type': 'multi_line_text_field'}, 'capucha': {'namespace': 'my_fields', 'type': 'single_line_text_field'}, 'cremallera': {'namespace': 'my_fields', 'type': 'single_line_text_field'}, 'cuello': {'namespace': 'my_fields', 'type': 'single_line_text_field'}, 'manga': {'namespace': 'my_fields', 'type': 'single_line_text_field'}, 'dise_o_de_la_tela_': {'namespace': 'my_fields', 'type': 'single_line_text_field'}, 'composici_n': {'namespace': 'my_fields', 'type': 'single_line_text_field'}, 'g_nero': {'namespace': 'my_fields', 'type': 'single_line_text_field'}}

while 1:
    type_request = input(
        "What type of request do you want to make? (GET/POST/PUT/DELETE): ")

    if type_request == "GET":
        while 1:
            action = input(
                'What action do you want to perform? ( GET_PID_VID_VTITLE_VSKU / GET_MONTH_ORDERS / GET_ALL_PRODUCTS / GET_SPECIFIC_FIELD_PRODUCT / GET_METAFIELDS / GET_METAFIELDS_ONE_PRODUCT / GET_METAFIELDS_ONE_VARIANT / GET_PRODUCTS_IDS_BY_HANDLE_TITLE ) : ')

            if action == "GET_MONTH_ORDERS":
                array_r = shopify.get_month_orders(
                    datetime.now() - timedelta(days=49, hours=21, minutes=10, seconds=0))
                json_obj = json.dumps(array_r, indent=4, sort_keys=True)

                name_file = input('Nombre del archivo : ')

                with open('{}.json'.format(name_file), 'w') as outfile:
                    outfile.write(json_obj)

                df_json = pd.read_json("{}.json".format(name_file))
                # df_json.to_excel('{}.xlsx'.format(name_file), index=False)
                df_json.to_csv(
                    '{}.csv'.format(name_file), index=False)
                break
            elif action == "GET_PID_VID_VTITLE_VSKU":
                products = shopify.get_products(fields='id,title,variants')
                info = [
                    {
                        "productID-variantID": "-".join([str(product["id"]), str(variant["id"])]),
                        "productTitle": product["title"],
                        "variantTitle": variant["title"],
                        "variantSku": variant["sku"],
                        "price": variant["price"],
                        "inventoryID": variant["inventory_item_id"],
                    }
                    for product in products
                    for variant in product["variants"]
                ]
                df_json = pd.DataFrame(info)
                df_json.to_excel("info.xlsx", index=False)
                break
            elif action == 'GET_ALL_PRODUCTS':
                array_r = shopify.get_products()

                json_obj = json.dumps(array_r, indent=4, sort_keys=True)

                name_file = input('Nombre del archivo : ')

                with open('{}.json'.format(name_file), 'w') as outfile:
                    outfile.write(json_obj)

                df_json = pd.read_json("{}.json".format(name_file))
                # df_json.to_excel('{}.xlsx'.format(name_file), index=False)
                df_json.to_excel(
                    '{}_indexed.xlsx'.format(name_file), index=True)
                break
            elif action == 'GET_PRODUCTS_IDS_BY_HANDLE_TITLE':
                array = shopify.get_products(fields='handle,title,id')
                df_json_excel = [row.to_dict() for index, row in pd.read_excel('{}.xlsx'.format(
                    input('Path del archivo con la data para filtrar: '))).iterrows()]
                filter_data = ['{} {}'.format(
                    row.get('handle'), row.get('title')) for row in df_json_excel]
                print(len(filter_data))
                if len(array) == len(filter_data):
                    json_obj = json.dumps(array, indent=4, sort_keys=True)

                    name_file = input('Nombre del archivo : ')

                    with open('{}.json'.format(name_file), 'w') as outfile:
                        outfile.write(json_obj)

                    df_json = pd.read_json("{}.json".format(name_file))

                    df_json.to_excel('{}_indexed.xlsx'.format(
                        name_file), index=True, index_label='indexed')

                    break

                # Found
                array_r = tuple(filter(lambda data: '{} {}'.format(
                    data.get('handle'), data.get('title')) in filter_data, array))

                json_obj = json.dumps(array_r, indent=4, sort_keys=True)

                name_file = input('Nombre del archivo : ')

                with open('{}.json'.format(name_file), 'w') as outfile:
                    outfile.write(json_obj)

                df_json = pd.read_json("{}.json".format(name_file))

                df_json.to_excel('{}_indexed.xlsx'.format(
                    name_file), index=True, index_label='indexed')

                # Not found
                filter_data = ['{} {}'.format(
                    row.get('handle'), row.get('title')) for row in array_r]
                array_r_nf = tuple(filter(lambda data: '{} {}'.format(
                    data.get('handle'), data.get('title')) not in filter_data, df_json_excel))

                json_obj_nf = json.dumps(array_r_nf, indent=4, sort_keys=True)

                name_file_nf = '_'.join([name_file, 'not_found'])

                with open('{}.json'.format(name_file_nf), 'w') as outfile:
                    outfile.write(json_obj_nf)

                df_json_nf = pd.read_json("{}.json".format(name_file_nf))

                df_json_nf.to_excel('{}_indexed.xlsx'.format(
                    name_file_nf), index=True, index_label='indexed')

                break
            elif action == 'GET_SPECIFIC_FIELD_PRODUCT':
                array_r = shopify.get_products(fields=input(
                    'Ingrese los campos que desea retornar ej = id,title... : '))

                json_obj = json.dumps(array_r, indent=4, sort_keys=True)

                name_file = input('Nombre del archivo : ')

                with open('{}.json'.format(name_file), 'w') as outfile:
                    outfile.write(json_obj)

                df_json = pd.read_json("{}.json".format(name_file))
                # df_json.to_excel('{}.xlsx'.format(name_file), index=False)
                df_json.to_excel(
                    '{}_indexed.xlsx'.format(name_file), index=True, index_label='indexed')
                break
            elif action == 'GET_METAFIELDS_ONE_PRODUCT':
                array_r = shopify.get_metafields_product(
                    product_id=input('Ingrese el id del producto : '))

                keys = ['product_id', 'id', 'owner_resource', 'owner_id',
                        'type', 'value', 'value_type', 'namespace', 'key']
                metafields = [
                    {key: value for key, value in d.items() if key in keys}
                    for d in array_r
                ]

                json_obj = json.dumps(metafields)

                name_file = input('Nombre del archivo : ')

                with open('{}.json'.format(name_file), 'w') as outfile:
                    outfile.write(json_obj)

                df_json = pd.read_json("{}.json".format(name_file))
                # df_json.to_excel('{}.xlsx'.format(name_file), index=False)
                df_json.to_excel(
                    '{}_indexed.xlsx'.format(name_file), index=True, index_label='indexed')
                break
            elif action == 'GET_METAFIELDS_ONE_VARIANT':
                array_r = shopify.get_metafields_variant(
                    input('Ingrese el id del producto : '),
                    input('Ingrese el id de la variantte : ')
                )

                keys = ['product_id', 'id', 'owner_resource', 'owner_id',
                        'type', 'value', 'value_type', 'namespace', 'key']
                metafields = [
                    {key: value for key, value in d.items() if key in keys}
                    for d in array_r
                ]

                json_obj = json.dumps(metafields)

                name_file = input('Nombre del archivo : ')

                with open('{}.json'.format(name_file), 'w') as outfile:
                    outfile.write(json_obj)

                df_json = pd.read_json("{}.json".format(name_file))
                # df_json.to_excel('{}.xlsx'.format(name_file), index=False)
                df_json.to_excel(
                    '{}_indexed.xlsx'.format(name_file), index=True, index_label='indexed')
                break
            elif action == 'GET_METAFIELDS':
                array_r = shopify.get_products(metafield='id,handle,title,variants')
                # variants = [
                #     variant
                #     for product in array_r
                #     for variant in product['variants']
                # ]
                metafields_products = [
                    data
                    for t in filter(
                        lambda x: x,
                        map(
                            shopify.get_metafields_product_v2,
                            [d for d in array_r if d.get('id')]
                        )
                    )
                    for data in t
                ]
                # metafields_variants = [data for t in filter(lambda x: x, map(shopify.get_metafields_variant, [(d.get(
                #     'product_id'), d.get('id')) for d in variants if d.get('product_id') and d.get('id')])) for data in t]
                # metafields = metafields_products + metafields_variants
                metafields = metafields_products
                # metafields = metafields_products
                keys = ['product_id', 'id', 'owner_resource', 'owner_id',
                        'type', 'value', 'value_type', 'namespace', 'key', 'handle', 'title']
                metafields = [
                    {
                        key: value
                        for key, value in d.items() if key in keys
                    }
                    for d in metafields
                ]
                # [(d.pop('updated_at'), d.pop('created_at'))
                #  for d in metafields]
                # metafields = [{key: pd.to_datetime(value).date() if key in ['updated_at', 'created_at'] else value for key, value in d.items()} for d in metafields]

                json_obj = json.dumps(metafields, indent=4, sort_keys=True)

                name_file = input('Nombre del archivo :')

                with open('{}.json'.format(name_file), 'w') as outfile:
                    outfile.write(json_obj)

                df_json = pd.read_json("{}.json".format(name_file))
                # df_json.to_excel('{}.xlsx'.format(name_file), index=False)
                df_json.to_excel('{}_indexed.xlsx'.format(
                    name_file), index=True, index_label='indexed')
                break
        break
    elif type_request == 'PUT':
        name_file = input('Path del archivo excel : ')

        while 1:
            action = input(
                'What action do you want to perform? ( PUT_PRODUCTS / PUT_METAFIELDS ) : ')
            if action == 'PUT_PRODUCTS':
                df_json = pd.read_excel('{}.xlsx'.format(
                    name_file), converters={'id': int})
                for index, row in df_json.iterrows():
                    shopify.put_product(product=row.to_dict())
                break
            elif action == 'PUT_METAFIELDS':
                df_json = pd.read_excel('{}.xlsx'.format(name_file), converters={
                                        'id': int, 'owner_id': int})
                for index, row in df_json.iterrows():
                    data = row.to_dict()
                    shopify.put_metafield(metafield=data)
                break
        break
    elif type_request == 'POST':
        name_file = input('Path del archivo excel : ')

        while 1:
            action = input(
                'What action do you want to perform? ( POST_PRODUCTS / POST_METAFIELDS / DATA_SCIENCE_POST_METAFIELDS ) : ')
            if action == 'POST_PRODUCTS':
                df_json = pd.read_excel('{}.xlsx'.format(name_file))
                for index, row in df_json.iterrows():
                    shopify.post_product(product=row.to_dict())
                break
            elif action == 'POST_METAFIELDS':
                df_json = pd.read_excel('{}.xlsx'.format(
                    name_file), converters={'owner_id': int})
                for index, row in df_json.iterrows():
                    shopify.post_metafield(metafield=row.to_dict())
                break
            elif action == 'DATA_SCIENCE_POST_METAFIELDS':
                products = shopify.get_products(fields='handle,title,id')
                ids = {
                    f"{product['handle'].lower().strip()} {product['title']}": product["id"]
                    # f"{product['title']}": product["id"]
                    for product in products
                }
                # products = shopify.get_products(fields='variants')
                # ids = {
                #     f"{variant['sku']}": variant["id"]
                #     for product in products
                #     for variant in product.get("variants", [])
                # }
                df_json = pd.read_excel('{}.xlsx'.format(
                    name_file))
                array_data = list()
                for index, row in df_json.iterrows():
                    data = row.to_dict()

                    # ondademar
                    if f"{str(data['handle']).lower().strip()} {data['title']}" in ids:
                    # if f"{data['title']}" in ids:
                    # if f"{data['sku']}" in ids:
                        array_data += [shopify.post_metafield(metafield={
                            'owner_id': ids[f"{str(data['handle']).lower().strip()} {data['title']}"],
                            # 'owner_id': ids[f"{data['title']}"],
                            # 'owner_id': ids[f"{data['sku']}"],
                            'type': metafields[key]["type"],
                            'key': key,
                            "value": value,
                            'namespace': metafields[key]["namespace"],
                            'owner_resource': "product"
                        }) for key, value in data.items() if value and key not in ['owner_id', 'namespace', 'key', 'value', 'value_type', 'type', 'owner_resource', 'handle', 'title', "sku", "hojas"]]
                    else:
                        array_data.append({
                            "status_code": "404",
                            "handle": str(data['handle']).lower().strip(),
                            "title": data['title']
                        })
                        print(f"{str(data['handle']).lower().strip()} {data['title']}")
                status_codes = set(d['status_code'] for d in array_data)
                for status in status_codes:
                    print('Status code {}'.format(status))
                    data_to_excel = tuple(
                        filter(lambda x: x.get('status_code') == status, array_data))
                    if status in [201, 200, '200', '201']:
                        data_to_excel = [d['metafield'] for d in data_to_excel]
                    df_json = pd.DataFrame(data_to_excel)
                    df_json.to_excel('{}_status_{}.xlsx'.format(
                        name_file, status), index=False)
                break
        break
    elif type_request == 'DELETE':
        name_file = input('Path del archivo excel : ')

        while 1:
            action = input(
                'What action do you want to perform? ( DELETE_PRODUCTS / DELETE_METAFIELDS ) : ')
            if action == 'DELETE_PRODUCTS':
                # df_json = pd.read_excel('{}.xlsx'.format(name_file), converters={'id': int})
                # for index, row in df_json.iterrows():
                #     shopify.delete_product(id=row.to_dict().get('id'))
                # break
                pass
            elif action == 'DELETE_METAFIELDS':
                df_json = pd.read_excel('{}.xlsx'.format(
                    name_file), converters={'id': int})
                for index, row in df_json.iterrows():
                    shopify.delete_metafield(
                        metafield_id=row.to_dict().get('id'))
                break
        break

print('Done')
