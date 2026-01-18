#!/usr/bin/env python3
"""
Script d'audit pour vérifier les plateformes dans Infrahub
Vérifie la cohérence des attributs ansible_network_os
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from config import REQUIRED_FIELDS, EXPECTED_NETWORK_OS, REPORTS_DIR
from utils import (
    InfrahubClient,
    check_required_fields,
    save_report,
    print_summary,
    extract_value,
    logger
)


def audit_platforms(output_file: Path = None) -> dict:
    """
    Audit complet des plateformes dans Infrahub

    Args:
        output_file: Chemin du fichier de sortie (optionnel)

    Returns:
        Rapport d'audit
    """
    logger.info("Début de l'audit des plateformes Infrahub")

    # Initialiser le client
    client = InfrahubClient()

    # Récupérer toutes les plateformes
    logger.info("Récupération des plateformes...")
    platforms = client.get_all_platforms()
    logger.info(f"{len(platforms)} plateformes récupérées")

    # Récupérer les devices pour vérifier la cohérence
    logger.info("Récupération des devices...")
    devices = client.get_all_devices()

    # Compter les devices par plateforme
    devices_per_platform = defaultdict(int)
    devices_without_platform = []

    for device in devices:
        platform_name = extract_value(device, "platform.node.name.value")
        if platform_name:
            devices_per_platform[platform_name] += 1
        else:
            devices_without_platform.append(extract_value(device, "name.value"))

    # Identifier les plateformes référencées mais non définies
    platform_names = {extract_value(p, "name.value") for p in platforms}
    undefined_platforms = set(devices_per_platform.keys()) - platform_names

    # Analyser chaque plateforme
    issues = []
    complete_count = 0
    incomplete_count = 0
    critical_count = 0
    platforms_without_devices = []
    invalid_network_os = []

    for platform in platforms:
        result = check_required_fields(
            platform,
            "InfraPlatform",
            REQUIRED_FIELDS["InfraPlatform"]
        )

        platform_name = extract_value(platform, "name.value")
        device_count = devices_per_platform.get(platform_name, 0)
        ansible_os = extract_value(platform, "ansible_network_os.value")

        # Ajouter info sur les devices
        result["device_count"] = device_count

        if device_count == 0:
            platforms_without_devices.append(platform_name)
            result["issues"].append({
                "type": "no_devices",
                "message": f"Aucun device n'utilise la plateforme '{platform_name}'"
            })
            if result["severity"] == "ok":
                result["severity"] = "info"

        # Vérifier la validité de ansible_network_os
        if ansible_os:
            is_valid = False
            for expected_os, keywords in EXPECTED_NETWORK_OS.items():
                if any(keyword.lower() in platform_name.lower() for keyword in keywords):
                    if ansible_os.lower() != expected_os.lower():
                        invalid_network_os.append({
                            "platform": platform_name,
                            "current": ansible_os,
                            "expected": expected_os
                        })
                        result["issues"].append({
                            "type": "invalid_network_os",
                            "message": f"ansible_network_os='{ansible_os}' ne correspond pas au nom de plateforme (attendu: '{expected_os}')"
                        })
                        if result["severity"] == "ok":
                            result["severity"] = "warning"
                    is_valid = True
                    break

            if not is_valid:
                result["issues"].append({
                    "type": "unknown_network_os",
                    "message": f"ansible_network_os='{ansible_os}' non reconnu dans les correspondances attendues"
                })

        if result["severity"] in ["ok", "info"]:
            complete_count += 1
        else:
            incomplete_count += 1
            issues.append(result)
            if result["severity"] == "critical":
                critical_count += 1

    # Construire le rapport
    report = {
        "timestamp": datetime.now().isoformat(),
        "audit_type": "platforms",
        "summary": {
            "total_platforms": len(platforms),
            "complete": complete_count,
            "incomplete": incomplete_count,
            "missing_critical": critical_count,
            "platforms_without_devices": len(platforms_without_devices),
            "devices_without_platform": len(devices_without_platform),
            "undefined_platforms_referenced": len(undefined_platforms),
            "invalid_network_os": len(invalid_network_os),
            "total_devices": len(devices)
        },
        "issues": issues,
        "platforms_without_devices": platforms_without_devices,
        "devices_without_platform": devices_without_platform,
        "undefined_platforms": list(undefined_platforms),
        "invalid_network_os": invalid_network_os,
        "devices_per_platform": dict(devices_per_platform)
    }

    # Sauvegarder si un fichier de sortie est spécifié
    if output_file:
        save_report(report, output_file)

    return report


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="Audit des plateformes Infrahub"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Fichier de sortie pour le rapport JSON"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Mode verbeux"
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel("DEBUG")

    # Définir le fichier de sortie par défaut
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = REPORTS_DIR / f"audit_platforms_{timestamp}.json"

    try:
        # Exécuter l'audit
        report = audit_platforms(args.output)

        # Afficher le résumé
        print_summary(report)

        # Afficher les plateformes non définies mais référencées
        if report["undefined_platforms"]:
            print(f"\n⚠️  {len(report['undefined_platforms'])} PLATEFORMES RÉFÉRENCÉES MAIS NON DÉFINIES:")
            for platform in report["undefined_platforms"]:
                device_count = report["devices_per_platform"].get(platform, 0)
                print(f"  - {platform} ({device_count} devices)")
            print()

        # Afficher les ansible_network_os invalides
        if report["invalid_network_os"]:
            print(f"\n🔧 {len(report['invalid_network_os'])} ANSIBLE_NETWORK_OS INCORRECTS:")
            for item in report["invalid_network_os"]:
                print(f"  - {item['platform']}: '{item['current']}' → devrait être '{item['expected']}'")
            print()

        # Afficher les devices sans plateforme
        if report["devices_without_platform"]:
            print(f"\n📍 {len(report['devices_without_platform'])} DEVICES SANS PLATEFORME:")
            for device in report["devices_without_platform"][:10]:  # Limiter à 10
                print(f"  - {device}")
            if len(report["devices_without_platform"]) > 10:
                print(f"  ... et {len(report['devices_without_platform']) - 10} autres")
            print()

        # Code de sortie selon le résultat
        critical_issues = [i for i in report["issues"] if i["severity"] == "critical"]
        if critical_issues or report["undefined_platforms"]:
            sys.exit(1)
        elif report["devices_without_platform"]:
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        logger.error(f"Erreur lors de l'audit: {e}", exc_info=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
