import frappe
from frappe import _
import json


def get_cart_key():
    """Get the cart session key for current user."""
    if frappe.session.user and frappe.session.user != "Guest":
        return f"pharmacy_cart:{frappe.session.user}"
    # Safely get session ID
    try:
        session_id = frappe.session.sid
    except Exception:
        session_id = "anonymous"
    return f"pharmacy_cart:guest:{session_id}"


def get_cart_data():
    """Retrieve cart from cache, deduplicating and fixing items."""
    cart_key = get_cart_key()
    cart = frappe.cache().get_value(cart_key)
    if not cart:
        cart = {
            "items": [],
            "coupon_code": None,
            "coupon_discount": 0,
        }
    # Deduplicate items by medicine name (merge qty/amount for duplicates)
    changed = False
    deduped = {}
    for item in cart.get("items", []):
        med = item.get("medicine")
        if not med:
            continue
        if med in deduped:
            deduped[med]["qty"] += item.get("qty", 1)
            deduped[med]["amount"] = deduped[med]["qty"] * deduped[med].get("rate", 0)
            changed = True
        else:
            deduped[med] = dict(item)
    if changed:
        cart["items"] = list(deduped.values())
        save_cart_data(cart)
    elif len(cart.get("items", [])) != len(deduped):
        cart["items"] = list(deduped.values())
        save_cart_data(cart)
    return cart


def save_cart_data(cart):
    """Save cart to cache (24 hour expiry)."""
    cart_key = get_cart_key()
    frappe.cache().set_value(cart_key, cart, expires_in_sec=86400)


def get_medicine_stock(medicine_name):
    """Get available stock for a medicine.
    
    Checks multiple sources in priority order:
    1. Medicine Batch records (primary source of truth)
    2. ERPNext Bin table (if fix_stock.py was run)
    3. Defaults to 999 if no stock tracking exists (allows cart to work)
    """
    from frappe.utils import today

    # Source 1: Medicine Batch - sum of current_qty for active, non-expired batches
    try:
        batch_stock = frappe.db.sql("""
            SELECT COALESCE(SUM(current_qty), 0) as total
            FROM `tabMedicine Batch`
            WHERE medicine = %s
              AND batch_status NOT IN ('Disposed', 'Expired')
              AND (expiry_date >= %s OR expiry_date IS NULL)
        """, (medicine_name, today()), as_dict=True)
        
        if batch_stock and batch_stock[0].total > 0:
            return batch_stock[0].total
    except Exception:
        pass  # Medicine Batch table may not exist yet
    
    # Source 2: ERPNext Bin table
    try:
        bin_stock = frappe.db.get_value("Bin", {"item_code": medicine_name}, "actual_qty")
        if bin_stock and bin_stock > 0:
            return bin_stock
    except Exception:
        pass
    
    # Source 3: Check if ANY stock tracking exists at all
    has_batches = False
    has_bins = False
    try:
        has_batches = frappe.db.count("Medicine Batch", {"medicine": medicine_name}) > 0
    except Exception:
        pass
    try:
        has_bins = frappe.db.exists("Bin", {"item_code": medicine_name})
    except Exception:
        pass
    
    if has_batches or has_bins:
        # Stock tracking exists but stock is zero
        return 0
    
    # No stock tracking at all - default to available (allows demo/initial use)
    return 999


def merge_guest_cart_to_user():
    """Merge guest cart into user cart on login."""
    if frappe.session.user == "Guest":
        return
    
    try:
        guest_key = f"pharmacy_cart:guest:{frappe.session.sid}"
        guest_cart = frappe.cache().get_value(guest_key)
        if not guest_cart or not guest_cart.get("items"):
            return
        
        user_cart = get_cart_data()
        
        for guest_item in guest_cart["items"]:
            found = False
            for user_item in user_cart["items"]:
                if user_item["medicine"] == guest_item["medicine"]:
                    user_item["qty"] += guest_item["qty"]
                    found = True
                    break
            if not found:
                user_cart["items"].append(guest_item)
        
        save_cart_data(user_cart)
        frappe.cache().delete_value(guest_key)
    except Exception:
        pass


@frappe.whitelist(allow_guest=True)
def add_to_cart(medicine, qty=1):
    """Add a medicine to cart."""
    try:
        qty = int(qty)
    except (ValueError, TypeError):
        qty = 1
    if qty < 1:
        qty = 1
    
    # Validate medicine exists and is active
    medicine_doc = frappe.db.get_value("Medicine Master", medicine, 
                                       ["name", "medicine_name", "mrp", "selling_rate", 
                                        "requires_prescription", "image", "strength", "dosage_form"],
                                       as_dict=True)
    if not medicine_doc:
        frappe.throw(_("Medicine not found"))
    
    # Check stock using the unified stock check
    stock = get_medicine_stock(medicine)
    if stock <= 0:
        frappe.throw(_("{0} is currently out of stock").format(medicine_doc.medicine_name))
    
    cart = get_cart_data()
    
    # Check if already in cart
    for item in cart["items"]:
        if item["medicine"] == medicine:
            item["qty"] += qty
            if stock < 999:  # Only cap if real stock tracking exists
                item["qty"] = min(item["qty"], int(stock))
            item["amount"] = item["qty"] * item["rate"]
            save_cart_data(cart)
            return {"success": True, "cart": cart, "message": _("Cart updated")}
    
    # Add new item
    rate = medicine_doc.selling_rate or medicine_doc.mrp or 0
    cart["items"].append({
        "medicine": medicine,
        "medicine_name": medicine_doc.medicine_name,
        "mrp": medicine_doc.mrp,
        "rate": rate,
        "qty": qty,
        "amount": qty * rate,
        "requires_prescription": medicine_doc.requires_prescription,
        "image": medicine_doc.image,
        "strength": medicine_doc.strength,
        "dosage_form": medicine_doc.dosage_form,
    })
    
    save_cart_data(cart)
    return {"success": True, "cart": cart, "message": _("Added to cart")}


@frappe.whitelist(allow_guest=True)
def update_cart(medicine, qty):
    """Update quantity of a cart item."""
    try:
        qty = int(qty)
    except (ValueError, TypeError):
        qty = 0
    if qty < 0:
        qty = 0
    
    cart = get_cart_data()
    
    for item in cart["items"]:
        if item["medicine"] == medicine:
            if qty == 0:
                cart["items"].remove(item)
            else:
                stock = get_medicine_stock(medicine)
                if stock < 999:
                    item["qty"] = min(qty, int(stock))
                else:
                    item["qty"] = qty
                item["amount"] = item["qty"] * item["rate"]
            break
    
    save_cart_data(cart)
    return {"success": True, "cart": cart}


@frappe.whitelist(allow_guest=True)
def remove_cart_item(medicine):
    """Remove item from cart."""
    cart = get_cart_data()
    cart["items"] = [item for item in cart["items"] if item["medicine"] != medicine]
    save_cart_data(cart)
    return {"success": True, "cart": cart}


@frappe.whitelist(allow_guest=True)
def get_cart():
    """Get current cart contents."""
    cart = get_cart_data()
    
    # Calculate totals with fresh pricing
    subtotal = 0
    requires_prescription = False
    
    cart_items = []
    total_saving = 0
    
    for item in cart.get("items", []):
        # Get fresh pricing from DB
        med = frappe.db.get_value("Medicine Master", item["medicine"],
                                   ["mrp", "selling_rate", "requires_prescription", "medicine_name"],
                                   as_dict=True)
        if not med:
            continue
        
        rate = med.selling_rate or med.mrp or 0
        qty = item["qty"]
        amount = qty * rate
        
        if med.mrp and med.selling_rate:
            saving = (med.mrp - med.selling_rate) * qty
            total_saving += saving
        
        subtotal += amount
        
        if med.requires_prescription:
            requires_prescription = True
        
        cart_items.append({
            "medicine": item["medicine"],
            "medicine_name": med.medicine_name,
            "mrp": med.mrp,
            "rate": rate,
            "qty": qty,
            "amount": amount,
            "requires_prescription": med.requires_prescription,
            "image": item.get("image"),
            "strength": item.get("strength"),
            "dosage_form": item.get("dosage_form"),
        })
    
    cart["items"] = cart_items
    
    # Estimate shipping (free above ₹500)
    shipping = 49 if subtotal < 500 and subtotal > 0 else 0
    coupon_discount = cart.get("coupon_discount", 0)
    grand_total = subtotal - coupon_discount + shipping
    
    result = {
        "items": cart_items,
        "subtotal": subtotal,
        "total_saving": total_saving,
        "coupon_code": cart.get("coupon_code"),
        "coupon_discount": coupon_discount,
        "shipping": shipping,
        "free_shipping_threshold": 500,
        "grand_total": grand_total,
        "item_count": sum(item["qty"] for item in cart_items),
        "requires_prescription": requires_prescription,
        "is_empty": len(cart_items) == 0,
    }
    
    return result


@frappe.whitelist(allow_guest=True)
def clear_cart():
    """Clear entire cart."""
    cart_key = get_cart_key()
    frappe.cache().delete_value(cart_key)
    return {"success": True, "message": _("Cart cleared")}


@frappe.whitelist(allow_guest=True)
def apply_coupon(coupon_code):
    """Apply a coupon code to the cart."""
    if not coupon_code:
        return {"success": False, "message": _("Please enter a coupon code")}
    
    # Check if Coupon Code DocType exists
    try:
        coupon = frappe.db.get_value("Coupon Code", {"coupon_name": coupon_code}, 
                                      ["name", "coupon_type", "rate", "maximum_use", "used", "valid_from", "valid_upto"],
                                      as_dict=True)
    except Exception:
        return {"success": False, "message": _("Coupon system is not configured")}
    
    if not coupon:
        return {"success": False, "message": _("Invalid coupon code")}
    
    # Check validity dates
    from datetime import date
    today = date.today()
    if coupon.valid_from and coupon.valid_from > today:
        return {"success": False, "message": _("Coupon is not yet valid")}
    if coupon.valid_upto and coupon.valid_upto < today:
        return {"success": False, "message": _("Coupon has expired")}
    
    # Check usage
    if coupon.maximum_use and coupon.used and coupon.used >= coupon.maximum_use:
        return {"success": False, "message": _("Coupon usage limit reached")}
    
    # Calculate discount
    cart = get_cart()
    subtotal = cart["subtotal"]
    
    if coupon.coupon_type == "Percentage":
        discount = subtotal * coupon.rate / 100
        if discount > subtotal:
            discount = subtotal
    else:  # Fixed amount
        discount = min(coupon.rate, subtotal)
    
    # Save to cart
    cart_data = get_cart_data()
    cart_data["coupon_code"] = coupon_code
    cart_data["coupon_discount"] = discount
    save_cart_data(cart_data)
    
    return {"success": True, "discount": discount, "message": _("Coupon applied successfully!")}


@frappe.whitelist(allow_guest=True)
def remove_coupon():
    """Remove applied coupon."""
    cart = get_cart_data()
    cart["coupon_code"] = None
    cart["coupon_discount"] = 0
    save_cart_data(cart)
    return {"success": True, "message": _("Coupon removed")}


@frappe.whitelist(allow_guest=True)
def get_cart_count():
    """Get number of items in cart (for badge)."""
    cart = get_cart_data()
    count = sum(item["qty"] for item in cart.get("items", []))
    return {"count": count}


@frappe.whitelist()
def place_order(address_name=None, payment_method="COD", prescription_ref=None, notes=None):
    """Place an order from the cart."""
    try:
        return _place_order(address_name, payment_method, prescription_ref, notes)
    except Exception as e:
        # Log full error for debugging
        error_details = {
            "error": str(e),
            "address_name": address_name,
            "payment_method": payment_method,
            "user": frappe.session.user
        }
        frappe.log_error(f"place_order failed: {str(e)}\n\nDetails: {error_details}", "Pharmacy Order Error")
        
        # Check if it's a validation error we can show to user
        error_str = str(e)
        if "login" in error_str.lower():
            return {"success": False, "message": "Please login to place an order", "redirect": "/login"}
        elif "address" in error_str.lower():
            return {"success": False, "message": error_str}
        elif "empty" in error_str.lower():
            return {"success": False, "message": "Your cart is empty"}
        else:
            return {"success": False, "message": f"Failed to place order: {error_str}"}


def _place_order(address_name=None, payment_method="COD", prescription_ref=None, notes=None):
    """Internal order placement - wrapped by place_order for consistent error handling."""
    frappe.flags.in_import = True  # Skip some validations
    
    cart = get_cart_data()
    if not cart.get("items"):
        frappe.throw(_("Your cart is empty"))

    user = frappe.session.user
    
    # Guest user check - redirect to login
    if user == "Guest":
        frappe.throw(_("Please login to place an order"))
    
    email = frappe.db.get_value("User", user, "email") or user
    full_name = frappe.db.get_value("User", user, "full_name") or user

    # Ensure customer exists
    customer = frappe.db.get_value("Customer", {"email_id": email}, "name")
    if not customer:
        # Create customer
        customer_group = frappe.db.get_single_value("Selling Settings", "customer_group") or "Individual"
        territory = frappe.db.get_single_value("Selling Settings", "territory") or "India"
        customer_doc = frappe.new_doc("Customer")
        customer_doc.customer_name = full_name
        customer_doc.customer_type = "Individual"
        customer_doc.customer_group = customer_group
        customer_doc.territory = territory
        customer_doc.email_id = email
        customer_doc.flags.ignore_permissions = True
        customer_doc.insert(ignore_permissions=True, ignore_mandatory=True)
        customer = customer_doc.name

    # Validate address - must be provided or exist
    if not address_name:
        frappe.throw(_("Please provide a shipping address"))
    
    if not frappe.db.exists("Address", address_name):
        # Try to find existing address
        addresses = frappe.get_all("Address",
            filters={"email_id": email}, fields=["name"], limit=1)
        if addresses:
            address_name = addresses[0].name
        else:
            # Search by customer link
            addr_links = frappe.get_all("Dynamic Link",
                filters={"link_doctype": "Customer", "link_name": customer},
                fields=["parent"])
            if addr_links:
                address_name = addr_links[0].parent
            else:
                frappe.throw(_("Shipping address not found. Please add an address first."))

    # Check address exists
    if not frappe.db.exists("Address", address_name):
        frappe.throw(_("Invalid shipping address"))

    # Rx check — advisory, not blocking. Order is placed with "Prescription Pending" status.
    # The pharmacy will verify the Rx before dispensing.
    rx_required = any(item.get("requires_prescription") for item in cart["items"])

    # Check stock using the same unified stock check as add_to_cart/get_cart
    for item in cart["items"]:
        stock = get_medicine_stock(item["medicine"])
        if stock < item["qty"]:
            frappe.throw(_("Insufficient stock for {0}. Available: {1}, Requested: {2}").format(
                item["medicine_name"], int(stock), item["qty"]))

    # Ensure Item records exist for Sales Order compatibility
    try:
        for cart_item in cart["items"]:
            if not frappe.db.exists("Item", cart_item["medicine"]):
                med = frappe.db.get_value("Medicine Master", cart_item["medicine"],
                    ["medicine_name", "dosage_form", "strength"], as_dict=True)
                item_doc = frappe.new_doc("Item")
                item_doc.item_code = cart_item["medicine"]
                item_doc.item_name = med.medicine_name if med else cart_item["medicine_name"]
                item_doc.item_group = "Products"
                item_doc.stock_uom = "Nos"
                item_doc.is_stock_item = 0
                item_doc.flags.ignore_permissions = True
                item_doc.insert(ignore_permissions=True)
    except Exception as e:
        frappe.log_error(f"Failed to create Item for order: {e}", "Pharmacy Order")

    # Determine company
    company = (frappe.defaults.get_defaults().get("company")
        or frappe.db.get_single_value("Global Defaults", "default_company"))
    if not company:
        companies = frappe.get_all("Company", limit=1, pluck="name")
        company = companies[0] if companies else None
    if not company:
        frappe.throw(_("No Company found. Please set a default company in Global Defaults or create a Company."))

    # Create Sales Order
    so = frappe.new_doc("Sales Order")
    so.customer = customer
    so.transaction_date = frappe.utils.today()
    so.delivery_date = frappe.utils.add_days(frappe.utils.today(), 3)
    so.company = company
    so.shipping_address_name = address_name
    so.customer_address = address_name
    if notes:
        so.notes = notes

    for item in cart["items"]:
        so.append("items", {
            "item_code": item["medicine"],
            "item_name": item["medicine_name"],
            "qty": item["qty"],
            "rate": item["rate"],
            "delivery_date": frappe.utils.add_days(frappe.utils.today(), 3),
        })

    if cart.get("coupon_code"):
        so.coupon_code = cart["coupon_code"]
        if cart["coupon_discount"] > 0:
            so.discount_amount = cart["coupon_discount"]
            so.apply_discount_on = "Grand Total"

    so.flags.ignore_permissions = True
    so.insert(ignore_permissions=True)

    if prescription_ref:
        try:
            frappe.db.set_value("Prescription", prescription_ref, {"sales_invoice": so.name, "status": "Dispensing"})
        except Exception:
            pass

    try:
        so.db_set("custom_order_source", "Website", update_modified=False)
    except Exception:
        pass
    try:
        so.db_set("custom_payment_method", payment_method, update_modified=False)
    except Exception:
        pass

    # Determine initial status
    initial_status = "Prescription Pending" if (rx_required and not prescription_ref) else "Confirmed"

    if payment_method == "COD":
        so.submit()
        create_order_status_record(so, initial_status)
        clear_cart()
        return {"success": True, "order_id": so.name, "payment_required": False}
    elif payment_method == "UPI":
        create_order_status_record(so, "Pending Payment")
        clear_cart()
        upi_id = frappe.db.get_single_value("Pharmacy Settings", "upi_id") or ""
        upi_holder = frappe.db.get_single_value("Pharmacy Settings", "upi_holder_name") or ""
        return {
            "success": True,
            "order_id": so.name,
            "payment_required": True,
            "payment_method": "UPI",
            "upi_id": upi_id,
            "upi_holder_name": upi_holder,
            "grand_total": so.grand_total,
        }
    elif payment_method == "CARD":
        create_order_status_record(so, "Pending Payment")
        clear_cart()
        return {"success": True, "order_id": so.name, "payment_required": True, "payment_method": "CARD"}
    else:
        create_order_status_record(so, "Pending Payment")
        clear_cart()
        return {"success": True, "order_id": so.name, "payment_required": True}


def create_order_status_record(so, status):
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


@frappe.whitelist(allow_guest=True)
def get_checkout_summary():
    """Get checkout summary with cart, user info, and addresses."""
    cart = get_cart()

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
                        "is_shipping": getattr(addr, "is_shipping_address", 0),
                        "is_billing": getattr(addr, "is_primary_billing_address", 0),
                    })
                except Exception:
                    continue
        except Exception:
            pass

    return {
        "cart": cart,
        "user": {
            "full_name": full_name,
            "email": email,
            "mobile": frappe.db.get_value("User", user, "mobile_no") or "",
        },
        "addresses": addresses,
    }


@frappe.whitelist(allow_guest=True)
def confirm_upi_payment(order_id):
    """Confirm a UPI payment manually - submits the order."""
    try:
        if not frappe.db.exists("Sales Order", order_id):
            return {"success": False, "message": _("Order not found")}

        so = frappe.get_doc("Sales Order", order_id)
        if so.docstatus == 1:
            return {"success": True, "order_id": order_id, "message": _("Order already confirmed")}

        so.flags.ignore_permissions = True
        try:
            so.db_set("custom_payment_method", "UPI", update_modified=False)
        except Exception:
            pass
        so.submit()

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
            pe.mode_of_payment = "UPI"
            pe.flags.ignore_permissions = True
            pe.insert(ignore_permissions=True)
            pe.submit()
        except Exception as e:
            frappe.log_error(f"UPI Payment Entry failed: {e}", "Payment")

        return {"success": True, "order_id": order_id, "message": _("Order confirmed! Thank you for your payment.")}
    except Exception as e:
        frappe.log_error(f"UPI confirm error: {e}", "Payment")
        return {"success": False, "message": f"Confirmation error: {str(e)}"}


@frappe.whitelist(allow_guest=True)
def razorpay_pay(order_id):
    """Initiate Razorpay payment for a pending order."""
    try:
        if not frappe.db.exists("Sales Order", order_id):
            return {"success": False, "message": _("Order not found")}

        so = frappe.get_doc("Sales Order", order_id)
        if so.docstatus == 1:
            return {"success": False, "message": _("Order already paid")}

        user = frappe.session.user
        email = frappe.db.get_value("User", user, "email") or ""
        mobile = frappe.db.get_value("User", user, "mobile_no") or ""

        # Get Razorpay credentials (use db.get_single_value to bypass permission checks)
        key_id = frappe.db.get_single_value("Pharmacy Settings", "razorpay_key_id") or None
        key_secret = frappe.db.get_single_value("Pharmacy Settings", "razorpay_key_secret") or None

        if not key_id or not key_secret:
            # Test mode — no real keys configured, submit order directly
            # Return test_mode flag so frontend bypasses Razorpay checkout
            # and calls razorpay_verify directly to submit the order
            return {
                "success": True,
                "test_mode": True,
                "order_id": so.name,
            }

        import razorpay
        client = razorpay.Client(auth=(key_id, key_secret))
        import secrets
        receipt = f"receipt_{secrets.token_hex(4)}"
        razorpay_order = client.order.create({
            "amount": int(so.grand_total * 100),
            "currency": "INR",
            "receipt": receipt,
            "notes": {"order_id": so.name, "customer": so.customer_name},
        })

        return {
            "success": True,
            "gateway": "razorpay",
            "key_id": key_id,
            "amount": razorpay_order["amount"],
            "currency": razorpay_order["currency"],
            "order_id": so.name,
            "razorpay_order_id": razorpay_order["id"],
            "customer_name": so.customer_name,
            "customer_email": email,
            "customer_phone": mobile,
            "prefill": {"name": so.customer_name, "email": email, "contact": mobile},
            "theme": {"color": "#2563eb"},
        }
    except Exception as e:
        frappe.log_error(f"Razorpay init error: {e}", "Payment")
        return {"success": False, "message": f"Payment error: {str(e)}"}


@frappe.whitelist(allow_guest=True)
def razorpay_verify(order_id, razorpay_payment_id, razorpay_order_id, razorpay_signature):
    """Verify Razorpay payment and submit the Sales Order."""
    try:
        if not frappe.db.exists("Sales Order", order_id):
            return {"success": False, "message": _("Order not found")}

        # Verify signature
        key_secret = frappe.db.get_single_value("Pharmacy Settings", "razorpay_key_secret") or None

        if key_secret:
            import razorpay
            params_dict = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            }
            razorpay.Utility.verify_payment_signature(params_dict, key_secret)

        # Complete the order
        so = frappe.get_doc("Sales Order", order_id)
        if so.docstatus == 1:
            return {"success": True, "order_id": order_id, "message": _("Order already confirmed")}

        so.flags.ignore_permissions = True
        try:
            so.db_set("custom_payment_id", razorpay_payment_id, update_modified=False)
        except Exception:
            pass
        try:
            so.db_set("custom_payment_method", "Razorpay", update_modified=False)
        except Exception:
            pass
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
            pe.mode_of_payment = "Razorpay"
            pe.flags.ignore_permissions = True
            pe.insert(ignore_permissions=True)
            pe.submit()
        except Exception as e:
            frappe.log_error(f"Payment Entry creation failed: {e}", "Payment")

        # Order status record is created automatically by doc_events hook on submit
        return {"success": True, "order_id": order_id, "message": _("Payment successful! Order confirmed.")}
    except Exception as e:
        frappe.log_error(f"Razorpay verify error: {e}", "Payment")
        return {"success": False, "message": f"Payment verification error: {str(e)}"}
