import json

# Opening JSON file
f = open('look.json')

# returns JSON object as
# a dictionary
data = json.load(f)

# Iterating through the json
# list
metafields = {}
for metafield in data:
    metafields[metafield["key"]] = {
        "namespace": metafield["namespace"],
        "type": metafield["type"]
    }
print(metafields)

# Closing file
f.close()
