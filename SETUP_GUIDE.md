# Paymob Integration Setup Guide

## 🚀 Quick Setup Steps

### 1. Configure Paymob Settings

1. Go to **Paymob Settings** in ERPNext
2. Enter your credentials from the Paymob portal:

```
HMAC: 61E924AEBDDF5DB3CB1A8745B0F8EAB1
API Key: ZXIKaGJHY2IPaUpJVXpVeE1pSXNJbIl1Y0NJNklrcFhWQ0o5LmV5SmpiR0Z6Y3IJNklrMWxjbU5vWVc1MElpd2IjSEp2Wm1sc1pWOXdheUk2TVRFNU56Z3NJbTVoYldVaU9pSnBibWwwYVdGc0luMC44VXpzdjRIYnIROENPMEJDNJFKRDh0WXFNQV9XbndsMFVvVFIVN0dpUEs3S01GVnJaNGIGMHIBZmRSWXppcU9pR3NwaTIMMGgxLXZkNEVnVINyd0VaUQ==
Secret Key: c43fed3f9d073d761425f72d680725af19fdef6cf3d9f448bc9c1c67f0
Public Key: sau_pk_test_IsSbAxe1iU0LYtcWmbaOqTZLZYmJ9JBq
```

### 2. Update Integration ID

1. Get your **Integration ID** from Paymob portal
2. Open: `apps/paymob_integration/paymob_integration/paymob_integration/api.py`
3. Find line 145: `"integration_id": 123456`
4. Replace `123456` with your actual Integration ID

### 3. Set Webhook URL in Paymob Portal

In your Paymob portal, set the webhook URL to:
```
https://your-erpnext-site.com/api/method/paymob_integration.paymob_integration.api.paymob_webhook
```

### 4. Test the Integration

1. **Create a Sales Order:**
   - Go to Sales Order → New
   - Add customer, items, submit

2. **Create Payment Link:**
   - Click "Create Payment Link" button
   - Check if email is sent to customer

3. **Test Payment:**
   - Use the payment link to make a test payment
   - Verify Payment Entry is created automatically

## 🔧 Manual Setup (if needed)

If the automatic setup doesn't work, run this in ERPNext console:

```python
exec(open('apps/paymob_integration/paymob_integration/paymob_integration/api.py').read())
setup_paymob_integration()
```

## 🧪 Testing

Run the test script:

```python
exec(open('apps/paymob_integration/paymob_integration/test_paymob.py').read())
test_paymob_integration()
```

## 📋 What You Need from Paymob Portal

1. **Integration ID** - Get this from your Paymob integration settings
2. **Webhook URL** - Set this in Paymob portal to point to your ERPNext

## ✅ Verification Checklist

- [ ] Paymob Settings configured with correct credentials
- [ ] Integration ID updated in api.py
- [ ] Webhook URL set in Paymob portal
- [ ] Sales Order can be submitted without errors
- [ ] Payment link creation works
- [ ] Email sending works
- [ ] Payment Entry creation works on successful payment

## 🆘 Troubleshooting

### Error: "Failed to authenticate with Paymob"
- Check API Key in Paymob Settings
- Verify API Key is correct in Paymob portal

### Error: "Integration ID not found"
- Update integration_id in api.py with your actual Paymob Integration ID

### Error: "Webhook signature verification failed"
- Check HMAC key in Paymob Settings
- Verify HMAC key matches Paymob portal

### Error: "Payment Entry creation failed"
- Check if default receivable account is set for company
- Verify customer has valid email address

## 📞 Support

If you encounter any issues:
1. Check the error logs in ERPNext (System → Error Log)
2. Verify Paymob portal configuration
3. Test with Paymob's test environment first
