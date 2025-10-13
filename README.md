# Paymob Integration for ERPNext

This app integrates Paymob payment gateway with ERPNext, allowing you to create payment links for Sales Orders and automatically create Payment Entries when payments are received.

## Features

- ✅ Create Paymob orders from Sales Orders
- ✅ Generate secure payment links
- ✅ Send payment emails to customers
- ✅ Handle payment webhooks
- ✅ Automatically create Payment Entries
- ✅ Real-time payment status updates
- ✅ Comprehensive error handling and logging

## Installation

1. **Install the app:**
   ```bash
   cd /path/to/your/frappe-bench
   bench get-app paymob_integration
   bench install-app paymob_integration
   ```

2. **Migrate the database:**
   ```bash
   bench migrate
   ```

3. **Restart the server:**
   ```bash
   bench restart
   ```

## Configuration

### 1. Paymob Portal Setup

Before configuring ERPNext, you need to set up your Paymob account:

1. **Login to Paymob Portal** (https://portal.paymob.com)
2. **Get your credentials:**
   - API Key
   - HMAC Key
   - Secret Key
   - Public Key

3. **Create an Integration:**
   - Go to Integrations → Create Integration
   - Choose "Iframe" integration type
   - Note down the Integration ID (you'll need this)

4. **Set Webhook URL:**
   - In your Paymob portal, set the webhook URL to:
   ```
   https://your-erpnext-site.com/api/method/paymob_integration.paymob_integration.api.paymob_webhook
   ```

### 2. ERPNext Configuration

1. **Configure Paymob Settings:**
   - Go to `Paymob Settings` doctype
   - Enter your Paymob credentials:
     - HMAC
     - API Key
     - Secret Key
     - Public Key

2. **Update Integration ID:**
   - In `api.py`, find the line with `integration_id: 123456`
   - Replace `123456` with your actual Integration ID from Paymob portal

3. **Test Connection:**
   - Go to any Sales Order
   - Click "Test Paymob Connection" button
   - Verify the connection is successful

## Usage

### Creating Payment Links

1. **Create a Sales Order** in ERPNext
2. **Submit the Sales Order**
3. **Click "Create Payment Link"** button in the Paymob section
4. The system will:
   - Create an order in Paymob
   - Generate a payment link
   - Send an email to the customer with the payment link

### Payment Flow

1. **Customer receives email** with payment link
2. **Customer clicks link** and completes payment
3. **Paymob sends webhook** to ERPNext
4. **ERPNext automatically:**
   - Verifies the payment
   - Creates a Payment Entry
   - Updates Sales Order status
   - Links Payment Entry to Sales Order

### Manual Operations

You can also manually:
- **View Payment Link**: See the generated payment link
- **Copy Payment Link**: Copy link to clipboard
- **Send Payment Email**: Resend payment email to customer
- **Check Payment Status**: Get latest payment status from Paymob

## API Endpoints

### Public Endpoints

- `POST /api/method/paymob_integration.paymob_integration.api.paymob_webhook`
  - Webhook endpoint for Paymob payment notifications
  - Requires valid HMAC signature

### Authenticated Endpoints

- `POST /api/method/paymob_integration.paymob_integration.api.create_payment_link`
  - Create payment link for Sales Order
  - Parameters: `sales_order_name`

- `GET /api/method/paymob_integration.paymob_integration.api.get_payment_status`
  - Get payment status for Sales Order
  - Parameters: `sales_order_name`

- `GET /api/method/paymob_integration.paymob_integration.api.test_paymob_connection`
  - Test Paymob API connection

## Testing

Run the test script to verify your integration:

```bash
cd /path/to/your/frappe-bench
bench --site your-site-name console
```

Then in the console:
```python
exec(open('/path/to/paymob_integration/test_paymob.py').read())
```

## Custom Fields Added

The integration automatically adds these custom fields to Sales Order:

- `paymob_order_id`: Paymob Order ID
- `paymob_transaction_id`: Paymob Transaction ID
- `paymob_payment_status`: Payment Status (Pending/Paid/Failed)
- `paymob_payment_link`: Generated Payment Link
- `paymob_payment_entry`: Created Payment Entry

## Security

- All API communications use HTTPS
- Webhook signatures are verified using HMAC
- API keys are stored securely in ERPNext
- Payment links expire after 1 hour

## Troubleshooting

### Common Issues

1. **"Failed to authenticate with Paymob"**
   - Check your API Key in Paymob Settings
   - Verify API Key is correct in Paymob portal

2. **"Webhook signature verification failed"**
   - Check HMAC key in Paymob Settings
   - Verify HMAC key matches Paymob portal

3. **"Payment Entry creation failed"**
   - Check if default receivable account is set for company
   - Verify customer has valid email address

4. **"Integration ID not found"**
   - Update integration_id in api.py with your actual Paymob Integration ID

### Debugging

1. **Check Error Logs:**
   - Go to System → Error Log
   - Look for "Paymob" related errors

2. **Test API Connection:**
   - Use "Test Paymob Connection" button
   - Verify all credentials are correct

3. **Check Webhook URL:**
   - Ensure webhook URL is accessible from internet
   - Test webhook endpoint manually if needed

## Support

For issues and support:
1. Check the error logs in ERPNext
2. Verify Paymob portal configuration
3. Test with Paymob's test environment first
4. Contact Paymob support for API-related issues

## Changelog

### Version 1.0.0
- Initial release
- Basic Paymob integration
- Payment link generation
- Webhook handling
- Automatic Payment Entry creation# paymob_integration
