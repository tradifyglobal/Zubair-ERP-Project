"""Utility functions for vendor operations."""
from .models import Vendor


def generate_next_vendor_code(entity):
    """
    Generate the next vendor code for an entity.
    
    Format: VEND-XXXX where XXXX is a zero-padded sequence number.
    Example: VEND-0001, VEND-0002, etc.
    
    Args:
        entity: Entity instance
        
    Returns:
        str: Next vendor code in format VEND-XXXX
    """
    if not entity:
        return None
    
    # Get all vendors for this entity, ordered by vendor_code descending
    existing_vendors = Vendor.objects.filter(
        entity=entity
    ).order_by('-vendor_code').values_list('vendor_code', flat=True)
    
    if not existing_vendors.exists():
        # No vendors yet, start with 1
        return "VEND-0001"
    
    # Get the last vendor code and extract the sequence number
    last_code = existing_vendors.first()
    
    try:
        if last_code.startswith('VEND-'):
            # Extract the number part after 'VEND-'
            seq_str = last_code.split('-')[1]
            seq_num = int(seq_str)
            next_seq = seq_num + 1
        else:
            # Code doesn't match our pattern, start fresh
            next_seq = 1
    except (ValueError, IndexError):
        # If parsing fails, start fresh
        next_seq = 1
    
    # Format with zero-padding to 4 digits
    return f"VEND-{next_seq:04d}"
