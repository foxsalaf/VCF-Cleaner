def nettoyer_vcf(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    clean_blocks = []
    current_block = []
    keep_block = False
    in_photo_block = False

    for line in lines:
        line_stripped = line.strip()

        if line_stripped.startswith('BEGIN'):
            current_block = [line]
            keep_block = False
            in_photo_block = False

        elif line_stripped.startswith('END'):
            current_block.append(line)
            if keep_block:
                clean_blocks.extend(current_block)
            current_block = []

        elif line_stripped.startswith('PHOTO'):
            in_photo_block = True  # Commencer à skipper le bloc photo

        elif in_photo_block:
            if line_stripped == '':
                in_photo_block = False  # Fin du bloc photo sur ligne vide
            continue

        elif any(line_stripped.startswith(prefix) for prefix in ['NOTE', 'item1.URL', 'item1.X-ABLabel', 'ORG:', 'TITLE:', 'PRODID', 'VERSION', 'LABEL', 'ADR', 'BDAY', 'IMPP']):
            continue  # Ignorer ces lignes

        else:
            current_block.append(line)
            if line_stripped.startswith('TEL'):
                keep_block = True

    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(clean_blocks)

    print(f"Fichier nettoyé créé : {output_path}")

# à modifier et ajouter votre répertoire :
nettoyer_vcf(r'C:\Users\votrechemin\votrefichierlourdexporterdepuisvotresmartphone.vcf',
             r'C:\Users\votrechemin\fichier_nettoye.vcf')