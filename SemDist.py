#!/usr/bin/env python3
# encoding: utf-8
import json
import math
#########################################
## TO OMEKA TEST salon M ################
#########################################
from omekaclient2 import OmekaClient

laptoplocalkey = "86363a7651722e9542efeca8348f46eda390e41d"
desktoplocalkey = '86363a7651722e9542efeca8348f46eda390e41d'

client = OmekaClient("http://localhost/omeka/api", laptoplocalkey)




############################
#####SCORE THE TAGS#########
#####CREATE BASE############
############################
# chaque mot-clef est dans un dict [key = id_keyword; value = poids]
# chaque item est dans un dict [key = id_item; value = 'tags' = un set de id_keyword, 'totWeight' = somme des poids de chaque mots clef]
items_tags = {}
idskey = {}
tagdict = {}
response, content = client.get("tags")
tags = json.loads(content, encoding='utf8', cls=None, object_hook=None, parse_float=None, parse_int=None, parse_constant=None, object_pairs_hook=None)
response, content = client.get("items")
items = json.loads(content, encoding='utf8', cls=None, object_hook=None, parse_float=None, parse_int=None, parse_constant=None, object_pairs_hook=None)

for tag in tags:
    idskey[tag['id']] = 0.0
    tagdict[tag['id']] = [tag['name']]

for item in items:
    tags_set = set()
    for tague in item['tags']:
        tags_set.add(tague['id'])
        idskey[tague['id']] += 1
    items_tags[item['id']] = {'tags': tags_set, 'totWeight': 0}

for tag in idskey:
    idskey[tag] = 1-((idskey[tag])/len(items))

for item in items_tags:
    for tag in items_tags[item]['tags']:
        items_tags[item]['totWeight'] += idskey[tag]#add the weight of each tag related to a item

for id_key, value in idskey.items():
    if value == 1:
        print 'this tag is only used one time (USELESS TAG!)', id_key, tagdict[id_key][0]


############################
#####SEM-DISTANCE###########
############################
dist = {}
seen = set()
for item in items_tags:
    for item2 in items_tags:
        if item <> item2 and not item2 not in seen:
            # print 'in'
            common_tags_weight = 0.0
            common_tags = items_tags[item]['tags'] & items_tags[item2]['tags']
            # print 'Common tags', common_tags
            if common_tags:
                nb_keywords = len(items_tags[item]['tags']) + len(items_tags[item2]['tags'])
                for common_tag in common_tags:
                    common_tags_weight += idskey[common_tag]
                # distance = 100 * common_tags_weight*2 / (items_tags[item]['totWeight']+items_tags[item2]['totWeight']) * math.log(nb_keywords)
                # distance = 100 * common_tags_weight*2 / (items_tags[item]['totWeight']+items_tags[item2]['totWeight'])# * math.log(nb_keywords)
                distance = int(100 * common_tags_weight) * math.log(nb_keywords)
                dist.setdefault(item2, {}).update({item:distance})
                dist.setdefault(item, {}).update({item2:distance})
    seen.add(item)
# print dist

# # print item_max, distance_max
# # print items_tags[item_max[0]], items_tags[item_max[1]]
print items_tags[313], idskey[241], idskey[242], idskey[243]
for item in dist[313]:
    print item, items_tags[item], dist[313][item]
