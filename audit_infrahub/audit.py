#!/usr/bin/env python3
"""
Script d'audit unifié pour Infrahub
Analyse les devices, interfaces, sites et plateformes
"""
import argparse
import json
import sys
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import requests

# Ajouter le répertoire parent pour importer extract_custom_fields
sys.path.insert(0, str(Path(__file__).parent))
from extract_custom_fields import (
    extract_custom_fields_from_templates,
    extract_custom_fields_from_playbooks,
    categorize_custom_fields
)

# Configuration
BASE_DIR = Path(__file__).parent
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

INFRAHUB_URL = "http://jeysrv10:8000/graphql"
INFRAHUB_TOKEN = "188600a3-6e17-9f97-339f-c516618aa3c0"

class InfrahubAuditor:
    """Auditeur pour Infrahub"""

    def __init__(self, url=INFRAHUB_URL, token=INFRAHUB_TOKEN):
        self.url = url
        self.headers = {
            "Content-Type": "application/json",
            "X-INFRAHUB-KEY": token
        }

    def query(self, graphql_query):
        """Exécute une requête GraphQL"""
        try:
            response = requests.post(
                self.url,
                json={"query": graphql_query},
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            if "errors" in data:
                print(f"⚠️  Erreurs GraphQL: {data['errors']}")
                return None

            return data.get("data")
        except Exception as e:
            print(f"❌ Erreur requête API: {e}")
            return None

    def get_devices(self):
        """Récupère tous les devices avec tous les champs disponibles"""
        query = """
        {
          JeylanDevice {
            edges {
              node {
                id
                display_label
                name { value }
                fqdn { value }
                mgmt_ip { value }
                status { value }
                asset_tag { value }
                serial_number { value }
                os_version { value }
                dns_suffix { value }
                interfaces_count { value }
                warranty_expiration { value }
                purchase_date { value }
                role { node { id name { value } } }
                type { node { id name { value } } }
                platform { node { id name { value } } }
                manufacturer { node { id name { value } } }
                model { node { id name { value } } }
                osversion { node { id display_label } }
                location_ref { node { id name { value } } }
              }
            }
          }
        }
        """
        data = self.query(query)
        if data and "JeylanDevice" in data:
            return [edge["node"] for edge in data["JeylanDevice"]["edges"]]
        return []

    def audit_devices(self):
        """Audit détaillé des devices"""
        print("\n📱 AUDIT DES DEVICES")
        print("="*80)

        devices = self.get_devices()
        print(f"✅ {len(devices)} devices trouvés")

        # Analyse
        issues = []
        stats = {
            "total": len(devices),
            "sans_ip": 0,
            "sans_role": 0,
            "sans_platform": 0,
            "sans_type": 0,
            "sans_manufacturer": 0,
            "sans_model": 0,
            "sans_location": 0,
            "sans_serial": 0,
            "sans_asset_tag": 0,
            "sans_fqdn": 0,
            "sans_os_version": 0,
            "sans_interfaces": 0,
            "status_inactive": 0,
            "warranty_expired": 0,
            "warranty_soon": 0
        }

        from datetime import datetime, timedelta
        today = datetime.now()
        warning_period = today + timedelta(days=90)

        for device in devices:
            name = device["name"]["value"]
            ip = device.get("mgmt_ip", {}).get("value") if device.get("mgmt_ip") else None
            role = device.get("role", {}).get("node") if device.get("role") else None
            platform = device.get("platform", {}).get("node") if device.get("platform") else None
            device_type = device.get("type", {}).get("node") if device.get("type") else None
            manufacturer = device.get("manufacturer", {}).get("node") if device.get("manufacturer") else None
            model = device.get("model", {}).get("node") if device.get("model") else None
            location = device.get("location_ref", {}).get("node") if device.get("location_ref") else None
            status = device.get("status", {}).get("value") if device.get("status") else None
            serial = device.get("serial_number", {}).get("value") if device.get("serial_number") else None
            asset_tag = device.get("asset_tag", {}).get("value") if device.get("asset_tag") else None
            fqdn = device.get("fqdn", {}).get("value") if device.get("fqdn") else None
            os_version = device.get("os_version", {}).get("value") if device.get("os_version") else None
            warranty = device.get("warranty_expiration", {}).get("value") if device.get("warranty_expiration") else None
            interfaces_count = device.get("interfaces_count", {}).get("value", 0) if device.get("interfaces_count") else 0

            device_issues = []

            # Vérifications critiques
            if not ip:
                stats["sans_ip"] += 1
                device_issues.append("❌ Pas d'IP de management")

            if not role:
                stats["sans_role"] += 1
                device_issues.append("❌ Pas de rôle défini")

            # Vérifications importantes
            if not platform:
                stats["sans_platform"] += 1
                device_issues.append("⚠️  Pas de plateforme définie")

            if not device_type:
                stats["sans_type"] += 1
                device_issues.append("⚠️  Pas de type défini")

            if not manufacturer:
                stats["sans_manufacturer"] += 1
                device_issues.append("ℹ️  Pas de fabricant défini")

            if not model:
                stats["sans_model"] += 1
                device_issues.append("ℹ️  Pas de modèle défini")

            if not location:
                stats["sans_location"] += 1
                device_issues.append("ℹ️  Pas de localisation définie")

            # Vérifications optionnelles
            if not serial:
                stats["sans_serial"] += 1
                device_issues.append("📝 Pas de numéro de série")

            if not asset_tag:
                stats["sans_asset_tag"] += 1
                device_issues.append("📝 Pas d'asset tag")

            if not fqdn:
                stats["sans_fqdn"] += 1
                device_issues.append("📝 Pas de FQDN")

            if not os_version:
                stats["sans_os_version"] += 1
                device_issues.append("📝 Pas de version OS")

            if interfaces_count == 0:
                stats["sans_interfaces"] += 1
                device_issues.append("⚠️  Aucune interface")

            if status and status != "active":
                stats["status_inactive"] += 1
                device_issues.append(f"⚠️  Status: {status}")

            # Vérification garantie
            if warranty:
                try:
                    warranty_date = datetime.fromisoformat(warranty.replace('Z', '+00:00'))
                    if warranty_date < today:
                        stats["warranty_expired"] += 1
                        device_issues.append(f"⏰ Garantie expirée: {warranty}")
                    elif warranty_date < warning_period:
                        stats["warranty_soon"] += 1
                        device_issues.append(f"⏰ Garantie bientôt expirée: {warranty}")
                except:
                    pass

            if device_issues:
                issues.append({
                    "device": name,
                    "issues": device_issues
                })

        # Affichage résumé
        print(f"\n📊 Statistiques:")
        print(f"  Total: {stats['total']}")
        print(f"\n  🔴 Critiques:")
        print(f"    Sans IP management: {stats['sans_ip']}")
        print(f"    Sans rôle: {stats['sans_role']}")
        print(f"\n  🟠 Importantes:")
        print(f"    Sans plateforme: {stats['sans_platform']}")
        print(f"    Sans type: {stats['sans_type']}")
        print(f"    Sans interfaces: {stats['sans_interfaces']}")
        print(f"    Status non-actif: {stats['status_inactive']}")
        print(f"\n  🟡 Informatives:")
        print(f"    Sans fabricant: {stats['sans_manufacturer']}")
        print(f"    Sans modèle: {stats['sans_model']}")
        print(f"    Sans localisation: {stats['sans_location']}")
        print(f"\n  📝 Optionnelles:")
        print(f"    Sans numéro série: {stats['sans_serial']}")
        print(f"    Sans asset tag: {stats['sans_asset_tag']}")
        print(f"    Sans FQDN: {stats['sans_fqdn']}")
        print(f"    Sans version OS: {stats['sans_os_version']}")
        print(f"\n  ⏰ Garanties:")
        print(f"    Garanties expirées: {stats['warranty_expired']}")
        print(f"    Garanties <90j: {stats['warranty_soon']}")

        if issues:
            print(f"\n⚠️  {len(issues)} devices avec problèmes:")
            for item in issues[:10]:
                print(f"  - {item['device']}")
                for issue in item['issues']:
                    print(f"    • {issue}")
            if len(issues) > 10:
                print(f"  ... et {len(issues) - 10} autres")

        return {
            "type": "devices",
            "stats": stats,
            "issues": issues,
            "devices": devices
        }

    def audit_roles(self):
        """Audit des rôles"""
        print("\n👥 AUDIT DES RÔLES")
        print("="*80)

        devices = self.get_devices()

        # Compter devices par rôle
        roles = defaultdict(list)
        devices_sans_role = []

        for device in devices:
            name = device["name"]["value"]
            role = device.get("role", {}).get("node")

            if role:
                role_name = role.get("name", {}).get("value", "unknown")
                roles[role_name].append(name)
            else:
                devices_sans_role.append(name)

        print(f"✅ {len(roles)} rôles trouvés")
        print(f"\n📊 Distribution:")
        for role, device_list in sorted(roles.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"  {role}: {len(device_list)} devices")

        if devices_sans_role:
            print(f"\n⚠️  {len(devices_sans_role)} devices sans rôle:")
            for name in devices_sans_role[:5]:
                print(f"  - {name}")
            if len(devices_sans_role) > 5:
                print(f"  ... et {len(devices_sans_role) - 5} autres")

        return {
            "type": "roles",
            "roles": dict(roles),
            "devices_sans_role": devices_sans_role
        }

    def audit_platforms(self):
        """Audit des plateformes"""
        print("\n🔧 AUDIT DES PLATEFORMES")
        print("="*80)

        devices = self.get_devices()

        # Compter devices par plateforme
        platforms = defaultdict(list)
        devices_sans_platform = []

        for device in devices:
            name = device["name"]["value"]
            platform = device.get("platform", {}).get("node")

            if platform:
                platform_name = platform.get("name", {}).get("value", "unknown")
                platforms[platform_name].append(name)
            else:
                devices_sans_platform.append(name)

        print(f"✅ {len(platforms)} plateformes trouvées")
        print(f"\n📊 Distribution:")
        for platform, device_list in sorted(platforms.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"  {platform}: {len(device_list)} devices")

        if devices_sans_platform:
            print(f"\n⚠️  {len(devices_sans_platform)} devices sans plateforme:")
            for name in devices_sans_platform[:5]:
                print(f"  - {name}")
            if len(devices_sans_platform) > 5:
                print(f"  ... et {len(devices_sans_platform) - 5} autres")

        return {
            "type": "platforms",
            "platforms": dict(platforms),
            "devices_sans_platform": devices_sans_platform
        }

    def audit_custom_fields(self):
        """Audit des custom fields NetBox manquants dans Infrahub"""
        print("\n🔧 AUDIT DES CUSTOM FIELDS (Héritage NetBox)")
        print("="*80)

        # Extraire les custom_fields depuis templates et playbooks
        print(f"📁 Extraction depuis templates et playbooks...")
        template_fields = extract_custom_fields_from_templates()
        playbook_fields = extract_custom_fields_from_playbooks()

        # Combiner les champs
        all_fields_set = set(template_fields) | set(playbook_fields.keys())
        # Créer un dict avec les sources pour chaque champ
        all_fields = {}
        for field in template_fields:
            all_fields[field] = ["templates"]
        for field, sources in playbook_fields.items():
            if field in all_fields:
                all_fields[field].extend(sources)
            else:
                all_fields[field] = sources

        categorized = categorize_custom_fields(all_fields_set)

        total_custom_fields = len(all_fields_set)
        print(f"\n📊 {total_custom_fields} custom_fields uniques trouvés")

        # Vérifier quels champs existent dans Infrahub
        schema_query = """
        {
          __type(name: "JeylanDevice") {
            fields {
              name
            }
          }
        }
        """

        data = self.query(schema_query)
        infrahub_fields = []
        if data and "__type" in data and data["__type"]:
            infrahub_fields = [f["name"] for f in data["__type"]["fields"]]

        # Chercher les custom fields dans Infrahub
        infrahub_custom_fields = [f for f in infrahub_fields if "custom" in f.lower() or f.startswith("cf_")]

        # Comparer - tous les custom_fields NetBox sont manquants car Infrahub n'a pas de custom_fields
        missing_fields = [(cat, field) for cat in categorized.keys()
                         for field in categorized[cat]]

        # Affichage
        print(f"\n📊 Résultat:")
        print(f"  Custom fields dans NetBox: {total_custom_fields}")
        print(f"  Custom fields dans Infrahub: {len(infrahub_custom_fields)}")
        print(f"  ❌ Manquants: {len(missing_fields)}")

        if infrahub_custom_fields:
            print(f"\n✅ Custom fields trouvés dans Infrahub:")
            for field in infrahub_custom_fields[:10]:
                print(f"  - {field}")
            if len(infrahub_custom_fields) > 10:
                print(f"  ... et {len(infrahub_custom_fields) - 10} autres")

        if missing_fields:
            print(f"\n⚠️  Custom fields à créer dans Infrahub:")

            for category, fields in sorted(categorized.items()):
                if fields:
                    print(f"\n  📁 {category} ({len(fields)} champs):")
                    for field in sorted(fields):
                        # Compter les usages depuis all_fields
                        count = len(all_fields.get(field, []))
                        print(f"    - {field:25} ({count:2} fichiers)")

            # Champs critiques
            critical_fields = [(field, len(sources))
                              for field, sources in all_fields.items()
                              if len(sources) > 5]

            if critical_fields:
                print(f"\n  ⚠️  CHAMPS CRITIQUES (> 5 fichiers):")
                for field, count in sorted(critical_fields, key=lambda x: x[1], reverse=True):
                    print(f"    - {field:25} ({count} fichiers)")

            print(f"\n💡 Ces champs sont utilisés dans les templates Jinja2 et playbooks pour:")
            print(f"   - Génération de configurations réseau (Juniper, Cisco)")
            print(f"   - Routage (BGP, OSPF)")
            print(f"   - Services (SNMP, DNS)")
            print(f"   - Interfaces et VLANs")

        return {
            "type": "custom_fields",
            "total_netbox": total_custom_fields,
            "infrahub_custom_fields": infrahub_custom_fields,
            "total_infrahub": len(infrahub_custom_fields),
            "missing_fields": [{"category": cat, "field": field} for cat, field in missing_fields],
            "categorized": {cat: fields for cat, fields in categorized.items()},
            "critical_fields": dict(critical_fields) if critical_fields else {}
        }

    def audit_summary(self):
        """Résumé de l'audit avec tous les devices"""
        print("\n📋 RÉSUMÉ DES DEVICES")
        print("="*80)

        devices = self.get_devices()

        print(f"Nom | IP | Status | Role | Platform | Interfaces")
        print("-" * 100)

        for device in sorted(devices, key=lambda d: d["name"]["value"]):
            name = device["name"]["value"]
            ip = device.get("mgmt_ip", {}).get("value", "N/A") if device.get("mgmt_ip") else "N/A"
            status = device.get("status", {}).get("value", "N/A") if device.get("status") else "N/A"

            role_node = device.get("role", {})
            role = role_node.get("node", {}).get("name", {}).get("value", "N/A") if role_node and role_node.get("node") else "N/A"

            platform_node = device.get("platform", {})
            platform = platform_node.get("node", {}).get("name", {}).get("value", "N/A") if platform_node and platform_node.get("node") else "N/A"

            interfaces = device.get("interfaces_count", {}).get("value", 0) if device.get("interfaces_count") else 0

            print(f"{name[:40]:40} | {ip:15} | {status:8} | {role:12} | {platform:8} | {interfaces:2}")

        return {"type": "summary", "devices": devices}

    def run_full_audit(self):
        """Exécute l'audit complet"""
        print("\n" + "="*80)
        print("  AUDIT COMPLET INFRAHUB")
        print("="*80)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        results = {}

        # Devices
        results["devices"] = self.audit_devices()

        # Rôles
        results["roles"] = self.audit_roles()

        # Plateformes
        results["platforms"] = self.audit_platforms()

        # Custom fields (NetBox → Infrahub)
        results["custom_fields"] = self.audit_custom_fields()

        # Résumé
        results["summary"] = self.audit_summary()

        return results


def save_report(data, output_path):
    """Sauvegarde le rapport en JSON"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Rapport sauvegardé: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Audit Infrahub - Script unifié",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s                    # Audit complet
  %(prog)s --devices          # Audit devices uniquement
  %(prog)s --roles            # Audit rôles uniquement
  %(prog)s --platforms        # Audit plateformes uniquement
  %(prog)s --custom-fields    # Audit custom fields NetBox
  %(prog)s --summary          # Résumé des devices
  %(prog)s -o rapport.json    # Sauvegarder en JSON
        """
    )

    parser.add_argument(
        "--devices", action="store_true",
        help="Audit des devices uniquement"
    )
    parser.add_argument(
        "--roles", action="store_true",
        help="Audit des rôles uniquement"
    )
    parser.add_argument(
        "--platforms", action="store_true",
        help="Audit des plateformes uniquement"
    )
    parser.add_argument(
        "--custom-fields", action="store_true",
        help="Audit des custom fields NetBox manquants"
    )
    parser.add_argument(
        "--summary", action="store_true",
        help="Afficher le résumé des devices"
    )
    parser.add_argument(
        "-o", "--output", type=Path,
        help="Fichier de sortie JSON"
    )

    args = parser.parse_args()

    # Créer l'auditeur
    auditor = InfrahubAuditor()

    # Déterminer quels audits exécuter
    if not any([args.devices, args.roles, args.platforms, args.custom_fields, args.summary]):
        # Audit complet par défaut
        results = auditor.run_full_audit()
    else:
        results = {}
        if args.devices:
            results["devices"] = auditor.audit_devices()
        if args.roles:
            results["roles"] = auditor.audit_roles()
        if args.platforms:
            results["platforms"] = auditor.audit_platforms()
        if args.custom_fields:
            results["custom_fields"] = auditor.audit_custom_fields()
        if args.summary:
            results["summary"] = auditor.audit_summary()

    # Sauvegarder si demandé
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = REPORTS_DIR / f"audit_{timestamp}.json"

    results["timestamp"] = datetime.now().isoformat()
    save_report(results, output_path)

    print("\n" + "="*80)
    print("✅ Audit terminé!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
