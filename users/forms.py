from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User, ProjectOwnerProfile, InvestorProfile


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
            'avatar': forms.FileInput(attrs={'class': 'file-input'}),
            'bio': forms.Textarea(attrs={'class': 'input-field', 'rows': 4}),
        }


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
