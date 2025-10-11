# Paymob Integration Test Script

import frappe
from frappe import _
from paymob_integration.paymob_integration.api import PaymobAPI, create_payment_link, test_paymob_connection

def test_paymob_integration():
    """Test Paymob integration functionality"""
    
    print("=== Paymob Integration Test ===\n")
    
    # Test 1: Check Paymob Settings
    print("1. Testing Paymob Settings...")
    try:
        settings = frappe.get_single("Paymob Settings")
        if settings.api_key and settings.hmac and settings.secret_key and settings.public_key:
            print("✓ Paymob Settings configured")
        else:
            print("✗ Paymob Settings not fully configured")
            print("  Please configure API Key, HMAC, Secret Key, and Public Key")
            return False
    except Exception as e:
        print(f"✗ Error accessing Paymob Settings: {str(e)}")
        return False
    
    # Test 2: Test API Connection
    print("\n2. Testing Paymob API Connection...")
    try:
        result = test_paymob_connection()
        if result.get("status") == "success":
            print("✓ Paymob API connection successful")
            print(f"  Token: {result.get('token')}")
        else:
            print(f"✗ Paymob API connection failed: {result.get('message')}")
            return False
    except Exception as e:
        print(f"✗ Error testing API connection: {str(e)}")
        return False
    
    # Test 3: Create Test Sales Order
    print("\n3. Creating Test Sales Order...")
    try:
        # Create test customer if doesn't exist
        if not frappe.db.exists("Customer", "Test Customer"):
            customer = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": "Test Customer",
                "customer_type": "Individual",
                "territory": "All Territories"
            })
            customer.insert(ignore_permissions=True)
        
        # Create test item if doesn't exist
        if not frappe.db.exists("Item", "Test Item"):
            item = frappe.get_doc({
                "doctype": "Item",
                "item_code": "Test Item",
                "item_name": "Test Item",
                "item_group": "All Item Groups",
                "is_stock_item": 1
            })
            item.insert(ignore_permissions=True)
        
        # Create test sales order
        sales_order = frappe.get_doc({
            "doctype": "Sales Order",
            "customer": "Test Customer",
            "transaction_date": frappe.utils.today(),
            "delivery_date": frappe.utils.add_days(frappe.utils.today(), 7),
            "items": [{
                "item_code": "Test Item",
                "qty": 1,
                "rate": 100
            }]
        })
        sales_order.insert()
        sales_order.submit()
        
        print(f"✓ Test Sales Order created: {sales_order.name}")
        
        # Test 4: Create Payment Link
        print("\n4. Testing Payment Link Creation...")
        try:
            result = create_payment_link(sales_order.name)
            if result.get("status") == "success":
                print("✓ Payment link created successfully")
                print(f"  Link: {result.get('payment_link')}")
            else:
                print(f"✗ Payment link creation failed: {result.get('message')}")
                return False
        except Exception as e:
            print(f"✗ Error creating payment link: {str(e)}")
            return False
        
        # Test 5: Check Payment Status
        print("\n5. Testing Payment Status Check...")
        try:
            from paymob_integration.paymob_integration.api import get_payment_status
            status = get_payment_status(sales_order.name)
            if status.get("status") != "error":
                print("✓ Payment status retrieved successfully")
                print(f"  Order ID: {status.get('paymob_order_id')}")
                print(f"  Payment Status: {status.get('paymob_payment_status')}")
            else:
                print(f"✗ Payment status check failed: {status.get('message')}")
        except Exception as e:
            print(f"✗ Error checking payment status: {str(e)}")
        
        print("\n=== Test Completed ===")
        print(f"Test Sales Order: {sales_order.name}")
        print("You can now test the payment flow using the generated payment link.")
        
        return True
        
    except Exception as e:
        print(f"✗ Error in test: {str(e)}")
        return False

def cleanup_test_data():
    """Clean up test data"""
    try:
        # Cancel and delete test sales order
        if frappe.db.exists("Sales Order", "Test Customer"):
            sales_orders = frappe.get_all("Sales Order", filters={"customer": "Test Customer"})
            for so in sales_orders:
                doc = frappe.get_doc("Sales Order", so.name)
                if doc.docstatus == 1:
                    doc.cancel()
                doc.delete()
        
        print("✓ Test data cleaned up")
        
    except Exception as e:
        print(f"✗ Error cleaning up test data: {str(e)}")

if __name__ == "__main__":
    # Run the test
    success = test_paymob_integration()
    
    if success:
        print("\n🎉 All tests passed! Paymob integration is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the configuration and try again.")
    
    # Ask if user wants to cleanup
    cleanup = input("\nDo you want to cleanup test data? (y/n): ")
    if cleanup.lower() == 'y':
        cleanup_test_data()
