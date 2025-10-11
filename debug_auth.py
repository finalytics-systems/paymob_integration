# Debug Paymob Authentication

import frappe
import requests
import json

def debug_paymob_auth():
    """Debug Paymob authentication issues"""
    
    print("=== Paymob Authentication Debug ===\n")
    
    # Get settings
    try:
        settings = frappe.get_single("Paymob Settings")
        api_key = settings.api_key
        
        print(f"1. API Key found: {api_key[:20]}..." if api_key else "1. API Key: NOT FOUND")
        print(f"2. API Key length: {len(api_key) if api_key else 0}")
        
        if not api_key:
            print("❌ No API Key found in Paymob Settings")
            return False
            
    except Exception as e:
        print(f"❌ Error accessing Paymob Settings: {str(e)}")
        return False
    
    # Test API call
    print("\n3. Testing Paymob API call...")
    
    url = "https://accept.paymob.com/api/auth/tokens"
    
    payload = {
        "api_key": api_key
    }
    
    print(f"   URL: {url}")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        print(f"   Response Text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if "token" in data:
                print(f"✅ Authentication successful!")
                print(f"   Token: {data['token'][:20]}...")
                return True
            else:
                print(f"❌ No token in response: {data}")
                return False
        else:
            print(f"❌ Authentication failed with status {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout - Paymob API not responding")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - Cannot reach Paymob API")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_different_api_keys():
    """Test with different possible API key formats"""
    
    print("\n=== Testing Different API Key Formats ===\n")
    
    settings = frappe.get_single("Paymob Settings")
    api_key = settings.api_key
    
    # Test variations
    test_keys = [
        api_key,
        api_key.strip(),
        api_key.replace(" ", ""),
        api_key.replace("\n", ""),
        api_key.replace("\r", "")
    ]
    
    for i, test_key in enumerate(test_keys):
        if test_key != api_key:
            print(f"Testing variation {i+1}: {test_key[:20]}...")
            
            url = "https://accept.paymob.com/api/auth/tokens"
            payload = {"api_key": test_key}
            
            try:
                response = requests.post(url, json=payload, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if "token" in data:
                        print(f"✅ Variation {i+1} works!")
                        return test_key
            except:
                pass
    
    return None

if __name__ == "__main__":
    debug_paymob_auth()
    test_different_api_keys()
