from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm


def home(request):
    """Page d'accueil"""
    return render(request, 'core/home.html')


def about(request):
    """Page À propos"""
    return render(request, 'core/about.html')


def blog(request):
    """Page Blog"""
    return render(request, 'core/blog.html')


def contact(request):
    """Page Contact avec formulaire"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Ici on pourrait envoyer un email
            # Pour l'instant on affiche juste un message de succès
            messages.success(
                request, 
                'Votre message a été envoyé avec succès. Nous vous répondrons dans les plus brefs délais.'
            )
            return redirect('core:contact')
    else:
        form = ContactForm()
    
    return render(request, 'core/contact.html', {'form': form})


def faq(request):
    """Page FAQ"""
    return render(request, 'core/faq.html')


def terms(request):
    """Page CGU"""
    return render(request, 'core/terms.html')


def privacy(request):
    """Page Politique de confidentialité"""
    return render(request, 'core/privacy.html')


def legal(request):
    """Page Mentions légales"""
    return render(request, 'core/legal.html')

