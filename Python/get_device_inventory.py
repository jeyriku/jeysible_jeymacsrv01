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

# Imports from Request to create REST API Call
import requests

# Imports from Json to export datas in Json Format
import json

# Define Netbox object and correct IP to build REST API Request
netbox = {
   "ip": "192.168.0.251"
}
headers = {
      "Accept" : "application/json",
      "Content-Type" : "application/json",
      "Authorization" : "Token 7435d9eb9841dc8a941417a0993fc531c3dc35ca",
   }
devices_path = "/api/dcim/devices"
url = f"https://{netbox['ip']}{devices_path}"
devices = requests.get(url, headers=headers, verify=False).json()  # type: ignore
print(json.dumps(devices, indent=4))
with open('/Users/jeremierouzet/jeysible/Json/devices.json', 'w', encoding='utf-8') as f:
    json.dump(devices, f, ensure_ascii=False, indent=4)

ifaces_path = "/api/dcim/interfaces"
url = f"https://{netbox['ip']}{ifaces_path}"
ifaces = requests.get(url, headers=headers, verify=False).json()  # type: ignore
print(json.dumps(ifaces, indent=4))
with open('/Users/jeremierouzet/jeysible/Json/ifaces.json', 'w', encoding='utf-8') as f:
    json.dump(ifaces, f, ensure_ascii=False, indent=4)


ips_path = "/api/ipam/ip-addresses/"
url = f"https://{netbox['ip']}{ips_path}"
ips = requests.get(url, headers=headers, verify=False).json()  # type: ignore
print(json.dumps(ips, indent=4))
with open('/Users/jeremierouzet/jeysible/Json/ips.json', 'w', encoding='utf-8') as f:
    json.dump(ips, f, ensure_ascii=False, indent=4)
