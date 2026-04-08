from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from django.conf import settings
import os
from .models import User, ProjectOwnerProfile, InvestorProfile


def validate_avatar_file(file):
    """Valide le fichier avatar"""
    # Vérifier la taille
    if file.size > settings.MAX_UPLOAD_SIZE:
        raise ValidationError(f'La taille du fichier ne doit pas dépasser {settings.MAX_UPLOAD_SIZE / (1024 * 1024):.0f} MB.')
    
    # Vérifier l'extension
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(f'Extension de fichier non autorisée. Extensions acceptées : {", ".join(settings.ALLOWED_IMAGE_EXTENSIONS)}.')


class UserRegistrationForm(UserCreationForm):
    """Formulaire de base pour l'inscription"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'input-field',
            'placeholder': 'votre@email.com'
        })
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label='Prénom',
        widget=forms.TextInput(attrs={
            'class': 'input-field',
            'placeholder': 'Prénom'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label='Nom',
        widget=forms.TextInput(attrs={
            'class': 'input-field',
            'placeholder': 'Nom'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        label='Téléphone',
        widget=forms.TextInput(attrs={
            'class': 'input-field',
            'placeholder': '+243 XXX XXX XXX'
        })
    )
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'radio-field'}),
        label='Type de compte'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'user_type', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': 'Nom d\'utilisateur'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajouter les classes CSS aux champs de mot de passe
        self.fields['password1'].widget.attrs.update({'class': 'input-field', 'placeholder': 'Mot de passe'})
        self.fields['password2'].widget.attrs.update({'class': 'input-field', 'placeholder': 'Confirmer le mot de passe'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Un compte avec cet email existe déjà.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.user_type = self.cleaned_data.get('user_type', 'porteur')
        
        if commit:
            user.save()
            # Créer le profil correspondant
            if user.user_type == 'porteur':
                ProjectOwnerProfile.objects.create(user=user)
            elif user.user_type == 'investisseur':
                InvestorProfile.objects.create(user=user)
        
        return user


class ProjectOwnerRegistrationForm(UserRegistrationForm):
    """Formulaire d'inscription pour porteur de projet"""
    
    company_name = forms.CharField(
        max_length=200,
        required=False,
        label='Nom de l\'entreprise',
        widget=forms.TextInput(attrs={
            'class': 'input-field',
            'placeholder': 'Nom de votre entreprise'
        })
    )
    company_registration = forms.CharField(
        max_length=100,
        required=False,
        label='Numéro d\'enregistrement',
        widget=forms.TextInput(attrs={
            'class': 'input-field',
            'placeholder': 'RCCM, NIF, etc.'
        })
    )
    website = forms.URLField(
        required=False,
        label='Site web',
        widget=forms.URLInput(attrs={
            'class': 'input-field',
            'placeholder': 'https://www.example.com'
        })
    )
    gdpr_consent = forms.BooleanField(
        required=True,
        label='J\'accepte la politique de confidentialité et les conditions d\'utilisation (RGPD)',
        widget=forms.CheckboxInput(attrs={'class': 'checkbox-field'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': 'Nom d\'utilisateur'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Retirer le champ user_type car il sera défini automatiquement
        if 'user_type' in self.fields:
            del self.fields['user_type']
    
    def save(self, commit=True):
        # Ne pas appeler super().save() car il essaie d'accéder à user_type
        # Appeler directement UserCreationForm.save()
        user = UserCreationForm.save(self, commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data.get('phone', '')
        user.user_type = 'porteur'
        
        if commit:
            user.save()
            # Enregistrer le consentement RGPD
            if self.cleaned_data.get('gdpr_consent'):
                user.give_gdpr_consent()
            # Créer le profil porteur avec les infos supplémentaires
            ProjectOwnerProfile.objects.create(
                user=user,
                company_name=self.cleaned_data.get('company_name', ''),
                company_registration=self.cleaned_data.get('company_registration', ''),
                website=self.cleaned_data.get('website', '')
            )
        
        return user


class InvestorRegistrationForm(UserRegistrationForm):
    """Formulaire d'inscription pour investisseur"""
    
    investment_range = forms.ChoiceField(
        choices=InvestorProfile.INVESTMENT_RANGE_CHOICES,
        required=False,
        label='Fourchette d\'investissement',
        widget=forms.Select(attrs={'class': 'input-field'})
    )
    risk_level = forms.ChoiceField(
        choices=InvestorProfile.RISK_LEVEL_CHOICES,
        required=False,
        label='Niveau de risque accepté',
        widget=forms.Select(attrs={'class': 'input-field'})
    )
    preferred_sectors = forms.CharField(
        required=False,
        label='Secteurs préférés',
        widget=forms.Textarea(attrs={
            'class': 'input-field',
            'placeholder': 'Technologies, Santé, Agriculture...',
            'rows': 3
        })
    )
    location_preference = forms.CharField(
        max_length=200,
        required=False,
        label='Préférence de localisation',
        widget=forms.TextInput(attrs={
            'class': 'input-field',
            'placeholder': 'Kinshasa, RDC, Afrique...'
        })
    )
    gdpr_consent = forms.BooleanField(
        required=True,
        label='J\'accepte la politique de confidentialité et les conditions d\'utilisation (RGPD)',
        widget=forms.CheckboxInput(attrs={'class': 'checkbox-field'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': 'Nom d\'utilisateur'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Retirer le champ user_type car il sera défini automatiquement
        if 'user_type' in self.fields:
            del self.fields['user_type']
    
    def save(self, commit=True):
        # Ne pas appeler super().save() car il essaie d'accéder à user_type
        # Appeler directement UserCreationForm.save()
        user = UserCreationForm.save(self, commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data.get('phone', '')
        user.user_type = 'investisseur'
        
        if commit:
            user.save()
            # Enregistrer le consentement RGPD
            if self.cleaned_data.get('gdpr_consent'):
                user.give_gdpr_consent()
            # Créer le profil investisseur avec les préférences
            InvestorProfile.objects.create(
                user=user,
                investment_range=self.cleaned_data.get('investment_range', ''),
                risk_level=self.cleaned_data.get('risk_level', 'medium'),
                preferred_sectors=self.cleaned_data.get('preferred_sectors', ''),
                location_preference=self.cleaned_data.get('location_preference', '')
            )
        
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Formulaire de connexion personnalisé"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'input-field',
            'placeholder': 'Nom d\'utilisateur ou email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'input-field',
            'placeholder': 'Mot de passe'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'checkbox-field'})
    )


class ProfileUpdateForm(forms.ModelForm):
    """Formulaire de mise à jour du profil utilisateur"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'avatar', 'bio']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input-field'}),
            'last_name': forms.TextInput(attrs={'class': 'input-field'}),
            'email': forms.EmailInput(attrs={'class': 'input-field'}),
            'phone': forms.TextInput(attrs={'class': 'input-field'}),
            'avatar': forms.FileInput(attrs={'class': 'file-input', 'accept': 'image/*'}),
            'bio': forms.Textarea(attrs={'class': 'input-field', 'rows': 4}),
        }
    
    def clean_avatar(self):
        """Valider le fichier avatar"""
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            validate_avatar_file(avatar)
        return avatar


class ProjectOwnerProfileUpdateForm(forms.ModelForm):
    """Formulaire de mise à jour du profil porteur"""
    
    class Meta:
        model = ProjectOwnerProfile
        fields = ['company_name', 'company_registration', 'website', 'linkedin', 'experience', 'achievements']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'input-field'}),
            'company_registration': forms.TextInput(attrs={'class': 'input-field'}),
            'website': forms.URLInput(attrs={'class': 'input-field'}),
            'linkedin': forms.URLInput(attrs={'class': 'input-field'}),
            'experience': forms.Textarea(attrs={'class': 'input-field', 'rows': 4}),
            'achievements': forms.Textarea(attrs={'class': 'input-field', 'rows': 4}),
        }


class InvestorProfileUpdateForm(forms.ModelForm):
    """Formulaire de mise à jour du profil investisseur"""
    
    class Meta:
        model = InvestorProfile
        fields = ['investment_range', 'preferred_sectors', 'risk_level', 'location_preference']
        widgets = {
            'investment_range': forms.Select(attrs={'class': 'input-field'}),
            'preferred_sectors': forms.Textarea(attrs={'class': 'input-field', 'rows': 3}),
            'risk_level': forms.Select(attrs={'class': 'input-field'}),
            'location_preference': forms.TextInput(attrs={'class': 'input-field'}),
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    """Formulaire de changement de mot de passe personnalisé"""
    
    old_password = forms.CharField(
        label='Mot de passe actuel',
        widget=forms.PasswordInput(attrs={
            'class': 'input-field',
            'placeholder': 'Entrez votre mot de passe actuel'
        })
    )
    new_password1 = forms.CharField(
        label='Nouveau mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'input-field',
            'placeholder': 'Entrez votre nouveau mot de passe'
        }),
        help_text='Minimum 8 caractères'
    )
    new_password2 = forms.CharField(
        label='Confirmer le nouveau mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'input-field',
            'placeholder': 'Confirmez votre nouveau mot de passe'
        })
    )

class AdminCreateUserForm(forms.ModelForm):
    """Formulaire admin pour créer un nouvel utilisateur"""
    
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'input-field',
            'placeholder': 'Mot de passe (minimum 8 caractères)'
        }),
        help_text='Minimum 8 caractères'
    )
    password_confirm = forms.CharField(
        label='Confirmer le mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'input-field',
            'placeholder': 'Confirmez le mot de passe'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'user_type', 'is_active', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': 'Nom d\'utilisateur'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'input-field',
                'placeholder': 'adresse@email.com'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': 'Prénom'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': 'Nom'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': '+243 XXX XXX XXX'
            }),
            'user_type': forms.Select(attrs={
                'class': 'input-field'
            }),
        }
        labels = {
            'username': 'Nom d\'utilisateur',
            'email': 'Email',
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'phone': 'Téléphone',
            'user_type': 'Type d\'utilisateur',
            'is_active': 'Compte actif',
            'is_staff': 'Statut administrateur',
        }
    
    def clean_email(self):
        """Vérifier que l'email n'existe pas déjà"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Un utilisateur avec cet email existe déjà.')
        return email
    
    def clean_username(self):
        """Vérifier que le nom d'utilisateur n'existe pas déjà"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Ce nom d\'utilisateur est déjà pris.')
        return username
    
    def clean(self):
        """Valider que les mots de passe correspondent"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise ValidationError('Les mots de passe ne correspondent pas.')
            if len(password) < 8:
                raise ValidationError('Le mot de passe doit contenir au moins 8 caractères.')
        
        return cleaned_data
    
    def save(self, commit=True):
        """Créer l'utilisateur avec le mot de passe hashé"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
        
        return user