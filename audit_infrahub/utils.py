"""
Fonctions utilitaires pour les scripts d'audit Infrahub
"""
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import requests
from pathlib import Path

from config import (
    GRAPHQL_ENDPOINT,
    INFRAHUB_API_TOKEN,
    INFRAHUB_VERIFY_SSL,
    API_TIMEOUT,
    LOG_FORMAT,
    LOG_LEVEL
)

# Configuration du logging
logging.basicConfig(format=LOG_FORMAT, level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)


class InfrahubClient:
    """Client pour interagir avec l'API GraphQL d'Infrahub"""

    def __init__(self):
        self.endpoint = GRAPHQL_ENDPOINT
        self.headers = {
            "Content-Type": "application/json",
        }
        if INFRAHUB_API_TOKEN:
            self.headers["X-INFRAHUB-KEY"] = INFRAHUB_API_TOKEN
        self.verify_ssl = INFRAHUB_VERIFY_SSL
        self.timeout = API_TIMEOUT

    def execute_query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """
        Exécute une requête GraphQL

        Args:
            query: Requête GraphQL
            variables: Variables pour la requête

        Returns:
            Réponse JSON de l'API
        """
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=self.headers,
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            if "errors" in data:
                logger.error(f"GraphQL errors: {data['errors']}")
                return {"data": None, "errors": data["errors"]}

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {"data": None, "errors": [str(e)]}

    def get_all_devices(self) -> List[Dict]:
        """Récupère tous les devices depuis Infrahub"""
        query = """
        query GetAllDevices {
          JeylanDevice {
            edges {
              node {
                id
                name {
                  value
                }
                primary_address {
                  node {
                    address {
                      value
                    }
                  }
                }
                site {
                  node {
                    name {
                      value
                    }
                  }
                }
                role {
                  value
                }
                type {
                  value
                }
                platform {
                  node {
                    name {
                      value
                    }
                    ansible_network_os {
                      value
                    }
                  }
                }
                interfaces {
                  count
                }
                description {
                  value
                }
              }
            }
          }
        }
        """

        result = self.execute_query(query)
        if result.get("data") and result["data"].get("JeylanDevice"):
            return [edge["node"] for edge in result["data"]["JeylanDevice"]["edges"]]
        query = """
        query GetAllInterfaces {
          JeylanInterface {
            edges {
              node {
                id
                name {
                  value
                }
                device {
                  node {
                    name {
                      value
                    }
                  }
                }
                status {
                  value
                }
                enabled {
                  value
                }
                description {
                  value
                }
              }
            }
          }
        }
        """

        result = self.execute_query(query)
        if result.get("data") and result["data"].get("JeylanInterface"):
            return [edge["node"] for edge in result["data"]["JeylanInterface"]["edges"]]
        return []

    def get_all_sites(self) -> List[Dict]:
        """Récupère tous les sites depuis Infrahub"""
        query = """
        query GetAllSites {
          JeylanSite {
            edges {
              node {
                id
                name {
                  value
                }
                location {
                  value
                }
                description {
                  value
                }
              }
            }
          }
        }
        """

        result = self.execute_query(query)
        if result.get("data") and result["data"].get("JeylanSite"):
            return [edge["node"] for edge in result["data"]["JeylanSite"]["edges"]]
        return []

    def get_all_platforms(self) -> List[Dict]:
        """Récupère toutes les plateformes depuis Infrahub"""
        query = """
        query GetAllPlatforms {
          JeylanPlatform {
            edges {
              node {
                id
                name {
                  value
                }
                ansible_network_os {
                  value
                }
                manufacturer {
                  value
                }
                description {
                  value
                }
              }
            }
          }
        }
        """

        result = self.execute_query(query)
        if result.get("data") and result["data"].get("JeylanPlatform"):
            return [edge["node"] for edge in result["data"]["JeylanPlatform"]["edges"]]
        return []


def extract_value(obj: Dict, path: str) -> Optional[Any]:
    """
    Extrait une valeur d'un objet Infrahub en suivant un chemin

    Args:
        obj: Objet Infrahub
        path: Chemin vers la valeur (ex: "site.node.name.value")

    Returns:
        Valeur extraite ou None
    """
    keys = path.split(".")
    current = obj

    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None

    return current


def check_required_fields(obj: Dict, object_type: str, required_fields: Dict[str, List[str]]) -> Dict:
    """
    Vérifie les champs requis d'un objet

    Args:
        obj: Objet à vérifier
        object_type: Type d'objet (InfraDevice, JeylanInterface, etc.)
        required_fields: Dictionnaire des champs requis par criticité

    Returns:
        Dictionnaire avec les résultats de la vérification
    """
    result = {
        "object_type": object_type,
        "object_id": obj.get("id"),
        "object_name": extract_value(obj, "name.value"),
        "issues": [],
        "severity": "ok"
    }

    missing_critical = []
    missing_important = []
    missing_optional = []

    # Vérifier les champs critiques
    for field in required_fields.get("critical", []):
        value = extract_value(obj, f"{field}.value") or extract_value(obj, f"{field}.node")
        if not value:
            missing_critical.append(field)

    # Vérifier les champs importants
    for field in required_fields.get("important", []):
        value = extract_value(obj, f"{field}.value") or extract_value(obj, f"{field}.node")
        if not value:
            missing_important.append(field)

    # Vérifier les champs optionnels
    for field in required_fields.get("optional", []):
        value = extract_value(obj, f"{field}.value") or extract_value(obj, f"{field}.node")
        if not value:
            missing_optional.append(field)

    # Déterminer la sévérité
    if missing_critical:
        result["severity"] = "critical"
        result["issues"].append({
            "type": "missing_critical_fields",
            "fields": missing_critical,
            "message": f"Champs critiques manquants: {', '.join(missing_critical)}"
        })

    if missing_important:
        if result["severity"] == "ok":
            result["severity"] = "warning"
        result["issues"].append({
            "type": "missing_important_fields",
            "fields": missing_important,
            "message": f"Champs importants manquants: {', '.join(missing_important)}"
        })

    if missing_optional:
        result["issues"].append({
            "type": "missing_optional_fields",
            "fields": missing_optional,
            "message": f"Champs optionnels manquants: {', '.join(missing_optional)}"
        })

    return result


def save_report(report: Dict, output_path: Path):
    """
    Sauvegarde un rapport au format JSON

    Args:
        report: Dictionnaire du rapport
        output_path: Chemin du fichier de sortie
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        logger.info(f"Rapport sauvegardé: {output_path}")
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du rapport: {e}")


def print_summary(report: Dict):
    """
    Affiche un résumé du rapport dans la console

    Args:
        report: Dictionnaire du rapport
    """
    print("\n" + "="*80)
    print(f"RAPPORT D'AUDIT - {report.get('audit_type', '').upper()}")
    print("="*80)
    print(f"Timestamp: {report.get('timestamp')}")
    print(f"\nRésumé:")

    summary = report.get('summary', {})
    for key, value in summary.items():
        print(f"  {key}: {value}")

    print(f"\nProblèmes détectés: {len(report.get('issues', []))}")

    # Compter par sévérité
    severity_counts = {}
    for issue in report.get('issues', []):
        severity = issue.get('severity', 'unknown')
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    if severity_counts:
        print(f"\nPar sévérité:")
        for severity, count in sorted(severity_counts.items()):
            print(f"  {severity}: {count}")

    print("="*80 + "\n")
