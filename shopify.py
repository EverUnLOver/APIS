import pandas as pd
import json
from utils import Shopify

shopify = Shopify(store_name=input('Ingrese la tienda : '), password=input(
    'Ingrese el password o accesstoken : '), api_version=input('ingrese la version del api : '))

while 1:
    type_request = input(
        "What type of request do you want to make? (GET/POST/PUT/DELETE): ")

    if type_request == "GET":
        while 1:
            action = input(
                'What action do you want to perform? ( GET_ALL_PRODUCTS / GET_SPECIFIC_FIELD_PRODUCT / GET_METAFIELDS ) : ')

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
            elif action == 'GET_SPECIFIC_FIELD_PRODUCT':
                array_r = shopify.get_products(metafield=input(
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
                    print(data)
                    shopify.put_metafield(metafield=data)
                break
        break
    elif type_request == 'POST':
        name_file = input('Path del archivo excel : ')

        while 1:
            action = input('What action do you want to perform? ( POST_PRODUCTS / POST_METAFIELDS ) : ')
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
        break
    elif type_request == 'DELETE':
        pass

print('Done')
