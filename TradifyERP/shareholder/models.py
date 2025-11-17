from django.db import models
from accounting.models import Stakeholder, CapitalContribution, Shareholding

# Re-export models from accounting for backwards compatibility
# These are referenced through the shareholder app for organizational clarity
__all__ = ['Stakeholder', 'CapitalContribution', 'Shareholding']
