#!/opt/homebrew/bin/python3
# -*- coding:utf-8 -*-
########################################################################################################################
# This file is a part of Jeyriku.net
#
# Created: 20.06.2022 16:55:57
# Author: Jeremie Rouzet
#
# Last Modified: 01.07.2022 16:23:48
# Modified By: Jeremie Rouzet
#
# Copyright (c) 2022 Jeyriku.net
########################################################################################################################

# Imports from Json to import datas from Json Format
import json
# Imports from Glob to ease Directory browsing
import glob
# Imports from Pandas to ease data analysis and manipulation
import pandas as pd
# Imports from Jinja2 to render Json datas with template
from jinja2 import Environment, FileSystemLoader
# Imports from os to manipulate files
import os


# Create a Python dictionary from Multiple Json Files
# Read each file and append the result
PATH1 = "/Users/jeremierouzet/jeysible/Json/"
PATH2 = "/Users/jeremierouzet/jeysible/templates/"
json_export = []

for file_json in glob.glob(PATH1 + "*.json"):
    with open(file_json, "r", encoding="utf-8") as data_json:
        print(type(data_json))
        json_export.append(json.load(data_json))

with open(PATH1 + "merged_file.json", "w", encoding="utf-8") as outfile:
    json.dump(json_export, outfile, indent=4)

# Build device List. This part of the script builds one list, each item has its own index.
with open(PATH1 + "merged_file.json", encoding="utf-8") as json_inventory:
    device_matrix = json.load(json_inventory)
    print(type(device_matrix))
    device_list = []
    for list_key in range(33):
        device_list.append(device_matrix[2]["results"][list_key]["id"])
        device_list.append(device_matrix[2]["results"][list_key]["name"])


# The previous list is splitted into sublists of two values each
def split(list_dev, chunk_size):

    for i in range(0, len(list_dev), chunk_size):
        yield list_dev[i:i + chunk_size]

# This chunk value allows the creation of multiple sublists with 2 elements Device_ID & Device_Name.
chunk_size = 2
list_device = list(split(device_list, chunk_size))
print(list_device)

# Now that we have a list with sublist we can use Pandas to create an easy to use dataframe
final_device_list = pd.DataFrame(list_device, columns=['ID', 'Name'])
print(final_device_list)

# Allows user to input device name to be configured
select_device_config = input("which device would like to configure ? \n")
print(select_device_config)

# Load data from JSON file into Python dictionary
config = json.load(open("/Users/jeremierouzet/jeysible/Json/merged_file.json", encoding="utf-8"))

# Load Jinja2 template
file_loader = FileSystemLoader(PATH2)
env = Environment(loader=file_loader, trim_blocks=True, lstrip_blocks=True, autoescape=True)
template = env.get_template("router_juniper_full_cfg_test.j2")



# Render template using data and print the output
# print(template.render(config))

if os.path.exists("/Users/jeremierouzet/jeysible/Json/merged_file.json"):
    os.remove("/Users/jeremierouzet/jeysible/Json/merged_file.json")
    print("The file has been deleted successfully")
else:
    print("The file does not exist!")
