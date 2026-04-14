# Proper implementation of ShareholderInvestmentReportView.get_context_data
# This replaces the broken version in views.py

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id).first()
        
        if not entity:
            context['investment_data'] = []
            return context
        
        from decimal import Decimal
        from accounting.models import CapitalContribution, Account, LedgerEntry

        def normalize_name(name):
            if not name:
                return ''
            value = ' '.join(str(name).split())
            if value.lower().endswith(' - capital'):
                value = value[:-10]
            return value.strip().lower()

        # Build invested amounts from Chart of Accounts/posted GL (same source as accounts page).
        stakeholder_capital_accounts = Account.objects.filter(
            entity=entity,
            account_type='EQUITY',  
            is_active=True
        ).filter(
            Q(account_number__startswith='SHR-') |
            Q(name__iendswith=' - Capital')
        )

        account_ids = list(stakeholder_capital_accounts.values_list('id', flat=True))
        ledger_sums = LedgerEntry.objects.filter(
            entity=entity,
            is_posted=True,
            account_id__in=account_ids
        ).values('account_id', 'entry_type').annotate(total=Sum('amount'))

        debit_map = {}
        credit_map = {}
        for row in ledger_sums:
            if row['entry_type'] == 'DEBIT':
                debit_map[row['account_id']] = row['total'] or Decimal('0')
            elif row['entry_type'] == 'CREDIT':
                credit_map[row['account_id']] = row['total'] or Decimal('0')

        invested_by_name = {}
        for account in stakeholder_capital_accounts:
            debits = debit_map.get(account.id, Decimal('0'))
            credits = credit_map.get(account.id, Decimal('0'))
            # EQUITY balance rule used by accounts page: CR - DR + opening
            balance = (credits - debits) + (account.opening_balance or Decimal('0'))

            key = normalize_name(account.name)
            if not key:
                continue
            invested_by_name[key] = invested_by_name.get(key, Decimal('0')) + balance
        
        investment_data = []
        processed_stakeholders = set()  # Track processed stakeholders to avoid duplicates
        
        # Get international transfers for all stakeholders to calculate pending in foreign bank
        from accounting.models import InternationalTransferTracking
        
        # Build a map of pending in foreign bank amounts per stakeholder
        # Include all non-cancelled, non-posted transfers (these are still pending)
        # Note: Handle multi-entity stakeholder mapping by email
        pending_in_foreign_bank_by_stakeholder = {}
        intl_transfers = InternationalTransferTracking.objects.filter(
            capital_contribution__entity=entity,
            transfer_status__in=['PENDING_ABROAD', 'IN_TRANSIT', 'RECEIVED_LOCALLY', 'CONVERTED']
        ).select_related('capital_contribution__stakeholder')

        for transfer in intl_transfers:
            transfer_stakeholder = transfer.capital_contribution.stakeholder
            destination_amount = transfer.destination_amount
            
            # Try to find matching stakeholder in current entity by email
            # This handles cases where stakeholder exists in multiple entities
            matching_stakeholder = Stakeholder.objects.filter(
                entity=entity,
                email=transfer_stakeholder.email
            ).first()
            
            # Use current entity's stakeholder if found, otherwise use transfer's stakeholder
            target_stakeholder_id = matching_stakeholder.id if matching_stakeholder else transfer_stakeholder.id
            
            if target_stakeholder_id not in pending_in_foreign_bank_by_stakeholder:
                pending_in_foreign_bank_by_stakeholder[target_stakeholder_id] = Decimal('0')
            # Add destination_amount (INR Amount from international capital report) to pending total
            if destination_amount:
                pending_in_foreign_bank_by_stakeholder[target_stakeholder_id] += Decimal(str(destination_amount))
        
        # First: Get all investment limits for this entity
        limits = ShareholderInvestmentLimit.objects.filter(entity=entity, is_active=True)
        
        for limit in limits:
            processed_stakeholders.add(limit.stakeholder.id)
            
            actual_invested_amount = invested_by_name.get(
                normalize_name(limit.stakeholder.full_name),
                Decimal('0')
            )
            balance_to_invest = limit.target_investment_amount - actual_invested_amount
            invested_percentage = 0
            if limit.target_investment_amount > 0:
                invested_percentage = float((actual_invested_amount / limit.target_investment_amount) * 100)
            
            # Get pending payment commitment
            is_completed = limit.is_completed
            pending_commitments = limit.payment_commitments.filter(status='PENDING').first()
            paid_commitment = limit.payment_commitments.filter(status='PAID').first()
            
            if is_completed:
                pending_commitments = None
                paid_commitment = None
            
            # Get pending in foreign bank from international transfers (INR Amount column from international capital report)
            pending_foreign_bank = pending_in_foreign_bank_by_stakeholder.get(limit.stakeholder.id, Decimal('0'))
            
            investment_data.append({
                'stakeholder': limit.stakeholder,
                'target_amount': limit.target_investment_amount,
                'invested_amount': actual_invested_amount,
                'balance_to_invest': balance_to_invest,
                'invested_percentage': invested_percentage,
                'currency': limit.currency,
                'next_payment_date': pending_commitments.promised_payment_date if pending_commitments else (paid_commitment.actual_payment_date if paid_commitment else None),
                'next_payment_amount': pending_commitments.committed_amount if pending_commitments else (paid_commitment.committed_amount if paid_commitment else None),
                'is_overdue': pending_commitments.is_overdue if pending_commitments else False,
                'next_payment_id': pending_commitments.id if pending_commitments else (paid_commitment.id if paid_commitment else None),
                'payment_status': pending_commitments.status if pending_commitments else (paid_commitment.status if paid_commitment else None),
                'is_completed': is_completed,
                'pending_in_foreign_bank': pending_foreign_bank,
            })
        
        # Second: Get stakeholders with capital contributions but no investment limit
        capital_contributions = CapitalContribution.objects.filter(
            entity=entity,
            workflow_status='APPROVED'
        ).values_list('stakeholder_id', flat=True).distinct()
        
        for stakeholder_id in capital_contributions:
            if stakeholder_id not in processed_stakeholders:
                processed_stakeholders.add(stakeholder_id)
                
                stakeholder = Stakeholder.objects.get(id=stakeholder_id)
                actual_invested_amount = invested_by_name.get(
                    normalize_name(stakeholder.full_name),
                    Decimal('0')
                )
                
                # Get pending in foreign bank from international transfers
                pending_foreign_bank = pending_in_foreign_bank_by_stakeholder.get(stakeholder_id, Decimal('0'))
                
                # For contributions without investment limit, show invested amount with no target
                investment_data.append({
                    'stakeholder': stakeholder,
                    'target_amount': None,  # No target set
                    'invested_amount': actual_invested_amount,
                    'balance_to_invest': None,
                    'invested_percentage': 100,  # Show as complete since no target
                    'currency': None,  # Will use default currency in template
                    'next_payment_date': None,
                    'next_payment_amount': None,
                    'is_overdue': False,
                    'next_payment_id': None,
                    'payment_status': None,
                    'is_completed': True,  # No target = considered complete
                    'pending_in_foreign_bank': pending_foreign_bank,
                })
        
        # Sort by stakeholder name
        investment_data.sort(key=lambda x: x['stakeholder'].full_name)
        
        # Calculate totals for the tiles
        total_invested_amount = Decimal('0')
        total_pending_in_foreign_bank = Decimal('0')
        total_balance_to_invest = Decimal('0')
        total_target_investment = Decimal('0')
        
        for inv in investment_data:
            # Total invested amount
            total_invested_amount += Decimal(str(inv['invested_amount']))
            
            # Total pending in foreign bank (from international transfers destination_amount)
            total_pending_in_foreign_bank += Decimal(str(inv.get('pending_in_foreign_bank', Decimal('0'))))
            
            # Total balance to invest
            if inv['balance_to_invest']:
                total_balance_to_invest += Decimal(str(inv['balance_to_invest']))
            
            # Total target investment
            if inv['target_amount']:
                total_target_investment += Decimal(str(inv['target_amount']))
        
        context['investment_data'] = investment_data
        context['entity'] = entity
        context['total_shareholders'] = len(investment_data)
        context['total_invested_amount'] = total_invested_amount
        context['total_pending_in_foreign_bank'] = total_pending_in_foreign_bank
        context['total_balance_to_invest'] = total_balance_to_invest
        context['total_target_investment'] = total_target_investment
        return context
