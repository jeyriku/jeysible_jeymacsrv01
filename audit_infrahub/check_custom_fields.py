#!/usr/bin/env python3
"""
Vérifier les custom_fields dans le schéma Infrahub
"""
import requests
import json

query = '''
{
  __type(name: "JeylanDevice") {
    fields {
      name
      description
    }
  }
}
'''

response = requests.post(
    "http://jeysrv10:8000/graphql",
    json={"query": query},
    headers={"X-INFRAHUB-KEY": "188600a3-6e17-9f97-339f-c516618aa3c0"}
)

fields = response.json()["data"]["__type"]["fields"]
custom_fields = [f for f in fields if any(x in f["name"] for x in ["snmp", "dns", "dev_lpbk", "domain_name"])]

print(f"\n🔍 Custom fields Device trouvés: {len(custom_fields)}/10")
for field in sorted(custom_fields, key=lambda x: x["name"]):
    desc = field.get("description") or ""
    print(f"  ✓ {field['name']:25} {desc[:60]}")

# Vérifier les interfaces
query2 = '''
{
  __type(name: "JeylanInterfaces") {
    fields {
      name
      description
    }
  }
}
'''

response2 = requests.post(
    "http://jeysrv10:8000/graphql",
    json={"query": query2},
    headers={"X-INFRAHUB-KEY": "188600a3-6e17-9f97-339f-c516618aa3c0"}
)

fields2 = response2.json()["data"]["__type"]["fields"]
custom_fields2 = [f for f in fields2 if f["name"].startswith("iface_")]

print(f"\n🔍 Custom fields Interfaces trouvés: {len(custom_fields2)}/5")
for field in sorted(custom_fields2, key=lambda x: x["name"]):
    desc = field.get("description") or ""
    print(f"  ✓ {field['name']:25} {desc[:60]}")

# Vérifier le routing
query3 = '''
{
  __type(name: "JeylanRouting") {
    fields {
      name
      description
    }
  }
}
'''

response3 = requests.post(
    "http://jeysrv10:8000/graphql",
    json={"query": query3},
    headers={"X-INFRAHUB-KEY": "188600a3-6e17-9f97-339f-c516618aa3c0"}
)

fields3 = response3.json()["data"]["__type"]["fields"]
custom_fields3 = [f for f in fields3 if any(x in f["name"] for x in ["bgp", "ospf", "rr"])]

print(f"\n🔍 Custom fields Routing trouvés: {len(custom_fields3)}/5")
for field in sorted(custom_fields3, key=lambda x: x["name"]):
    desc = field.get("description") or ""
    print(f"  ✓ {field['name']:25} {desc[:60]}")

print(f"\n📊 Total: {len(custom_fields) + len(custom_fields2) + len(custom_fields3)}/20 custom_fields présents")
