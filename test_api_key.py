# Test Paymob API Key

import frappe
import requests
import json
import base64

def test_api_key():
    """Test the Paymob API key"""
    
    print("=== Paymob API Key Test ===\n")
    
    # The API key from your settings
    api_key = "ZXIKaGJHY2IPaUpJVXpVeE1pSXNJbIl1Y0NJNklrcFhWQ0o5LmV5SmpiR0Z6Y3IJNklrMWxjbU5vWVc1MElpd2IjSEp2Wm1sc1pWOXdheUk2TVRFNU56Z3NJbTVoYldVaU9pSnBibWwwYVdGc0luMC44VXpzdjRIYnIROENPMEJDNJFKRDh0WXFNQV9XbndsMFVvVFIVN0dpUEs3S01GVnJaNGIGMHIBZmRSWXppcU9pR3NwaTIMMGgxLXZkNEVnVINyd0VaUQ=="
    
    print(f"1. API Key: {api_key[:50]}...")
    print(f"2. API Key length: {len(api_key)}")
    
    # Try to decode if it's base64
    try:
        decoded = base64.b64decode(api_key).decode('utf-8')
        print(f"3. Base64 decoded: {decoded}")
    except:
        print("3. Not base64 encoded")
    
    # Test with Paymob API
    url = "https://accept.paymob.com/api/auth/tokens"
    
    payload = {
        "api_key": api_key
    }
    
    print(f"\n4. Testing API call...")
    print(f"   URL: {url}")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Token: {data.get('token', 'No token')}")
        else:
            print(f"❌ Failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_with_settings():
    """Test with actual settings from ERPNext"""
    
    print("\n=== Testing with ERPNext Settings ===\n")
    
    try:
        settings = frappe.get_single("Paymob Settings")
        api_key = settings.api_key
        
        if not api_key:
            print("❌ No API key in Paymob Settings")
            return
            
        print(f"1. API Key from settings: {api_key[:50]}...")
        
        url = "https://accept.paymob.com/api/auth/tokens"
        payload = {"api_key": api_key}
        
        response = requests.post(url, json=payload, timeout=30)
        print(f"2. Status Code: {response.status_code}")
        print(f"3. Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Authentication successful!")
            print(f"   Token: {data.get('token', 'No token')[:20]}...")
        else:
            print(f"❌ Authentication failed")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_api_key()
    test_with_settings()
