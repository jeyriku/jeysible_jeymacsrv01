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

with open('store.json', encoding="utf-8") as json_file:
    data = json.load(json_file)
print(type(data))
print(data)


# Result: <class 'dict'>
# Result: {'store': {'book': [{'category': 'reference', 'author': 'Nigel Rees', 'title': 'Sayings of the Century', 'price': 8.95}, {'category': 'fiction', 'author': 'Evelyn Waugh', 'title': 'Sword of Honour', 'price': 12.99}], 'bicycle': {'color': 'red', 'price': 19.95}}, 'expensive': 10}

print(data['store']['bicycle']['price'])

# Result: 19.95

print(data['store']['book'][1]['title'])

# Result: Sword of Honour

books = data['store']['book']
for book in books:
    if book['price'] <= 10.00:
        print(book)

# Result: {'category': 'reference', 'author': 'Nigel Rees', 'title': 'Sayings of the Century', 'price': 8.95}
