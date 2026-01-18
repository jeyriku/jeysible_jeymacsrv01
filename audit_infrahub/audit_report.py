#!/usr/bin/env python3
"""
Script de génération de rapport d'audit complet pour Infrahub
Exécute tous les audits et génère un rapport consolidé
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

from config import REPORTS_DIR
from utils import save_report, logger

# Importer les fonctions d'audit
from check_devices import audit_devices
from check_interfaces import audit_interfaces
from check_sites import audit_sites
from check_platforms import audit_platforms


def generate_full_audit(output_file: Path = None) -> dict:
    """
    Génère un rapport d'audit complet

    Args:
        output_file: Chemin du fichier de sortie (optionnel)

    Returns:
        Rapport d'audit complet
    """
    logger.info("Début de l'audit complet Infrahub")

    # Exécuter tous les audits
    logger.info("Audit des devices...")
    devices_report = audit_devices()

    logger.info("Audit des interfaces...")
    interfaces_report = audit_interfaces()

    logger.info("Audit des sites...")
    sites_report = audit_sites()

    logger.info("Audit des plateformes...")
    platforms_report = audit_platforms()

    # Calculer les statistiques globales
    total_issues = (
        len(devices_report["issues"]) +
        len(interfaces_report["issues"]) +
        len(sites_report["issues"]) +
        len(platforms_report["issues"])
    )

    total_critical = sum([
        devices_report["summary"]["missing_critical"],
        interfaces_report["summary"]["missing_critical"],
        sites_report["summary"]["missing_critical"],
        platforms_report["summary"]["missing_critical"]
    ])

    # Construire le rapport consolidé
    report = {
        "timestamp": datetime.now().isoformat(),
        "audit_type": "full_audit",
        "summary": {
            "total_objects_audited": (
                devices_report["summary"]["total_devices"] +
                interfaces_report["summary"]["total_interfaces"] +
                sites_report["summary"]["total_sites"] +
                platforms_report["summary"]["total_platforms"]
            ),
            "total_issues": total_issues,
            "total_critical": total_critical,
            "devices": devices_report["summary"],
            "interfaces": interfaces_report["summary"],
            "sites": sites_report["summary"],
            "platforms": platforms_report["summary"]
        },
        "devices": {
            "summary": devices_report["summary"],
            "critical_issues": [i for i in devices_report["issues"] if i["severity"] == "critical"]
        },
        "interfaces": {
            "summary": interfaces_report["summary"],
            "critical_issues": [i for i in interfaces_report["issues"] if i["severity"] == "critical"],
            "orphan_interfaces": interfaces_report["orphan_interfaces"],
            "devices_without_interfaces": interfaces_report["devices_without_interfaces"]
        },
        "sites": {
            "summary": sites_report["summary"],
            "critical_issues": [i for i in sites_report["issues"] if i["severity"] == "critical"],
            "undefined_sites": sites_report["undefined_sites"],
            "devices_without_site": sites_report["devices_without_site"]
        },
        "platforms": {
            "summary": platforms_report["summary"],
            "critical_issues": [i for i in platforms_report["issues"] if i["severity"] == "critical"],
            "undefined_platforms": platforms_report["undefined_platforms"],
            "invalid_network_os": platforms_report["invalid_network_os"],
            "devices_without_platform": platforms_report["devices_without_platform"]
        }
    }

    # Sauvegarder si un fichier de sortie est spécifié
    if output_file:
        save_report(report, output_file)

        # Générer aussi des rapports individuels
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_report(devices_report, REPORTS_DIR / f"audit_devices_{timestamp}.json")
        save_report(interfaces_report, REPORTS_DIR / f"audit_interfaces_{timestamp}.json")
        save_report(sites_report, REPORTS_DIR / f"audit_sites_{timestamp}.json")
        save_report(platforms_report, REPORTS_DIR / f"audit_platforms_{timestamp}.json")

    return report


def print_full_summary(report: dict):
    """
    Affiche un résumé détaillé du rapport complet

    Args:
        report: Rapport d'audit complet
    """
    print("\n" + "="*80)
    print("RAPPORT D'AUDIT COMPLET INFRAHUB")
    print("="*80)
    print(f"Timestamp: {report['timestamp']}")
    print(f"\nRésumé Global:")
    print(f"  Objets audités: {report['summary']['total_objects_audited']}")
    print(f"  Problèmes détectés: {report['summary']['total_issues']}")
    print(f"  Problèmes critiques: {report['summary']['total_critical']}")

    # Devices
    print(f"\n📱 DEVICES:")
    print(f"  Total: {report['summary']['devices']['total_devices']}")
    print(f"  Complets: {report['summary']['devices']['complete']}")
    print(f"  Incomplets: {report['summary']['devices']['incomplete']}")
    print(f"  Critiques: {report['summary']['devices']['missing_critical']}")

    # Interfaces
    print(f"\n🔌 INTERFACES:")
    print(f"  Total: {report['summary']['interfaces']['total_interfaces']}")
    print(f"  Complètes: {report['summary']['interfaces']['complete']}")
    print(f"  Incomplètes: {report['summary']['interfaces']['incomplete']}")
    print(f"  Critiques: {report['summary']['interfaces']['missing_critical']}")
    print(f"  Orphelines: {report['summary']['interfaces']['orphan_interfaces']}")
    print(f"  Devices sans interfaces: {report['summary']['interfaces']['devices_without_interfaces']}")

    # Sites
    print(f"\n📍 SITES:")
    print(f"  Total: {report['summary']['sites']['total_sites']}")
    print(f"  Complets: {report['summary']['sites']['complete']}")
    print(f"  Incomplets: {report['summary']['sites']['incomplete']}")
    print(f"  Critiques: {report['summary']['sites']['missing_critical']}")
    print(f"  Sites non définis: {report['summary']['sites']['undefined_sites_referenced']}")
    print(f"  Devices sans site: {report['summary']['sites']['devices_without_site']}")

    # Plateformes
    print(f"\n🔧 PLATEFORMES:")
    print(f"  Total: {report['summary']['platforms']['total_platforms']}")
    print(f"  Complètes: {report['summary']['platforms']['complete']}")
    print(f"  Incomplètes: {report['summary']['platforms']['incomplete']}")
    print(f"  Critiques: {report['summary']['platforms']['missing_critical']}")
    print(f"  Plateformes non définies: {report['summary']['platforms']['undefined_platforms_referenced']}")
    print(f"  ansible_network_os invalides: {report['summary']['platforms']['invalid_network_os']}")
    print(f"  Devices sans plateforme: {report['summary']['platforms']['devices_without_platform']}")

    print("\n" + "="*80)

    # Afficher les problèmes prioritaires
    priority_issues = []

    if report['devices']['critical_issues']:
        priority_issues.append(f"⚠️  Devices avec problèmes critiques: {len(report['devices']['critical_issues'])}")

    if report['interfaces']['orphan_interfaces']:
        priority_issues.append(f"⚠️  Interfaces orphelines: {len(report['interfaces']['orphan_interfaces'])}")

    if report['sites']['undefined_sites']:
        priority_issues.append(f"⚠️  Sites référencés mais non définis: {len(report['sites']['undefined_sites'])}")

    if report['platforms']['undefined_platforms']:
        priority_issues.append(f"⚠️  Plateformes référencées mais non définies: {len(report['platforms']['undefined_platforms'])}")

    if report['platforms']['devices_without_platform']:
        priority_issues.append(f"⚠️  Devices sans plateforme: {len(report['platforms']['devices_without_platform'])}")

    if priority_issues:
        print("\nPROBLÈMES PRIORITAIRES:")
        for issue in priority_issues:
            print(f"  {issue}")
        print()


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="Génération de rapport d'audit complet Infrahub"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Fichier de sortie pour le rapport JSON consolidé"
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
        args.output = REPORTS_DIR / f"audit_full_{timestamp}.json"

    try:
        # Générer l'audit complet
        report = generate_full_audit(args.output)

        # Afficher le résumé
        print_full_summary(report)

        print(f"✅ Rapports sauvegardés dans: {REPORTS_DIR}/")
        print(f"   - Rapport complet: {args.output.name}")
        print()

        # Code de sortie selon le résultat
        if report["summary"]["total_critical"] > 0:
            sys.exit(1)
        elif report["summary"]["total_issues"] > 0:
            sys.exit(1)
        else:
            print("✅ Aucun problème critique détecté!")
            sys.exit(0)

    except Exception as e:
        logger.error(f"Erreur lors de la génération du rapport: {e}", exc_info=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
