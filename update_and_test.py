# Update Paymob Settings and Test Integration

import frappe
from frappe import _

def update_paymob_settings():
    """Update Paymob Settings with new API key"""
    
    print("=== Updating Paymob Settings ===\n")
    
    try:
        # Get or create Paymob Settings
        if not frappe.db.exists("Paymob Settings", "Paymob Settings"):
            settings = frappe.get_doc({
                "doctype": "Paymob Settings",
                "hmac": "61E924AEBDDF5DB3CB1A8745B0F8EAB1",
                "api_key": "ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SmpiR0Z6Y3lJNklrMWxjbU5vWVc1MElpd2ljSEp2Wm1sc1pWOXdheUk2TVRFNU56Z3NJbkJvWVhOb0lqb2lPRGs0WldJME0yWXlOMlF5WW1VNU5qQTBOV0UwWW1FMVpqazVNalkyWW1Jd09HSTRNRFppTnpsaFpUUmpNVGN3WXpVek5XUmhNbVZrWVRVMU5XSmpaaUlzSW1WNGNDSTZNVGMxT1RrME16UTVNSDAuc3hLZl9MSDAtYUJjYy05d19rblpwS0lRZE9nTG9RTDl0QS1KNFhLdW85MUJXb1pIdEVISXgwWFVsTVdtSVJKTUUtakxwTHByVjFWQy0wU1dpZmZPNUE=",
                "secret_key": "c43fed3f9d073d761425f72d680725af19fdef6cf3d9f448bc9c1c67f0",
                "public_key": "sau_pk_test_IsSbAxe1iU0LYtcWmbaOqTZLZYmJ9JBq",
                "auto_create_payment_link": 0
            })
            settings.insert(ignore_permissions=True)
            print("✅ Paymob Settings created")
        else:
            settings = frappe.get_single("Paymob Settings")
            settings.api_key = "ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SmpiR0Z6Y3lJNklrMWxjbU5vWVc1MElpd2ljSEp2Wm1sc1pWOXdheUk2TVRFNU56Z3NJbkJvWVhOb0lqb2lPRGs0WldJME0yWXlOMlF5WW1VNU5qQTBOV0UwWW1FMVpqazVNalkyWW1Jd09HSTRNRFppTnpsaFpUUmpNVGN3WXpVek5XUmhNbVZrWVRVMU5XSmpaaUlzSW1WNGNDSTZNVGMxT1RrME16UTVNSDAuc3hLZl9MSDAtYUJjYy05d19rblpwS0lRZE9nTG9RTDl0QS1KNFhLdW85MUJXb1pIdEVISXgwWFVsTVdtSVJKTUUtakxwTHByVjFWQy0wU1dpZmZPNUE="
            settings.save()
            print("✅ Paymob Settings updated")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating settings: {str(e)}")
        return False

def test_paymob_connection():
    """Test Paymob connection"""
    
    print("\n=== Testing Paymob Connection ===\n")
    
    try:
        from paymob_integration.paymob_integration.api import test_paymob_connection
        result = test_paymob_connection()
        
        if result.get("status") == "success":
            print("✅ Paymob connection successful!")
            print(f"   Token: {result.get('token')}")
            return True
        else:
            print(f"❌ Paymob connection failed: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing connection: {str(e)}")
        return False

def test_sales_order():
    """Test with Sales Order"""
    
    print("\n=== Testing with Sales Order ===\n")
    
    try:
        # Check if Sales Order exists
        so_name = "SAL-ORD-2025-00006"
        if frappe.db.exists("Sales Order", so_name):
            so = frappe.get_doc("Sales Order", so_name)
            print(f"✅ Sales Order found: {so.name}")
            print(f"   Status: {so.status}")
            print(f"   Grand Total: {so.grand_total}")
            print(f"   Customer: {so.customer}")
            print(f"   Customer Email: {so.contact_email}")
            
            # Check Paymob fields
            paymob_fields = ['paymob_order_id', 'paymob_payment_status', 'paymob_payment_link']
            for field in paymob_fields:
                value = getattr(so, field, None)
                print(f"   {field}: {value}")
            
            return True
        else:
            print(f"❌ Sales Order {so_name} not found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Sales Order: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Paymob Integration Test\n")
    
    # Update settings
    if update_paymob_settings():
        # Test connection
        if test_paymob_connection():
            # Test Sales Order
            test_sales_order()
            
            print("\n🎉 Integration is ready!")
            print("You can now:")
            print("1. Go to Sales Order SAL-ORD-2025-00006")
            print("2. Click 'Create Payment Link' button")
            print("3. Test the complete payment flow")
        else:
            print("\n❌ Connection test failed")
    else:
        print("\n❌ Settings update failed")
