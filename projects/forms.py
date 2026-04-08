from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
import os
from .models import Project, ProjectDocument


def validate_file_size(file):
    """Valide la taille d'un fichier"""
    if file.size > settings.MAX_UPLOAD_SIZE:
        raise ValidationError(f'La taille du fichier ne doit pas dépasser {settings.MAX_UPLOAD_SIZE / (1024 * 1024):.0f} MB.')


def validate_file_extension(file, allowed_extensions):
    """Valide l'extension d'un fichier"""
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(f'Extension de fichier non autorisée. Extensions acceptées : {", ".join(allowed_extensions)}.')


class ProjectValidationForm(forms.ModelForm):
    """Formulaire pour la validation des projets par les admins"""
    
    class Meta:
        model = Project
        fields = ['status', 'admin_notes', 'rejection_reason']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'input-field',
            }),
            'admin_notes': forms.Textarea(attrs={
                'class': 'input-field',
                'rows': 4,
                'placeholder': 'Notes internes pour l\'équipe administrative...'
            }),
            'rejection_reason': forms.Textarea(attrs={
                'class': 'input-field',
                'rows': 4,
                'placeholder': 'Raison du refus (sera envoyée au porteur)...'
            }),
        }
        labels = {
            'status': 'Statut du projet',
            'admin_notes': 'Notes administratives (internes)',
            'rejection_reason': 'Motif de refus (visible par le porteur)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limiter les choix de statut disponibles pour la validation
        self.fields['status'].choices = [
            ('under_review', 'En cours d\'examen'),
            ('revision_requested', 'Révision demandée'),
            ('approved', 'Validé'),
            ('rejected', 'Refusé'),
        ]
    
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        rejection_reason = cleaned_data.get('rejection_reason')
        
        # Si le projet est rejeté, une raison est obligatoire
        if status == 'rejected' and not rejection_reason:
            raise ValidationError({
                'rejection_reason': 'Vous devez fournir une raison pour le refus du projet.'
            })
        
        # Si le projet n'est pas rejeté, vider le motif de refus
        if status != 'rejected':
            cleaned_data['rejection_reason'] = ''
        
        return cleaned_data


class MultipleFileInput(forms.ClearableFileInput):
    """Widget personnalisé pour l'upload multiple de fichiers"""
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """Champ personnalisé pour l'upload multiple de fichiers"""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class ProjectSubmissionForm(forms.ModelForm):
    """Formulaire de soumission de projet"""
    
    # Champs supplémentaires pour les documents
    business_plan = forms.FileField(
        required=False,
        label='Business Plan',
        widget=forms.FileInput(attrs={
            'class': 'input-field',
            'accept': '.pdf,.doc,.docx'
        }),
        help_text='Format accepté: PDF, DOC, DOCX (max 10 MB)'
    )
    financial_documents = MultipleFileField(
        required=False,
        label='Documents financiers',
        widget=MultipleFileInput(attrs={
            'class': 'input-field',
            'accept': '.pdf,.xlsx,.xls'
        }),
        help_text='Format accepté: PDF, Excel (max 10 MB par fichier)'
    )
    legal_documents = MultipleFileField(
        required=False,
        label='Documents juridiques',
        widget=MultipleFileInput(attrs={
            'class': 'input-field',
            'accept': '.pdf'
        }),
        help_text='Format accepté: PDF (max 10 MB par fichier)'
    )
    
    class Meta:
        model = Project
        fields = [
            'title', 'summary', 'description', 'sector', 'funding_stage',
            'location', 'funding_goal', 'min_investment', 'featured_image',
            'video_url'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': 'Nom de votre projet'
            }),
            'summary': forms.Textarea(attrs={
                'class': 'input-field',
                'placeholder': 'Résumé court du projet (500 caractères max)',
                'rows': 3,
                'maxlength': 500
            }),
            'description': forms.Textarea(attrs={
                'class': 'input-field',
                'placeholder': 'Description détaillée de votre projet, objectifs, impact attendu...',
                'rows': 8
            }),
            'sector': forms.Select(attrs={'class': 'input-field'}),
            'funding_stage': forms.Select(attrs={'class': 'input-field'}),
            'location': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': 'Ville, Province, Pays'
            }),
            'funding_goal': forms.NumberInput(attrs={
                'class': 'input-field',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'min_investment': forms.NumberInput(attrs={
                'class': 'input-field',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'input-field',
                'accept': 'image/*'
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'input-field',
                'placeholder': 'https://www.youtube.com/watch?v=...'
            }),
        }
        labels = {
            'title': 'Titre du projet *',
            'summary': 'Résumé court *',
            'description': 'Description détaillée *',
            'sector': 'Secteur d\'activité *',
            'funding_stage': 'Stade de financement *',
            'location': 'Localisation *',
            'funding_goal': 'Montant recherché (USD) *',
            'min_investment': 'Investissement minimum (USD) *',
            'featured_image': 'Image principale',
            'video_url': 'Lien vidéo (optionnel)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre certains champs obligatoires
        self.fields['title'].required = True
        self.fields['summary'].required = True
        self.fields['description'].required = True
        self.fields['sector'].required = True
        self.fields['funding_stage'].required = True
        self.fields['location'].required = True
        self.fields['funding_goal'].required = True
        self.fields['min_investment'].required = True
    
    def clean_funding_goal(self):
        """Valider le montant recherché"""
        funding_goal = self.cleaned_data.get('funding_goal')
        if funding_goal and funding_goal <= 0:
            raise ValidationError('Le montant recherché doit être supérieur à zéro.')
        if funding_goal and funding_goal > 10000000:  # 10 millions max
            raise ValidationError('Le montant recherché ne peut pas dépasser 10 millions USD.')
        return funding_goal
    
    def clean_min_investment(self):
        """Valider l'investissement minimum"""
        min_investment = self.cleaned_data.get('min_investment')
        funding_goal = self.cleaned_data.get('funding_goal')
        
        if min_investment and min_investment <= 0:
            raise ValidationError('L\'investissement minimum doit être supérieur à zéro.')
        
        if min_investment and funding_goal and min_investment > funding_goal:
            raise ValidationError('L\'investissement minimum ne peut pas dépasser le montant recherché.')
        
        return min_investment
    
    def clean_business_plan(self):
        """Valider le fichier business plan"""
        file = self.cleaned_data.get('business_plan')
        if file:
            validate_file_size(file)
            validate_file_extension(file, settings.ALLOWED_DOCUMENT_EXTENSIONS)
        return file
    
    def clean_financial_documents(self):
        """Valider les documents financiers"""
        files = self.cleaned_data.get('financial_documents')
        if files:
            if not isinstance(files, list):
                files = [files]
            for file in files:
                validate_file_size(file)
                validate_file_extension(file, settings.ALLOWED_DOCUMENT_EXTENSIONS)
        return files
    
    def clean_legal_documents(self):
        """Valider les documents juridiques"""
        files = self.cleaned_data.get('legal_documents')
        if files:
            if not isinstance(files, list):
                files = [files]
            for file in files:
                validate_file_size(file)
                validate_file_extension(file, ['.pdf'])
        return files
    
    def clean_featured_image(self):
        """Valider l'image principale"""
        file = self.cleaned_data.get('featured_image')
        if file:
            validate_file_size(file)
            validate_file_extension(file, settings.ALLOWED_IMAGE_EXTENSIONS)
        return file
    
    def clean_video_url(self):
        """Valider l'URL de la vidéo"""
        url = self.cleaned_data.get('video_url')
        if url:
            # Vérifier que c'est une URL YouTube ou Vimeo
            valid_domains = ['youtube.com', 'youtu.be', 'vimeo.com']
            if not any(domain in url.lower() for domain in valid_domains):
                raise ValidationError('Seules les vidéos YouTube et Vimeo sont acceptées.')
        
        return url


class ProjectUpdateForm(forms.ModelForm):
    """Formulaire de mise à jour de projet (avant validation)"""
    
    class Meta:
        model = Project
        fields = [
            'title', 'summary', 'description', 'sector', 'funding_stage',
            'location', 'funding_goal', 'min_investment', 'featured_image',
            'video_url'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': 'Nom de votre projet'
            }),
            'summary': forms.Textarea(attrs={
                'class': 'input-field',
                'placeholder': 'Résumé court du projet (500 caractères max)',
                'rows': 3,
                'maxlength': 500
            }),
            'description': forms.Textarea(attrs={
                'class': 'input-field',
                'placeholder': 'Description détaillée de votre projet',
                'rows': 8
            }),
            'sector': forms.Select(attrs={'class': 'input-field'}),
            'funding_stage': forms.Select(attrs={'class': 'input-field'}),
            'location': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': 'Ville, Province, Pays'
            }),
            'funding_goal': forms.NumberInput(attrs={
                'class': 'input-field',
                'step': '0.01'
            }),
            'min_investment': forms.NumberInput(attrs={
                'class': 'input-field',
                'step': '0.01'
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'input-field',
                'accept': 'image/*'
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'input-field',
                'placeholder': 'https://www.youtube.com/watch?v=...'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Vérifier que le projet n'est pas déjà validé
        if self.instance and self.instance.status == 'approved':
            raise ValidationError('Vous ne pouvez pas modifier un projet déjà validé.')
        
        return cleaned_data
