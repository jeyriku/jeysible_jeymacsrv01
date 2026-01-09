#!/usr/bin/env python3
"""Créer des dropdowns SNMP dans Infrahub via SDK ou GraphQL.

Usage:
  export INFRAHUB_TOKEN=...
  python3 script/create_snmp_dropdowns_sdk.py [--yes]

Le script :
- introspecte `SchemaDropdownAddInput` pour lister les champs requis
- affiche un payload suggéré pour chaque dropdown
- si `--yes` est fourni, tente d'exécuter la mutation pour chaque entrée

Remarque: tente d'utiliser un client SDK si disponible, sinon utilise `requests`.
"""
import os
import sys
import json
import argparse

# Try to import the Infrahub SDK (preferred)
INFRAHUB_TOKEN = os.getenv("INFRAHUB_API_TOKEN") or os.getenv("INFRAHUB_TOKEN")
ENDPOINT_ADDRESS = os.getenv("INFRAHUB_ADDRESS", "http://192.168.0.237:8000")
INFRAHUB_KEY = os.getenv("INFRAHUB_KEY", None)

try:
    from infrahub_sdk import Config
    try:
        # prefer synchronous client when available
        from infrahub_sdk import InfrahubClientSync as InfrahubClient
        SYNC_CLIENT = True
    except Exception:
        from infrahub_sdk import InfrahubClient as InfrahubClient
        SYNC_CLIENT = False
except Exception:
    InfrahubClient = None
    Config = None

SAMPLE_DROPDOWNS = {
    "snmp_location": [
        "int.jeyriku.net, 2 allee des campagnols, Seynod, 74600, Annecy, France [45.85995, 6.0793]"
    ],
    "snmp_community": ["jeyricorp"],
    "snmp_server1": ["192.168.0.239"],
    "snmp_server2": ["192.168.0.248"],
    "snmp_server3": ["192.168.0.249"],
    "snmp_server4": ["192.168.0.251"],
}


def _gql_requests(query, variables=None):
    import requests
    if not INFRAHUB_TOKEN:
        raise RuntimeError("INFRAHUB_TOKEN non défini dans l'environnement")
    payload = {"query": query}
    if variables is not None:
        payload["variables"] = variables
    x_infrahub_key = INFRAHUB_KEY or INFRAHUB_TOKEN
    headers = {
        "Content-Type": "application/json",
        "X-INFRAHUB-KEY": x_infrahub_key,
        "Authorization": f"Bearer {INFRAHUB_TOKEN}",
    }
    resp = requests.post(f"{ENDPOINT_ADDRESS}/graphql", json=payload, headers=headers, timeout=10)
    try:
        return resp.json()
    except ValueError:
        resp.raise_for_status()


def _get_sdk_client():
    if not InfrahubClient or not Config:
        return None
    # Avoid mixing env username/password with token-based auth
    backup_username = os.environ.pop("INFRAHUB_USERNAME", None)
    backup_password = os.environ.pop("INFRAHUB_PASSWORD", None)
    try:
        cfg = Config(address=ENDPOINT_ADDRESS, api_token=INFRAHUB_TOKEN)
    finally:
        # restore environment (if any)
        if backup_username is not None:
            os.environ["INFRAHUB_USERNAME"] = backup_username
        if backup_password is not None:
            os.environ["INFRAHUB_PASSWORD"] = backup_password
    client = InfrahubClient(config=cfg)
    return client


def gql(query, variables=None):
    """Execute GraphQL using SDK when available, otherwise fallback to requests."""
    client = _get_sdk_client()
    if client:
        try:
            if SYNC_CLIENT:
                return client.execute_graphql(query, variables=variables)
            else:
                import asyncio
                return asyncio.run(client.execute_graphql(query, variables=variables))
        finally:
            try:
                client.close()
            except Exception:
                pass
    return _gql_requests(query, variables)


def introspect_input(name):
    query = (
        'query Introspect($name: String!) { '
        '__type(name: $name) { name inputFields { name description '
        'type { kind name ofType { kind name ofType { kind name } } } } } }'
    )
    res = gql(query, {"name": name})
    return res


def test_auth():
    """Small query to validate token/headers by requesting CoreAccountList."""
    query = '{ CoreAccountList { edges { node { id username email isActive } } } }'
    return gql(query)


def build_suggested_payload(dropdown_name, values, input_fields):
    # Map available input fields to sensible keys when possible
    data = {}
    names = [f["name"] for f in input_fields]
    if "attribute" in names:
        data["attribute"] = dropdown_name
    if "dropdown" in names:
        data["dropdown"] = dropdown_name
    if "kind" in names:
        # best-effort default; may need adjustment per installation
        data["kind"] = "profile"
    if "label" in names:
        data["label"] = dropdown_name
    # Many schemas expect the actual option as `value`/`label` within `object` or similar.
    # We'll try common field names if present.
    if "object" in names:
        # create a list of objects
        data["object"] = [{"value": v, "label": v, "description": ""} for v in values]
    elif "value" in names or "values" in names or "items" in names:
        # fallback: expose as 'values'
        data["values"] = values
    return data


def create_dropdown_mutation(data):
    # generic mutation using variable $data
    mutation = """
    mutation SchemaDropdownAdd($data: SchemaDropdownAddInput!) {
      SchemaDropdownAdd(data: $data) { ok object { value label description } }
    }
    """
    return gql(mutation, {"data": data})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--yes", action="store_true", help="Procéder sans demander confirmation")
    args = parser.parse_args()

    if not INFRAHUB_TOKEN:
        print("ERROR: INFRAHUB_TOKEN non défini. Exportez-le et réessayez.")
        print("Ex: export INFRAHUB_TOKEN=xxx")
        sys.exit(2)

    print(f"Endpoint: {ENDPOINT_ADDRESS}")
    print("Vérification d'authentification via CoreAccountList...")
    auth_res = test_auth()
    if auth_res.get("errors"):
        print("Authentification échouée:", json.dumps(auth_res["errors"], indent=2, ensure_ascii=False))
        print("Vérifiez que INFRAHUB_TOKEN est correct et réessayez.")
        sys.exit(3)

    print("Introspection de SchemaDropdownAddInput...")
    res = introspect_input("SchemaDropdownAddInput")
    if res.get("errors"):
        print("Introspection échouée:", json.dumps(res["errors"], indent=2, ensure_ascii=False))
        sys.exit(4)

    type_info = res.get("data", {}).get("__type")
    if not type_info:
        print("Aucune information __type retournée")
        print(json.dumps(res, indent=2))
        sys.exit(4)

    input_fields = type_info.get("inputFields", [])
    print("Champs de SchemaDropdownAddInput:")
    for f in input_fields:
        kind = f.get("type", {}).get("kind")
        tname = f.get("type", {}).get("name") or f.get("type", {}).get("ofType", {}).get("name")
        req = "(required)" if f.get("type", {}).get("kind") == "NON_NULL" else ""
        print(f" - {f['name']}: {tname} {kind} {req}")

    print("\nGénération des payloads suggérés (à vérifier avant création):")
    suggested = {}
    for name, vals in SAMPLE_DROPDOWNS.items():
        payload = build_suggested_payload(name, vals, input_fields)
        suggested[name] = payload
        print(f"\n-- {name} --")
        print(json.dumps(payload, indent=2, ensure_ascii=False))

    if not args.yes:
        print("\nSi les payloads semblent corrects, relancez avec --yes pour créer les dropdowns.")
        return

    print("\nCréation des dropdowns (tentative)...")
    for name, payload in suggested.items():
        print(f"--- Creating {name} ---")
        resp = create_dropdown_mutation(payload)
        print(json.dumps(resp, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
