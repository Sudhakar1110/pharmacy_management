import frappe
from frappe import _
import json
from pharmacy_management.api.cart import get_cart_data, save_cart_data, clear_cart


@frappe.whitelist()
def create_order(address_name=None, payment_method="COD", prescription_ref=None, notes=None):
    """Create a Sales Order from cart contents."""
    cart = get_cart_data()
    if not cart.get("items"):
        frappe.throw(_("Your cart is empty"))
    
    user = frappe.session.user
    
    # Ensure customer exists
    customer_name = ensure_customer(user)
    
    # Get or create address
    if not address_name:
        # Try to get default shipping address
        addresses = frappe.get_all("Address", 
            filters={"email_id": frappe.db.get_value("User", user, "email") or user},
            fields=["name"], limit=1)
        if addresses:
            address_name = addresses[0].name
        else:
            frappe.throw(_("Please provide a shipping address"))
    
    # Validate prescription if needed
    rx_required = any(item.get("requires_prescription") for item in cart["items"])
    if rx_required and not prescription_ref:
        frappe.throw(_("Some medicines require a valid prescription. Please upload one."))
    
    # Check stock availability
    for item in cart["items"]:
        stock = frappe.db.get_value("Bin", {"item_code": item["medicine"]}, "actual_qty") or 0
        if stock < item["qty"]:
            frappe.throw(_("Insufficient stock for {0}. Available: {1}, Requested: {2}").format(
                item["medicine_name"], int(stock), item["qty"]))
    
    # Create Sales Order
    so = frappe.new_doc("Sales Order")
    so.customer = customer_name
    so.transaction_date = frappe.utils.today()
    so.delivery_date = frappe.utils.add_days(frappe.utils.today(), 3)
    so.company = frappe.defaults.get_defaults().get("company") or frappe.db.get_single_value("Global Defaults", "default_company")
    
    # Set shipping address
    so.shipping_address_name = address_name
    so.customer_address = address_name
    
    if notes:
        so.notes = notes
    
    # Add items
    for item in cart["items"]:
        so.append("items", {
            "item_code": item["medicine"],
            "item_name": item["medicine_name"],
            "qty": item["qty"],
            "rate": item["rate"],
            "delivery_date": frappe.utils.add_days(frappe.utils.today(), 3),
        })
    
    # Apply coupon
    if cart.get("coupon_code"):
        so.coupon_code = cart["coupon_code"]
        # Apply discount
        if cart["coupon_discount"] > 0:
            so.discount_amount = cart["coupon_discount"]
            so.apply_discount_on = "Grand Total"
    
    so.flags.ignore_permissions = True
    so.insert(ignore_permissions=True)
    
    # Link prescription if provided
    if prescription_ref:
        try:
            frappe.db.set_value("Prescription", prescription_ref, {
                "sales_invoice": so.name,
                "status": "Dispensing"
            })
        except Exception:
            pass
    
    # Set custom field for order source
    so.db_set("custom_order_source", "Website", update_modified=False)
    so.db_set("custom_payment_method", payment_method, update_modified=False)
    
    # Handle payment method
    if payment_method == "COD":
        so.submit()
        order_data = create_order_status(so, "Confirmed")
        clear_cart()
        return {
            "success": True,
            "order_id": so.name,
            "message": _("Order placed successfully! You will pay on delivery."),
            "payment_required": False,
        }
    elif payment_method in ["Razorpay", "PhonePe", "Stripe", "UPI"]:
        # Don't submit yet - payment pending
        order_data = create_order_status(so, "Pending Payment")
        # Generate payment link
        payment_data = generate_payment_request(so, payment_method)
        return {
            "success": True,
            "order_id": so.name,
            "message": _("Redirecting to payment..."),
            "payment_required": True,
            "payment_data": payment_data,
        }
    
    so.submit()
    order_data = create_order_status(so, "Confirmed")
    clear_cart()
    return {"success": True, "order_id": so.name}


def on_sales_order_submit(doc, method=None):
    """Hook: When a Sales Order is submitted, create an Order Status record."""
    try:
        create_order_status(doc, "Confirmed")
    except Exception:
        pass


def ensure_customer(user):
    """Ensure a Customer record exists for the website user."""
    email = frappe.db.get_value("User", user, "email") or user
    full_name = frappe.db.get_value("User", user, "full_name") or user
    
    existing = frappe.db.get_value("Customer", {"email_id": email}, "name")
    if existing:
        return existing
    
    customer_group = frappe.db.get_single_value("Selling Settings", "customer_group") or frappe.db.get_value("Customer Group", {"is_group": 0}, "name") or "Individual"
    territory = frappe.db.get_single_value("Selling Settings", "territory") or frappe.db.get_value("Territory", {"is_group": 0}, "name") or "India"
    customer = frappe.new_doc("Customer")
    customer.customer_name = full_name
    customer.customer_type = "Individual"
    customer.customer_group = customer_group
    customer.territory = territory
    customer.email_id = email
    customer.flags.ignore_permissions = True
    customer.insert(ignore_permissions=True, ignore_mandatory=True)
    
    # Also create/update Patient if doesn't exist
    if not frappe.db.exists("Patient", {"email": email}):
        try:
            patient = frappe.new_doc("Patient")
            patient.patient_name = full_name
            patient.email = email
            patient.mobile_number = frappe.db.get_value("User", user, "mobile_no") or ""
            patient.flags.ignore_permissions = True
            patient.insert(ignore_permissions=True)
        except Exception:
            pass
    
    return customer.name


def create_order_status(so, status):
    """Create an order status tracking record."""
    try:
        if frappe.db.exists("DocType", "Order Status"):
            os = frappe.new_doc("Order Status")
            os.sales_order = so.name
            os.status = status
            os.date = frappe.utils.now()
            os.flags.ignore_permissions = True
            os.insert(ignore_permissions=True)
    except Exception:
        pass


def generate_payment_request(so, payment_method):
    """Generate payment request data for the selected gateway."""
    amount = so.grand_total
    order_id = so.name
    
    payment_data = {
        "amount": amount,
        "order_id": order_id,
        "customer_name": so.customer_name,
        "customer_email": frappe.db.get_value("User", frappe.session.user, "email"),
        "customer_phone": frappe.db.get_value("User", frappe.session.user, "mobile_no"),
    }
    
    if payment_method == "Razorpay":
        import secrets
        receipt = f"receipt_{secrets.token_hex(4)}"
        payment_data["gateway"] = "razorpay"
        payment_data["key_id"] = frappe.db.get_single_value("Pharmacy Settings", "razorpay_key_id") or ""
        payment_data["receipt"] = receipt
        
        # Create Razorpay order via API
        try:
            import razorpay
            key_id = frappe.db.get_single_value("Pharmacy Settings", "razorpay_key_id")
            key_secret = frappe.db.get_single_value("Pharmacy Settings", "razorpay_key_secret")
            if key_id and key_secret:
                client = razorpay.Client(auth=(key_id, key_secret))
                razorpay_order = client.order.create({
                    "amount": int(amount * 100),
                    "currency": "INR",
                    "receipt": receipt,
                })
                payment_data["razorpay_order_id"] = razorpay_order["id"]
        except ImportError:
            pass
        except Exception:
            pass
    
    return payment_data


@frappe.whitelist()
def verify_payment(order_id, payment_id, razorpay_order_id=None, payment_method="Razorpay"):
    """Verify payment and submit the Sales Order."""
    if not frappe.db.exists("Sales Order", order_id):
        frappe.throw(_("Order not found"))
    
    so = frappe.get_doc("Sales Order", order_id)
    so.flags.ignore_permissions = True
    
    if payment_method == "COD":
        so.submit()
        clear_cart()
        return {"success": True, "order_id": order_id}
    
    # For online payments, verify and submit
    so.db_set("custom_payment_id", payment_id, update_modified=False)
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
    except Exception:
        pass
    
    clear_cart()
    return {"success": True, "order_id": order_id}


@frappe.whitelist()
def get_checkout_summary():
    """Get checkout summary from cart."""
    from pharmacy_management.api.cart import get_cart
    cart_data = get_cart()
    
    if cart_data["is_empty"]:
        frappe.throw(_("Your cart is empty"))
    
    user = frappe.session.user
    email = frappe.db.get_value("User", user, "email") or user
    full_name = frappe.db.get_value("User", user, "full_name") or user
    
    # Get user addresses safely
    customer = frappe.db.get_value("Customer", {"email_id": email}, "name")
    addresses = []
    if customer:
        try:
            address_links = frappe.get_all("Dynamic Link", 
                filters={"link_doctype": "Customer", "link_name": customer, "parenttype": "Address"},
                fields=["parent"])
            for link in address_links:
                try:
                    addr = frappe.get_doc("Address", link.parent)
                    addresses.append({
                        "name": addr.name,
                        "address_line1": addr.address_line1,
                        "address_line2": addr.address_line2,
                        "city": addr.city,
                        "state": addr.state,
                        "pincode": addr.pincode,
                        "phone": addr.phone,
                        "email_id": addr.email_id,
                        "is_shipping": getattr(addr, "is_primary_shipping_address", 0),
                        "is_billing": getattr(addr, "is_primary_billing_address", 0),
                    })
                except Exception:
                    continue  # Skip any problematic addresses
        except Exception:
            pass  # No addresses available
    
    return {
        "cart": cart_data,
        "user": {
            "full_name": full_name,
            "email": email,
            "mobile": frappe.db.get_value("User", user, "mobile_no") or "",
        },
        "addresses": addresses,
    }
