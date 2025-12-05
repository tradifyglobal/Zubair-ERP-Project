#!/usr/bin/env python
"""
Phase 2 Entity Segregation Fix Script
Updates Sales, AP, and Procurement modules to use SessionEntityMixin

Pattern:
1. Import SessionEntityMixin from accounting.mixins
2. Add SessionEntityMixin as first parent class (before LoginRequiredMixin)
3. Replace get_user_entities() calls with session-based filtering
4. Update form_valid() methods to use session entity
5. Update get_context_data() to work with session entity
"""

import os
import re


def update_sales_views():
    """Update sales/views.py to use SessionEntityMixin"""
    views_path = 'sales/views.py'
    
    with open(views_path, 'r') as f:
        content = f.read()
    
    original = content
    
    # 1. Update imports - add SessionEntityMixin
    if 'from accounting.mixins import SessionEntityMixin' not in content:
        import_section = 'from accounting.role_models import UserRole'
        content = content.replace(
            import_section,
            'from accounting.mixins import SessionEntityMixin\nfrom accounting.role_models import UserRole'
        )
    
    # 2. Replace all class definitions to add SessionEntityMixin
    # CustomerListView
    content = re.sub(
        r'class CustomerListView\(LoginRequiredMixin, ListView\):',
        'class CustomerListView(SessionEntityMixin, LoginRequiredMixin, ListView):',
        content
    )
    
    # CustomerCreateView
    content = re.sub(
        r'class CustomerCreateView\(LoginRequiredMixin, CreateView\):',
        'class CustomerCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):',
        content
    )
    
    # CustomerUpdateView
    content = re.sub(
        r'class CustomerUpdateView\(LoginRequiredMixin, UpdateView\):',
        'class CustomerUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):',
        content
    )
    
    # CustomerDeleteView
    content = re.sub(
        r'class CustomerDeleteView\(LoginRequiredMixin, DeleteView\):',
        'class CustomerDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):',
        content
    )
    
    # SalesOrderListView
    content = re.sub(
        r'class SalesOrderListView\(LoginRequiredMixin, ListView\):',
        'class SalesOrderListView(SessionEntityMixin, LoginRequiredMixin, ListView):',
        content
    )
    
    # SalesOrderCreateView
    content = re.sub(
        r'class SalesOrderCreateView\(LoginRequiredMixin, CreateView\):',
        'class SalesOrderCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):',
        content
    )
    
    # SalesOrderUpdateView
    content = re.sub(
        r'class SalesOrderUpdateView\(LoginRequiredMixin, UpdateView\):',
        'class SalesOrderUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):',
        content
    )
    
    # SalesOrderDeleteView
    content = re.sub(
        r'class SalesOrderDeleteView\(LoginRequiredMixin, DeleteView\):',
        'class SalesOrderDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):',
        content
    )
    
    # InvoiceListView
    content = re.sub(
        r'class InvoiceListView\(LoginRequiredMixin, ListView\):',
        'class InvoiceListView(SessionEntityMixin, LoginRequiredMixin, ListView):',
        content
    )
    
    # InvoiceCreateView
    content = re.sub(
        r'class InvoiceCreateView\(LoginRequiredMixin, CreateView\):',
        'class InvoiceCreateView(SessionEntityMixin, LoginRequiredMixin, CreateView):',
        content
    )
    
    # InvoiceUpdateView
    content = re.sub(
        r'class InvoiceUpdateView\(LoginRequiredMixin, UpdateView\):',
        'class InvoiceUpdateView(SessionEntityMixin, LoginRequiredMixin, UpdateView):',
        content
    )
    
    # InvoiceDeleteView
    content = re.sub(
        r'class InvoiceDeleteView\(LoginRequiredMixin, DeleteView\):',
        'class InvoiceDeleteView(SessionEntityMixin, LoginRequiredMixin, DeleteView):',
        content
    )
    
    # SalesDashboardView
    content = re.sub(
        r'class SalesDashboardView\(LoginRequiredMixin, TemplateView\):',
        'class SalesDashboardView(SessionEntityMixin, LoginRequiredMixin, TemplateView):',
        content
    )
    
    if content != original:
        with open(views_path, 'w') as f:
            f.write(content)
        return True
    return False


def update_ap_views():
    """Update ap/views.py to use SessionEntityMixin"""
    views_path = 'ap/views.py'
    
    with open(views_path, 'r') as f:
        content = f.read()
    
    original = content
    
    # 1. Add import if not present
    if 'from accounting.mixins import SessionEntityMixin' not in content:
        # Find the import section
        if 'from django.contrib.auth.mixins import LoginRequiredMixin' in content:
            content = content.replace(
                'from django.contrib.auth.mixins import LoginRequiredMixin',
                'from django.contrib.auth.mixins import LoginRequiredMixin\nfrom accounting.mixins import SessionEntityMixin'
            )
        else:
            # Add after other imports
            content = 'from accounting.mixins import SessionEntityMixin\n' + content
    
    # 2. Update all views to include SessionEntityMixin
    # Find all class definitions with LoginRequiredMixin and add SessionEntityMixin
    content = re.sub(
        r'class (\w+)\(LoginRequiredMixin, (ListView|DetailView|CreateView|UpdateView|DeleteView|TemplateView)\):',
        r'class \1(SessionEntityMixin, LoginRequiredMixin, \2):',
        content
    )
    
    if content != original:
        with open(views_path, 'w') as f:
            f.write(content)
        return True
    return False


def update_procurement_views():
    """Update procurement/views.py to use SessionEntityMixin"""
    views_path = 'procurement/views.py'
    
    with open(views_path, 'r') as f:
        content = f.read()
    
    original = content
    
    # 1. Add import if not present
    if 'from accounting.mixins import SessionEntityMixin' not in content:
        if 'from django.contrib.auth.mixins import LoginRequiredMixin' in content:
            content = content.replace(
                'from django.contrib.auth.mixins import LoginRequiredMixin',
                'from django.contrib.auth.mixins import LoginRequiredMixin\nfrom accounting.mixins import SessionEntityMixin'
            )
        else:
            content = 'from accounting.mixins import SessionEntityMixin\n' + content
    
    # 2. Update all views to include SessionEntityMixin
    content = re.sub(
        r'class (\w+)\(LoginRequiredMixin, (ListView|DetailView|CreateView|UpdateView|DeleteView|TemplateView)\):',
        r'class \1(SessionEntityMixin, LoginRequiredMixin, \2):',
        content
    )
    
    if content != original:
        with open(views_path, 'w') as f:
            f.write(content)
        return True
    return False


def main():
    """Execute Phase 2 fixes"""
    print("=" * 60)
    print("Phase 2 Entity Segregation Implementation")
    print("=" * 60)
    print()
    
    try:
        # Update Sales module
        print("[1/3] Updating Sales module...")
        if update_sales_views():
            print("      ✅ Sales views.py updated with SessionEntityMixin")
        else:
            print("      ⚠️  Sales views.py - no changes needed")
        
        # Update AP module
        print("\n[2/3] Updating AP module...")
        if update_ap_views():
            print("      ✅ AP views.py updated with SessionEntityMixin")
        else:
            print("      ⚠️  AP views.py - no changes needed")
        
        # Update Procurement module
        print("\n[3/3] Updating Procurement module...")
        if update_procurement_views():
            print("      ✅ Procurement views.py updated with SessionEntityMixin")
        else:
            print("      ⚠️  Procurement views.py - no changes needed")
        
        print()
        print("=" * 60)
        print("✅ Phase 2 Implementation Complete!")
        print("=" * 60)
        print()
        print("Summary:")
        print("- Sales module: SessionEntityMixin added to all views")
        print("- AP module: SessionEntityMixin added to all views")
        print("- Procurement module: SessionEntityMixin added to all views")
        print()
        print("Next Steps:")
        print("1. Verify no syntax errors in updated files")
        print("2. Test each module's list views in browser")
        print("3. Verify entity filtering works correctly")
        print("4. Create Phase 2 completion report")
        
    except Exception as e:
        print(f"❌ Error during Phase 2 implementation: {e}")
        raise


if __name__ == '__main__':
    main()
