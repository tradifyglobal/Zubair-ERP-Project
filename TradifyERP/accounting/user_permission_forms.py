"""
Forms for user management with module permissions.
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from accounting.module_permissions import ModulePermission
from accounting.models import Entity, UserEntity


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
    
    def clean_username(self):
        """Check username uniqueness within current entity only."""
        username = self.cleaned_data.get('username')
        entity = self.entity if hasattr(self, 'entity') else None
        
        if not username:
            return username
        
        # Check if username exists for THIS ENTITY only
        if entity:
            from accounting.models import UserEntity
            existing_in_entity = UserEntity.objects.filter(
                entity=entity,
                user__username=username
            ).exists()
            
            if existing_in_entity:
                raise forms.ValidationError(
                    f'Username "{username}" is already used by another user in {entity.name}. '
                    f'However, you can use this username in a different entity.'
                )
        
        return username
    
    def save(self, commit=True):
        user = super().save(commit=False)
        # Ensure is_staff is True by default for admin access
        if not user.is_staff and not user.is_superuser:
            user.is_staff = True
        if commit:
            user.save()
        return user
    
    def __init__(self, *args, entity=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity = entity
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
    
    def clean_username(self):
        """Check username uniqueness within current entity only (excluding self)."""
        username = self.cleaned_data.get('username')
        entity = self.entity if hasattr(self, 'entity') else None
        
        if not username:
            return username
        
        # Check if username exists for THIS ENTITY only (excluding the current user)
        if entity:
            from accounting.models import UserEntity
            existing_in_entity = UserEntity.objects.filter(
                entity=entity,
                user__username=username
            ).exclude(user=self.instance).exists()
            
            if existing_in_entity:
                raise forms.ValidationError(
                    f'Username "{username}" is already used by another user in {entity.name}. '
                    f'However, you can use this username in a different entity.'
                )
        
        return username
    
    def __init__(self, *args, entity=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity = entity


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
            
            self.fields[f'{module_code}_can_review'] = forms.BooleanField(
                required=False,
                initial=existing_perm.can_review if existing_perm else False,
                label='Review',
                widget=forms.CheckboxInput(attrs={
                    'class': 'form-check-input permission-checkbox',
                    'data-module': module_code,
                    'data-permission': 'review'
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
            can_review = self.cleaned_data.get(f'{module_code}_can_review', False)
            can_approve = self.cleaned_data.get(f'{module_code}_can_approve', False)
            can_export = self.cleaned_data.get(f'{module_code}_can_export', False)
            
            # Only create/update if at least one permission is granted
            if any([can_view, can_add, can_edit, can_delete, can_review, can_approve, can_export]):
                permission, created = ModulePermission.objects.update_or_create(
                    user=user,
                    module=module_code,
                    defaults={
                        'can_view': can_view,
                        'can_add': can_add,
                        'can_edit': can_edit,
                        'can_delete': can_delete,
                        'can_review': can_review,
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


class UserEntityAssignmentForm(forms.Form):
    """Form for assigning entities to users."""
    
    entities = forms.ModelMultipleChoiceField(
        queryset=Entity.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input entity-checkbox',
        }),
        label="Assigned Entities",
        help_text="Select which entities this user can access",
        required=False  # Make optional so permission saves even if no entity selected
    )
    
    default_entity = forms.ModelChoiceField(
        queryset=Entity.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label="Default Entity",
        help_text="The entity the user will see on login",
        required=False
    )
    
    can_switch_entities = forms.BooleanField(
        required=False,
        initial=True,
        label="Allow Entity Switching",
        help_text="User can switch between assigned entities",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.user = user
        
        # Set initial values if user is provided
        if user:
            assigned_entities = user.entity_assignments.values_list('entity_id', flat=True)
            self.fields['entities'].initial = assigned_entities
            
            default_entity = user.entity_assignments.filter(is_default=True).first()
            if default_entity:
                self.fields['default_entity'].initial = default_entity.entity_id
            
            can_switch = user.entity_assignments.filter(can_switch=True).exists()
            self.fields['can_switch_entities'].initial = can_switch
    
    def clean(self):
        """Validate that if default_entity is set, it must be in selected entities."""
        cleaned_data = super().clean()
        selected_entities = cleaned_data.get('entities', [])
        default_entity = cleaned_data.get('default_entity')
        
        # If default_entity is set but not in selected_entities, add it
        if default_entity and selected_entities and default_entity not in selected_entities:
            # Add the default entity to selected entities
            selected_entities = list(selected_entities) + [default_entity]
            cleaned_data['entities'] = selected_entities
        
        return cleaned_data
    
    def save(self, user=None, granted_by=None):
        """Save entity assignments for user."""
        target_user = user or self.user
        if not target_user:
            return
        
        selected_entities = self.cleaned_data.get('entities', [])
        default_entity = self.cleaned_data.get('default_entity')
        can_switch = self.cleaned_data.get('can_switch_entities', True)
        
        # Only update if entities are actually selected
        if selected_entities:
            # Remove all existing assignments
            UserEntity.objects.filter(user=target_user).delete()
            
            # Create new assignments
            for entity in selected_entities:
                is_default = (entity == default_entity) if default_entity else False
                UserEntity.objects.create(
                    user=target_user,
                    entity=entity,
                    is_default=is_default,
                    can_switch=can_switch,
                    assigned_by=granted_by
                )


class UserChangePasswordForm(forms.Form):
    """Form for users to change their own password."""
    
    current_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your current password'
        })
    )
    
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'
        }),
        help_text='Password must be at least 8 characters long and contain a mix of letters, numbers, and special characters.'
    )
    
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
    
    def clean_current_password(self):
        """Validate that current password is correct."""
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError('Current password is incorrect.')
        return current_password
    
    def clean_new_password2(self):
        """Validate that new passwords match and are different from current."""
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')
        
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError('New passwords do not match.')
            
            # Check if new password is different from current
            if self.user.check_password(new_password1):
                raise forms.ValidationError('New password must be different from your current password.')
        
        return new_password2
    
    def save(self):
        """Set the new password."""
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        self.user.save()
        return self.user


class UserResetPasswordForm(forms.Form):
    """Form for admins to reset a user's password."""
    
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'
        }),
        help_text='Leave blank to generate a random password.',
        required=False
    )
    
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        }),
        required=False
    )
    
    send_email = forms.BooleanField(
        label='Send new password to user email',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
    
    def clean(self):
        """Validate password fields."""
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        # If passwords are provided, they must match
        if new_password1 or new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError('Passwords do not match.')
            if len(new_password1) < 8:
                raise forms.ValidationError('Password must be at least 8 characters long.')
        
        return cleaned_data
    
    def save(self):
        """Set the new password or generate random one."""
        import secrets
        import string
        
        new_password = self.cleaned_data.get('new_password1')
        
        # Generate random password if not provided
        if not new_password:
            alphabet = string.ascii_letters + string.digits + string.punctuation.replace('"', '').replace("'", '')
            new_password = ''.join(secrets.choice(alphabet) for _ in range(16))
        
        self.user.set_password(new_password)
        self.user.save()
        
        return self.user, new_password


class AdminPasswordChangeForm(forms.Form):
    """Form for admins to change a user's password during edit (without old password verification)."""
    
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'
        }),
        required=False,
        help_text='Leave blank to skip changing password. If provided, password must be at least 8 characters long.'
    )
    
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        }),
        required=False
    )
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
    
    def clean(self):
        """Validate password fields."""
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        # If either password field is provided, both must be provided and match
        if new_password1 or new_password2:
            if not new_password1 or not new_password2:
                raise forms.ValidationError('Both password fields must be filled if changing password.')
            
            if new_password1 != new_password2:
                raise forms.ValidationError('Passwords do not match.')
            
            if len(new_password1) < 8:
                raise forms.ValidationError('Password must be at least 8 characters long.')
        
        return cleaned_data
    
    def save(self):
        """Set the new password only if provided."""
        new_password = self.cleaned_data.get('new_password1')
        
        if new_password:
            self.user.set_password(new_password)
            self.user.save()
            return True  # Password was changed
        
        return False  # Password was not changed
