# omeka-py
## Features
- publish complete data (tags, collections, item_type...) on Omeka from csv file

## The CSV to omeka part:
* requieres omeka installed somewhere
* requieres imagemagick installed on your computer

### How to use
- fill a the config.json file
    * sqluser : Only if you need to get all tags (delete old, unused ones)
    * sqlpsw : Only if you need to get all tags (delete old, unused ones)
    * max_pict_size": in kb. check your authorized quota on omeka
    * full_path_to_picts: all the pictures should be in the same folder, NOT in subfolders
    * item_type_byname : true if the data in your csv contains type's name; false if it contains type's numbers
    * collection_by_name : true if the data in your csv contains collection's name; false if it contains collection's numbers
- fill a csv file based on the template one
- run toOmeka.py

### Limits
- the named collections you'll use in the csv column should be first created
- the named item_types you'll use in the csv column should first be created

## The relation creation part:
