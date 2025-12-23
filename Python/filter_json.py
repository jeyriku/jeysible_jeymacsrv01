#!/opt/homebrew/bin/python3
# -*- coding:utf-8 -*-
########################################################################################################################
# This file is a part of Jeyriku.net
#
# Created: 30.12.2022 15:27:57
# Author: Jeremie Rouzet
#
# Last Modified: 30.12.2022 15:35:42
# Modified By: Jeremie Rouzet
#
# Copyright (c) 2022 Jeyriku.net
########################################################################################################################
# Imports from Json to export datas in Json Format
import json
# Imports from Request to create REST API Call
import requests
# Imports from Jmespath to Filter Json data
import jmespath


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


devices = requests.get(url, headers=headers, verify=False, timeout=30).json()  # timeout:30sec
with open('./Python/devices.json', 'w', encoding='utf-8') as f:
    json.dump(devices, f, ensure_ascii=False, indent=4)
    data = jmespath.search('results[*].{Name: name, snmp_loc: custom_fields.snmp_location,IP: primary_ip.address, snmp_com: custom_fields.snmp_community, snmp_srv: custom_fields.snmp_server}', devices)

with open('./Python/results.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

input_dev = input("Enter the Hostname of the device to be configured: \n")
print(f"Is this what you just said?\n {input_dev}")

print("Started Reading JSON file")
with open('./Python/results.json', "r" , encoding='utf-8') as check_dev:
    print("Converting JSON encoded data into Python dictionary")
    data = json.load(check_dev)

# Search data based on key and value using filter and list method
result = (list(filter(lambda x:x["Name"]== input_dev, data)))
with open("./Python/target_dev.json", "w" , encoding='utf-8') as outfile:
    json.dump(result, outfile)
