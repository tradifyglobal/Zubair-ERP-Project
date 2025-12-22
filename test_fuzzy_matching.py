#!/usr/bin/env python3
"""
Test improved fuzzy matching with "Nasir Ali Ali Mohammed - Capital"
"""
import os
import sys
import django

# Add the Django project path
sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import Account, Stakeholder

def test_improved_matching():
    """Test the improved fuzzy matching logic"""
    print("🧪 Testing Improved Fuzzy Matching Logic")
    print("=" * 50)
    
    # Test the problematic case
    account = Account.objects.get(id=91972)  # Nasir Ali Ali Mohammed - Capital
    print(f"Testing Account: {account.name}")
    
    # Use the same logic as in the views
    account_name = account.name.strip()
    
    if ' - Capital' in account_name:
        stakeholder_name = account_name.replace(' - Capital', '').strip()
        print(f"Extracted name: '{stakeholder_name}'")
        
        stakeholders = Stakeholder.objects.filter(entity=account.entity)
        
        # 1. Exact match
        for stakeholder in stakeholders:
            if stakeholder.full_name == stakeholder_name:
                print(f"✅ EXACT MATCH: {stakeholder.full_name} (ID: {stakeholder.id})")
                return stakeholder
        
        # 2. Fuzzy matching
        extracted_words = set(stakeholder_name.lower().split())
        print(f"Extracted words: {extracted_words}")
        
        best_match = None
        best_score = 0
        
        for stakeholder in stakeholders:
            stakeholder_words = set(stakeholder.full_name.lower().split())
            
            overlap = len(extracted_words.intersection(stakeholder_words))
            total_words = max(len(extracted_words), len(stakeholder_words))
            
            if total_words > 0:
                score = overlap / total_words
                print(f"  Checking: {stakeholder.full_name}")
                print(f"    Words: {stakeholder_words}")
                print(f"    Overlap: {overlap}/{total_words} = {score:.2f}")
                
                if score >= 0.6 and overlap >= 2 and score > best_score:
                    best_match = stakeholder
                    best_score = score
                    print(f"    ✅ NEW BEST MATCH!")
        
        if best_match:
            print(f"\n🎯 FUZZY MATCH RESULT: {best_match.full_name} (ID: {best_match.id}) - Score: {best_score:.2f}")
            return best_match
        else:
            print(f"\n❌ NO FUZZY MATCH FOUND")
    
    return None

if __name__ == '__main__':
    test_improved_matching()