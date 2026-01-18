#!/usr/bin/env python3
"""
Script d'audit pour vérifier les interfaces dans Infrahub
Identifie les interfaces avec des attributs manquants
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from config import REQUIRED_FIELDS, REPORTS_DIR
from utils import (
    InfrahubClient,
    check_required_fields,
    save_report,
    print_summary,
    extract_value,
    logger
)


def audit_interfaces(output_file: Path = None) -> dict:
    """
    Audit complet des interfaces dans Infrahub

    Args:
        output_file: Chemin du fichier de sortie (optionnel)

    Returns:
        Rapport d'audit
    """
    logger.info("Début de l'audit des interfaces Infrahub")

    # Initialiser le client
    client = InfrahubClient()

    # Récupérer toutes les interfaces
    logger.info("Récupération des interfaces...")
    interfaces = client.get_all_interfaces()
    logger.info(f"{len(interfaces)} interfaces récupérées")

    # Récupérer les devices pour vérifier la cohérence
    logger.info("Récupération des devices...")
    devices = client.get_all_devices()
    device_names = {extract_value(d, "name.value") for d in devices}

    # Analyser chaque interface
    issues = []
    complete_count = 0
    incomplete_count = 0
    critical_count = 0
    orphan_interfaces = []
    interfaces_per_device = defaultdict(int)

    for interface in interfaces:
        result = check_required_fields(
            interface,
            "InfraInterface",
            REQUIRED_FIELDS["InfraInterface"]
        )

        # Vérifier si le device parent existe
        device_name = extract_value(interface, "device.node.name.value")
        if device_name:
            interfaces_per_device[device_name] += 1
            if device_name not in device_names:
                orphan_interfaces.append({
                    "interface": extract_value(interface, "name.value"),
                    "device": device_name
                })

        if result["severity"] == "ok":
            complete_count += 1
        else:
            incomplete_count += 1
            issues.append(result)
            if result["severity"] == "critical":
                critical_count += 1

    # Identifier les devices sans interfaces
    devices_without_interfaces = []
    for device in devices:
        device_name = extract_value(device, "name.value")
        if device_name not in interfaces_per_device:
            devices_without_interfaces.append(device_name)

    # Construire le rapport
    report = {
        "timestamp": datetime.now().isoformat(),
        "audit_type": "interfaces",
        "summary": {
            "total_interfaces": len(interfaces),
            "complete": complete_count,
            "incomplete": incomplete_count,
            "missing_critical": critical_count,
            "orphan_interfaces": len(orphan_interfaces),
            "devices_without_interfaces": len(devices_without_interfaces),
            "avg_interfaces_per_device": round(len(interfaces) / len(devices), 2) if devices else 0
        },
        "issues": issues,
        "orphan_interfaces": orphan_interfaces,
        "devices_without_interfaces": devices_without_interfaces
    }

    # Sauvegarder si un fichier de sortie est spécifié
    if output_file:
        save_report(report, output_file)

    return report


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="Audit des interfaces Infrahub"
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
        args.output = REPORTS_DIR / f"audit_interfaces_{timestamp}.json"

    try:
        # Exécuter l'audit
        report = audit_interfaces(args.output)

        # Afficher le résumé
        print_summary(report)

        # Afficher les interfaces orphelines
        if report["orphan_interfaces"]:
            print(f"\n⚠️  {len(report['orphan_interfaces'])} INTERFACES ORPHELINES:")
            for orphan in report["orphan_interfaces"][:10]:  # Limiter à 10
                print(f"  - {orphan['interface']} -> device '{orphan['device']}' inexistant")
            if len(report["orphan_interfaces"]) > 10:
                print(f"  ... et {len(report['orphan_interfaces']) - 10} autres")
            print()

        # Afficher les devices sans interfaces
        if report["devices_without_interfaces"]:
            print(f"\n📊 {len(report['devices_without_interfaces'])} DEVICES SANS INTERFACES:")
            for device in report["devices_without_interfaces"][:10]:  # Limiter à 10
                print(f"  - {device}")
            if len(report["devices_without_interfaces"]) > 10:
                print(f"  ... et {len(report['devices_without_interfaces']) - 10} autres")
            print()

        # Code de sortie selon le résultat
        critical_issues = [i for i in report["issues"] if i["severity"] == "critical"]
        if critical_issues or report["orphan_interfaces"]:
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        logger.error(f"Erreur lors de l'audit: {e}", exc_info=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
