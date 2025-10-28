from django.shortcuts import render


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
    """Page Contact"""
    return render(request, 'core/contact.html')


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

