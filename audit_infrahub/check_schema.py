#!/usr/bin/env python3
import requests

INFRAHUB_URL = "http://jeysrv10:8000/graphql"
INFRAHUB_TOKEN = "188600a3-6e17-9f97-339f-c516618aa3c0"

query = """
{
  __type(name: "JeylanDevice") {
    name
    fields {
      name
      type { name kind }
    }
  }
}
"""

response = requests.post(
    INFRAHUB_URL,
    json={"query": query},
    headers={"Content-Type": "application/json", "X-INFRAHUB-KEY": INFRAHUB_TOKEN},
    timeout=30
)

data = response.json()
if "data" in data and data["data"]["__type"]:
    fields = data["data"]["__type"]["fields"]
    print(f"Total: {len(fields)} champs\n")

    custom = [f["name"] for f in fields if "custom" in f["name"].lower() or f["name"].startswith("cf_")]
    if custom:
        print("🔧 CUSTOM FIELDS trouvés:")
        for c in custom:
            print(f"  - {c}")
    else:
        print("❌ Aucun custom field trouvé dans le schéma")

    print("\n📋 Tous les champs disponibles:")
    for f in sorted(fields, key=lambda x: x["name"]):
        print(f"  - {f['name']}")
