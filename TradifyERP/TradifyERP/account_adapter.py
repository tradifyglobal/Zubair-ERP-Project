from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter
from accounting.models import UserEntity


class MyAccountAdapter(DefaultAccountAdapter):
    """Custom adapter to control where users are redirected after login.

    This keeps the rest of allauth's behavior intact (including email
    verification), but ensures the login redirect goes to
    `settings.LOGIN_REDIRECT_URL` (set to `/dashboard/` in settings.py).
    
    Also auto-selects the user's default entity on login to skip entity selection.
    """

    def get_login_redirect_url(self, request):
        # Try to set default entity from UserEntity
        if request.user.is_authenticated:
            # Get user's default entity
            user_entity = UserEntity.objects.filter(
                user=request.user,
                entity__is_active=True,
                is_default=True
            ).first()
            
            if user_entity:
                # Set session with default entity
                request.session['selected_entity_id'] = user_entity.entity.id
                request.session['selected_entity_code'] = user_entity.entity.code
                request.session['selected_entity_name'] = user_entity.entity.name
                request.session.modified = True
        
        return getattr(settings, 'LOGIN_REDIRECT_URL', '/')
