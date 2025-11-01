from django import forms
from .models import BlogPost, BlogCategory


class ContactForm(forms.Form):
    """Formulaire de contact"""
    
    name = forms.CharField(
        max_length=100,
        label='Nom complet',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition',
            'placeholder': 'Votre nom complet'
        })
    )
    
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition',
            'placeholder': 'votre@email.com'
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        label='Téléphone (optionnel)',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition',
            'placeholder': '+243 XXX XXX XXX'
        })
    )
    
    subject = forms.CharField(
        max_length=200,
        label='Sujet',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition',
            'placeholder': 'Sujet de votre message'
        })
    )
    
    message = forms.CharField(
        label='Message',
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition',
            'placeholder': 'Votre message...',
            'rows': 6
        })
    )
    
    def clean_message(self):
        message = self.cleaned_data.get('message')
        if len(message) < 10:
            raise forms.ValidationError('Le message doit contenir au moins 10 caractères.')
        return message


class BlogPostForm(forms.ModelForm):
    """Formulaire d'article de blog"""
    
    class Meta:
        model = BlogPost
        fields = ['title', 'category', 'featured_image', 'excerpt', 'content', 
                 'status', 'tags', 'meta_description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-blue-600',
                'placeholder': 'Titre de l\'article'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-blue-600'
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-blue-600',
                'accept': 'image/*'
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-blue-600',
                'placeholder': 'Résumé de l\'article (300 caractères max)',
                'rows': 3
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-blue-600',
                'placeholder': 'Contenu complet de l\'article',
                'rows': 15
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-blue-600'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-blue-600',
                'placeholder': 'Séparez les tags par des virgules (ex: finance, investissement, startup)'
            }),
            'meta_description': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-blue-600',
                'placeholder': 'Description pour le référencement SEO (160 caractères max)'
            }),
        }


class BlogCategoryForm(forms.ModelForm):
    """Formulaire de catégorie"""
    
    class Meta:
        model = BlogCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-blue-600',
                'placeholder': 'Nom de la catégorie'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-blue-600',
                'placeholder': 'Description de la catégorie',
                'rows': 4
            }),
        }
