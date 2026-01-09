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
import pandas as pd

series = pd.Series(data=[111, 222, 3], index=['un' , 'deux' , 'trois'])
# ou series = pd.Series([111, 222, 3])

print(series['deux'])
# ou
print(series[0])
# colonnes multiples
print(series[['un' , 'trois']])

d = {'ColonneA' : pd.Series([111, 222, 333]),
     'ColonneB' : pd.Series([444, 555, 666])}
df = pd.DataFrame(d)

