#!/usr/bin/env python
"""
Script de restauration des données Django

Usage:
    python restore_data.py backup_full_20251105_143000.json
    python restore_data.py backups/backup_users_20251105_143000.json
"""

import os
import sys
import django
import subprocess

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


def restore_data(filepath):
    """Restaure les données depuis un fichier JSON."""
    
    if not os.path.exists(filepath):
        print(f"❌ Erreur : Le fichier '{filepath}' n'existe pas.")
        sys.exit(1)
    
    # Vérifier la taille du fichier
    file_size = os.path.getsize(filepath)
    if file_size == 0:
        print(f"❌ Erreur : Le fichier '{filepath}' est vide.")
        sys.exit(1)
    
    size_kb = file_size / 1024
    
    print(f"📦 Restauration des données depuis : {filepath}")
    print(f"📊 Taille : {size_kb:.2f} KB")
    print()
    
    # Confirmation
    response = input("⚠️  Cette opération va modifier la base de données. Continuer ? (oui/non) : ")
    if response.lower() not in ['oui', 'yes', 'o', 'y']:
        print("❌ Restauration annulée.")
        sys.exit(0)
    
    print("\n🔄 Restauration en cours...")
    
    cmd = [
        sys.executable,
        'manage.py',
        'loaddata',
        filepath
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✅ Restauration réussie !")
        if result.stdout:
            print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la restauration : {e}")
        if e.stderr:
            print(f"Détails : {e.stderr}")
        sys.exit(1)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Restauration des données Django')
    parser.add_argument(
        'filepath',
        type=str,
        help='Chemin vers le fichier de sauvegarde (.json)'
    )
    
    args = parser.parse_args()
    
    restore_data(args.filepath)
