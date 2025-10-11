# Paymob Webhook Handler
from __future__ import unicode_literals
import frappe
from frappe import _
from paymob_integration.paymob_integration.api import paymob_webhook

def get_context(context):
    # This is a webhook endpoint, so we don't need to render a template
    # The actual webhook processing is handled by the paymob_webhook function
    pass
