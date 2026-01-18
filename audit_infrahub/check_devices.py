#!/usr/bin/env python3
"""
Script d'audit pour vérifier les devices dans Infrahub
Identifie les devices avec des attributs manquants ou incomplets
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

from config import REQUIRED_FIELDS, REPORTS_DIR
from utils import (
    InfrahubClient,
    check_required_fields,
    save_report,
    print_summary,
    logger
)


def audit_devices(output_file: Path = None) -> dict:
    """
    Audit complet des devices dans Infrahub

    Args:
        output_file: Chemin du fichier de sortie (optionnel)

    Returns:
        Rapport d'audit
    """
    logger.info("Début de l'audit des devices Infrahub")

    # Initialiser le client
    client = InfrahubClient()

    # Récupérer tous les devices
    logger.info("Récupération des devices...")
    devices = client.get_all_devices()
    logger.info(f"{len(devices)} devices récupérés")

    # Analyser chaque device
    issues = []
    complete_count = 0
    incomplete_count = 0
    critical_count = 0

    for device in devices:
        result = check_required_fields(
            device,
            "InfraDevice",
            REQUIRED_FIELDS["InfraDevice"]
        )

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
        "audit_type": "devices",
        "summary": {
            "total_devices": len(devices),
            "complete": complete_count,
            "incomplete": incomplete_count,
            "missing_critical": critical_count
        },
        "issues": issues
    }

    # Sauvegarder si un fichier de sortie est spécifié
    if output_file:
        save_report(report, output_file)

    return report


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="Audit des devices Infrahub"
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
        args.output = REPORTS_DIR / f"audit_devices_{timestamp}.json"

    try:
        # Exécuter l'audit
        report = audit_devices(args.output)

        # Afficher le résumé
        print_summary(report)

        # Afficher les problèmes critiques
        critical_issues = [i for i in report["issues"] if i["severity"] == "critical"]
        if critical_issues:
            print(f"\n⚠️  {len(critical_issues)} PROBLÈMES CRITIQUES DÉTECTÉS:\n")
            for issue in critical_issues:
                print(f"  Device: {issue['object_name']}")
                for problem in issue["issues"]:
                    if problem["type"] == "missing_critical_fields":
                        print(f"    - {problem['message']}")
                print()

        # Code de sortie selon le résultat
        if critical_issues:
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        logger.error(f"Erreur lors de l'audit: {e}", exc_info=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
