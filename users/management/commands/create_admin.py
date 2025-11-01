"""
Commande de gestion Django pour créer un superuser admin.
Usage: python manage.py create_admin
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Crée un superuser avec le rôle admin'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Nom d\'utilisateur du superuser (défaut: admin)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@investlink.com',
            help='Email du superuser'
        )
        parser.add_argument(
            '--password',
            type=str,
            default=None,
            help='Mot de passe du superuser (sinon utilise ADMIN_PASSWORD de l\'environnement)'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password'] or os.environ.get('ADMIN_PASSWORD', 'admin123')

        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'L\'utilisateur "{username}" existe déjà.')
            )
            
            # Mettre à jour le user_type si nécessaire
            user = User.objects.get(username=username)
            if user.user_type != 'admin':
                user.user_type = 'admin'
                user.is_staff = True
                user.is_superuser = True
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'User type mis à jour vers "admin" pour {username}')
                )
            return

        # Créer le superuser
        try:
            admin = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name='Admin',
                last_name='InvestLink',
                user_type='admin'
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Superuser "{username}" créé avec succès!\n'
                    f'Email: {email}\n'
                    f'User type: {admin.user_type}\n'
                    f'Is staff: {admin.is_staff}\n'
                    f'Is superuser: {admin.is_superuser}'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erreur lors de la création du superuser: {str(e)}')
            )
