# Paymob Integration Setup Script

import frappe
from frappe import _
from paymob_integration.paymob_integration.api import add_custom_fields_to_sales_order

def setup_paymob_integration():
    """Setup Paymob integration"""
    try:
        # Add custom fields to Sales Order
        add_custom_fields_to_sales_order()
        
        # Create Paymob Settings document if it doesn't exist
        if not frappe.db.exists("Paymob Settings", "Paymob Settings"):
            paymob_settings = frappe.get_doc({
                "doctype": "Paymob Settings",
                "hmac": "",
                "api_key": "",
                "secret_key": "",
                "public_key": ""
            })
            paymob_settings.insert(ignore_permissions=True)
        
        frappe.msgprint(_("Paymob integration setup completed successfully!"))
        
    except Exception as e:
        frappe.log_error(f"Paymob Setup Error: {str(e)}", "Paymob Setup Error")
        frappe.throw(_("Failed to setup Paymob integration. Please check the logs."))

if __name__ == "__main__":
    setup_paymob_integration()
