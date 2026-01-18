#!/usr/bin/env python3
"""
Script pour extraire tous les custom_fields utilisés dans les templates Jinja2
"""
import re
from pathlib import Path
from collections import Counter

# Répertoire des templates
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

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

def categorize_custom_fields(fields):
    """Catégorise les custom fields par type"""
    categories = {
        "Interfaces": [],
        "Device": [],
        "Routing": [],
        "Network Services": [],
        "Other": []
    }

    for field in fields:
        if field.startswith("iface_"):
            categories["Interfaces"].append(field)
        elif field in ["dev_lpbk", "domain_name"]:
            categories["Device"].append(field)
        elif field in ["bgp_asn", "ospf_area", "rr1", "rr2"]:
            categories["Routing"].append(field)
        elif field.startswith("snmp_") or field.startswith("dns_"):
            categories["Network Services"].append(field)
        else:
            categories["Other"].append(field)

    return categories

if __name__ == "__main__":
    print("🔍 Extraction des custom_fields des templates NetBox...")
    print("="*80)

    fields = extract_custom_fields_from_templates()

    print(f"\n✅ {len(fields)} custom_fields trouvés\n")

    categories = categorize_custom_fields(fields)

    for category, field_list in categories.items():
        if field_list:
            print(f"\n📁 {category}:")
            for field in field_list:
                print(f"  - {field}")

    print("\n" + "="*80)
    print(f"Total: {len(fields)} custom_fields utilisés dans les templates")
