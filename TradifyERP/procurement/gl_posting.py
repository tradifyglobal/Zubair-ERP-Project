"""
GL Posting Utilities for Procure-to-Pay Flow

Handles GL entries for:
1. Goods Receipt (DR Inventory / CR GR/IR Clearing)
2. Invoice Receipt (DR GR/IR Clearing / CR AP)
3. Payment (DR AP / CR Bank)
"""

from accounting.models import LedgerEntry, Account, Entity
from django.utils import timezone
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class P2PGLPosting:
    """Handle GL entries for Procure-to-Pay flow"""
    
    @staticmethod
    def get_or_create_accounts(entity: Entity):
        """
        Ensure required accounts exist for P2P flow
        Returns: {
            'inventory': Account,
            'gr_ir_clearing': Account,
            'accounts_payable': Account,
            'bank': Account
        }
        """
        accounts = {}
        
        # Raw Material Inventory (Asset)
        inventory, _ = Account.objects.get_or_create(
            entity=entity,
            account_number='1041',  # Asset - Inventory
            defaults={
                'name': 'Raw Material Inventory',
                'account_type': 'ASSET',
                'description': 'Raw materials and supplies in inventory',
                'is_active': True,
            }
        )
        accounts['inventory'] = inventory
        
        # GR/IR Clearing Account (Clearing/Liability)
        gr_ir, _ = Account.objects.get_or_create(
            entity=entity,
            account_number='2091',  # Liability - Clearing
            defaults={
                'name': 'GR/IR Clearing Account',
                'account_type': 'LIABILITY',
                'description': 'Temporary clearing for goods received not invoiced',
                'is_active': True,
            }
        )
        accounts['gr_ir_clearing'] = gr_ir
        
        # Accounts Payable (Liability)
        ap, _ = Account.objects.get_or_create(
            entity=entity,
            account_number='2010',  # Liability - AP
            defaults={
                'name': 'Accounts Payable',
                'account_type': 'LIABILITY',
                'description': 'Amounts owed to suppliers',
                'is_active': True,
            }
        )
        accounts['accounts_payable'] = ap
        
        # Bank Account (Asset) - use first active bank account
        bank = Account.objects.filter(
            entity=entity,
            account_type='ASSET',
            name__icontains='bank',
            is_active=True
        ).first()
        
        if not bank:
            bank, _ = Account.objects.get_or_create(
                entity=entity,
                account_number='1010',
                defaults={
                    'name': 'Bank Account',
                    'account_type': 'ASSET',
                    'is_active': True,
                }
            )
        accounts['bank'] = bank
        
        return accounts
    
    @staticmethod
    def post_goods_receipt(goods_receipt, description: str = None):
        """
        Post GL entry for Goods Receipt
        
        DR: Raw Material Inventory (Asset)
        CR: GR/IR Clearing Account (Liability)
        
        Args:
            goods_receipt: GoodsReceipt instance
            description: Optional GL entry description
        
        Returns:
            LedgerEntry instance or None if fails
        """
        try:
            entity = goods_receipt.entity
            accounts = P2PGLPosting.get_or_create_accounts(entity)
            
            # Calculate total goods value
            total_amount = sum(
                line.line_total 
                for line in goods_receipt.line_items.all()
            )
            
            if total_amount <= 0:
                logger.warning(f"GRN {goods_receipt.receipt_number}: Zero amount, skipping GL posting")
                return None
            
            # Validate accounts exist
            required_accounts = ['inventory', 'gr_ir_clearing']
            for account_key in required_accounts:
                if not accounts[account_key]:
                    raise ValueError(f"Required account {account_key} not found for entity {entity}")
            
            # Create GL Entry
            gl_entry = LedgerEntry.objects.create(
                entity=entity,
                transaction_type='GRN',
                transaction_id=goods_receipt.receipt_number,
                transaction_date=goods_receipt.receipt_date,
                description=description or f'Goods Receipt {goods_receipt.receipt_number} from PO {goods_receipt.po.po_number}',
                posting_date=timezone.now().date(),
                posted_by=goods_receipt.received_by or None,
                amount=total_amount,
                status='POSTED'
            )
            
            # DR: Raw Material Inventory
            gl_entry.entries.create(
                account=accounts['inventory'],
                debit=total_amount,
                credit=0,
                description=f'Raw material received - {goods_receipt.receipt_number}'
            )
            
            # CR: GR/IR Clearing Account
            gl_entry.entries.create(
                account=accounts['gr_ir_clearing'],
                debit=0,
                credit=total_amount,
                description=f'GR/IR clearing for {goods_receipt.receipt_number}'
            )
            
            logger.info(f"GL Entry posted for GRN {goods_receipt.receipt_number}: {total_amount}")
            return gl_entry
            
        except Exception as e:
            logger.error(f"Error posting GL for GRN {goods_receipt.receipt_number}: {str(e)}")
            return None
    
    @staticmethod
    def post_vendor_invoice(vendor_bill, description: str = None):
        """
        Post GL entry for Vendor Invoice (three-way match)
        
        DR: GR/IR Clearing Account (Liability)
        CR: Accounts Payable (Liability)
        
        Args:
            vendor_bill: VendorBill instance
            description: Optional GL entry description
        
        Returns:
            LedgerEntry instance or None if fails
        """
        try:
            entity = vendor_bill.entity
            accounts = P2PGLPosting.get_or_create_accounts(entity)
            
            # Calculate invoice total
            total_amount = vendor_bill.total_amount
            
            if total_amount <= 0:
                logger.warning(f"Bill {vendor_bill.bill_number}: Zero amount, skipping GL posting")
                return None
            
            # Validate accounts
            required_accounts = ['gr_ir_clearing', 'accounts_payable']
            for account_key in required_accounts:
                if not accounts[account_key]:
                    raise ValueError(f"Required account {account_key} not found for entity {entity}")
            
            # Create GL Entry
            gl_entry = LedgerEntry.objects.create(
                entity=entity,
                transaction_type='INVOICE',
                transaction_id=vendor_bill.bill_number,
                transaction_date=vendor_bill.bill_date,
                description=description or f'Vendor Invoice {vendor_bill.bill_number} from {vendor_bill.vendor.name}',
                posting_date=timezone.now().date(),
                posted_by=None,
                amount=total_amount,
                status='POSTED'
            )
            
            # DR: GR/IR Clearing Account
            gl_entry.entries.create(
                account=accounts['gr_ir_clearing'],
                debit=total_amount,
                credit=0,
                description=f'Invoice received - clear GR/IR for {vendor_bill.bill_number}'
            )
            
            # CR: Accounts Payable
            gl_entry.entries.create(
                account=accounts['accounts_payable'],
                debit=0,
                credit=total_amount,
                description=f'Vendor liability - {vendor_bill.vendor.name}'
            )
            
            logger.info(f"GL Entry posted for Invoice {vendor_bill.bill_number}: {total_amount}")
            return gl_entry
            
        except Exception as e:
            logger.error(f"Error posting GL for Invoice {vendor_bill.bill_number}: {str(e)}")
            return None
    
    @staticmethod
    def post_vendor_payment(vendor_payment, description: str = None):
        """
        Post GL entry for Vendor Payment
        
        DR: Accounts Payable (Liability)
        CR: Bank Account (Asset)
        
        Args:
            vendor_payment: VendorPayment instance
            description: Optional GL entry description
        
        Returns:
            LedgerEntry instance or None if fails
        """
        try:
            entity = vendor_payment.entity
            accounts = P2PGLPosting.get_or_create_accounts(entity)
            
            payment_amount = vendor_payment.amount_paid
            
            if payment_amount <= 0:
                logger.warning(f"Payment {vendor_payment.payment_number}: Zero amount, skipping GL posting")
                return None
            
            # Validate accounts
            required_accounts = ['accounts_payable', 'bank']
            for account_key in required_accounts:
                if not accounts[account_key]:
                    raise ValueError(f"Required account {account_key} not found for entity {entity}")
            
            # Create GL Entry
            gl_entry = LedgerEntry.objects.create(
                entity=entity,
                transaction_type='PAYMENT',
                transaction_id=vendor_payment.payment_number,
                transaction_date=vendor_payment.payment_date,
                description=description or f'Payment {vendor_payment.payment_number} to {vendor_payment.vendor.name}',
                posting_date=timezone.now().date(),
                posted_by=None,
                amount=payment_amount,
                status='POSTED'
            )
            
            # DR: Accounts Payable
            gl_entry.entries.create(
                account=accounts['accounts_payable'],
                debit=payment_amount,
                credit=0,
                description=f'Payment to {vendor_payment.vendor.name}'
            )
            
            # CR: Bank Account
            gl_entry.entries.create(
                account=accounts['bank'],
                debit=0,
                credit=payment_amount,
                description=f'Check/Wire #{vendor_payment.payment_number}'
            )
            
            logger.info(f"GL Entry posted for Payment {vendor_payment.payment_number}: {payment_amount}")
            return gl_entry
            
        except Exception as e:
            logger.error(f"Error posting GL for Payment {vendor_payment.payment_number}: {str(e)}")
            return None
    
    # ============= ENHANCED GL POSTING METHODS =============
    
    @staticmethod
    def post_goods_receipt_with_landed_costs(goods_receipt, description: str = None):
        """
        Post GL entry for Goods Receipt with Landed Costs
        
        Handles freight, duty, insurance, handling added to cost
        
        DR: Raw Material Inventory (includes landed costs)
        CR: GR/IR Clearing Account
        
        If variance exists:
        DR/CR: Variance Account (for price difference)
        """
        try:
            entity = goods_receipt.entity
            accounts = P2PGLPosting.get_or_create_accounts(entity)
            
            total_inventory_amount = 0
            total_landed_costs = 0
            total_variance = 0
            
            # Calculate totals from line items
            for line in goods_receipt.line_items.all():
                line_with_costs = line.line_total + line.freight_cost + line.customs_duty + line.insurance_cost + line.handling_cost + line.other_cost
                total_inventory_amount += line_with_costs
                total_landed_costs += (line.freight_cost + line.customs_duty + line.insurance_cost + line.handling_cost + line.other_cost)
                if line.unit_cost_variance != 0:
                    total_variance += line.unit_cost_variance * line.quantity_received
            
            if total_inventory_amount <= 0:
                logger.warning(f"GRN {goods_receipt.receipt_number}: Zero amount, skipping GL posting")
                return None
            
            # Create GL Entry
            gl_entry = LedgerEntry.objects.create(
                entity=entity,
                transaction_type='GRN_LANDED',
                transaction_id=goods_receipt.receipt_number,
                transaction_date=goods_receipt.receipt_date,
                description=description or f'GRN with Landed Costs {goods_receipt.receipt_number}',
                posting_date=timezone.now().date(),
                posted_by=goods_receipt.received_by or None,
                amount=total_inventory_amount,
                status='POSTED'
            )
            
            # DR: Raw Material Inventory (includes landed costs)
            gl_entry.entries.create(
                account=accounts['inventory'],
                debit=total_inventory_amount,
                credit=0,
                description=f'Raw material + landed costs ({goods_receipt.receipt_number})'
            )
            
            # CR: GR/IR Clearing Account
            gl_entry.entries.create(
                account=accounts['gr_ir_clearing'],
                debit=0,
                credit=total_inventory_amount,
                description=f'Goods received - clearing ({goods_receipt.receipt_number})'
            )
            
            # Handle Price Variance (if outside tolerance)
            if abs(total_variance) > 0:
                variance_account = Account.objects.filter(
                    entity=entity,
                    account_number='5002',  # Price Variance
                    is_active=True
                ).first()
                
                if variance_account:
                    if total_variance > 0:
                        # Favorable variance (received more value)
                        gl_entry.entries.create(
                            account=variance_account,
                            debit=0,
                            credit=total_variance,
                            description=f'Favorable price variance - {goods_receipt.receipt_number}'
                        )
                    else:
                        # Unfavorable variance (received less value)
                        gl_entry.entries.create(
                            account=variance_account,
                            debit=abs(total_variance),
                            credit=0,
                            description=f'Unfavorable price variance - {goods_receipt.receipt_number}'
                        )
            
            logger.info(f"GL Entry posted for GRN with Landed Costs {goods_receipt.receipt_number}: {total_inventory_amount}")
            return gl_entry
            
        except Exception as e:
            logger.error(f"Error posting GL for GRN {goods_receipt.receipt_number}: {str(e)}")
            return None
    
    @staticmethod
    def post_invoice_with_tax_gl(vendor_bill, description: str = None):
        """
        Post GL entry for Vendor Invoice with Tax GL Posting
        
        Handles:
        - GR/IR Clearing clearance
        - Separate tax GL accounts per tax type (GST, VAT, etc)
        - Input tax recovery segregation
        
        DR: GR/IR Clearing (for expenses)
        DR: Input Tax Recoverable (if tax_recoverable=True)
        CR: Accounts Payable (full invoice amount including tax)
        """
        try:
            entity = vendor_bill.entity
            accounts = P2PGLPosting.get_or_create_accounts(entity)
            
            total_amount = Decimal('0')
            total_tax = Decimal('0')
            tax_breakup = {}  # {tax_type: amount}
            
            # Calculate totals and tax by type
            for line in vendor_bill.line_items.all():
                total_amount += line.line_total
                total_tax += line.tax_amount
                
                tax_key = line.tax_type or 'OTHER'
                if tax_key not in tax_breakup:
                    tax_breakup[tax_key] = Decimal('0')
                tax_breakup[tax_key] += line.tax_amount
            
            total_invoice_amount = total_amount + total_tax
            
            if total_invoice_amount <= 0:
                logger.warning(f"Invoice {vendor_bill.bill_number}: Zero amount, skipping GL posting")
                return None
            
            # Create GL Entry
            gl_entry = LedgerEntry.objects.create(
                entity=entity,
                transaction_type='INVOICE_TAX',
                transaction_id=vendor_bill.bill_number,
                transaction_date=vendor_bill.bill_date,
                description=description or f'Invoice with Tax GL {vendor_bill.bill_number}',
                posting_date=timezone.now().date(),
                posted_by=None,
                amount=total_invoice_amount,
                status='POSTED'
            )
            
            # DR: GR/IR Clearing Account (expense portion)
            gl_entry.entries.create(
                account=accounts['gr_ir_clearing'],
                debit=total_amount,
                credit=0,
                description=f'Invoice expense clearing - {vendor_bill.bill_number}'
            )
            
            # DR: Tax accounts (separate by type)
            for tax_type, tax_amount in tax_breakup.items():
                # Get or create tax account
                if tax_amount > 0:
                    # Input Tax Recoverable (Asset) for GST/VAT/Sales Tax
                    tax_account, _ = Account.objects.get_or_create(
                        entity=entity,
                        account_number='1045',  # Input Tax Recoverable
                        defaults={
                            'name': f'Input Tax Recoverable - {tax_type}',
                            'account_type': 'ASSET',
                            'description': f'Recoverable taxes - {tax_type}',
                            'is_active': True,
                        }
                    )
                    
                    gl_entry.entries.create(
                        account=tax_account,
                        debit=tax_amount,
                        credit=0,
                        description=f'Input tax recoverable - {tax_type} ({vendor_bill.bill_number})'
                    )
            
            # CR: Accounts Payable (full amount including tax)
            gl_entry.entries.create(
                account=accounts['accounts_payable'],
                debit=0,
                credit=total_invoice_amount,
                description=f'Vendor obligation - {vendor_bill.vendor.name}'
            )
            
            logger.info(f"GL Entry posted for Invoice with Taxes {vendor_bill.bill_number}: {total_invoice_amount}")
            return gl_entry
            
        except Exception as e:
            logger.error(f"Error posting GL for Invoice {vendor_bill.bill_number}: {str(e)}")
            return None
    
    @staticmethod
    def post_purchase_return_reversal(purchase_return, description: str = None):
        """
        Post GL entry for Purchase Return (reversal of GRN)
        
        If return is after GRN:
        DR: GR/IR Clearing Account
        CR: Raw Material Inventory
        
        If return is after Invoice:
        DR: Accounts Payable
        CR: Raw Material Inventory
        """
        try:
            entity = purchase_return.entity
            accounts = P2PGLPosting.get_or_create_accounts(entity)
            
            return_amount = purchase_return.return_amount
            
            if return_amount <= 0:
                logger.warning(f"Purchase Return {purchase_return.return_number}: Zero amount, skipping GL posting")
                return None
            
            # Create GL Entry
            gl_entry = LedgerEntry.objects.create(
                entity=entity,
                transaction_type='RETURN',
                transaction_id=purchase_return.return_number,
                transaction_date=purchase_return.return_date,
                description=description or f'Purchase Return {purchase_return.return_number}',
                posting_date=timezone.now().date(),
                posted_by=purchase_return.created_by or None,
                amount=return_amount,
                status='POSTED'
            )
            
            # Determine if return is post-GRN or post-Invoice
            if purchase_return.goods_receipt and not purchase_return.vendor_bill:
                # Return after GRN, before invoice
                # DR: GR/IR Clearing Account
                gl_entry.entries.create(
                    account=accounts['gr_ir_clearing'],
                    debit=return_amount,
                    credit=0,
                    description=f'Return reversal - clear GR/IR ({purchase_return.return_number})'
                )
                
                # CR: Raw Material Inventory
                gl_entry.entries.create(
                    account=accounts['inventory'],
                    debit=0,
                    credit=return_amount,
                    description=f'Return from inventory ({purchase_return.return_number})'
                )
                
            elif purchase_return.vendor_bill:
                # Return after invoice
                # DR: Accounts Payable
                gl_entry.entries.create(
                    account=accounts['accounts_payable'],
                    debit=return_amount,
                    credit=0,
                    description=f'Return reversal - reduce payables ({purchase_return.return_number})'
                )
                
                # CR: Raw Material Inventory
                gl_entry.entries.create(
                    account=accounts['inventory'],
                    debit=0,
                    credit=return_amount,
                    description=f'Return from inventory ({purchase_return.return_number})'
                )
            
            logger.info(f"GL Entry posted for Purchase Return {purchase_return.return_number}: {return_amount}")
            return gl_entry
            
        except Exception as e:
            logger.error(f"Error posting GL for Purchase Return {purchase_return.return_number}: {str(e)}")
            return None
    
    @staticmethod
    def post_debit_note(debit_note, description: str = None):
        """
        Post GL entry for Debit Note
        
        For adjustments to supplier liability:
        DR: Accounts Payable (reduces what we owe)
        CR: Expense Account (or adjustment account)
        """
        try:
            entity = debit_note.entity
            accounts = P2PGLPosting.get_or_create_accounts(entity)
            
            debit_amount = debit_note.debit_amount
            
            if debit_amount <= 0:
                logger.warning(f"Debit Note {debit_note.debit_note_number}: Zero amount, skipping GL posting")
                return None
            
            # Create GL Entry
            gl_entry = LedgerEntry.objects.create(
                entity=entity,
                transaction_type='DEBIT_NOTE',
                transaction_id=debit_note.debit_note_number,
                transaction_date=debit_note.created_date.date(),
                description=description or f'Debit Note {debit_note.debit_note_number}',
                posting_date=timezone.now().date(),
                posted_by=debit_note.created_by or None,
                amount=debit_amount,
                status='POSTED'
            )
            
            # DR: Accounts Payable (reduces liability)
            gl_entry.entries.create(
                account=accounts['accounts_payable'],
                debit=debit_amount,
                credit=0,
                description=f'Debit note - reduce payables ({debit_note.debit_note_number})'
            )
            
            # CR: Appropriate adjustment account
            adjustment_account, _ = Account.objects.get_or_create(
                entity=entity,
                account_number='5099',  # Adjustments/Allowances
                defaults={
                    'name': 'Purchase Adjustments',
                    'account_type': 'EXPENSE',
                    'description': f'Debit notes and purchase adjustments',
                    'is_active': True,
                }
            )
            
            gl_entry.entries.create(
                account=adjustment_account,
                debit=0,
                credit=debit_amount,
                description=f'{debit_note.get_debit_type_display()} - {debit_note.debit_note_number}'
            )
            
            logger.info(f"GL Entry posted for Debit Note {debit_note.debit_note_number}: {debit_amount}")
            return gl_entry
            
        except Exception as e:
            logger.error(f"Error posting GL for Debit Note {debit_note.debit_note_number}: {str(e)}")
            return None
            return gl_entry
            
        except Exception as e:
            logger.error(f"Error posting GL for Payment {vendor_payment.payment_number}: {str(e)}")
            return None
