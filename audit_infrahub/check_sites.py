#!/usr/bin/env python3
"""
Script d'audit pour vérifier les sites dans Infrahub
Identifie les sites incomplets et vérifie la cohérence avec les devices
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


def audit_sites(output_file: Path = None) -> dict:
    """
    Audit complet des sites dans Infrahub

    Args:
        output_file: Chemin du fichier de sortie (optionnel)

    Returns:
        Rapport d'audit
    """
    logger.info("Début de l'audit des sites Infrahub")

    # Initialiser le client
    client = InfrahubClient()

    # Récupérer tous les sites
    logger.info("Récupération des sites...")
    sites = client.get_all_sites()
    logger.info(f"{len(sites)} sites récupérés")

    # Récupérer les devices pour vérifier la cohérence
    logger.info("Récupération des devices...")
    devices = client.get_all_devices()

    # Compter les devices par site
    devices_per_site = defaultdict(int)
    devices_without_site = []

    for device in devices:
        site_name = extract_value(device, "site.node.name.value")
        if site_name:
            devices_per_site[site_name] += 1
        else:
            devices_without_site.append(extract_value(device, "name.value"))

    # Identifier les sites référencés mais non définis
    site_names = {extract_value(s, "name.value") for s in sites}
    undefined_sites = set(devices_per_site.keys()) - site_names

    # Analyser chaque site
    issues = []
    complete_count = 0
    incomplete_count = 0
    critical_count = 0
    sites_without_devices = []

    for site in sites:
        result = check_required_fields(
            site,
            "InfraSite",
            REQUIRED_FIELDS["InfraSite"]
        )

        site_name = extract_value(site, "name.value")
        device_count = devices_per_site.get(site_name, 0)

        # Ajouter info sur les devices du site
        result["device_count"] = device_count

        if device_count == 0:
            sites_without_devices.append(site_name)
            result["issues"].append({
                "type": "no_devices",
                "message": f"Aucun device assigné au site '{site_name}'"
            })
            if result["severity"] == "ok":
                result["severity"] = "warning"

        if result["severity"] == "ok":
            complete_count += 1
        else:
            incomplete_count += 1
            issues.append(result)
            if result["severity"] == "critical":
                critical_count += 1

    # Construire le rapport
    report = {
        "timestamp": datetime.now().isoformat(),
        "audit_type": "sites",
        "summary": {
            "total_sites": len(sites),
            "complete": complete_count,
            "incomplete": incomplete_count,
            "missing_critical": critical_count,
            "sites_without_devices": len(sites_without_devices),
            "devices_without_site": len(devices_without_site),
            "undefined_sites_referenced": len(undefined_sites),
            "total_devices": len(devices)
        },
        "issues": issues,
        "sites_without_devices": sites_without_devices,
        "devices_without_site": devices_without_site,
        "undefined_sites": list(undefined_sites),
        "devices_per_site": dict(devices_per_site)
    }

    # Sauvegarder si un fichier de sortie est spécifié
    if output_file:
        save_report(report, output_file)

    return report


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="Audit des sites Infrahub"
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
        args.output = REPORTS_DIR / f"audit_sites_{timestamp}.json"

    try:
        # Exécuter l'audit
        report = audit_sites(args.output)

        # Afficher le résumé
        print_summary(report)

        # Afficher les sites non définis mais référencés
        if report["undefined_sites"]:
            print(f"\n⚠️  {len(report['undefined_sites'])} SITES RÉFÉRENCÉS MAIS NON DÉFINIS:")
            for site in report["undefined_sites"]:
                device_count = report["devices_per_site"].get(site, 0)
                print(f"  - {site} ({device_count} devices)")
            print()

        # Afficher les devices sans site
        if report["devices_without_site"]:
            print(f"\n📍 {len(report['devices_without_site'])} DEVICES SANS SITE:")
            for device in report["devices_without_site"][:10]:  # Limiter à 10
                print(f"  - {device}")
            if len(report["devices_without_site"]) > 10:
                print(f"  ... et {len(report['devices_without_site']) - 10} autres")
            print()

        # Afficher les sites sans devices
        if report["sites_without_devices"]:
            print(f"\n📊 {len(report['sites_without_devices'])} SITES SANS DEVICES:")
            for site in report["sites_without_devices"][:10]:  # Limiter à 10
                print(f"  - {site}")
            if len(report["sites_without_devices"]) > 10:
                print(f"  ... et {len(report['sites_without_devices']) - 10} autres")
            print()

        # Code de sortie selon le résultat
        critical_issues = [i for i in report["issues"] if i["severity"] == "critical"]
        if critical_issues or report["undefined_sites"]:
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        logger.error(f"Erreur lors de l'audit: {e}", exc_info=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
