"""
Configuration centralisée pour les scripts d'audit Infrahub
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env si présent
load_dotenv()

# Configuration API Infrahub
INFRAHUB_API_URL = os.getenv("INFRAHUB_API_URL", "http://jeysrv10:8080")
INFRAHUB_API_TOKEN = os.getenv("INFRAHUB_API_TOKEN", "")
INFRAHUB_VERIFY_SSL = os.getenv("INFRAHUB_VERIFY_SSL", "false").lower() == "true"

# Configuration GraphQL
GRAPHQL_ENDPOINT = f"{INFRAHUB_API_URL}/graphql"

# Répertoires
BASE_DIR = Path(__file__).parent
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# Champs requis par type d'objet
REQUIRED_FIELDS = {
    "InfraDevice": {
        "critical": ["name", "primary_address"],
        "important": ["site", "platform", "role"],
        "optional": ["type", "interfaces", "description"]
    },
    "InfraInterface": {
        "critical": ["name", "device"],
        "important": ["status", "enabled"],
        "optional": ["ip_addresses", "description", "mtu"]
    },
    "InfraSite": {
        "critical": ["name"],
        "important": ["location"],
        "optional": ["description", "devices"]
    },
    "InfraPlatform": {
        "critical": ["name", "ansible_network_os"],
        "important": ["manufacturer"],
        "optional": ["description"]
    }
}

# Correspondances attendues pour ansible_network_os
EXPECTED_NETWORK_OS = {
    "cisco_ios": ["cisco", "ios", "catalyst"],
    "cisco_iosxe": ["cisco", "iosxe", "isr4"],
    "cisco_iosxr": ["cisco", "iosxr", "asr9k"],
    "cisco_nxos": ["cisco", "nxos", "nexus"],
    "juniper_junos": ["juniper", "junos", "mx", "ex", "qfx"],
    "arista_eos": ["arista", "eos"],
    "paloalto_panos": ["paloalto", "panos"],
    "fortinet_fortios": ["fortinet", "fortigate"]
}

# Timeout pour les requêtes API (secondes)
API_TIMEOUT = 30

# Options de logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
