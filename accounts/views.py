from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from allauth.socialaccount.models import SocialApp

from .forms import SignUpForm


def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Plusieurs backends (ModelBackend + allauth) : Django exige le backend explicite.
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('dashboard')
    else:
        form = SignUpForm()

    # Protéger les boutons sociaux quand les apps ne sont pas encore configurées
    has_google_app = SocialApp.objects.filter(provider="google").exists()
    has_facebook_app = SocialApp.objects.filter(provider="facebook").exists()

    return render(
        request,
        'accounts/signup.html',
        {
            'form': form,
            'has_google_app': has_google_app,
            'has_facebook_app': has_facebook_app,
        },
    )


@login_required
def choose_role(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        if role in {'CUSTOMER', 'SELLER'}:
            request.user.role = role
            request.user.save(update_fields=['role'])
        return redirect('dashboard')
    return render(request, 'accounts/choose_role.html')
