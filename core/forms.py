from django import forms


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
