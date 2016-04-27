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
import time
import logging

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
item_type_byname = config["item_type_byname"]
collection_by_name = config["collection_by_name"]
date_format = config["date_format"]#usually %d/%m/%Y but may differ; only concerns the complete dates; if only year, or year and month there is no mapping problem.
force_same_name_item = config["force_same_name_item"]

path, extension = os.path.splitext(to_omeka_csv_file)
client = OmekaClient(APIurl.encode('ascii'), APIkey)
toOmeka_functions.start_log()


with open(to_omeka_csv_file, 'r')  as csvfile:
    logging.info('\n### loading from csv file: '+ str(to_omeka_csv_file))
    logging.info('\n### with config: '+ str(config))
    csv_data = csv.reader(csvfile, delimiter=',', quotechar='"')
    header = csv_data.next()
    column2DC = toOmeka_functions.build_mapping_column2DC(DCfields_prefix, client, header)
    item_types = None
    collections = None
    if item_type_byname:
        item_types = toOmeka_functions.get_item_types_byname(client)
    if collection_by_name:
        collections = toOmeka_functions.get_collections_byname(client)
    if not force_same_name_item:
        items_names = toOmeka_functions.get_allitems_names(client)
    else:
        items_names = False

    OneRow = sum(1 for line in open(to_omeka_csv_file))
    OneRow = 100.0/OneRow
    advence = 0.0
    allitems = set()
    allproblems = set()
    for row in csv_data:
        item = toOmeka_functions.omeka_item()
        problems = item.get_data_from_row(row, column2DC, item_types, collections, items_names, date_format)
        allitems.add(item)
        allproblems.update(problems)
    allproblems.update(toOmeka_functions.checkfileexists(full_path_to_picts, allitems))
    user_resp = toOmeka_functions.askuser(allproblems)
    if user_resp == 'y':
        for item in allitems:
            advence += OneRow
            print 'complete', int(advence), '%'
            if item.element_texts:
                item.upload_data(client)
            if item.files:
                item.upload_files(full_path_to_picts, max_pict_size, client)
            if item.tags:
                item.upload_tags(client)
            time.sleep(1)




# literal_dates = {'art déco':1937,
#                 'incendie':1940,
#                 'bombardement':1943,
#                 'agrandissement':1990}
