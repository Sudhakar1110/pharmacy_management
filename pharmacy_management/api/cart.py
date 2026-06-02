import frappe
from frappe import _
import json


def get_cart_key():
    """Get the cart session key for current user."""
    if frappe.session.user and frappe.session.user != "Guest":
        return f"pharmacy_cart:{frappe.session.user}"
    session_id = frappe.session.sid or frappe.local.session.sid
    return f"pharmacy_cart:guest:{session_id}"


def get_cart_data():
    """Retrieve cart from cache."""
    cart_key = get_cart_key()
    cart = frappe.cache().get(cart_key)
    if not cart:
        cart = {
            "items": [],
            "coupon_code": None,
            "coupon_discount": 0,
        }
    return cart


def save_cart_data(cart):
    """Save cart to cache (24 hour expiry)."""
    cart_key = get_cart_key()
    frappe.cache().set(cart_key, cart, expires_in_sec=86400)


def merge_guest_cart_to_user():
    """Merge guest cart into user cart on login."""
    if frappe.session.user == "Guest":
        return
    
    guest_key = f"pharmacy_cart:guest:{frappe.session.sid}"
    guest_cart = frappe.cache().get(guest_key)
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
    frappe.cache().delete(guest_key)


@frappe.whitelist()
def add_to_cart(medicine, qty=1):
    """Add a medicine to cart."""
    qty = int(qty)
    if qty < 1:
        qty = 1
    
    # Validate medicine exists and is active
    medicine_doc = frappe.db.get_value("Medicine Master", medicine, 
                                       ["name", "medicine_name", "mrp", "selling_rate", 
                                        "requires_prescription", "image", "strength", "dosage_form"],
                                       as_dict=True)
    if not medicine_doc:
        frappe.throw(_("Medicine not found"))
    
    # Check stock
    stock = frappe.db.get_value("Bin", {"item_code": medicine}, "actual_qty") or 0
    if stock <= 0:
        frappe.throw(_("{0} is currently out of stock").format(medicine_doc.medicine_name))
    
    cart = get_cart_data()
    
    # Check if already in cart
    for item in cart["items"]:
        if item["medicine"] == medicine:
            item["qty"] += qty
            if item["qty"] > stock:
                item["qty"] = stock
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


@frappe.whitelist()
def update_cart(medicine, qty):
    """Update quantity of a cart item."""
    qty = int(qty)
    if qty < 0:
        qty = 0
    
    cart = get_cart_data()
    
    for item in cart["items"]:
        if item["medicine"] == medicine:
            if qty == 0:
                cart["items"].remove(item)
            else:
                # Check stock
                stock = frappe.db.get_value("Bin", {"item_code": medicine}, "actual_qty") or 0
                item["qty"] = min(qty, stock)
                item["amount"] = item["qty"] * item["rate"]
            break
    
    save_cart_data(cart)
    return {"success": True, "cart": cart}


@frappe.whitelist()
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
    total_discount = 0
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


@frappe.whitelist()
def clear_cart():
    """Clear entire cart."""
    cart_key = get_cart_key()
    frappe.cache().delete(cart_key)
    return {"success": True, "message": _("Cart cleared")}


@frappe.whitelist()
def apply_coupon(coupon_code):
    """Apply a coupon code to the cart."""
    if not coupon_code:
        return {"success": False, "message": _("Please enter a coupon code")}
    
    # Check if coupon exists in ERPNext
    coupon = frappe.db.get_value("Coupon Code", {"coupon_name": coupon_code}, 
                                  ["name", "coupon_type", "rate", "maximum_use", "used", "valid_from", "valid_upto"],
                                  as_dict=True)
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


@frappe.whitelist()
def remove_coupon():
    """Remove applied coupon."""
    cart = get_cart_data()
    cart["coupon_code"] = None
    cart["coupon_discount"] = 0
    save_cart_data(cart)
    return {"success": True, "message": _("Coupon removed")}


@frappe.whitelist()
def get_cart_count():
    """Get number of items in cart (for badge)."""
    cart = get_cart_data()
    count = sum(item["qty"] for item in cart.get("items", []))
    return {"count": count}
