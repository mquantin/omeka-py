#!/usr/bin/env python2
# encoding: utf-8
import json
import re
import os
import datetime

def build_mapping_column2DC(DCfields_prefix, client, header):
    # A dictionary of all the element ids in the Omeka database
    #generate this dict using Omeka API elements resource
    DC = {}
    response, content = client.get("elements")
    elements = json.loads(content, encoding='utf8', cls=None, object_hook=None, parse_float=None, parse_int=None, parse_constant=None, object_pairs_hook=None)
    for element in elements:
        DC[element['id']] = element
    # Reversing the keys and values of elements dictionary for easier lookup
    CD = {}
    for key, val in DC.items():
        CD[val['name']] = key

    # Get csv from input file and catch the row index in header with the DC:field index
    column_2DC = {}
    for i, case in enumerate(header):
        if re.match(DCfields_prefix+r'(?iu)', case):
            fields = case.split(':', 1)
            column_2DC[i] = int(CD[fields[1]])# the row index is matching the DC field in omeka
        # the row index ddoesn't match any DC field id
        elif re.match(r'file.?(?iu)', case):
            column_2DC[i] = 'file'
        elif re.match(r'tag.?(?iu)', case):
            column_2DC[i] = 'tag'
        elif re.match(r'featured(?iu)', case):
            column_2DC[i] = 'featured'
        elif re.match(r'public(?iu)', case):
            column_2DC[i] = 'public'
        elif re.match(r'item.type(?iu)', case):
            column_2DC[i] = 'item_type'
        elif re.match(r'collection(?iu)', case):
            column_2DC[i] = 'collection'
        else:
            column_2DC[i] = None
            print 'WARNING: column {}: \'{}\'  in your csv file does not match any omeka field'.format(i+1,  case)
            # i+1  to count from the first column as column n°1
    return column_2DC

def get_item_types_byname(client):
    #dict item_type_name: item_type_id
    item_types_dict = {}
    response, content = client.get('item_types')
    item_types = json.loads(content, encoding='utf8', cls=None, object_hook=None, parse_float=None, parse_int=None, parse_constant=None, object_pairs_hook=None)
    for item_type in item_types:
        item_types_dict[item_type['name'].lower()] = int(item_type['id'])
    return item_types_dict

def get_collections_byname(client):
    #dict item_type_name: item_type_id
    collections_dict = {}
    response, content = client.get('collections')
    collections = json.loads(content, encoding='utf8', cls=None, object_hook=None, parse_float=None, parse_int=None, parse_constant=None, object_pairs_hook=None)
    for collec in collections:
        elems = collec["element_texts"]
        for elem in elems:
            if elem["element"]["id"] == 50:#the "title" element DC field
                collections_dict[elem["text"].lower()] = collec["id"]
                break
    return collections_dict


def get_alltags_byname(client, sql_user, sql_psw):
    tags_byname = {}
    tags = client.get_alltags(sql_user, sql_psw)
    for tag in tags:
        tags_byname[tag['name']] = tag['id']
    return tags_byname



class omeka_item:
    def __init__ (self):
        self.id = 0
        self.public = True
        self.featured = False
        self.tags = []
        self.element_texts = []
        self.collection = {}
        self.item_type = {}
        self.tags = []
        self.files = []
        self.log = []

    def write_log(self, logfileobj):
        logfileobj.write("\n###########################\n")
        logfileobj.write('item number')
        logfileobj.write(str(self.id))
        logfileobj.write('\n')
        for item in self.log:
            logfileobj.write(item)
            logfileobj.write('\n')
        logfileobj.write("###########################\n")

    def check_true(self, case):
        if re.match(r'true|vrai|oui|yes(?iu)', case):
            return True
        if re.match(r'false|faux|non|no(?iu)', case):
            return False

    def clean_text_imput(self, string, lower = True):
        if lower == True:
            string = string.lower()
        s = string.strip()
        s = re.sub(r'^[.,; ]*', '',s)
        s = re.sub(r'[.,; ]*$', '',s)
        s = s.strip()
        return s

    def get_data_from_row(self, row, col_2DC, item_type_byname, collections_byname):
        for i, case in enumerate(row):
            if type(col_2DC[i]) == int:# means it is a DC field
                element_text = {"html": False, "text": "none", "element_set": {"id": 1}}
                if re.search(r'<[^/]*/>', case):
                    element_text['html'] = True
                element_text['element'] = {"id":col_2DC[i]}
                if col_2DC[i] == 40:#trying to isoformat the date yyyy/mm/dd
                    if re.match(r'\d\d?/\d\d/\d\d\d\d', case):
                        case = datetime.datetime.strptime(case, '%d/%m/%Y').date().isoformat()
                    if re.match(r'\d\d/\d\d\d\d', case):
                        case = datetime.datetime.strptime(case, '%m/%Y').date().isoformat()
                element_text['text'] = self.clean_text_imput(case)
                # print 'ELEMENT TEXT',element_text.copy()
                self.element_texts.append(element_text)
                # print 'ITEM GROWING', item
            elif col_2DC[i] == 'featured':
                check = self.check_true(case)
                if check is not None : self.featured = check
            elif col_2DC[i] == 'public':
                check = self.check_true(case)
                if check is not None : self.public = check
            elif col_2DC[i] == 'collection':
                if not collections_byname:
                    try:
                        self.collection['id'] = int(case)
                    except:
                        self.log.append(str('COLLECTION ' + case + ' NOT RECOGNIZED'))
                else:
                    try:
                        self.collection['id'] = collections_byname[case.lower().decode('utf8')] #dict collection_name: collection_id
                    except:
                        self.log.append(str('COLLECTION ' + case + ' NOT RECOGNIZED'))
            elif col_2DC[i] == 'item_type':
                if not item_type_byname:
                    try:
                        self.item_type['id'] = int(case)
                    except:
                        self.log.append(str('ITEM_TYPE ' + case + ' NOT RECOGNIZED'))
                else:
                    try:
                        self.item_type['id'] = item_type_byname[case.lower().decode('utf8')] #dict item_type_name: item_type_id
                    except:
                        self.log.append(str('ITEM_TYPE ' + case + ' NOT RECOGNIZED'))
            elif col_2DC[i] == 'tag':
                self.tags = [self.clean_text_imput(tag) for tag in re.split(r'[,;]',case) if re.search(r'\w', tag)]
            elif col_2DC[i] == 'file':
                self.files = [self.clean_text_imput(fichier, False) for fichier in re.split(r'[,;]', case) if re.search(r'\w', fichier)]

    def upload_data(self, client):
        item_dict = {"collection": self.collection, "item_type": self.item_type, "featured": self.featured, "public": self.public, 'element_texts': self.element_texts}
        item_json = json.dumps(item_dict)
        # with open('jsonfichier.json', 'w') as itemfile:
        #     json.dump(item, itemfile, ensure_ascii=False, indent=4)
        # print '\n\n ##### \n\n JSON STR', jsonstr
        response, content = client.post("items", item_json)
        location = response["location"]
        self.id = int(location.split("/")[-1])


    def upload_files(self, full_path_to_picts, max_pict_size, client):
        # def shellquote(s):
        #     return "'" + s.replace("'", "'\\''") + "'"
        def reduce_pict_weight(fichier, max_pict_size, iteration=0):
            self.log.append(str('reducing pict weight. iteration n'+ str(iteration)))
            path, extension = os.path.splitext(fichier)
            if iteration == 0:
                # newpath = shellquote(path+'_mod.jpg')
                command = 'convert {} -define jpg:extent={}kb {}'.format(fichier, max_pict_size, path+'_mod.jpg')
                # command = pipes.quote(command)
                command = re.sub("(!|\$|#|&|\"|\'|\(|\)|\||<|>|`|\\\|;)", r"\\\1", command)
                os.system(command)
                fichier = path+'_mod.jpg'
            else:
                ratio = 100-10*iteration
                if ratio < 70: ratio = 70
                command = 'convert {} -define jpg:extent={}kb -scale {}% {}'.format(fichier, max_pict_size, ratio, fichier)
                # command = pipes.quote(command)
                command = re.sub("(!|\$|#|&|\"|\'|\(|\)|\||<|>|`|\\\|;)", r"\\\1", command)
                os.system(command)
            if os.path.getsize(fichier) > max_pict_size*1000:
                iteration += 1
                reduce_pict_weight(fichier, max_pict_size, iteration)
            return fichier

        uploadjson = {"item": {"id": self.id}}
        uploadmeta = json.dumps(uploadjson)
        for fichier in self.files:
            if not re.match(r'^\\', fichier) and not full_path_to_picts == '':
                fichier = os.path.join(full_path_to_picts, fichier)
            if os.path.isfile(fichier):
                if os.path.getsize(fichier) > max_pict_size*1000:
                    fichier = reduce_pict_weight(fichier, max_pict_size)
                uploadfile = open(fichier, "r").read()
                response, content = client.post_file(uploadmeta, fichier, uploadfile)
                if re.search(r'message', response):
                    self.log.append(str('FILE '+ str(fichier) + ' Has a problem' + content))
            else:
                self.log.append(str('FILE '+ str(fichier) + ' HAS INCORRECT NAME, NOT MATCHING ANY EXISTING FILE IN FOLDER'))

    def upload_tags(self, client):
        tags_found = []
        for tag in self.tags:
            tags_found.append({'name':tag})
        if tags_found:
            jsonstr = json.dumps({'tags': tags_found})
            response, content = client.put("items", iditem, jsonstr)
            if re.search(r'message', response):
                self.log.append(str('TAGS '+ str(tags) + ' Has a problem' + content))
