import pandas as pd
import json
from utils import Shopify

# shopify = Shopify(store_name=input('Ingrese la tienda : '), password=input(
#     'Ingrese el password or access_token : '), api_version=input('ingrese la version del api : '))

# ADH
shopify = Shopify(store_name="adh-colombia", password="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", api_version="2022-01")

while 1:
    type_request = input(
        "What type of request do you want to make? (GET/POST/PUT/DELETE): ")

    if type_request == "GET":
        while 1:
            action = input(
                'What action do you want to perform? ( GET_ALL_PRODUCTS / GET_SPECIFIC_FIELD_PRODUCT / GET_METAFIELDS / GET_METAFIELDS_ONE_PRODUCT / GET_PRODUCTS_IDS_BY_HANDLE_TITLE ) : ')

            if action == 'GET_ALL_PRODUCTS':
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
                metafields = [{key: value for key, value in d.items() if key in keys}
                              for d in array_r]

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
                array_r = shopify.get_products(metafield='id,variants')
                variants = [
                    variant
                    for product in array_r
                    for variant in product['variants']
                ]
                metafields_products = [
                    data
                    for t in filter(
                        lambda x: x,
                        map(
                            shopify.get_metafields_product,
                            [d.get('id')for d in array_r if d.get('id')]
                        )
                    )
                    for data in t
                ]
                metafields_variants = [data for t in filter(lambda x: x, map(shopify.get_metafields_variant, [(d.get(
                    'product_id'), d.get('id')) for d in variants if d.get('product_id') and d.get('id')])) for data in t]
                metafields = metafields_products + metafields_variants
                # metafields = metafields_products
                keys = ['product_id', 'id', 'owner_resource', 'owner_id',
                        'type', 'value', 'value_type', 'namespace', 'key']
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
                array = shopify.get_products(fields='handle,title,id')
                get_id = {f"{d['handle']} {d['title']}": d["id"] for d in array}
                df_json = pd.read_excel('{}.xlsx'.format(
                    name_file))
                # df_json = pd.read_excel('{}.xlsx'.format(
                #     name_file), converters={'owner_id': int})
                # to_excel = []
                array_data = list()
                for index, row in df_json.iterrows():
                    data = row.to_dict()

                    # array_data += [shopify.post_metafield(metafield=data)]

                    # array_data += [shopify.post_metafield(metafield={
                    #     'owner_id': data['owner_id'],
                    #     'type': 'single_line_text_field' if key == 'product_detail' else '',
                    #     'key': key,
                    #     'value': value,
                    #     'namespace': 'my_fields' if key == 'product_detail' else '',
                    #     'value_type': 'string' if key == 'product_detail' else '',
                    #     'owner_resource': data['owner_resource'] if data.get('owner_resource') else 'product'
                    # }) for key, value in data.items() if key not in ['owner_id', 'id', 'namespace', 'key', 'value', 'value_type', 'type', 'owner_resource']]

                    # ONEONE
                    # array_data += [shopify.post_metafield(metafield={
                    #     'owner_id': get_id[f"{data['handle']} {data['title']}"],
                    #     'type': 'string' if key in ['config', 'google_product_category', 'badge', 'widget'] else 'integer' if key == 'hidden' else 'number_integer' if key == 'rating_count' else 'json_string' if key == 'product_status' else 'rating' if key == 'rating' else 'product_reference' if key in ['details_foot_relation', 'complete_look_relation_1', 'complete_look_relation_2', 'complete_look_relation_3'] else 'multi_line_text_field' if key in ['reviews', 'shipping', 'returns'] else 'single_line_text_field',
                    #     'key': key,
                    #     'value': value,
                    #     'namespace': 'judgeme' if key in ['badge', 'widget'] else 'spr' if key == 'reviews' else 'SEOMetaManager' if key == 'config' else 'seo' if key == 'hidden' else 'msft_bingads' if key == 'product_status' else 'mc-facebook' if key == 'google_product_category' else 'reviews' if key in ['rating', 'rating_count'] else 'customs',
                    #     # 'value_type': 'integer' if key in ['hidden', 'rating_count'] else 'json_string' if key in ['product_status', 'rating'] else 'string',
                    #     'owner_resource': data['owner_resource'] if data.get('owner_resource') else 'product'
                    # }) for key, value in data.items() if key not in ['owner_id', 'namespace', 'key', 'value', 'value_type', 'type', 'owner_resource', 'handle', 'title']]

                    # ADH
                    # if f"{data['handle'].lower()} {data['title']}" in get_id:
                    #     array_data += [shopify.post_metafield(metafield={
                    #         'owner_id': get_id[f"{data['handle'].lower()} {data['title']}"],
                    #         'type': 'string' if key in ['description_tag', 'title_tag'] else 'number_decimal' if key == 'max_quantity' else 'single_line_text_field' if key in ['detail_title_1', 'video_1', 'family'] else 'multi_line_text_field' if key == 'detail_1' else 'url' if key == 'document_1' else 'dimension',
                    #         'key': key,
                    #         'value': str(value) if key in ['max_quantity'] else json.dumps({"value":value,"unit":"cm"}),
                    #         'namespace': "customs" if key in ["family"] else 'global' if key in ['description_tag', 'title_tag'] else 'dimensions' if key in ['height', 'width', 'large'] else 'my_fields',
                    #         #'value_type': 'json_string' if key in ['height', 'width', 'large'] else 'string',
                    #         'owner_resource': data['owner_resource'] if data.get('owner_resource') else 'product'
                    #     }) for key, value in data.items() if key not in ['owner_id', 'namespace', 'key', 'value', 'value_type', 'type', 'owner_resource', 'handle', 'title']]
                
                    if not f"{data['handle'].lower()} {data['title']}" in get_id:
                        array_data += [data]
                df_json = pd.DataFrame(array_data)
                df_json.to_excel('{}_status_{}.xlsx'.format(
                        name_file, '404'), index=False)
                # status_codes = set(d['status_code'] for d in array_data)
                # for status in status_codes:
                #     print('Status code {}'.format(status))
                #     data_to_excel = tuple(
                #         filter(lambda x: x.get('status_code') == status, array_data))
                #     if status in [201, 200, '200', '201']:
                #         data_to_excel = [d['metafield'] for d in data_to_excel]
                #     df_json = pd.DataFrame(data_to_excel)
                #     df_json.to_excel('{}_status_{}.xlsx'.format(
                #         name_file, status), index=False)
                #     array_data = [{
                #         'owner_id': data['owner_id'],
                #         'type': 'single_line_text_field' if key == 'family' else 'product_reference',
                #         'key': key,
                #         'value': value,
                #         'value_type': 'string',
                #         'owner_resource': data['owner_resource'] if data.get('owner_resource') else 'product'
                #     } for key, value in data.items() if key not in ['owner_id', 'namespace', 'key', 'value', 'value_type', 'type', 'owner_resource']]
                #     to_excel += array_data
                # df_json = pd.DataFrame(to_excel)
                # name_file = input('Nombre del archivo :')
                # df_json.to_excel('{}_indexed.xlsx'.format(name_file), index=True, index_label='indexed')
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
