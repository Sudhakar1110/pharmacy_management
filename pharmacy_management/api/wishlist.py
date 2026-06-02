import frappe
from frappe import _


def get_wishlist_key():
    """Get wishlist cache key based on user."""
    if frappe.session.user and frappe.session.user != "Guest":
        return f"pharmacy_wishlist:{frappe.session.user}"
    return f"pharmacy_wishlist:guest:{frappe.session.sid}"


@frappe.whitelist(allow_guest=True)
def add_to_wishlist(medicine):
    """Add medicine to wishlist."""
    # Validate
    if not frappe.db.exists("Medicine Master", medicine):
        frappe.throw(_("Medicine not found"))
    
    key = get_wishlist_key()
    wishlist = frappe.cache().get(key) or []
    
    if medicine not in wishlist:
        wishlist.append(medicine)
    
    frappe.cache().set(key, wishlist, expires_in_sec=86400 * 30)  # 30 days
    return {"success": True, "message": _("Added to wishlist")}


@frappe.whitelist(allow_guest=True)
def remove_from_wishlist(medicine):
    """Remove medicine from wishlist."""
    key = get_wishlist_key()
    wishlist = frappe.cache().get(key) or []
    
    if medicine in wishlist:
        wishlist.remove(medicine)
    
    frappe.cache().set(key, wishlist, expires_in_sec=86400 * 30)
    return {"success": True, "message": _("Removed from wishlist")}


@frappe.whitelist(allow_guest=True)
def get_wishlist():
    """Get wishlist with full medicine details."""
    key = get_wishlist_key()
    medicine_names = frappe.cache().get(key) or []
    
    if not medicine_names:
        return {"wishlist": [], "is_empty": True}
    
    medicines = frappe.get_all(
        "Medicine Master",
        filters={"name": ["in", medicine_names], "is_active": 1},
        fields=["name", "medicine_name", "generic_name", "mrp", "selling_rate",
                "strength", "dosage_form", "requires_prescription", "image"],
    )
    
    for med in medicines:
        stock = frappe.db.get_value("Bin", {"item_code": med.name}, "actual_qty") or 0
        med.in_stock = stock > 0
        if med.mrp and med.selling_rate:
            med.discount_percent = round((1 - med.selling_rate / med.mrp) * 100, 1)
    
    return {"wishlist": medicines, "is_empty": len(medicines) == 0}


@frappe.whitelist(allow_guest=True)
def is_in_wishlist(medicine):
    """Check if a medicine is in the wishlist."""
    key = get_wishlist_key()
    wishlist = frappe.cache().get(key) or []
    return {"in_wishlist": medicine in wishlist}


@frappe.whitelist()
def merge_guest_wishlist():
    """Merge guest wishlist into user wishlist on login."""
    if frappe.session.user == "Guest":
        return
    
    guest_key = f"pharmacy_wishlist:guest:{frappe.session.sid}"
    guest_wishlist = frappe.cache().get(guest_key) or []
    if not guest_wishlist:
        return
    
    user_key = get_wishlist_key()
    user_wishlist = frappe.cache().get(user_key) or []
    
    merged = list(set(user_wishlist + guest_wishlist))
    frappe.cache().set(user_key, merged, expires_in_sec=86400 * 30)
    frappe.cache().delete(guest_key)
