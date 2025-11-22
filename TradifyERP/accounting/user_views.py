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

from accounting.user_permission_forms import (
    UserCreateFormWithPermissions,
    UserEditFormWithPermissions,
    BulkModulePermissionForm,
    QuickAccessTemplateForm
)
from accounting.module_permissions import ModulePermission, UserModuleAccessLog


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure only admin users can access."""
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff
    
    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to access user management.')
        return redirect('accounting:dashboard')


class UserListView(AdminRequiredMixin, ListView):
    """List all users with their module permissions."""
    model = User
    template_name = 'accounting/user_management/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = User.objects.all().order_by('-date_joined')
        
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
        
        context['total_users'] = User.objects.count()
        context['active_users'] = User.objects.filter(is_active=True).count()
        
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
        
        # Create user
        user = form.save()
        
        # Grant all Django admin permissions if user is staff but not superuser
        if user.is_staff and not user.is_superuser:
            all_permissions = Permission.objects.all()
            user.user_permissions.set(all_permissions)
        
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add permission form with existing permissions
        if self.request.POST:
            context['permission_form'] = BulkModulePermissionForm(
                self.request.POST,
                user=self.object
            )
            context['template_form'] = QuickAccessTemplateForm(self.request.POST)
        else:
            context['permission_form'] = BulkModulePermissionForm(user=self.object)
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
        
        # Update user
        user = form.save()
        
        # Grant all Django admin permissions if user is staff but not superuser
        if user.is_staff and not user.is_superuser:
            all_permissions = Permission.objects.all()
            user.user_permissions.set(all_permissions)
        
        # Get permission form
        permission_form = BulkModulePermissionForm(self.request.POST, user=user)
        
        if permission_form.is_valid():
            # Save permissions
            permission_form.save_permissions(user, granted_by=self.request.user)
            
            messages.success(
                self.request,
                f'User "{user.username}" updated successfully with module permissions and admin access.'
            )
        else:
            messages.warning(
                self.request,
                f'User "{user.username}" updated but there were issues saving permissions.'
            )
        
        return redirect(self.success_url)


class UserDetailView(AdminRequiredMixin, DetailView):
    """View user details and permissions."""
    model = User
    template_name = 'accounting/user_management/user_detail.html'
    context_object_name = 'viewed_user'
    
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
