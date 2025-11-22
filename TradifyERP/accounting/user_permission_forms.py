"""
Forms for user management with module permissions.
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from accounting.module_permissions import ModulePermission


class UserModulePermissionForm(forms.ModelForm):
    """Form for individual module permission."""
    
    class Meta:
        model = ModulePermission
        fields = ['module', 'can_view', 'can_add', 'can_edit', 'can_delete', 
                  'can_approve', 'can_export', 'access_level', 'notes']
        widgets = {
            'can_view': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_add': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_edit': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_delete': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_approve': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_export': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'access_level': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'e.g., Full Access, Read Only'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes...'
            }),
        }


class UserCreateFormWithPermissions(UserCreationForm):
    """Extended user creation form with basic information."""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    is_staff = forms.BooleanField(
        required=False,
        initial=True,  # Default to True so users can access admin pages
        label="Staff Status",
        help_text="Required for admin site access (recommended: keep enabled)",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        label="Active",
        help_text="User account is active",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 
                  'password1', 'password2', 'is_staff', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        # Ensure is_staff is True by default for admin access
        if not user.is_staff and not user.is_superuser:
            user.is_staff = True
        if commit:
            user.save()
        return user
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'


class UserEditFormWithPermissions(UserChangeForm):
    """Extended user edit form."""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    is_staff = forms.BooleanField(
        required=False,
        label="Staff Status",
        help_text="Required for admin site access (recommended: keep enabled)",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    is_active = forms.BooleanField(
        required=False,
        label="Active",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Remove password field from edit form
    password = None
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 
                  'is_staff', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        # Ensure is_staff is True by default for admin access
        if not user.is_staff and not user.is_superuser:
            user.is_staff = True
        if commit:
            user.save()
        return user


class BulkModulePermissionForm(forms.Form):
    """
    Form for managing all module permissions at once.
    Displays checkboxes for each module and permission type.
    """
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Get all available modules
        modules = ModulePermission.MODULE_CHOICES
        
        # Create fields for each module
        for module_code, module_name in modules:
            # Get existing permission if user is provided
            existing_perm = None
            if user:
                existing_perm = ModulePermission.objects.filter(
                    user=user,
                    module=module_code
                ).first()
            
            # Create checkbox fields for each permission type
            self.fields[f'{module_code}_can_view'] = forms.BooleanField(
                required=False,
                initial=existing_perm.can_view if existing_perm else False,
                label='View',
                widget=forms.CheckboxInput(attrs={
                    'class': 'form-check-input permission-checkbox',
                    'data-module': module_code,
                    'data-permission': 'view'
                })
            )
            
            self.fields[f'{module_code}_can_add'] = forms.BooleanField(
                required=False,
                initial=existing_perm.can_add if existing_perm else False,
                label='Add',
                widget=forms.CheckboxInput(attrs={
                    'class': 'form-check-input permission-checkbox',
                    'data-module': module_code,
                    'data-permission': 'add'
                })
            )
            
            self.fields[f'{module_code}_can_edit'] = forms.BooleanField(
                required=False,
                initial=existing_perm.can_edit if existing_perm else False,
                label='Edit',
                widget=forms.CheckboxInput(attrs={
                    'class': 'form-check-input permission-checkbox',
                    'data-module': module_code,
                    'data-permission': 'edit'
                })
            )
            
            self.fields[f'{module_code}_can_delete'] = forms.BooleanField(
                required=False,
                initial=existing_perm.can_delete if existing_perm else False,
                label='Delete',
                widget=forms.CheckboxInput(attrs={
                    'class': 'form-check-input permission-checkbox',
                    'data-module': module_code,
                    'data-permission': 'delete'
                })
            )
            
            self.fields[f'{module_code}_can_approve'] = forms.BooleanField(
                required=False,
                initial=existing_perm.can_approve if existing_perm else False,
                label='Approve',
                widget=forms.CheckboxInput(attrs={
                    'class': 'form-check-input permission-checkbox',
                    'data-module': module_code,
                    'data-permission': 'approve'
                })
            )
            
            self.fields[f'{module_code}_can_export'] = forms.BooleanField(
                required=False,
                initial=existing_perm.can_export if existing_perm else False,
                label='Export',
                widget=forms.CheckboxInput(attrs={
                    'class': 'form-check-input permission-checkbox',
                    'data-module': module_code,
                    'data-permission': 'export'
                })
            )
    
    def save_permissions(self, user, granted_by=None):
        """Save all module permissions for the user."""
        modules = ModulePermission.MODULE_CHOICES
        
        for module_code, module_name in modules:
            # Get permission values from form
            can_view = self.cleaned_data.get(f'{module_code}_can_view', False)
            can_add = self.cleaned_data.get(f'{module_code}_can_add', False)
            can_edit = self.cleaned_data.get(f'{module_code}_can_edit', False)
            can_delete = self.cleaned_data.get(f'{module_code}_can_delete', False)
            can_approve = self.cleaned_data.get(f'{module_code}_can_approve', False)
            can_export = self.cleaned_data.get(f'{module_code}_can_export', False)
            
            # Only create/update if at least one permission is granted
            if any([can_view, can_add, can_edit, can_delete, can_approve, can_export]):
                permission, created = ModulePermission.objects.update_or_create(
                    user=user,
                    module=module_code,
                    defaults={
                        'can_view': can_view,
                        'can_add': can_add,
                        'can_edit': can_edit,
                        'can_delete': can_delete,
                        'can_approve': can_approve,
                        'can_export': can_export,
                        'granted_by': granted_by,
                        'is_active': True,
                    }
                )
            else:
                # Delete permission if no access granted
                ModulePermission.objects.filter(
                    user=user,
                    module=module_code
                ).delete()


class QuickAccessTemplateForm(forms.Form):
    """Form for applying quick access templates."""
    
    TEMPLATE_CHOICES = [
        ('', '-- Select Template --'),
        ('full_admin', 'Full Administrator (All Modules)'),
        ('accounting_full', 'Accountant (Full Accounting Access)'),
        ('accounting_readonly', 'Accounting View Only'),
        ('hr_manager', 'HR Manager (HR + View Others)'),
        ('sales_manager', 'Sales Manager (Sales, CRM, Inventory View)'),
        ('inventory_manager', 'Inventory Manager (Inventory, Procurement)'),
        ('readonly_all', 'Read Only (All Modules)'),
        ('custom', 'Custom (Select Manually)'),
    ]
    
    template = forms.ChoiceField(
        choices=TEMPLATE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'permission-template'
        })
    )
    
    @staticmethod
    def apply_template(user, template_name, granted_by=None):
        """Apply a permission template to a user."""
        
        # Clear existing permissions
        ModulePermission.objects.filter(user=user).delete()
        
        modules = dict(ModulePermission.MODULE_CHOICES)
        
        if template_name == 'full_admin':
            # Full access to all modules
            for module_code in modules.keys():
                ModulePermission.grant_full_access(user, module_code, granted_by)
        
        elif template_name == 'accounting_full':
            # Full access to accounting, AP, AR, cash management
            ModulePermission.grant_full_access(user, 'accounting', granted_by)
            ModulePermission.grant_full_access(user, 'ap', granted_by)
            ModulePermission.grant_full_access(user, 'ar', granted_by)
            ModulePermission.grant_full_access(user, 'cash_management', granted_by)
            ModulePermission.grant_full_access(user, 'shareholder', granted_by)
            
            # Read-only access to other modules
            ModulePermission.grant_read_only_access(user, 'hr', granted_by)
            ModulePermission.grant_read_only_access(user, 'sales', granted_by)
            ModulePermission.grant_read_only_access(user, 'procurement', granted_by)
            ModulePermission.grant_read_only_access(user, 'inventory', granted_by)
        
        elif template_name == 'accounting_readonly':
            # View-only access to accounting modules
            ModulePermission.grant_read_only_access(user, 'accounting', granted_by)
            ModulePermission.grant_read_only_access(user, 'ap', granted_by)
            ModulePermission.grant_read_only_access(user, 'ar', granted_by)
            ModulePermission.grant_read_only_access(user, 'cash_management', granted_by)
        
        elif template_name == 'hr_manager':
            # Full access to HR
            ModulePermission.grant_full_access(user, 'hr', granted_by)
            
            # Read-only to other modules
            for module_code in ['accounting', 'projects', 'crm']:
                ModulePermission.grant_read_only_access(user, module_code, granted_by)
        
        elif template_name == 'sales_manager':
            # Full access to sales and CRM
            ModulePermission.grant_full_access(user, 'sales', granted_by)
            ModulePermission.grant_full_access(user, 'crm', granted_by)
            ModulePermission.grant_full_access(user, 'ar', granted_by)
            
            # View access to inventory and accounting
            ModulePermission.grant_read_only_access(user, 'inventory', granted_by)
            ModulePermission.grant_read_only_access(user, 'accounting', granted_by)
        
        elif template_name == 'inventory_manager':
            # Full access to inventory and procurement
            ModulePermission.grant_full_access(user, 'inventory', granted_by)
            ModulePermission.grant_full_access(user, 'procurement', granted_by)
            ModulePermission.grant_full_access(user, 'ap', granted_by)
            
            # View access to manufacturing and accounting
            ModulePermission.grant_read_only_access(user, 'manufacturing', granted_by)
            ModulePermission.grant_read_only_access(user, 'accounting', granted_by)
        
        elif template_name == 'readonly_all':
            # Read-only access to all modules
            for module_code in modules.keys():
                ModulePermission.grant_read_only_access(user, module_code, granted_by)
