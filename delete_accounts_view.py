from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from accounting.models import Account

@csrf_exempt
@require_http_methods(["POST"])
def delete_capital_accounts(request):
    """Delete Capital accounts (3100 and its children)"""
    try:
        # Check what Capital accounts exist
        accounts = Account.objects.filter(account_number__startswith='3100').order_by('account_number')
        account_list = []
        for acc in accounts:
            account_list.append({
                'account_number': acc.account_number,
                'name': acc.name,
                'account_type': acc.account_type
            })
        
        # Delete the accounts
        deleted_count = 0
        
        # First delete child accounts (3100-XX)
        child_accounts = Account.objects.filter(account_number__startswith='3100-')
        child_deleted = child_accounts.count()
        child_accounts.delete()
        deleted_count += child_deleted
        
        # Then delete parent account (3100)
        parent_account = Account.objects.filter(account_number='3100').first()
        if parent_account:
            parent_account.delete()
            deleted_count += 1
        
        # Verify deletion
        remaining_accounts = Account.objects.filter(account_number__startswith='3100').count()
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully deleted {deleted_count} Capital accounts',
            'original_accounts': account_list,
            'deleted_count': deleted_count,
            'remaining_count': remaining_accounts
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })