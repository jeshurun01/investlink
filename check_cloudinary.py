#!/usr/bin/env python
"""
Script de diagnostic Cloudinary
Vérifie si Cloudinary est correctement configuré
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

print("=" * 60)
print("DIAGNOSTIC CLOUDINARY")
print("=" * 60)

# 1. Check DEBUG mode
print(f"\n1. Mode DEBUG: {settings.DEBUG}")
if settings.DEBUG:
    print("   ⚠️  DEBUG=True - Cloudinary ne sera PAS utilisé")
    print("   💡 Sur Render, assurez-vous que DEBUG=False")
else:
    print("   ✅ DEBUG=False - Cloudinary devrait être actif")

# 2. Check if Cloudinary is in INSTALLED_APPS
print(f"\n2. Cloudinary dans INSTALLED_APPS:")
if 'cloudinary' in settings.INSTALLED_APPS:
    print("   ✅ cloudinary trouvé")
else:
    print("   ❌ cloudinary manquant")
    
if 'cloudinary_storage' in settings.INSTALLED_APPS:
    print("   ✅ cloudinary_storage trouvé")
else:
    print("   ❌ cloudinary_storage manquant")

# 3. Check DEFAULT_FILE_STORAGE
print(f"\n3. Storage backend:")
storage = getattr(settings, 'DEFAULT_FILE_STORAGE', 'default')
print(f"   DEFAULT_FILE_STORAGE = {storage}")
if 'cloudinary' in storage.lower():
    print("   ✅ Utilise Cloudinary")
else:
    print("   ⚠️  N'utilise PAS Cloudinary")

# 4. Check Cloudinary configuration
print(f"\n4. Configuration Cloudinary:")
try:
    import cloudinary
    config = cloudinary.config()
    
    cloud_name = config.cloud_name or ''
    api_key = config.api_key or ''
    
    if cloud_name:
        print(f"   ✅ CLOUD_NAME: {cloud_name}")
    else:
        print("   ❌ CLOUD_NAME: Non configuré")
        
    if api_key:
        print(f"   ✅ API_KEY: {api_key[:8]}... (masqué)")
    else:
        print("   ❌ API_KEY: Non configuré")
        
    if config.api_secret:
        print("   ✅ API_SECRET: Configuré (masqué)")
    else:
        print("   ❌ API_SECRET: Non configuré")
        
except ImportError:
    print("   ❌ Module cloudinary non importable")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# 5. Check environment variables
print(f"\n5. Variables d'environnement:")
env_vars = {
    'DEBUG': os.getenv('DEBUG', 'non défini'),
    'CLOUDINARY_CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME', 'non défini'),
    'CLOUDINARY_API_KEY': os.getenv('CLOUDINARY_API_KEY', 'non défini'),
    'CLOUDINARY_API_SECRET': 'défini' if os.getenv('CLOUDINARY_API_SECRET') else 'non défini',
}

for key, value in env_vars.items():
    if value == 'non défini':
        print(f"   ❌ {key}: {value}")
    else:
        if key == 'CLOUDINARY_API_KEY' and value != 'non défini':
            print(f"   ✅ {key}: {value[:8]}... (masqué)")
        else:
            print(f"   ✅ {key}: {value}")

# 6. Test upload (optionnel)
print(f"\n6. Test d'upload Cloudinary:")
if not settings.DEBUG and 'cloudinary' in settings.INSTALLED_APPS:
    try:
        import cloudinary.uploader
        # Ne pas vraiment uploader, juste vérifier que l'API est accessible
        print("   ✅ Module cloudinary.uploader importé avec succès")
        print("   💡 Pour tester un vrai upload, ajoutez une image via l'admin")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
else:
    print("   ⏭️  Sauté (DEBUG=True ou Cloudinary non installé)")

print("\n" + "=" * 60)
print("RECOMMANDATIONS")
print("=" * 60)

if settings.DEBUG:
    print("\n⚠️  Sur Render, ajoutez cette variable d'environnement:")
    print("   DEBUG = False")
    
if os.getenv('CLOUDINARY_CLOUD_NAME') == 'non défini':
    print("\n❌ Variables Cloudinary manquantes sur Render:")
    print("   1. Créez un compte: https://cloudinary.com/users/register_free")
    print("   2. Récupérez vos credentials dans le Dashboard")
    print("   3. Ajoutez sur Render → Environment:")
    print("      CLOUDINARY_CLOUD_NAME = votre_cloud_name")
    print("      CLOUDINARY_API_KEY = votre_api_key")
    print("      CLOUDINARY_API_SECRET = votre_api_secret")
else:
    print("\n✅ Configuration semble correcte!")
    print("   Si les images ne s'affichent toujours pas:")
    print("   1. Uploadez une nouvelle image via l'admin Django")
    print("   2. Vérifiez dans Cloudinary Dashboard → Media Library")
    print("   3. Regardez les logs Render pour les erreurs")

print("\n" + "=" * 60)
