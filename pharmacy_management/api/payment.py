import frappe
from frappe import _
import json


@frappe.whitelist()
def get_payment_options():
    """Get available payment gateways with their configuration."""
    settings = frappe.get_single("Pharmacy Settings") if frappe.db.exists("DocType", "Pharmacy Settings") else None
    
    gateways = [
        {
            "id": "COD",
            "name": "Cash on Delivery",
            "icon": "/assets/pharmacy_management/images/cod.svg",
            "description": "Pay when you receive your order",
            "enabled": True,
        },
        {
            "id": "Razorpay",
            "name": "Razorpay",
            "icon": "/assets/pharmacy_management/images/razorpay.svg",
            "description": "Credit/Debit Card, Net Banking, UPI",
            "enabled": bool(settings and settings.razorpay_key_id),
        },
        {
            "id": "PhonePe",
            "name": "PhonePe",
            "icon": "/assets/pharmacy_management/images/phonepe.svg",
            "description": "Pay using PhonePe UPI",
            "enabled": bool(settings and settings.razorpay_key_id),
        },
        {
            "id": "Stripe",
            "name": "Stripe",
            "icon": "/assets/pharmacy_management/images/stripe.svg",
            "description": "Pay with International Cards",
            "enabled": bool(settings and settings.stripe_publishable_key),
        },
        {
            "id": "UPI",
            "name": "UPI (GPay, Paytm, BHIM)",
            "icon": "/assets/pharmacy_management/images/upi.svg",
            "description": "Pay via any UPI app",
            "enabled": True,
        },
    ]
    
    return {"gateways": [g for g in gateways if g["enabled"]]}


@frappe.whitelist()
def initiate_payment(order_id, gateway="Razorpay"):
    """Initiate payment for an order."""
    if not frappe.db.exists("Sales Order", order_id):
        frappe.throw(_("Order not found"))
    
    so = frappe.get_doc("Sales Order", order_id)
    amount = so.grand_total
    user = frappe.session.user
    email = frappe.db.get_value("User", user, "email") or ""
    mobile = frappe.db.get_value("User", user, "mobile_no") or ""
    
    payment_data = {
        "amount": amount,
        "order_id": order_id,
        "customer_name": so.customer_name,
        "customer_email": email,
        "customer_phone": mobile,
        "gateway": gateway.lower(),
    }
    
    if gateway == "Razorpay":
        return initiate_razorpay_payment(so, payment_data)
    elif gateway == "Stripe":
        return initiate_stripe_payment(so, payment_data)
    elif gateway == "PhonePe":
        return initiate_phonepe_payment(so, payment_data)
    else:
        # COD or UPI - just return order info
        return {
            "success": True,
            "gateway": gateway,
            "amount": amount,
            "order_id": order_id,
            "payment_data": payment_data,
            "payment_url": None,
        }


def initiate_razorpay_payment(so, payment_data):
    """Create Razorpay order."""
    settings = frappe.get_single("Pharmacy Settings") if frappe.db.exists("DocType", "Pharmacy Settings") else None
    key_id = settings.razorpay_key_id if settings else None
    key_secret = settings.razorpay_key_secret if settings else None
    
    if not key_id or not key_secret:
        # Fallback to test mode data
        import secrets
        return {
            "success": True,
            "gateway": "razorpay",
            "key_id": "rzp_test_XXXXXXXXXXXXXXXX",
            "amount": int(payment_data["amount"] * 100),
            "currency": "INR",
            "order_id": payment_data["order_id"],
            "receipt": f"receipt_{secrets.token_hex(4)}",
            "customer_name": payment_data["customer_name"],
            "customer_email": payment_data["customer_email"],
            "customer_phone": payment_data["customer_phone"],
            "prefill": {
                "name": payment_data["customer_name"],
                "email": payment_data["customer_email"],
                "contact": payment_data["customer_phone"],
            },
            "theme": {"color": "#2563eb"},
        }
    
    try:
        import razorpay
        client = razorpay.Client(auth=(key_id, key_secret))
        import secrets
        receipt = f"receipt_{secrets.token_hex(4)}"
        razorpay_order = client.order.create({
            "amount": int(payment_data["amount"] * 100),
            "currency": "INR",
            "receipt": receipt,
            "notes": {
                "order_id": payment_data["order_id"],
                "customer": payment_data["customer_name"],
            },
        })
        
        return {
            "success": True,
            "gateway": "razorpay",
            "key_id": key_id,
            "amount": razorpay_order["amount"],
            "currency": razorpay_order["currency"],
            "order_id": payment_data["order_id"],
            "razorpay_order_id": razorpay_order["id"],
            "receipt": receipt,
            "customer_name": payment_data["customer_name"],
            "customer_email": payment_data["customer_email"],
            "customer_phone": payment_data["customer_phone"],
            "prefill": {
                "name": payment_data["customer_name"],
                "email": payment_data["customer_email"],
                "contact": payment_data["customer_phone"],
            },
            "theme": {"color": "#2563eb"},
        }
    except Exception as e:
        frappe.log_error(f"Razorpay error: {str(e)}", "Payment Initiation")
        return {
            "success": False,
            "error": _("Payment gateway error. Please try COD."),
        }


def initiate_stripe_payment(so, payment_data):
    """Create Stripe payment intent."""
    settings = frappe.get_single("Pharmacy Settings") if frappe.db.exists("DocType", "Pharmacy Settings") else None
    publishable_key = settings.stripe_publishable_key if settings else None
    secret_key = settings.stripe_secret_key if settings else None
    
    if not publishable_key:
        return {
            "success": True,
            "gateway": "stripe",
            "publishable_key": "pk_test_XXXXXXXXXXXXXXXXXXXX",
            "amount": int(payment_data["amount"] * 100),
            "currency": "inr",
            "order_id": payment_data["order_id"],
            "customer_email": payment_data["customer_email"],
        }
    
    try:
        import stripe
        stripe.api_key = secret_key
        
        intent = stripe.PaymentIntent.create(
            amount=int(payment_data["amount"] * 100),
            currency="inr",
            metadata={"order_id": payment_data["order_id"]},
        )
        
        return {
            "success": True,
            "gateway": "stripe",
            "publishable_key": publishable_key,
            "client_secret": intent.client_secret,
            "amount": intent.amount,
            "currency": intent.currency,
            "order_id": payment_data["order_id"],
        }
    except Exception as e:
        frappe.log_error(f"Stripe error: {str(e)}", "Payment Initiation")
        return {
            "success": False,
            "error": _("Payment gateway error. Please try COD."),
        }


def initiate_phonepe_payment(so, payment_data):
    """Initiate PhonePe payment."""
    import secrets
    transaction_id = f"TXN{secrets.token_hex(8).upper()}"
    
    return {
        "success": True,
        "gateway": "phonepe",
        "merchant_id": "PHARMACY_ONLINE",
        "transaction_id": transaction_id,
        "amount": payment_data["amount"],
        "order_id": payment_data["order_id"],
        "callback_url": f"/api/method/pharmacy_management.api.payment.phonepe_callback",
        "customer_name": payment_data["customer_name"],
        "customer_phone": payment_data["customer_phone"],
    }


@frappe.whitelist()
def razorpay_callback():
    """Handle Razorpay payment callback."""
    data = frappe.local.form_dict
    
    order_id = data.get("order_id") or data.get("razorpay_order_id")
    payment_id = data.get("razorpay_payment_id")
    signature = data.get("razorpay_signature")
    
    if not order_id:
        frappe.throw(_("Missing order information"))
    
    # Verify signature
    try:
        settings = frappe.get_single("Pharmacy Settings") if frappe.db.exists("DocType", "Pharmacy Settings") else None
        key_secret = settings.razorpay_key_secret if settings else "test_secret"
        
        import razorpay
        params_dict = {
            "razorpay_order_id": data.get("razorpay_order_id"),
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
        }
        razorpay.Utility.verify_payment_signature(params_dict, key_secret)
        
        # Find actual Sales Order
        # Map from Razorpay order to our order
        so_name = data.get("custom_order_id") or order_id
        
        return complete_payment(so_name, payment_id, "Razorpay")
    except Exception as e:
        frappe.log_error(f"Razorpay verification failed: {str(e)}", "Payment Callback")
        return {"success": False, "error": _("Payment verification failed")}


@frappe.whitelist()
def stripe_callback():
    """Handle Stripe payment callback."""
    data = frappe.local.form_dict
    order_id = data.get("order_id")
    payment_intent_id = data.get("payment_intent_id")
    
    if not order_id or not payment_intent_id:
        frappe.throw(_("Missing payment information"))
    
    return complete_payment(order_id, payment_intent_id, "Stripe")


@frappe.whitelist()
def phonepe_callback():
    """Handle PhonePe payment callback."""
    data = frappe.local.form_dict
    order_id = data.get("order_id")
    transaction_id = data.get("transaction_id")
    status = data.get("status")
    
    if status == "SUCCESS" and order_id:
        return complete_payment(order_id, transaction_id, "PhonePe")
    
    return {"success": False, "error": _("Payment failed")}


def complete_payment(order_id, payment_ref, payment_method):
    """Complete order after successful payment."""
    if not frappe.db.exists("Sales Order", order_id):
        return {"success": False, "error": _("Order not found")}
    
    so = frappe.get_doc("Sales Order", order_id)
    
    if so.docstatus == 1:
        return {"success": True, "order_id": order_id, "message": _("Order already confirmed")}
    
    so.db_set("custom_payment_id", payment_ref, update_modified=False)
    so.db_set("custom_payment_method", payment_method, update_modified=False)
    so.submit()
    
    # Create Payment Entry
    try:
        pe = frappe.new_doc("Payment Entry")
        pe.payment_type = "Receive"
        pe.company = so.company
        pe.posting_date = frappe.utils.today()
        pe.party_type = "Customer"
        pe.party = so.customer
        pe.paid_amount = so.grand_total
        pe.received_amount = so.grand_total
        pe.reference_doctype = "Sales Order"
        pe.reference_name = so.name
        pe.mode_of_payment = payment_method
        pe.flags.ignore_permissions = True
        pe.insert(ignore_permissions=True)
        pe.submit()
    except Exception as e:
        frappe.log_error(f"Payment Entry creation failed: {str(e)}", "Payment")
    
    # Clear cart
    from pharmacy_management.api.cart import clear_cart
    try:
        clear_cart()
    except Exception:
        pass
    
    # Clear wishlist purchased items
    try:
        for item in so.items:
            from pharmacy_management.api.wishlist import remove_from_wishlist
            remove_from_wishlist(item.item_code)
    except Exception:
        pass
    
    return {"success": True, "order_id": order_id, "message": _("Payment successful! Order confirmed.")}
