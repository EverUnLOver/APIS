import pandas as pd
import json
from utils import Shopify

shopify = Shopify(store_name=input('Ingrese la tienda : '), password=input(
    'Ingrese el password or access_token : '), api_version=input('ingrese la version del api : '))

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
                array_r = shopify.get_products(fields='handle,title,id')
                df_json = [row.to_dict() for index, row in pd.read_excel('{}.xlsx'.format(input('Path del archivo con la data para filtrar: '))).iterrows()]
                filter_data =['{} {}'.format(row.get('Handle'), row.get('Title')) for row in df_json]
                array_r = tuple(filter(lambda data: '{} {}'.format(data.get('handle'), data.get('title')) in filter_data, array_r))

                json_obj = json.dumps(array_r, indent=4, sort_keys=True)

                name_file = input('Nombre del archivo : ')

                with open('{}.json'.format(name_file), 'w') as outfile:
                    outfile.write(json_obj)

                df_json = pd.read_json("{}.json".format(name_file))

                df_json.to_excel('{}_indexed.xlsx'.format(name_file), index=True, index_label='indexed')
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

                keys = ['product_id', 'id', 'owner_resource', 'owner_id', 'type', 'value', 'value_type', 'namespace', 'key']
                metafields = [{key: value for key, value in d.items() if key in keys } for d in array_r]

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
                    variant for product in array_r for variant in product['variants']]
                metafields_products = [data for t in filter(lambda x: x, map(shopify.get_metafields_product, [
                                                            d.get('id') for d in array_r if d.get('id')])) for data in t]
                metafields_variants = [data for t in filter(lambda x: x, map(shopify.get_metafields_variant, [(d.get(
                    'product_id'), d.get('id')) for d in variants if d.get('product_id') and d.get('id')])) for data in t]
                metafields = metafields_products + metafields_variants
                keys = ['product_id', 'id', 'owner_resource', 'owner_id', 'type', 'value', 'value_type', 'namespace', 'key']
                metafields = [{key: value for key, value in d.items() if key in keys } for d in metafields]
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
            action = input('What action do you want to perform? ( PUT_PRODUCTS / PUT_METAFIELDS ) : ')
            if action == 'PUT_PRODUCTS':
                df_json = pd.read_excel('{}.xlsx'.format(name_file), converters={'id': int})
                for index, row in df_json.iterrows():
                    shopify.put_product(product=row.to_dict())
                break
            elif action == 'PUT_METAFIELDS':
                df_json = pd.read_excel('{}.xlsx'.format(name_file), converters={'id': int, 'owner_id': int})
                for index, row in df_json.iterrows():
                    data = row.to_dict()
                    shopify.put_metafield(metafield=data)
                break
        break
    elif type_request == 'POST':
        name_file = input('Path del archivo excel : ')

        while 1:
            action = input('What action do you want to perform? ( POST_PRODUCTS / POST_METAFIELDS / DATA_SCIENCE_POST_METAFIELDS ) : ')
            if action == 'POST_PRODUCTS':
                df_json = pd.read_excel('{}.xlsx'.format(name_file))
                for index, row in df_json.iterrows():
                    shopify.post_product(product=row.to_dict())
                break
            elif action == 'POST_METAFIELDS':
                df_json = pd.read_excel('{}.xlsx'.format(name_file), converters={'owner_id': int})
                for index, row in df_json.iterrows():
                    shopify.post_metafield(metafield=row.to_dict())
                break
            elif action == 'DATA_SCIENCE_POST_METAFIELDS':
                df_json = pd.read_excel('{}.xlsx'.format(name_file), converters={'owner_id': int})
                to_excel = []
                for index, row in df_json.iterrows():
                    data = row.to_dict()
                    array_data = [shopify.post_metafield(metafield={
                        'owner_id': data['owner_id'],
                        'type': 'single_line_text_field' if key == 'family' else 'product_reference',
                        'key': key,
                        'value': value,
                        'namespace': 'customs',
                        'value_type': 'string',
                        'owner_resource': data['owner_resource'] if data.get('owner_resource') else 'product'
                    }) for key, value in data.items() if key not in ['owner_id', 'namespace', 'key', 'value', 'value_type', 'type', 'owner_resource']]
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
            action = input('What action do you want to perform? ( DELETE_PRODUCTS / DELETE_METAFIELDS ) : ')
            if action == 'DELETE_PRODUCTS':
                # df_json = pd.read_excel('{}.xlsx'.format(name_file), converters={'id': int})
                # for index, row in df_json.iterrows():
                #     shopify.delete_product(id=row.to_dict().get('id'))
                # break
                pass
            elif action == 'DELETE_METAFIELDS':
                df_json = pd.read_excel('{}.xlsx'.format(name_file), converters={'id': int})
                for index, row in df_json.iterrows():
                    shopify.delete_metafield(metafield_id=row.to_dict().get('id'))
                break
        break

print('Done')
