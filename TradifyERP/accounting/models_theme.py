"""
Theme management models for TradifyERP.
Allows users to switch between different themes while maintaining all module functionality.
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Theme(models.Model):
    """Available themes in the system"""
    THEME_CHOICES = [
        ('minia', 'Minia - Dark Professional'),
        ('starterkit', 'Starter Kit - Light Clean'),
    ]
    
    name = models.CharField(
        max_length=50, 
        choices=THEME_CHOICES,
        unique=True,
        help_text="Unique identifier for the theme"
    )
    display_name = models.CharField(
        max_length=100,
        help_text="Display name shown to users"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the theme"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether theme is available for selection"
    )
    thumbnail_url = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL to theme thumbnail image"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'theme'
        verbose_name = 'Theme'
        verbose_name_plural = 'Themes'
        ordering = ['name']

    def __str__(self):
        return self.display_name

    def get_static_path(self):
        """Get the base static path for this theme"""
        return f'themes/{self.name}/'


class UserThemePreference(models.Model):
    """
    Store user's theme preference.
    When a user changes theme, this preference is saved.
    All modules will load with the selected theme.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='theme_preference',
        help_text="User who has this preference"
    )
    theme = models.ForeignKey(
        Theme,
        on_delete=models.PROTECT,
        default='minia',
        help_text="Currently selected theme"
    )
    sidebar_color = models.CharField(
        max_length=50,
        default='light',
        choices=[
            ('light', 'Light Sidebar'),
            ('dark', 'Dark Sidebar'),
        ],
        help_text="Sidebar color preference"
    )
    layout_mode = models.CharField(
        max_length=50,
        default='vertical',
        choices=[
            ('vertical', 'Vertical Layout'),
            ('horizontal', 'Horizontal Layout'),
        ],
        help_text="Page layout mode"
    )
    layout_size = models.CharField(
        max_length=50,
        default='fluid',
        choices=[
            ('fluid', 'Fluid Width'),
            ('boxed', 'Boxed Width'),
        ],
        help_text="Container width mode"
    )
    # Chart color preferences
    chart_color_1 = models.CharField(
        max_length=20,
        default='rgba(54, 162, 235, 0.8)',
        help_text="Chart color for dataset 1 (Target Investment)"
    )
    chart_color_2 = models.CharField(
        max_length=20,
        default='rgba(255, 159, 64, 0.8)',
        help_text="Chart color for dataset 2 (Invested Amount)"
    )
    chart_color_3 = models.CharField(
        max_length=20,
        default='rgba(153, 102, 255, 0.8)',
        help_text="Chart color for dataset 3 (Balance to Invest)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_theme_preference'
        verbose_name = 'User Theme Preference'
        verbose_name_plural = 'User Theme Preferences'

    def __str__(self):
        return f"{self.user.username} - {self.theme.display_name}"

    @staticmethod
    def get_or_create_for_user(user):
        """Get or create theme preference for a user"""
        pref, created = UserThemePreference.objects.get_or_create(
            user=user,
            defaults={
                'theme_id': Theme.objects.filter(name='minia').first().id or 1
            }
        )
        return pref


@receiver(post_save, sender=User)
def create_or_update_user_theme_preference(sender, instance, created, **kwargs):
    """
    Signal: Automatically create theme preference when user is created.
    Ensures every user has a theme preference.
    """
    if created:
        default_theme = Theme.objects.filter(name='minia').first()
        if default_theme:
            UserThemePreference.objects.get_or_create(
                user=instance,
                defaults={'theme': default_theme}
            )
