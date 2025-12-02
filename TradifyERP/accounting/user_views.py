"""
User management views with module permissions.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy
from django.db import transaction, models
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control

from accounting.user_permission_forms import (
    UserCreateFormWithPermissions,
    UserEditFormWithPermissions,
    BulkModulePermissionForm,
    QuickAccessTemplateForm,
    UserEntityAssignmentForm
)
from accounting.module_permissions import ModulePermission, UserModuleAccessLog
from accounting.mixins import SessionEntityMixin
from accounting.models import Entity


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure only admin users can access."""
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff
    
    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to access user management.')
        return redirect('accounting:dashboard')


class UserListView(AdminRequiredMixin, SessionEntityMixin, ListView):
    """List users with their module permissions filtered by entity."""
    model = User
    template_name = 'accounting/user_management/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    @method_decorator(cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self):
        # Get entity from session
        entity_id = self.request.session.get('selected_entity_id')
        
        # Filter users by entity through UserEntity
        from accounting.models import UserEntity
        user_ids = UserEntity.objects.filter(
            entity_id=entity_id
        ).values_list('user_id', flat=True)
        
        queryset = User.objects.filter(id__in=user_ids).order_by('-date_joined')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(username__icontains=search) |
                models.Q(email__icontains=search) |
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get entity from session
        entity_id = self.request.session.get('selected_entity_id')
        from accounting.models import UserEntity
        
        # Get filtered user IDs for current entity
        user_ids = UserEntity.objects.filter(
            entity_id=entity_id
        ).values_list('user_id', flat=True)
        
        entity_users = User.objects.filter(id__in=user_ids)
        
        # Add module permission counts for each user
        for user in context['users']:
            user.permission_count = ModulePermission.objects.filter(
                user=user,
                is_active=True
            ).count()
            user.module_list = ModulePermission.objects.filter(
                user=user,
                is_active=True,
                can_view=True
            ).values_list('module', flat=True)
        
        # Count users for current entity only
        context['total_users'] = entity_users.count()
        context['active_users'] = entity_users.filter(is_active=True).count()
        
        return context


class UserCreateView(AdminRequiredMixin, CreateView):
    """Create a new user with module permissions."""
    model = User
    form_class = UserCreateFormWithPermissions
    template_name = 'accounting/user_management/user_create.html'
    success_url = reverse_lazy('accounting:user_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add permission form
        if self.request.POST:
            context['permission_form'] = BulkModulePermissionForm(self.request.POST)
            context['template_form'] = QuickAccessTemplateForm(self.request.POST)
        else:
            context['permission_form'] = BulkModulePermissionForm()
            context['template_form'] = QuickAccessTemplateForm()
        
        # Add module list for display
        context['modules'] = ModulePermission.MODULE_CHOICES
        
        return context
    
    @transaction.atomic
    def form_valid(self, form):
        from django.contrib.auth.models import Permission
        from accounting.models import UserEntity
        
        # Create user
        user = form.save()
        
        # Grant all Django admin permissions if user is staff but not superuser
        if user.is_staff and not user.is_superuser:
            all_permissions = Permission.objects.all()
            user.user_permissions.set(all_permissions)
        
        # Assign user to current entity
        entity_id = self.request.session.get('selected_entity_id')
        if entity_id:
            UserEntity.objects.get_or_create(
                user=user,
                entity_id=entity_id,
                defaults={'is_default': True}
            )
        
        # Get permission form
        permission_form = BulkModulePermissionForm(self.request.POST, user=user)
        
        if permission_form.is_valid():
            # Save permissions
            permission_form.save_permissions(user, granted_by=self.request.user)
            
            messages.success(
                self.request,
                f'User "{user.username}" created successfully with module permissions and admin access.'
            )
        else:
            messages.warning(
                self.request,
                f'User "{user.username}" created but there were issues saving permissions.'
            )
        
        return redirect(self.success_url)


class UserEditView(AdminRequiredMixin, UpdateView):
    """Edit user information and module permissions."""
    model = User
    form_class = UserEditFormWithPermissions
    template_name = 'accounting/user_management/user_edit.html'
    success_url = reverse_lazy('accounting:user_list')
    context_object_name = 'edited_user'
    
    @method_decorator(cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add permission form with existing permissions
        if self.request.POST:
            context['permission_form'] = BulkModulePermissionForm(
                self.request.POST,
                user=self.object
            )
            context['entity_form'] = UserEntityAssignmentForm(
                self.request.POST,
                user=self.object
            )
            context['template_form'] = QuickAccessTemplateForm(self.request.POST)
        else:
            context['permission_form'] = BulkModulePermissionForm(user=self.object)
            context['entity_form'] = UserEntityAssignmentForm(user=self.object)
            context['template_form'] = QuickAccessTemplateForm()
        
        # Add module list for display
        context['modules'] = ModulePermission.MODULE_CHOICES
        
        # Get existing permissions
        context['existing_permissions'] = ModulePermission.objects.filter(
            user=self.object,
            is_active=True
        )
        
        return context
    
    @transaction.atomic
    def form_valid(self, form):
        from django.contrib.auth.models import Permission
        import logging
        logger = logging.getLogger('django')
        
        try:
            # Update user
            user = form.save()
            logger.info(f"UserEditView: Saved user {user.username}")
            
            # Grant all Django admin permissions if user is staff but not superuser
            if user.is_staff and not user.is_superuser:
                all_permissions = Permission.objects.all()
                user.user_permissions.set(all_permissions)
            
            # Get permission form
            permission_form = BulkModulePermissionForm(self.request.POST, user=user)
            
            if permission_form.is_valid():
                logger.info(f"Permission form valid for {user.username}")
                # Save permissions
                permission_form.save_permissions(user, granted_by=self.request.user)
                logger.info(f"Permissions saved for {user.username}")
                
                messages.success(
                    self.request,
                    f'User "{user.username}" updated successfully with module permissions and admin access.'
                )
            else:
                logger.error(f"Permission form invalid: {permission_form.errors}")
                messages.warning(
                    self.request,
                    f'User "{user.username}" updated but there were issues saving permissions: {permission_form.errors}'
                )
            
            # Get entity assignment form
            entity_form = UserEntityAssignmentForm(self.request.POST, user=user)
            if entity_form.is_valid():
                entity_form.save(user=user, granted_by=self.request.user)
                messages.success(
                    self.request,
                    f'Entity assignments updated for "{user.username}".'
                )
            else:
                # Log entity form errors but don't prevent saving
                logger.warning(f"Entity form had validation errors (non-blocking): {entity_form.errors}")
                # Show warning to user about entity assignments, but permissions should still save
                if entity_form.errors.get('entities'):
                    messages.info(
                        self.request,
                        f'Note: Entity assignments were not changed. Please select at least one entity to update assignments.'
                    )
            
            return redirect(self.success_url)
        except Exception as e:
            logger.exception(f"Error in UserEditView.form_valid: {str(e)}")
            messages.error(
                self.request,
                f'An error occurred while updating user: {str(e)}'
            )
            return redirect(self.success_url)


class UserDetailView(AdminRequiredMixin, DetailView):
    """View user details and permissions."""
    model = User
    template_name = 'accounting/user_management/user_detail.html'
    context_object_name = 'viewed_user'
    
    @method_decorator(cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user permissions
        context['permissions'] = ModulePermission.objects.filter(
            user=self.object,
            is_active=True
        ).order_by('module')
        
        # Get access logs
        context['recent_access_logs'] = UserModuleAccessLog.objects.filter(
            user=self.object
        ).order_by('-timestamp')[:20]
        
        # Module access summary
        context['modules_with_access'] = []
        for perm in context['permissions']:
            context['modules_with_access'].append({
                'module': perm.get_module_display(),
                'permissions': perm.permission_summary,
                'access_level': perm.access_level or 'Custom',
            })
        
        return context


class UserApplyTemplateView(AdminRequiredMixin, UpdateView):
    """Apply a permission template to a user."""
    model = User
    fields = []
    template_name = 'accounting/user_management/user_apply_template.html'
    success_url = reverse_lazy('accounting:user_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['template_form'] = QuickAccessTemplateForm()
        return context
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        template_form = QuickAccessTemplateForm(request.POST)
        
        if template_form.is_valid():
            template = template_form.cleaned_data.get('template')
            
            if template and template != 'custom':
                # Apply template
                QuickAccessTemplateForm.apply_template(
                    self.object,
                    template,
                    granted_by=request.user
                )
                
                messages.success(
                    request,
                    f'Permission template applied successfully to "{self.object.username}".'
                )
            else:
                messages.info(request, 'No template selected.')
        
        return redirect(self.success_url)


class UserToggleStatusView(AdminRequiredMixin, UpdateView):
    """Toggle user active status."""
    model = User
    fields = []
    
    def post(self, request, *args, **kwargs):
        user = self.get_object()
        
        # Prevent deactivating yourself
        if user == request.user:
            messages.error(request, 'You cannot deactivate your own account.')
            return redirect('accounting:user_list')
        
        # Toggle status
        user.is_active = not user.is_active
        user.save()
        
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User "{user.username}" has been {status}.')
        
        return redirect('accounting:user_list')
