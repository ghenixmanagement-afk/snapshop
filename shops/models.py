from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from datetime import time
from accounts.models import CustomUser

class Shop(models.Model):
    CITY_CHOICES = [
        ('Douala', 'Douala'),
        ('Yaounde', 'Yaounde'),
        ('Bafoussam', 'Bafoussam'),
        ('Bamenda', 'Bamenda'),
        ('Garoua', 'Garoua'),
        ('Maroua', 'Maroua'),
        ('Ngaoundere', 'Ngaoundere'),
        ('Buea', 'Buea'),
        ('Limbe', 'Limbe'),
        ('Kribi', 'Kribi'),
    ]
    THEME_CHOICES = [
        ('elegant', 'Élégant Noir'),
        ('vif', 'Vif Orange'),
        ('nature', 'Nature Vert'),
        ('modern', 'Moderne Bleu'),
        ('classic', 'Classique Blanc'),
    ]
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('REJECTED', 'Rejected'),
    ]
    owner = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='shop')
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    city = models.CharField(max_length=40, choices=CITY_CHOICES, blank=True)
    location = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    logo = models.ImageField(upload_to='shops/logos/', blank=True, null=True, help_text="Logo ou image de profil de la boutique")
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='elegant')
    custom_theme_color = models.CharField(max_length=7, default='#1B3320', help_text="Couleur de signature (ex: #1B3320)")
    facebook = models.CharField(max_length=200, blank=True, help_text="Lien Facebook ou nom de page")
    instagram = models.CharField(max_length=200, blank=True, help_text="Lien Instagram ou nom d'utilisateur")
    
    # Horaires d'ouverture par jour
    opening_time_monday = models.TimeField(null=True, blank=True, help_text="Heure d'ouverture")
    closing_time_monday = models.TimeField(null=True, blank=True, help_text="Heure de fermeture")
    is_closed_monday = models.BooleanField(default=False, help_text="Fermé ce jour")
    
    opening_time_tuesday = models.TimeField(null=True, blank=True)
    closing_time_tuesday = models.TimeField(null=True, blank=True)
    is_closed_tuesday = models.BooleanField(default=False)
    
    opening_time_wednesday = models.TimeField(null=True, blank=True)
    closing_time_wednesday = models.TimeField(null=True, blank=True)
    is_closed_wednesday = models.BooleanField(default=False)
    
    opening_time_thursday = models.TimeField(null=True, blank=True)
    closing_time_thursday = models.TimeField(null=True, blank=True)
    is_closed_thursday = models.BooleanField(default=False)
    
    opening_time_friday = models.TimeField(null=True, blank=True)
    closing_time_friday = models.TimeField(null=True, blank=True)
    is_closed_friday = models.BooleanField(default=False)
    
    opening_time_saturday = models.TimeField(null=True, blank=True)
    closing_time_saturday = models.TimeField(null=True, blank=True)
    is_closed_saturday = models.BooleanField(default=False)
    
    opening_time_sunday = models.TimeField(null=True, blank=True)
    closing_time_sunday = models.TimeField(null=True, blank=True)
    is_closed_sunday = models.BooleanField(default=False)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    rejection_reason = models.TextField(blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            candidate = base_slug
            index = 1
            while Shop.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f'{base_slug}-{index}'
                index += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def get_today_hours(self):
        """Retourne les heures du jour actuel (ouverture, fermeture, fermé)"""
        now = timezone.now()
        day_of_week = now.weekday()  # 0=lundi, 6=dimanche
        
        days = {
            0: ('monday', self.opening_time_monday, self.closing_time_monday, self.is_closed_monday),
            1: ('tuesday', self.opening_time_tuesday, self.closing_time_tuesday, self.is_closed_tuesday),
            2: ('wednesday', self.opening_time_wednesday, self.closing_time_wednesday, self.is_closed_wednesday),
            3: ('thursday', self.opening_time_thursday, self.closing_time_thursday, self.is_closed_thursday),
            4: ('friday', self.opening_time_friday, self.closing_time_friday, self.is_closed_friday),
            5: ('saturday', self.opening_time_saturday, self.closing_time_saturday, self.is_closed_saturday),
            6: ('sunday', self.opening_time_sunday, self.closing_time_sunday, self.is_closed_sunday),
        }
        
        day_name, opening, closing, is_closed = days.get(day_of_week, ('', None, None, True))
        return {
            'day': day_name,
            'opening_time': opening,
            'closing_time': closing,
            'is_closed': is_closed,
        }

    def is_currently_open(self):
        """Retourne True si la boutique est actuellement ouverte"""
        today = self.get_today_hours()
        
        if today['is_closed']:
            return False
        
        if not today['opening_time'] or not today['closing_time']:
            return False
        
        now = timezone.now().time()
        return today['opening_time'] <= now <= today['closing_time']

    def get_status_display_text(self):
        """Retourne le texte du statut d'ouverture"""
        today = self.get_today_hours()
        
        if today['is_closed']:
            return 'Fermé aujourd\'hui'
        
        if not today['opening_time'] or not today['closing_time']:
            return 'Horaires non configurés'
        
        if self.is_currently_open():
            return f'Ouvert (ferme à {today["closing_time"].strftime("%H:%M")})'
        else:
            now = timezone.now().time()
            if now < today['opening_time']:
                return f'Fermé (ouvre à {today["opening_time"].strftime("%H:%M")})'
            else:
                return 'Fermé (reouvert demain)'

    def __str__(self):
        return self.name


class ModerationLog(models.Model):
    ACTION_APPROVE = 'approve'
    ACTION_REJECT = 'reject'
    ACTION_CHOICES = [
        (ACTION_APPROVE, 'Approuvé'),
        (ACTION_REJECT, 'Rejeté'),
    ]

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='moderation_logs')
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moderation_actions',
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.action} {self.shop.name}'
