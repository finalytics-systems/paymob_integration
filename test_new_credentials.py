# Test New Paymob Credentials

import frappe
import requests
import json

@frappe.whitelist()
def test_new_credentials():
    """Test new Paymob credentials"""
    
    print("=== Testing New Paymob Credentials ===\n")
    
    try:
        settings = frappe.get_single("Paymob Settings")
        api_key = settings.api_key
        
        if not api_key:
            return {"status": "error", "message": "No API key found in Paymob Settings"}
        
        print(f"Testing API Key: {api_key[:20]}...")
        
        # Test authentication
        url = "https://accept.paymob.com/api/auth/tokens"
        payload = {"api_key": api_key}
        
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            return {
                "status": "success", 
                "message": "Authentication successful!",
                "token": token[:20] + "..." if token else "No token"
            }
        else:
            return {
                "status": "error",
                "message": f"Authentication failed: {response.text}"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

if __name__ == "__main__":
    result = test_new_credentials()
    print(json.dumps(result, indent=2))
