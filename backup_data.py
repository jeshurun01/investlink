#!/usr/bin/env python
"""
Script de sauvegarde des données Django

Usage:
    python backup_data.py          # Sauvegarde complète
    python backup_data.py --app users  # Sauvegarde d'une app spécifique
"""

import os
import sys
import django
from datetime import datetime
import subprocess

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


def backup_data(app_name=None):
    """Sauvegarde les données de la base de données."""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = os.path.join(os.path.dirname(__file__), 'backups')
    
    # Créer le dossier backups si nécessaire
    os.makedirs(backup_dir, exist_ok=True)
    
    if app_name:
        # Sauvegarde d'une app spécifique
        filename = f'backup_{app_name}_{timestamp}.json'
        filepath = os.path.join(backup_dir, filename)
        
        print(f"📦 Sauvegarde de l'app '{app_name}'...")
        cmd = [
            sys.executable,
            'manage.py',
            'dumpdata',
            app_name,
            '--natural-foreign',
            '--natural-primary',
            '--indent=2',
            f'--output={filepath}'
        ]
    else:
        # Sauvegarde complète
        filename = f'backup_full_{timestamp}.json'
        filepath = os.path.join(backup_dir, filename)
        
        print("📦 Sauvegarde complète de la base de données...")
        cmd = [
            sys.executable,
            'manage.py',
            'dumpdata',
            '--natural-foreign',
            '--natural-primary',
            '--indent=2',
            '--exclude=contenttypes',
            '--exclude=auth.permission',
            '--exclude=sessions.session',
            f'--output={filepath}'
        ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Vérifier la taille du fichier
        file_size = os.path.getsize(filepath)
        size_kb = file_size / 1024
        
        print(f"✅ Sauvegarde réussie !")
        print(f"📁 Fichier : {filename}")
        print(f"📊 Taille : {size_kb:.2f} KB")
        print(f"📍 Emplacement : {filepath}")
        
        return filepath
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la sauvegarde : {e}")
        if e.stderr:
            print(f"Détails : {e.stderr}")
        sys.exit(1)


def backup_all_apps():
    """Sauvegarde toutes les apps principales séparément."""
    
    apps = ['users', 'projects', 'core', 'messaging', 'notifications']
    
    print("🚀 Sauvegarde de toutes les apps...\n")
    
    for app in apps:
        backup_data(app)
        print()
    
    # Sauvegarde complète également
    backup_data()
    
    print("✅ Toutes les sauvegardes sont terminées !")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Sauvegarde des données Django')
    parser.add_argument(
        '--app',
        type=str,
        help='Nom de l\'app à sauvegarder (ex: users, projects)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Sauvegarder toutes les apps séparément'
    )
    
    args = parser.parse_args()
    
    if args.all:
        backup_all_apps()
    elif args.app:
        backup_data(args.app)
    else:
        backup_data()
