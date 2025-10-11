# Quick Test Script for Paymob Integration

import frappe
from frappe import _

def test_paymob_setup():
    """Quick test to check Paymob integration setup"""
    
    print("=== Paymob Integration Quick Test ===\n")
    
    # Test 1: Check if Paymob Settings exist
    print("1. Checking Paymob Settings...")
    try:
        settings = frappe.get_single("Paymob Settings")
        if settings.api_key:
            print("✓ Paymob Settings found")
            print(f"  API Key: {settings.api_key[:20]}...")
        else:
            print("✗ Paymob Settings not configured")
            print("  Please configure API Key, HMAC, Secret Key, and Public Key")
            return False
    except Exception as e:
        print(f"✗ Error accessing Paymob Settings: {str(e)}")
        return False
    
    # Test 2: Check Sales Order custom fields
    print("\n2. Checking Sales Order custom fields...")
    try:
        custom_fields = frappe.get_all("Custom Field", 
            filters={"dt": "Sales Order", "fieldname": ["in", ["paymob_order_id", "paymob_payment_status"]]},
            fields=["fieldname", "label"]
        )
        
        if len(custom_fields) >= 2:
            print("✓ Sales Order custom fields found")
            for field in custom_fields:
                print(f"  - {field.fieldname}: {field.label}")
        else:
            print("✗ Sales Order custom fields missing")
            print("  Running setup...")
            from paymob_integration.paymob_integration.api import add_custom_fields_to_sales_order
            add_custom_fields_to_sales_order()
            print("✓ Custom fields setup completed")
            
    except Exception as e:
        print(f"✗ Error checking custom fields: {str(e)}")
        return False
    
    # Test 3: Check Sales Order with Paymob fields
    print("\n3. Checking Sales Order SAL-ORD-2025-00006...")
    try:
        so = frappe.get_doc("Sales Order", "SAL-ORD-2025-00006")
        print(f"✓ Sales Order found: {so.name}")
        print(f"  Status: {so.status}")
        print(f"  Grand Total: {so.grand_total}")
        print(f"  Paymob Payment Status: {getattr(so, 'paymob_payment_status', 'Not set')}")
        print(f"  Paymob Order ID: {getattr(so, 'paymob_order_id', 'Not set')}")
        
    except Exception as e:
        print(f"✗ Error accessing Sales Order: {str(e)}")
        return False
    
    # Test 4: Test Paymob API connection
    print("\n4. Testing Paymob API connection...")
    try:
        from paymob_integration.paymob_integration.api import test_paymob_connection
        result = test_paymob_connection()
        if result.get("status") == "success":
            print("✓ Paymob API connection successful")
        else:
            print(f"✗ Paymob API connection failed: {result.get('message')}")
            return False
    except Exception as e:
        print(f"✗ Error testing API connection: {str(e)}")
        return False
    
    print("\n=== All Tests Passed! ===")
    print("You can now:")
    print("1. Go to Sales Order SAL-ORD-2025-00006")
    print("2. Click 'Create Payment Link' button")
    print("3. Check if email is sent to customer")
    
    return True

if __name__ == "__main__":
    test_paymob_setup()
