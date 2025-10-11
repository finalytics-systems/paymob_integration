import frappe
import json
import requests
import hashlib
import hmac
from frappe import _
from frappe.utils import now, flt, cstr, cint, random_string
from frappe.model.document import Document
from frappe.desk.form.load import get_attachments


class PaymobAPI:
    """Paymob API Integration Class"""
    
    def __init__(self):
        self.settings = frappe.get_single("Paymob Settings")
        self.api_key = self.settings.api_key
        self.hmac = self.settings.hmac
        self.secret_key = self.settings.secret_key
        self.public_key = self.settings.public_key
        self.base_url = "https://ksa.paymob.com/api"
        
    def get_auth_token(self):
        """Get authentication token from Paymob"""
        url = f"{self.base_url}/auth/tokens"
        
        payload = {
            "api_key": self.api_key
        }
        
        try:
            response = requests.post(url, json=payload)
            # Paymob returns 201 for successful authentication
            if response.status_code in [200, 201]:
                data = response.json()
                return data.get("token")
            else:
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            frappe.log_error(f"Paymob Auth Token Error: {str(e)}", "Paymob API Error")
            frappe.throw(_("Failed to authenticate with Paymob. Please check your API credentials."))
    
    def create_order(self, sales_order):
        """Create order in Paymob"""
        token = self.get_auth_token()
        
        url = f"{self.base_url}/ecommerce/orders"
        
        # Calculate total amount in cents (Paymob expects amount in cents)
        total_amount = int(flt(sales_order.grand_total) * 100)
        
        # Ensure unique merchant_order_id to avoid Paymob "duplicate" error
        merchant_order_id = sales_order.get("paymob_merchant_order_id")
        if not merchant_order_id:
            merchant_order_id = f"{sales_order.name}-{random_string(6)}"
            sales_order.db_set("paymob_merchant_order_id", merchant_order_id)

        payload = {
            "auth_token": token,
            "delivery_needed": False,
            "amount_cents": str(total_amount),
            "currency": (sales_order.currency or "SAR").upper(),
            "merchant_order_id": merchant_order_id,
            "items": []
        }
        
        # Add items to the order
        for item in sales_order.items:
            payload["items"].append({
                "name": item.item_name,
                "amount_cents": str(int(flt(item.amount) * 100)),
                "description": item.description or item.item_name,
                "quantity": int(item.qty)
            })
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code not in [200, 201]:
                try:
                    error_body = response.text
                    frappe.log_error(
                        f"Create Order failed | Status: {response.status_code} | Body: {error_body}",
                        "Paymob Create Order Response",
                    )
                except Exception:
                    pass
                # If duplicate merchant_order_id, regenerate and retry once
                if "duplicate" in (error_body or "").lower():
                    merchant_order_id = f"{sales_order.name}-{random_string(6)}"
                    sales_order.db_set("paymob_merchant_order_id", merchant_order_id)
                    payload["merchant_order_id"] = merchant_order_id
                    retry_resp = requests.post(url, json=payload, timeout=30)
                    if retry_resp.status_code in [200, 201]:
                        data = retry_resp.json()
                        sales_order.db_set("paymob_order_id", data.get("id"))
                        sales_order.db_set("paymob_order_token", data.get("token"))
                        return data
                    else:
                        frappe.throw(_(f"Paymob order creation failed after retry: {retry_resp.text}"))
                else:
                    # Bubble up with Paymob's response body for clarity
                    frappe.throw(_(f"Paymob order creation failed: {error_body}"))
            data = response.json()
            
            # Store Paymob order ID in Sales Order
            sales_order.db_set("paymob_order_id", data.get("id"))
            sales_order.db_set("paymob_order_token", data.get("token"))
            
            return data
            
        except requests.exceptions.RequestException as e:
            frappe.log_error(f"Paymob Create Order Error: {str(e)}", "Paymob API Error")
            frappe.throw(_(f"Failed to create order in Paymob. ({str(e)})"))
    
    def create_payment_key(self, sales_order, paymob_order_id):
        """Create payment key for Paymob"""
        token = self.get_auth_token()
        
        url = f"{self.base_url}/acceptance/payment_keys"
        
        # Calculate total amount in cents
        total_amount = int(flt(sales_order.grand_total) * 100)

        # Resolve integration id from settings, fallback to 16326
        try:
            integration_id = cint(getattr(self.settings, "integration_id", None)) or 16326
        except Exception:
            integration_id = 16326
        
        payload = {
            "auth_token": token,
            "amount_cents": str(total_amount),
            "expiration": 3600,  # 1 hour expiration
            "order_id": paymob_order_id,
            "billing_data": {
                "apartment": "NA",
                "email": sales_order.contact_email or sales_order.customer,
                "floor": "NA",
                "first_name": sales_order.customer_name.split()[0] if sales_order.customer_name else "Customer",
                "street": "NA",
                "building": "NA",
                "phone_number": sales_order.contact_mobile or sales_order.customer,
                "shipping_method": "PKG",
                "postal_code": "NA",
                "city": "NA",
                "country": "SA",
                "last_name": sales_order.customer_name.split()[-1] if len(sales_order.customer_name.split()) > 1 else "Customer",
                "state": "NA"
            },
            "currency": sales_order.currency or "SAR",
            "integration_id": integration_id,
            "lock_order_when_paid": "false"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code not in [200, 201]:
                try:
                    frappe.log_error(
                        f"Create Payment Key failed | Status: {response.status_code} | Body: {response.text}",
                        "Paymob Payment Key Response",
                    )
                except Exception:
                    pass
                response.raise_for_status()
            data = response.json()
            
            # Store payment token in Sales Order
            sales_order.db_set("paymob_payment_token", data.get("token"))
            
            return data
            
        except requests.exceptions.RequestException as e:
            frappe.log_error(f"Paymob Payment Key Error: {str(e)}", "Paymob API Error")
            frappe.throw(_(f"Failed to create payment key in Paymob. Please try again. ({str(e)})"))
    
    def generate_payment_link(self, sales_order):
        """Generate payment link for customer using Paymob Payment Link API"""
        try:
            token = self.get_auth_token()
            
            # Calculate total amount in cents
            total_amount = int(flt(sales_order.grand_total) * 100)
            
            # Resolve integration id from settings
            try:
                integration_id = cint(getattr(self.settings, "integration_id", None)) or 16326
            except Exception:
                integration_id = 16326
            
            # Paymob Payment Link API endpoint
            url = f"{self.base_url}/acceptance/payment_keys"
            
            payload = {
                "auth_token": token,
                "amount_cents": str(total_amount),
                "expiration": 3600,  # 1 hour expiration
                "billing_data": {
                    "apartment": "NA",
                    "email": sales_order.contact_email or sales_order.customer,
                    "floor": "NA",
                    "first_name": sales_order.customer_name.split()[0] if sales_order.customer_name else "Customer",
                    "street": "NA",
                    "building": "NA",
                    "phone_number": sales_order.contact_mobile or sales_order.customer,
                    "shipping_method": "PKG",
                    "postal_code": "NA",
                    "city": "Riyadh",
                    "country": "SA",
                    "last_name": sales_order.customer_name.split()[-1] if len(sales_order.customer_name.split()) > 1 else "Customer",
                    "state": "NA"
                },
                "currency": (sales_order.currency or "SAR").upper(),
                "integration_id": integration_id,
                "lock_order_when_paid": "false"
            }
            
            try:
                response = requests.post(url, json=payload, timeout=30)
                if response.status_code not in [200, 201]:
                    try:
                        error_body = response.text
                        frappe.log_error(
                            f"Create Payment Link failed | Status: {response.status_code} | Body: {error_body}",
                            "Paymob Payment Link Response",
                        )
                    except Exception:
                        pass
                    frappe.throw(_(f"Paymob payment link creation failed: {error_body}"))
                
                data = response.json()
                payment_token = data.get("token")
                
                if not payment_token:
                    frappe.throw(_("No payment token received from Paymob"))
                
                # Generate payment link using iframe integration ID (different from API integration ID)
                iframe_integration_id = 10524  # Correct iframe ID
                payment_link = f"https://ksa.paymob.com/api/acceptance/iframes/{iframe_integration_id}?payment_token={payment_token}"
                
                # Store payment link and token in Sales Order
                sales_order.db_set("paymob_payment_link", payment_link)
                sales_order.db_set("paymob_payment_token", payment_token)
                
                return payment_link
                
            except requests.exceptions.RequestException as e:
                frappe.log_error(f"Paymob Payment Link Error: {str(e)}", "Paymob API Error")
                frappe.throw(_(f"Failed to create payment link. ({str(e)})"))
            
        except Exception as e:
            frappe.log_error(f"Generate Payment Link Error: {str(e)}", "Paymob API Error")
            frappe.throw(_("Failed to generate payment link. Please try again."))
    
    def send_payment_email(self, sales_order, payment_link):
        """Send payment link to customer via email"""
        try:
            # Get customer email
            customer_email = sales_order.contact_email
            if not customer_email:
                customer = frappe.get_doc("Customer", sales_order.customer)
                customer_email = customer.email_id
            
            if not customer_email:
                frappe.throw(_("Customer email not found. Please add email to customer or contact."))
            
            # Email template
            subject = f"Payment Link for Sales Order {sales_order.name}"
            
            message = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2c3e50;">Payment Request</h2>
                <p>Dear {sales_order.customer_name or 'Valued Customer'},</p>
                
                <p>Thank you for your order. Please complete your payment using the link below:</p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3>Order Details:</h3>
                    <p><strong>Sales Order:</strong> {sales_order.name}</p>
                    <p><strong>Total Amount:</strong> {sales_order.currency} {sales_order.grand_total}</p>
                    <p><strong>Due Date:</strong> {sales_order.delivery_date or 'Not specified'}</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{payment_link}" 
                       style="background-color: #007bff; color: white; padding: 15px 30px; 
                              text-decoration: none; border-radius: 5px; font-weight: bold;
                              display: inline-block;">
                        Pay Now
                    </a>
                </div>
                
                <p><strong>Note:</strong> This payment link will expire in 1 hour for security reasons.</p>
                
                <p>If you have any questions, please contact us.</p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                <p style="color: #666; font-size: 12px;">
                    This is an automated message. Please do not reply to this email.
                </p>
            </div>
            """
            
            # Send email
            frappe.sendmail(
                recipients=[customer_email],
                subject=subject,
                message=message,
                header=["Payment Request", "green"]
            )
            
            # Log email sent
            frappe.get_doc({
                "doctype": "Communication",
                "communication_type": "Communication",
                "communication_medium": "Email",
                "sent_or_received": "Sent",
                "email_status": "Open",
                "subject": subject,
                "content": message,
                "reference_doctype": "Sales Order",
                "reference_name": sales_order.name,
                "sender": frappe.session.user,
                "recipients": customer_email
            }).insert(ignore_permissions=True)
            
            frappe.msgprint(_("Payment link sent to customer successfully!"))
            
        except Exception as e:
            frappe.log_error(f"Send Payment Email Error: {str(e)}", "Paymob Email Error")
            frappe.throw(_("Failed to send payment email. Please try again."))
    
    def verify_webhook_signature(self, payload, signature):
        """Verify webhook signature from Paymob"""
        try:
            # Create expected signature
            expected_signature = hmac.new(
                self.hmac.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            frappe.log_error(f"Webhook Signature Verification Error: {str(e)}", "Paymob Webhook Error")
            return False
    
    def process_payment_webhook(self, webhook_data):
        """Process payment webhook from Paymob"""
        try:
            # Extract data from webhook
            order_id = webhook_data.get("obj", {}).get("order", {}).get("merchant_order_id")
            transaction_id = webhook_data.get("obj", {}).get("id")
            amount = webhook_data.get("obj", {}).get("amount_cents", 0) / 100
            currency = webhook_data.get("obj", {}).get("currency")
            payment_status = webhook_data.get("obj", {}).get("success")
            
            if not order_id:
                frappe.log_error("No order ID in webhook data", "Paymob Webhook Error")
                return
            
            # Get Sales Order
            sales_order = frappe.get_doc("Sales Order", order_id)
            
            if not sales_order:
                frappe.log_error(f"Sales Order {order_id} not found", "Paymob Webhook Error")
                return
            
            # Update Sales Order with transaction details
            sales_order.db_set("paymob_transaction_id", transaction_id)
            sales_order.db_set("paymob_payment_status", "Paid" if payment_status else "Failed")
            
            if payment_status:
                # Create Payment Entry
                self.create_payment_entry(sales_order, amount, currency, transaction_id)
                
                # Update Sales Order status
                if sales_order.docstatus == 1:  # Only if submitted
                    sales_order.db_set("status", "Completed")
                
                frappe.msgprint(_("Payment received and Payment Entry created successfully!"))
            else:
                frappe.log_error(f"Payment failed for Sales Order {order_id}", "Paymob Payment Error")
                
        except Exception as e:
            frappe.log_error(f"Process Payment Webhook Error: {str(e)}", "Paymob Webhook Error")
    
    def create_payment_entry(self, sales_order, amount, currency, transaction_id):
        """Create Payment Entry in ERPNext"""
        try:
            # Get company from Sales Order
            company = sales_order.company
            
            # Get default payment account for the company
            payment_account = frappe.get_value("Company", company, "default_receivable_account")
            
            if not payment_account:
                frappe.throw(_("Default receivable account not found for company {0}").format(company))
            
            # Create Payment Entry
            payment_entry = frappe.get_doc({
                "doctype": "Payment Entry",
                "payment_type": "Receive",
                "party_type": "Customer",
                "party": sales_order.customer,
                "company": company,
                "paid_amount": amount,
                "received_amount": amount,
                "reference_no": transaction_id,
                "reference_date": now(),
                "mode_of_payment": "Paymob",
                "paid_to": payment_account,
                "paid_to_account_currency": currency,
                "source_exchange_rate": 1,
                "target_exchange_rate": 1,
                "references": [{
                    "reference_doctype": "Sales Order",
                    "reference_name": sales_order.name,
                    "allocated_amount": amount
                }]
            })
            
            payment_entry.insert(ignore_permissions=True)
            payment_entry.submit()
            
            # Link Payment Entry to Sales Order
            sales_order.db_set("paymob_payment_entry", payment_entry.name)
            
            frappe.log_error(f"Payment Entry {payment_entry.name} created for Sales Order {sales_order.name}", "Paymob Payment Entry")
            
        except Exception as e:
            frappe.log_error(f"Create Payment Entry Error: {str(e)}", "Paymob Payment Entry Error")
            frappe.throw(_("Failed to create Payment Entry. Please check the logs."))


@frappe.whitelist()
def create_payment_link(sales_order_name):
    """API endpoint to create payment link for Sales Order"""
    try:
        sales_order = frappe.get_doc("Sales Order", sales_order_name)
        
        if not sales_order:
            frappe.throw(_("Sales Order not found"))
        
        if sales_order.docstatus != 1:
            frappe.throw(_("Sales Order must be submitted to create payment link"))
        
        # Initialize Paymob API
        paymob_api = PaymobAPI()
        
        # Generate payment link
        payment_link = paymob_api.generate_payment_link(sales_order)
        
        # Send email to customer
        paymob_api.send_payment_email(sales_order, payment_link)
        
        return {
            "status": "success",
            "payment_link": payment_link,
            "message": "Payment link created and sent to customer successfully!"
        }
        
    except Exception as e:
        frappe.log_error(f"Create Payment Link Error: {str(e)}", "Paymob API Error")
        return {
            "status": "error",
            "message": str(e)
        }


@frappe.whitelist(allow_guest=True)
def paymob_webhook():
    """Webhook endpoint for Paymob payment notifications"""
    try:
        # Get webhook data
        webhook_data = frappe.request.get_json()
        
        if not webhook_data:
            frappe.throw(_("No webhook data received"))
        
        # Get signature from headers
        signature = frappe.request.headers.get("X-Paymob-Signature")
        
        if not signature:
            frappe.throw(_("No signature in webhook headers"))
        
        # Initialize Paymob API
        paymob_api = PaymobAPI()
        
        # Verify signature
        payload = json.dumps(webhook_data, separators=(',', ':'))
        
        if not paymob_api.verify_webhook_signature(payload, signature):
            frappe.throw(_("Invalid webhook signature"))
        
        # Process webhook
        paymob_api.process_payment_webhook(webhook_data)
        
        return {"status": "success"}
        
    except Exception as e:
        frappe.log_error(f"Paymob Webhook Error: {str(e)}", "Paymob Webhook Error")
        frappe.throw(_("Webhook processing failed"))


@frappe.whitelist()
def test_paymob_connection():
    """Test Paymob API connection"""
    try:
        paymob_api = PaymobAPI()
        token = paymob_api.get_auth_token()
        
        if token:
            return {
                "status": "success",
                "message": "Paymob connection successful!",
                "token": token[:20] + "..."  # Show only first 20 characters for security
            }
        else:
            return {
                "status": "error",
                "message": "Failed to get authentication token"
            }
            
    except Exception as e:
        frappe.log_error(f"Test Paymob Connection Error: {str(e)}", "Paymob Test Error")
        return {
            "status": "error",
            "message": str(e)
        }


@frappe.whitelist()
def get_payment_status(sales_order_name):
    """Get payment status for Sales Order"""
    try:
        sales_order = frappe.get_doc("Sales Order", sales_order_name)
        
        return {
            "paymob_order_id": sales_order.get("paymob_order_id"),
            "paymob_transaction_id": sales_order.get("paymob_transaction_id"),
            "paymob_payment_status": sales_order.get("paymob_payment_status"),
            "paymob_payment_link": sales_order.get("paymob_payment_link"),
            "paymob_payment_entry": sales_order.get("paymob_payment_entry")
        }
        
    except Exception as e:
        frappe.log_error(f"Get Payment Status Error: {str(e)}", "Paymob Status Error")
        return {
            "status": "error",
            "message": str(e)
        }


# Custom Fields for Sales Order
def add_custom_fields_to_sales_order():
    """Add custom fields to Sales Order for Paymob integration"""
    custom_fields = [
        {
            "fieldname": "paymob_order_id",
            "label": "Paymob Order ID",
            "fieldtype": "Data",
            "insert_after": "delivery_date",
            "read_only": 1,
            "allow_on_submit": 1
        },
            {
                "fieldname": "paymob_merchant_order_id",
                "label": "Paymob Merchant Order ID",
                "fieldtype": "Data",
                "insert_after": "paymob_order_id",
                "read_only": 1,
                "allow_on_submit": 1
            },
        {
            "fieldname": "paymob_transaction_id",
            "label": "Paymob Transaction ID", 
            "fieldtype": "Data",
                "insert_after": "paymob_merchant_order_id",
            "read_only": 1,
            "allow_on_submit": 1
        },
        {
            "fieldname": "paymob_payment_status",
            "label": "Paymob Payment Status",
            "fieldtype": "Select",
            "options": "Pending\nPaid\nFailed",
            "insert_after": "paymob_transaction_id",
            "read_only": 1,
            "allow_on_submit": 1
        },
        {
            "fieldname": "paymob_payment_link",
            "label": "Paymob Payment Link",
            "fieldtype": "Small Text",
            "insert_after": "paymob_payment_status",
            "read_only": 1,
            "allow_on_submit": 1
        },
        {
            "fieldname": "paymob_payment_entry",
            "label": "Paymob Payment Entry",
            "fieldtype": "Link",
            "options": "Payment Entry",
            "insert_after": "paymob_payment_link",
            "read_only": 1,
            "allow_on_submit": 1
        }
    ]
    
    for field in custom_fields:
        if not frappe.get_value("Custom Field", {"dt": "Sales Order", "fieldname": field["fieldname"]}):
            custom_field = frappe.get_doc({
                "doctype": "Custom Field",
                "dt": "Sales Order",
                **field
            })
            custom_field.insert(ignore_permissions=True)


# Initialize custom fields when module is installed
def initialize_paymob_integration(doc, method=None):
    """Initialize Paymob integration on Sales Order submit"""
    try:
        add_custom_fields_to_sales_order()
        # Set initial payment status
        doc.db_set("paymob_payment_status", "Pending")
        
        # Auto-create payment link if enabled in settings
        settings = frappe.get_single("Paymob Settings")
        if hasattr(settings, 'auto_create_payment_link') and settings.auto_create_payment_link:
            if doc.grand_total > 0:
                frappe.enqueue(
                    'paymob_integration.paymob_integration.api.create_payment_link',
                    queue='short',
                    timeout=300,
                    sales_order_name=doc.name
                )
                frappe.msgprint(_("Payment link will be created and sent to customer automatically."))
        
    except Exception as e:
        frappe.log_error(f"Paymob Integration Init Error: {str(e)}", "Paymob Integration Error")


@frappe.whitelist()
def setup_paymob_integration():
    """Setup Paymob integration manually"""
    try:
        add_custom_fields_to_sales_order()
        frappe.msgprint("Paymob integration setup completed successfully!")
    except Exception as e:
        frappe.log_error(f"Paymob Setup Error: {str(e)}", "Paymob Setup Error")
        frappe.throw(_("Failed to setup Paymob integration. Please check the logs."))


@frappe.whitelist()
def send_payment_email(sales_order_name):
    """API endpoint to send payment email for Sales Order"""
    try:
        sales_order = frappe.get_doc("Sales Order", sales_order_name)
        
        if not sales_order:
            frappe.throw(_("Sales Order not found"))
        
        if not sales_order.paymob_payment_link:
            frappe.throw(_("No payment link found. Please create payment link first."))
        
        # Initialize Paymob API
        paymob_api = PaymobAPI()
        
        # Send email to customer
        paymob_api.send_payment_email(sales_order, sales_order.paymob_payment_link)
        
        return {
            "status": "success",
            "message": "Payment email sent to customer successfully!"
        }
        
    except Exception as e:
        frappe.log_error(f"Send Payment Email Error: {str(e)}", "Paymob Email Error")
        return {
            "status": "error",
            "message": str(e)
        }
