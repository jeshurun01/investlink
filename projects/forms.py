from django import forms
from django.core.exceptions import ValidationError
from .models import Project, ProjectDocument


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
            # Vérifier la taille (10 MB max)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError('La taille du fichier ne doit pas dépasser 10 MB.')
            
            # Vérifier l'extension
            allowed_extensions = ['.pdf', '.doc', '.docx']
            file_extension = file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise ValidationError('Format non autorisé. Utilisez PDF, DOC ou DOCX.')
        
        return file
    
    def clean_featured_image(self):
        """Valider l'image principale"""
        image = self.cleaned_data.get('featured_image')
        if image:
            # Vérifier la taille (5 MB max)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('La taille de l\'image ne doit pas dépasser 5 MB.')
            
            # Vérifier que c'est bien une image
            if not image.content_type.startswith('image/'):
                raise ValidationError('Le fichier doit être une image.')
        
        return image
    
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
