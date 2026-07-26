from django import forms
from django.core.exceptions import ValidationError

from .branding import ALLOWED_LOGO_TYPES, MAX_LOGO_BYTES, normalize_hex
from .models import Shop

_INPUT = (
    'w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-slate-900 '
    'placeholder:text-slate-400 shadow-sm transition '
    'focus:border-orange-500 focus:outline-none focus:ring-2 focus:ring-orange-500/25'
)
_TEXTAREA = (
    'w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-slate-900 '
    'placeholder:text-slate-400 shadow-sm transition resize-vertical '
    'focus:border-orange-500 focus:outline-none focus:ring-2 focus:ring-orange-500/25'
)
_SELECT = (
    'w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-slate-900 '
    'shadow-sm transition focus:border-orange-500 focus:outline-none focus:ring-2 focus:ring-orange-500/25'
)


class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = [
            'name', 
            'description', 
            'logo',
            'city', 
            'location', 
            'phone', 
            'whatsapp_number', 
            'theme',
            'custom_theme_color',
            'facebook',
            'instagram',
            # Horaires
            'opening_time_monday', 'closing_time_monday', 'is_closed_monday',
            'opening_time_tuesday', 'closing_time_tuesday', 'is_closed_tuesday',
            'opening_time_wednesday', 'closing_time_wednesday', 'is_closed_wednesday',
            'opening_time_thursday', 'closing_time_thursday', 'is_closed_thursday',
            'opening_time_friday', 'closing_time_friday', 'is_closed_friday',
            'opening_time_saturday', 'closing_time_saturday', 'is_closed_saturday',
            'opening_time_sunday', 'closing_time_sunday', 'is_closed_sunday',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Ex: Mon Super Marché'}),
            'description': forms.Textarea(attrs={'class': _TEXTAREA, 'rows': 4, 'placeholder': 'Décrivez votre boutique, vos produits, votre style...'}),
            'logo': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3',
                'accept': 'image/png,image/jpeg,image/jpg,image/webp',
            }),
            'city': forms.Select(attrs={'class': _SELECT}),
            'location': forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Ex: Zone Faux-Pas, Douala'}),
            'phone': forms.TextInput(attrs={'class': _INPUT, 'type': 'tel', 'placeholder': '+237 6 XX XXX XXX'}),
            'whatsapp_number': forms.TextInput(attrs={'class': _INPUT, 'type': 'tel', 'placeholder': '+237612345678 (format international)'}),
            'theme': forms.Select(attrs={'class': _SELECT}),
            'custom_theme_color': forms.TextInput(attrs={'class': 'w-full rounded-xl border border-slate-200 h-12 cursor-pointer', 'type': 'color', 'title': 'Choisir une couleur'}),
            'facebook': forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'https://facebook.com/votreentreprise'}),
            'facebook_followers': forms.NumberInput(attrs={'class': _INPUT, 'min': '0', 'placeholder': '0'}),
            'instagram': forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'https://instagram.com/votreentreprise'}),
            # Horaires widgets
            'opening_time_monday': forms.TimeInput(attrs={'class': _INPUT, 'type': 'time'}),
            'closing_time_monday': forms.TimeInput(attrs={'class': _INPUT, 'type': 'time'}),
            'is_closed_monday': forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded border-slate-300 text-orange-600 focus:ring-orange-500'}),
            'opening_time_tuesday': forms.TimeInput(attrs={'class': _INPUT, 'type': 'time'}),
            'closing_time_tuesday': forms.TimeInput(attrs={'class': _INPUT, 'type': 'time'}),
            'is_closed_tuesday': forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded border-slate-300 text-orange-600 focus:ring-orange-500'}),
            'opening_time_wednesday': forms.TimeInput(attrs={'class': _INPUT, 'type': 'time'}),
            'closing_time_wednesday': forms.TimeInput(attrs={'class': _INPUT, 'type': 'time'}),
            'is_closed_wednesday': forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded border-slate-300 text-orange-600 focus:ring-orange-500'}),
            'opening_time_thursday': forms.TimeInput(attrs={'class': _INPUT, 'type': 'time'}),
            'closing_time_thursday': forms.TimeInput(attrs={'class': _INPUT, 'type': 'time'}),
            'is_closed_thursday': forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded border-slate-300 text-orange-600 focus:ring-orange-500'}),
            'opening_time_friday': forms.TimeInput(attrs={'class': _INPUT, 'type': 'time'}),
            'closing_time_friday': forms.TimeInput(attrs={'class': _INPUT, 'type': 'time'}),
            'is_closed_friday': forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded border-slate-300 text-orange-600 focus:ring-orange-500'}),
            'opening_time_saturday': forms.TimeInput(attrs={'class': _INPUT, 'type': 'time'}),
            'closing_time_saturday': forms.TimeInput(attrs={'class': _INPUT, 'type': 'time'}),
            'is_closed_saturday': forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded border-slate-300 text-orange-600 focus:ring-orange-500'}),
            'opening_time_sunday': forms.TimeInput(attrs={'class': _INPUT, 'type': 'time'}),
            'closing_time_sunday': forms.TimeInput(attrs={'class': _INPUT, 'type': 'time'}),
            'is_closed_sunday': forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded border-slate-300 text-orange-600 focus:ring-orange-500'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajouter des labels explicatifs
        self.fields['name'].label = 'Nom de la boutique'
        self.fields['name'].help_text = 'Votre identité commerciale'
        self.fields['description'].label = 'Description'
        self.fields['description'].help_text = 'Présentez votre boutique, vos services, votre univers'
        self.fields['logo'].label = 'Logo ou image de profil'
        self.fields['logo'].help_text = 'Image carrée de préférence (PNG, JPG, max 5MB)'
        self.fields['city'].label = 'Ville'
        self.fields['location'].label = 'Adresse / Localisation'
        self.fields['location'].help_text = 'Quartier, rue ou point de repère'
        self.fields['phone'].label = 'Téléphone'
        self.fields['phone'].help_text = 'Format: +237 6 XX XXX XXX'
        self.fields['whatsapp_number'].label = 'Numéro WhatsApp'
        self.fields['whatsapp_number'].help_text = 'Format international avec indicatif pays (+237...)'
        self.fields['theme'].label = 'Thème de la boutique'
        self.fields['theme'].help_text = 'Style visuel de votre vitrine publique'
        self.fields['custom_theme_color'].label = 'Couleur de signature'
        self.fields['custom_theme_color'].help_text = 'Couleur personnalisée de votre marque'
        self.fields['facebook'].label = 'Lien Facebook'
        self.fields['facebook'].help_text = 'URL complète de votre page/profil Facebook'
        self.fields['instagram'].label = 'Lien Instagram'
        self.fields['instagram'].help_text = 'URL complète de votre profil Instagram'
        
        # Horaires
        days_fr = {
            'monday': 'Lundi',
            'tuesday': 'Mardi',
            'wednesday': 'Mercredi',
            'thursday': 'Jeudi',
            'friday': 'Vendredi',
            'saturday': 'Samedi',
            'sunday': 'Dimanche',
        }
        
        for day_en, day_fr in days_fr.items():
            opening_field = f'opening_time_{day_en}'
            closing_field = f'closing_time_{day_en}'
            is_closed_field = f'is_closed_{day_en}'
            
            if opening_field in self.fields:
                self.fields[opening_field].label = f'{day_fr} - Ouverture'
                self.fields[opening_field].required = False
            if closing_field in self.fields:
                self.fields[closing_field].label = f'{day_fr} - Fermeture'
                self.fields[closing_field].required = False
            if is_closed_field in self.fields:
                self.fields[is_closed_field].label = f'{day_fr} - Fermé'
                self.fields[is_closed_field].required = False

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if not logo:
            return logo
        if logo.size > MAX_LOGO_BYTES:
            raise ValidationError('Le logo ne doit pas dépasser 5 Mo.')
        content_type = getattr(logo, 'content_type', '') or ''
        if content_type and content_type not in ALLOWED_LOGO_TYPES:
            raise ValidationError('Format accepté : PNG ou JPG (max 5 Mo).')
        name = (getattr(logo, 'name', '') or '').lower()
        if name and not name.endswith(('.png', '.jpg', '.jpeg', '.webp')):
            raise ValidationError('Format accepté : PNG ou JPG (max 5 Mo).')
        return logo

    def clean_custom_theme_color(self):
        color = self.cleaned_data.get('custom_theme_color')
        return normalize_hex(color or '#1B3320')
