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

PATH = '/Users/jeremierouzet/jeysible/Json/'
result = []

for f in glob.glob(PATH + "*.json"):
    with open(f, "r", encoding="utf-8") as data:
        print(type(data))
        result.append(json.load(data))
        print(type(result))

with open(PATH + "merged_file.json", 'w', encoding="utf-8") as outfile:
    json.dump(result, outfile)
