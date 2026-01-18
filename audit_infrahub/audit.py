#!/usr/bin/env python3
"""
Script d'audit unifié pour Infrahub
Analyse les devices, interfaces, sites et plateformes
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import requests

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
        """Récupère tous les devices"""
        query = """
        {
          JeylanDevice {
            edges {
              node {
                id
                name { value }
                mgmt_ip { value }
                status { value }
                os_version { value }
                dns_suffix { value }
                interfaces_count { value }
                warranty_expiration { value }
                role { node { id name { value } } }
                type { node { id name { value } } }
                platform { node { id name { value } } }
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
        """Audit des devices"""
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
            "sans_interfaces": 0,
            "status_inactive": 0
        }

        for device in devices:
            name = device["name"]["value"]
            ip = device.get("mgmt_ip", {}).get("value")
            role = device.get("role", {}).get("node")
            platform = device.get("platform", {}).get("node")
            status = device.get("status", {}).get("value")
            interfaces_count = device.get("interfaces_count", {}).get("value", 0)

            device_issues = []

            if not ip:
                stats["sans_ip"] += 1
                device_issues.append("Pas d'IP de management")

            if not role:
                stats["sans_role"] += 1
                device_issues.append("Pas de rôle défini")

            if not platform:
                stats["sans_platform"] += 1
                device_issues.append("Pas de plateforme définie")

            if interfaces_count == 0:
                stats["sans_interfaces"] += 1
                device_issues.append("Aucune interface")

            if status != "active":
                stats["status_inactive"] += 1
                device_issues.append(f"Status: {status}")

            if device_issues:
                issues.append({
                    "device": name,
                    "issues": device_issues
                })

        # Affichage résumé
        print(f"\n📊 Statistiques:")
        print(f"  Total: {stats['total']}")
        print(f"  Sans IP management: {stats['sans_ip']}")
        print(f"  Sans rôle: {stats['sans_role']}")
        print(f"  Sans plateforme: {stats['sans_platform']}")
        print(f"  Sans interfaces: {stats['sans_interfaces']}")
        print(f"  Status non-actif: {stats['status_inactive']}")

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
    if not any([args.devices, args.roles, args.platforms, args.summary]):
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
