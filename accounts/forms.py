from django import forms
from django.contrib.auth.forms import UserCreationForm
from allauth.account.forms import LoginForm as AllauthLoginForm
from allauth.account.forms import ResetPasswordForm as AllauthResetPasswordForm
from allauth.account.forms import ResetPasswordKeyForm as AllauthResetPasswordKeyForm

from .models import CustomUser

_INPUT = (
    'w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-slate-900 '
    'placeholder:text-slate-400 shadow-sm transition '
    'focus:border-orange-500 focus:outline-none focus:ring-2 focus:ring-orange-500/25'
)


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='E-mail',
        widget=forms.EmailInput(
            attrs={'class': _INPUT, 'placeholder': 'vous@exemple.com', 'autocomplete': 'email'}
        ),
    )
    first_name = forms.CharField(
        label='Prénom',
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={'class': _INPUT, 'placeholder': 'Prénom', 'autocomplete': 'given-name'}
        ),
    )
    last_name = forms.CharField(
        label='Nom',
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={'class': _INPUT, 'placeholder': 'Nom', 'autocomplete': 'family-name'}
        ),
    )
    username = forms.CharField(
        label='Pseudo',
        max_length=150,
        required=False,
        help_text='Optionnel. Sinon un identifiant est dérivé de votre e-mail.',
        widget=forms.TextInput(
            attrs={'class': _INPUT, 'placeholder': 'Ex. afrique_style', 'autocomplete': 'username'}
        ),
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'gender', 'email', 'username', 'password1', 'password2', 'role']
        widgets = {
            'gender': forms.Select(
                attrs={'class': _INPUT, 'autocomplete': 'sex'},
            ),
            'role': forms.Select(attrs={'class': _INPUT}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gender'].required = False
        self.fields['gender'].label = 'Sexe'
        self.fields['gender'].choices = [
            ('', '— Non précisé —'),
            ('M', 'Homme'),
            ('F', 'Femme'),
            ('O', 'Autre'),
        ]
        self.fields['role'].label = 'Vous inscrivez-vous comme'
        self.fields['role'].choices = [
            ('CUSTOMER', 'Client — parcourir, favoris, WhatsApp'),
            ('SELLER', 'Vendeur — créer et gérer ma boutique'),
        ]
        self.fields['role'].initial = 'CUSTOMER'
        for name in ('password1', 'password2'):
            self.fields[name].widget.attrs.update(
                {
                    'class': _INPUT,
                    'autocomplete': 'new-password' if name == 'password1' else 'new-password',
                }
            )
        self.fields['password1'].label = 'Mot de passe'
        self.fields['password2'].label = 'Confirmer le mot de passe'
        self.fields['password1'].help_text = (
            'Minimum recommandé : 8 caractères. Évitez un mot de passe trop simple.'
        )
        self.fields['password2'].help_text = ''

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if role not in ('CUSTOMER', 'SELLER'):
            raise forms.ValidationError('Profil invalide.')
        return role

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if username:
            return username
        email = self.cleaned_data.get('email', '')
        base = email.split('@')[0] if email else 'user'
        candidate = base
        i = 1
        while CustomUser.objects.filter(username=candidate).exists():
            candidate = f'{base}{i}'
            i += 1
        return candidate


class SnapShopLoginForm(AllauthLoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'login' in self.fields:
            self.fields['login'].label = 'E-mail'
            self.fields['login'].widget.attrs.update(
                {'class': _INPUT, 'placeholder': 'vous@exemple.com', 'autocomplete': 'email'}
            )
        if 'password' in self.fields:
            self.fields['password'].label = 'Mot de passe'
            self.fields['password'].widget.attrs.update(
                {'class': _INPUT, 'placeholder': '••••••••', 'autocomplete': 'current-password'}
            )
        if 'remember' in self.fields:
            self.fields['remember'].label = 'Rester connecté sur cet appareil'
            self.fields['remember'].widget.attrs.setdefault(
                'class',
                'h-4 w-4 rounded border-slate-300 text-orange-600 focus:ring-orange-500',
            )


class SnapShopResetPasswordForm(AllauthResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'email' in self.fields:
            self.fields['email'].label = 'E-mail'
            self.fields['email'].widget.attrs.update(
                {'class': _INPUT, 'placeholder': 'vous@exemple.com', 'autocomplete': 'email'}
            )


class SnapShopResetPasswordKeyForm(AllauthResetPasswordKeyForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password1' in self.fields:
            self.fields['password1'].label = 'Nouveau mot de passe'
            self.fields['password1'].widget.attrs.update(
                {'class': _INPUT, 'autocomplete': 'new-password'}
            )
        if 'password2' in self.fields:
            self.fields['password2'].label = 'Confirmer le mot de passe'
            self.fields['password2'].widget.attrs.update(
                {'class': _INPUT, 'autocomplete': 'new-password'}
            )
