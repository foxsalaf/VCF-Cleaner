import os
import re
import logging
from typing import List, Optional
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VCFCleaner:
    """
    Classe pour nettoyer les fichiers VCF (contacts) en supprimant :
    - Les doublons basés sur le nom et le téléphone
    - Les blocs inutiles (photos, notes, adresses, etc.)
    - Les contacts sans numéro de téléphone
    """
    
    def __init__(self):
        # Champs à supprimer (préfixes)
        self.fields_to_remove = [
            'PHOTO', 'NOTE', 'ADR', 'ORG', 'TITLE', 'BDAY', 'IMPP',
            'LABEL', 'URL', 'X-ABLabel', 'PRODID', 'VERSION',
            'X-ANDROID-CUSTOM', 'X-PHONETIC', 'NICKNAME', 'ROLE',
            'CATEGORIES', 'CALURI', 'FBURL', 'KEY', 'LOGO', 'SOUND',
            'UID', 'TZ', 'GEO', 'CLASS', 'SORT-STRING'
        ]
        
        # Champs essentiels à conserver
        self.essential_fields = ['BEGIN', 'END', 'FN', 'N', 'TEL', 'EMAIL']
        
        # Statistiques
        self.stats = {
            'total_contacts': 0,
            'contacts_with_phone': 0,
            'contacts_removed': 0,
            'duplicates_removed': 0,
            'blocks_removed': 0
        }
    
    def _should_remove_field(self, line: str) -> bool:
        """
        Détermine si une ligne doit être supprimée
        """
        line_upper = line.upper()
        
        # Vérifie si la ligne commence par un champ à supprimer
        for field in self.fields_to_remove:
            if line_upper.startswith(field + ':') or line_upper.startswith(field + ';'):
                return True
        return False
    
    def _extract_contact_info(self, contact_lines: List[str]) -> dict:
        """
        Extrait les informations essentielles d'un contact
        """
        info = {'name': '', 'phones': [], 'emails': []}
        
        for line in contact_lines:
            line_upper = line.upper()
            if line_upper.startswith('FN:'):
                info['name'] = line[3:].strip()
            elif line_upper.startswith('TEL'):
                # Extrait le numéro de téléphone (après les deux points)
                tel_match = re.search(r':([\d\s\-\+\(\)]+)', line)
                if tel_match:
                    phone = re.sub(r'[\s\-\(\)]', '', tel_match.group(1))
                    if phone:
                        info['phones'].append(phone)
            elif line_upper.startswith('EMAIL'):
                email_match = re.search(r':(.+)', line)
                if email_match:
                    info['emails'].append(email_match.group(1).strip())
        
        return info
    
    def _is_duplicate(self, contact1: dict, contact2: dict) -> bool:
        """
        Détermine si deux contacts sont des doublons
        """
        # Comparaison par nom (en ignorant la casse)
        if contact1['name'] and contact2['name']:
            if contact1['name'].lower() == contact2['name'].lower():
                return True
        
        # Comparaison par numéro de téléphone
        for phone1 in contact1['phones']:
            for phone2 in contact2['phones']:
                # Compare les derniers 8 chiffres (pour gérer les préfixes internationaux)
                if len(phone1) >= 8 and len(phone2) >= 8:
                    if phone1[-8:] == phone2[-8:]:
                        return True
        
        return False
    
    def _parse_vcf_contacts(self, lines: List[str]) -> List[List[str]]:
        """
        Parse le fichier VCF et retourne une liste de contacts
        """
        contacts = []
        current_contact = []
        in_vcard = False
        
        for line in lines:
            line_stripped = line.strip()
            
            if line_stripped.startswith('BEGIN:VCARD'):
                current_contact = [line]
                in_vcard = True
            elif line_stripped.startswith('END:VCARD'):
                current_contact.append(line)
                if in_vcard:
                    contacts.append(current_contact)
                current_contact = []
                in_vcard = False
            elif in_vcard:
                current_contact.append(line)
        
        return contacts
    
    def _clean_contact(self, contact_lines: List[str]) -> Optional[List[str]]:
        """
        Nettoie un contact individuel
        """
        cleaned_lines = []
        has_phone = False
        skip_until_next_field = False
        
        for line in contact_lines:
            line_stripped = line.strip()
            
            # Gestion des blocs multilignes (comme PHOTO)
            if skip_until_next_field:
                # Continue à ignorer jusqu'à trouver une nouvelle propriété
                if ':' in line_stripped and not line_stripped.startswith(' '):
                    skip_until_next_field = False
                else:
                    self.stats['blocks_removed'] += 1
                    continue
            
            # Vérifie si c'est un champ à supprimer
            if self._should_remove_field(line_stripped):
                skip_until_next_field = True
                self.stats['blocks_removed'] += 1
                continue
            
            # Vérifie la présence d'un téléphone
            if line_stripped.upper().startswith('TEL'):
                has_phone = True
            
            cleaned_lines.append(line)
        
        # Retourne le contact seulement s'il a un numéro de téléphone
        if has_phone:
            self.stats['contacts_with_phone'] += 1
            return cleaned_lines
        else:
            self.stats['contacts_removed'] += 1
            return None
    
    def _remove_duplicates(self, contacts: List[List[str]]) -> List[List[str]]:
        """
        Supprime les contacts en double
        """
        unique_contacts = []
        contact_infos = []
        
        for contact in contacts:
            info = self._extract_contact_info(contact)
            
            # Vérifie si c'est un doublon
            is_duplicate = False
            for existing_info in contact_infos:
                if self._is_duplicate(info, existing_info):
                    is_duplicate = True
                    self.stats['duplicates_removed'] += 1
                    break
            
            if not is_duplicate:
                unique_contacts.append(contact)
                contact_infos.append(info)
        
        return unique_contacts
    
    def nettoyer_vcf(self, input_path: str, output_path: str) -> bool:
        """
        Fonction principale pour nettoyer un fichier VCF
        """
        try:
            # Validation des chemins
            input_file = Path(input_path)
            output_file = Path(output_path)
            
            if not input_file.exists():
                logger.error(f"Le fichier d'entrée n'existe pas : {input_path}")
                return False
            
            if not input_file.suffix.lower() == '.vcf':
                logger.warning(f"Le fichier n'a pas l'extension .vcf : {input_path}")
            
            # Création du dossier de sortie si nécessaire
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Début du nettoyage de {input_path}")
            
            # Lecture du fichier avec gestion d'erreurs d'encodage
            try:
                with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                logger.warning("Erreur d'encodage UTF-8, tentative avec latin-1")
                with open(input_path, 'r', encoding='latin-1', errors='replace') as f:
                    lines = f.readlines()
            
            # Parse des contacts
            contacts = self._parse_vcf_contacts(lines)
            self.stats['total_contacts'] = len(contacts)
            logger.info(f"Nombre de contacts trouvés : {len(contacts)}")
            
            if not contacts:
                logger.warning("Aucun contact trouvé dans le fichier")
                return False
            
            # Nettoyage des contacts
            cleaned_contacts = []
            for contact in contacts:
                cleaned_contact = self._clean_contact(contact)
                if cleaned_contact:
                    cleaned_contacts.append(cleaned_contact)
            
            # Suppression des doublons
            final_contacts = self._remove_duplicates(cleaned_contacts)
            
            # Écriture du fichier nettoyé
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                for contact in final_contacts:
                    f.writelines(contact)
            
            # Affichage des statistiques
            self._print_stats(output_path)
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage : {str(e)}")
            return False
    
    def _print_stats(self, output_path: str):
        """
        Affiche les statistiques du nettoyage
        """
        final_count = self.stats['contacts_with_phone'] - self.stats['duplicates_removed']
        
        print("\n" + "="*50)
        print("STATISTIQUES DU NETTOYAGE")
        print("="*50)
        print(f"Contacts initiaux      : {self.stats['total_contacts']}")
        print(f"Contacts avec téléphone: {self.stats['contacts_with_phone']}")
        print(f"Contacts supprimés     : {self.stats['contacts_removed']}")
        print(f"Doublons supprimés     : {self.stats['duplicates_removed']}")
        print(f"Blocs supprimés        : {self.stats['blocks_removed']}")
        print(f"Contacts finaux        : {final_count}")
        print(f"Réduction              : {((self.stats['total_contacts'] - final_count) / self.stats['total_contacts'] * 100):.1f}%")
        print("="*50)
        print(f"Fichier nettoyé créé : {output_path}")


# Fonction utilitaire pour compatibilité avec le code original
def nettoyer_vcf(input_path: str, output_path: str) -> bool:
    """
    Fonction de compatibilité avec l'API originale
    """
    cleaner = VCFCleaner()
    return cleaner.nettoyer_vcf(input_path, output_path)


# Exemple d'utilisation
if __name__ == "__main__":
    # À modifier avec vos chemins
    input_file = r'C:\Users\votrechemin\contacts_export_smartphone.vcf'
    output_file = r'C:\Users\votrechemin\fichier_nettoye.vcf'
    
    cleaner = VCFCleaner()
    success = cleaner.nettoyer_vcf(input_file, output_file)
    
    if success:
        print("\nNettoyage terminé avec succès !")
    else:
        print("\nErreur lors du nettoyage.")
