# VCF-Cleaner
Automatiser le nettoyage de 30 000 contacts VCF avec Python et Google Contacts (fusion des doublons).

# VCF Cleaner Python Script

Un script Python simple et efficace pour nettoyer les fichiers VCF volumineux (cartes de contacts) en supprimant :

* Les doublons
* Les blocs inutiles (photos, notes, adresses, organisation, etc.)
* Les contacts sans numéro de téléphone

## Pourquoi ?

Lorsque vous exportez vos contacts depuis un téléphone ou un compte (Android, Outlook, etc.), le fichier `.vcf` peut contenir :

* Des doublons
* Des pavés base64 de photos
* Des informations inutiles qui alourdissent le fichier

Ce script automatise le nettoyage pour un import propre dans Google Contacts, Outlook ou tout autre gestionnaire de contacts.

## Fonctionnalités :

* Suppression des blocs `PHOTO`, `NOTE`, `ADR`, `ORG`, etc.
* Suppression des contacts sans numéro de téléphone (`TEL`)
* Conservation des blocs structurés

## Utilisation :

### Prérequis :

* Python 3.x installé ([https://www.python.org/downloads/](https://www.python.org/downloads/))

### Exemple :

```python
from nettoyage_vcf import nettoyer_vcf

nettoyer_vcf(r'C:\Users\VotreNom\Downloads\MYCARD.vcf',
             r'C:\Users\VotreNom\Downloads\fichier_nettoye.vcf')
```

1. Remplacez les chemins par ceux de votre fichier source et du fichier de sortie.
2. Exécutez le script via votre terminal :

```bash
python nettoyage_vcf.py
```

## Remarque :

* Pour éviter les pertes, vous pouvez ensuite importer le fichier nettoyé dans [Google Contacts](https://contacts.google.com) pour une déduplication avancée et un export final. Google Contacts accepte jusqu'à 25 000 contacts, mais le fichier sera largement réduit après le nettoyage.

---

## Auteur :

* [Mouhammad AHMED](https://www.linkedin.com/in/mouhammad-ahmed)

Licence : MIT — Libre pour un usage personnel ou professionnel sans garantie.

## .gitignore suggéré :

```
__pycache__/
*.pyc
*.log
*.vcf
.env
```

Ce fichier permet d'éviter d'inclure les fichiers temporaires, personnels ou inutiles dans le dépôt GitHub.

Screenshots : 
![image](https://github.com/user-attachments/assets/1557357e-ddfe-41a3-b189-2c27fc658657)
![image](https://github.com/user-attachments/assets/2c811ebd-3587-481c-86be-59003970d98a)


