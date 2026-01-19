# Custom Fields ajoutés au schéma Infrahub
Date: 2026-01-19
Schéma: ipam_schema.yml (version 1.0)

## Résumé
- **20 custom_fields** NetBox ajoutés à Infrahub
- **3 entités** modifiées : JeylanDevice, JeylanInterfaces, JeylanRouting
- **Type**: Text (tous optionnels)

---

## 1. JeylanDevice - SNMP Configuration (6 champs)

### snmp_community
- **Type**: Text
- **Description**: SNMP community string
- **Utilisation**: 10 fichiers (playbooks SNMP Cisco/Junos)
- **Exemple**: `public` ou `private`

### snmp_location
- **Type**: Text
- **Description**: SNMP location string
- **Utilisation**: 10 fichiers
- **Exemple**: `Datacenter A - Rack 42`

### snmp_server
- **Type**: Text
- **Description**: SNMP server address
- **Utilisation**: 5 fichiers
- **Exemple**: `192.168.0.10`

### snmp_server1
- **Type**: Text
- **Description**: Primary SNMP server
- **Utilisation**: 5 fichiers
- **Exemple**: `192.168.0.10`

### snmp_server2
- **Type**: Text
- **Description**: Secondary SNMP server
- **Utilisation**: 13 fichiers ⚠️ CRITIQUE (le plus utilisé pour SNMP)
- **Exemple**: `192.168.0.11`

### snmp_server3
- **Type**: Text
- **Description**: Tertiary SNMP server
- **Utilisation**: 5 fichiers
- **Exemple**: `192.168.0.12`

---

## 2. JeylanDevice - DNS Configuration (2 champs)

### dns_server_pri
- **Type**: Text
- **Description**: Primary DNS server
- **Utilisation**: 3 fichiers
- **Exemple**: `192.168.0.1`

### dns_server_sec
- **Type**: Text
- **Description**: Secondary DNS server
- **Utilisation**: 3 fichiers
- **Exemple**: `192.168.0.2`

---

## 3. JeylanDevice - Device Configuration (2 champs)

### dev_lpbk
- **Type**: Text
- **Description**: Device loopback address
- **Utilisation**: 18 fichiers ⚠️ CRITIQUE (le plus utilisé de tous!)
- **Exemple**: `10.0.0.1` ou `10.0.0.1/32`
- **Note**: Utilisé pour configuration loopback des routeurs/switches

### domain_name
- **Type**: Text
- **Description**: DNS domain name
- **Utilisation**: 5 fichiers
- **Exemple**: `int.jeyriku.net`

---

## 4. JeylanInterfaces - Interface Configuration (5 champs)

### iface_device
- **Type**: Text
- **Description**: Interface device association
- **Utilisation**: 13 fichiers ⚠️ CRITIQUE
- **Exemple**: `ge-0/0/0` ou `GigabitEthernet0/0`
- **Note**: Nom de l'interface physique

### iface_parent
- **Type**: Text
- **Description**: Parent interface
- **Utilisation**: 7 fichiers ⚠️ CRITIQUE
- **Exemple**: `ge-0/0/0` (pour subinterface ge-0/0/0.100)

### iface_role
- **Type**: Text
- **Description**: Interface role
- **Utilisation**: 7 fichiers ⚠️ CRITIQUE
- **Exemple**: `uplink`, `trunk`, `access`, `wan`

### iface_unit
- **Type**: Text
- **Description**: Interface unit/subinterface number
- **Utilisation**: 7 fichiers ⚠️ CRITIQUE
- **Exemple**: `100` (pour ge-0/0/0.100)

### iface_vrf
- **Type**: Text
- **Description**: VRF assignment
- **Utilisation**: 1 fichier
- **Exemple**: `MGMT`, `CUSTOMER_A`

---

## 5. JeylanRouting - Routing Configuration (5 champs)

### bgp_asn
- **Type**: Number
- **Description**: BGP Autonomous System Number
- **Utilisation**: 1 fichier (template)
- **Exemple**: `65000`

### bgp_vrf
- **Type**: Text
- **Description**: BGP VRF instance
- **Utilisation**: 2 fichiers
- **Exemple**: `CUSTOMER_A`

### ospf_area
- **Type**: Text
- **Description**: OSPF area
- **Utilisation**: 3 fichiers
- **Exemple**: `0.0.0.0` ou `0`

### rr1
- **Type**: Text
- **Description**: Route Reflector 1 address
- **Utilisation**: 3 fichiers
- **Exemple**: `10.0.0.11`

### rr2
- **Type**: Text
- **Description**: Route Reflector 2 address
- **Utilisation**: 3 fichiers
- **Exemple**: `10.0.0.12`

---

## Champs critiques par ordre d'importance

1. **dev_lpbk** (18 fichiers) - Loopback device pour routeurs PE/CE/RR
2. **iface_device** (13 fichiers) - Nom interface pour configuration
3. **snmp_server2** (13 fichiers) - Serveur SNMP secondaire
4. **snmp_community** (10 fichiers) - Community string SNMP
5. **snmp_location** (10 fichiers) - Localisation SNMP
6. **iface_parent** (7 fichiers) - Interface parent pour subinterfaces
7. **iface_role** (7 fichiers) - Rôle de l'interface
8. **iface_unit** (7 fichiers) - Numéro d'unité/VLAN

---

## Devices nécessitant les valeurs

### Priorité 1 - Routeurs PE/CE/RR (BGP/OSPF)
- **jey-srx3x-pe-01 à pe-05** : dev_lpbk, bgp_asn, ospf_area, rr1, rr2
- **jey-srx3x-rr-01 à rr-02** : dev_lpbk, bgp_asn, ospf_area
- **jey-srx3x-ce-01** : dev_lpbk
- **jey-isr1k-pe-01 à pe-02, isr4k-pe-01, isr8x-pe-01** : dev_lpbk, bgp_asn
- **jey-isr1k-ce-01 à ce-03** : dev_lpbk

### Priorité 2 - Switches (SNMP)
- **jey-c1000-sw-01, c1200-sw-01/02, c2960-sw-01 à 05** : snmp_community, snmp_location, snmp_server1/2/3
- **jey-cbs220-sw-01** : snmp_community, snmp_location
- **jey-ex23k-sw-01** : snmp_community, snmp_location

### Priorité 3 - Serveurs/NAS
- **jeysrv01 à jeysrv10, jeynas01 à 03** : domain_name (int.jeyriku.net)

---

## Format pour saisie des valeurs

### Exemple CSV pour devices PE/CE/RR:
```csv
device_name,dev_lpbk,bgp_asn,ospf_area,rr1,rr2,domain_name
jey-srx3x-pe-01,10.0.0.1/32,65000,0.0.0.0,10.0.0.11,10.0.0.12,int.jeyriku.net
jey-srx3x-pe-02,10.0.0.2/32,65000,0.0.0.0,10.0.0.11,10.0.0.12,int.jeyriku.net
jey-srx3x-rr-01,10.0.0.11/32,65000,0.0.0.0,,,int.jeyriku.net
```

### Exemple CSV pour switches:
```csv
device_name,snmp_community,snmp_location,snmp_server1,snmp_server2,snmp_server3,domain_name
jey-c1000-sw-01,public,"Datacenter - Rack 1",192.168.0.10,192.168.0.11,192.168.0.12,int.jeyriku.net
jey-c2960-sw-01,public,"Datacenter - Rack 2",192.168.0.10,192.168.0.11,192.168.0.12,int.jeyriku.net
```

### Exemple JSON pour serveurs:
```json
{
  "servers": [
    {"device": "jeysrv01", "domain_name": "int.jeyriku.net"},
    {"device": "jeysrv10", "domain_name": "int.jeyriku.net"},
    {"device": "jeynas01", "domain_name": "int.jeyriku.net"}
  ]
}
```

---

## Notes importantes

1. **Tous les champs sont optionnels** - Pas besoin de remplir tous les devices immédiatement
2. **Priorité sur les routeurs PE/CE/RR** - Ces devices utilisent le plus de custom_fields (dev_lpbk critique)
3. **SNMP pour les switches** - Configuration monitoring réseau
4. **Les champs Interfaces et Routing** - Seront remplis automatiquement par les playbooks lors de la génération de config

## Accès dans l'interface Infrahub

Les nouveaux champs sont maintenant visibles dans l'interface web Infrahub:
- URL: http://jeysrv10:8000 ou http://192.168.0.237:8000
- Navigation: Objects → Jeylan → Device → [Sélectionner un device]
- Les custom_fields apparaissent dans les sections appropriées du formulaire d'édition
