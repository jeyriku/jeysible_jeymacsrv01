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
import json
import glob
from pprint import pformat

# import os
# os.path.join()


# import ast
# data = json.dumps(ast.literal_eval(json_data_single_quote))

PATH = '/Users/jeremierouzet/jeysible/Json/'
result = []


for f in glob.glob(PATH + "devices.json"):
    with open(f, 'r', encoding="utf-8") as infile:
        for line in infile.readlines():
            result.append(json.loads(line))

with open("merged_file.json", "w", encoding="utf-8") as outfile:
    json.dump(result, outfile)
    print("merged_file.json")

with open("merged_file.json", "r" , encoding="utf-8") as fp:
    print(pformat(json.load(fp)))
