#!/usr/bin/env python3
"""
Script pour extraire tous les custom_fields utilisés dans les templates Jinja2 et playbooks
"""
import re
from pathlib import Path
from collections import Counter, defaultdict

# Répertoires
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
PLAYBOOKS_DIR = Path(__file__).parent.parent / "playbooks"

def extract_custom_fields_from_templates():
    """Extrait tous les custom_fields des templates"""
    custom_fields = set()
    pattern = re.compile(r'custom_fields\.([a-zA-Z_][a-zA-Z0-9_]*)')

    # Parcourir tous les fichiers .j2
    for template_file in TEMPLATES_DIR.rglob("*.j2"):
        try:
            content = template_file.read_text()
            matches = pattern.findall(content)
            custom_fields.update(matches)
        except Exception as e:
            print(f"⚠️  Erreur lecture {template_file}: {e}")

    return sorted(custom_fields)

def extract_custom_fields_from_playbooks():
    """Extrait tous les custom_fields des playbooks YAML"""
    custom_fields = defaultdict(list)

    # Patterns pour trouver les custom_fields
    patterns = [
        re.compile(r'custom_fields\.([a-zA-Z_][a-zA-Z0-9_]*)\.value'),
        re.compile(r'custom_fields\.([a-zA-Z_][a-zA-Z0-9_]*)'),
        re.compile(r"'custom_fields\.([a-zA-Z_][a-zA-Z0-9_]*)'"),
        re.compile(r'"custom_fields\.([a-zA-Z_][a-zA-Z0-9_]*)"'),
    ]

    # Parcourir tous les playbooks
    for playbook_file in PLAYBOOKS_DIR.rglob("*.yml"):
        try:
            content = playbook_file.read_text()
            for pattern in patterns:
                matches = pattern.findall(content)
                if matches:
                    for match in matches:
                        custom_fields[match].append(str(playbook_file.relative_to(PLAYBOOKS_DIR.parent)))
        except Exception as e:
            print(f"⚠️  Erreur lecture {playbook_file}: {e}")

    return custom_fields

def categorize_custom_fields(fields):
    """Catégorise les custom fields par type"""
    categories = {
        "SNMP": [],
        "DNS": [],
        "Interfaces": [],
        "Device": [],
        "Routing": [],
        "Network Services": [],
        "Other": []
    }

    for field in fields:
        if field.startswith("snmp_"):
            categories["SNMP"].append(field)
        elif field.startswith("dns_"):
            categories["DNS"].append(field)
        elif field.startswith("iface_"):
            categories["Interfaces"].append(field)
        elif field in ["dev_lpbk", "domain_name"]:
            categories["Device"].append(field)
        elif field in ["bgp_asn", "ospf_area", "rr1", "rr2"]:
            categories["Routing"].append(field)
        else:
            categories["Other"].append(field)

    return categories

if __name__ == "__main__":
    print("🔍 Extraction des custom_fields des templates et playbooks NetBox...")
    print("="*80)

    # Extraction des templates
    print("\n📄 Analyse des templates Jinja2...")
    template_fields = extract_custom_fields_from_templates()
    print(f"  ✅ {len(template_fields)} custom_fields trouvés dans les templates")

    # Extraction des playbooks
    print("\n📋 Analyse des playbooks YAML...")
    playbook_fields = extract_custom_fields_from_playbooks()
    print(f"  ✅ {len(playbook_fields)} custom_fields trouvés dans les playbooks")

    # Fusion des résultats
    all_fields = set(template_fields) | set(playbook_fields.keys())

    print(f"\n📊 TOTAL: {len(all_fields)} custom_fields uniques\n")
    print("="*80)

    # Catégorisation
    categories = categorize_custom_fields(sorted(all_fields))

    for category, field_list in categories.items():
        if field_list:
            print(f"\n📁 {category}:")
            for field in field_list:
                print(f"  - {field}", end="")
                # Afficher dans quels fichiers le champ est utilisé
                if field in playbook_fields and len(playbook_fields[field]) <= 3:
                    print(f" (utilisé dans {len(playbook_fields[field])} playbook(s))")
                elif field in playbook_fields:
                    print(f" (utilisé dans {len(playbook_fields[field])} playbooks)")
                else:
                    print(" (template uniquement)")

    # Résumé détaillé pour les champs critiques (SNMP)
    if categories["SNMP"]:
        print("\n" + "="*80)
        print("📌 DÉTAILS DES CHAMPS SNMP (les plus utilisés dans les playbooks):")
        print("="*80)
        for field in sorted(categories["SNMP"]):
            if field in playbook_fields:
                print(f"\n🔹 {field}:")
                print(f"  Utilisé dans {len(playbook_fields[field])} fichier(s):")
                for file_path in playbook_fields[field][:5]:  # Limiter à 5 exemples
                    print(f"    • {file_path}")
                if len(playbook_fields[field]) > 5:
                    print(f"    ... et {len(playbook_fields[field]) - 5} autre(s)")

    print("\n" + "="*80)
    print(f"💡 Ces {len(all_fields)} custom_fields doivent être recréés dans Infrahub")
    print("   sous forme de profils ou d'attributs sur les objets correspondants.")
    print("="*80)
