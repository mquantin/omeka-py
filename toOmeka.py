#!/usr/bin/env python2
# encoding: utf-8
"""
Adapted from https://github.com/wcaleb/omekadd
A basic Python API for Omeka, extended to deal with extra functionalities such as tag posting.

"""


from omekaclient2 import OmekaClient
import csv
import json
import re
import toOmeka_functions
import codecs
import os

config = json.loads(open('config.json').read())
APIurl = config['APIurl']
APIkey = config["APIkey"]
sqluser = config["sqluser"]
sqlpsw = config["sqlpsw"]
to_omeka_csv_file = config["to_omeka_csv_file"] # path to the csvfile with the data
delimiter = config["csvdelimiter"]#for the csv file
quotechar = config["csvquotechar"]#for the csv file
max_pict_size = config["max_pict_size"]#in kB, 1.9MB by default
DCfields_prefix = config["DCfields_prefix"]#case incensitive
full_path_to_picts = config["full_path_to_picts"]# path to pict folder if full path is not indicated in the pict names
create_collec = config["create_collec"]#create collection by name if does not exist
item_type_byname = config["item_type_byname"]
collection_by_name = config["collection_by_name"]


path, extension = os.path.splitext(to_omeka_csv_file)
logfilepath = path + '.log'
client = OmekaClient(APIurl.encode('ascii'), APIkey)




with open(to_omeka_csv_file, 'r')  as csvfile:
    with open(logfilepath, 'w') as logfileobj:
        csv_data = csv.reader(csvfile, delimiter=',', quotechar='"')
        header = csv_data.next()
        column2DC = toOmeka_functions.build_mapping_column2DC(DCfields_prefix, client, header)
        item_types = None
        collections = None
        if item_type_byname:
            item_types = toOmeka_functions.get_item_types_byname(client)
        if collection_by_name:
            collections = toOmeka_functions.get_collections_byname(client)
        print collections
        OneRow = sum(1 for line in open(to_omeka_csv_file))
        OneRow = 100.0/OneRow
        advence = 0.0
        for row in csv_data:
            advence += OneRow
            print 'complete', int(advence), '%'
            item = toOmeka_functions.omeka_item()
            item.get_data_from_row(row, column2DC, item_types, collections)
            item.upload_data(client)
            if item.files:
                item.upload_files(full_path_to_picts, max_pict_size, client)
            if item.tags:
                item.upload_tags(client)
            if item.log:
                item.write_log(logfileobj)
                print 'check log for item n°', item.id




# literal_dates = {'art déco':1937,
#                 'incendie':1940,
#                 'bombardement':1943,
#                 'agrandissement':1990}
