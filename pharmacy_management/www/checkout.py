import json
from decimal import Decimal
from datetime import date, datetime

import frappe

no_cache = 1


# ---------------------------------------------------------------------------
# JSON serialisation helper
# ---------------------------------------------------------------------------

def _make_json_safe(obj):
    """Recursively convert non-JSON-serialisable types to plain Python equivalents."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _make_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_make_json_safe(v) for v in obj]
    return obj


# ---------------------------------------------------------------------------
# Page context
# ---------------------------------------------------------------------------

def get_context(context):
    """Render the checkout page with cart data, saved addresses, and payment config."""
    context.no_sidebar = True
    context.no_breadcrumbs = True
    context.title = "Checkout"
    context.csrf_token = frappe.session.csrf_token

    try:
        from pharmacy_management.api.cart import get_cart

        # --- single DB round-trips -------------------------------------------

        # 1. All Pharmacy Settings fields in one call
        settings = frappe.db.get_singles_dict("Pharmacy Settings")

        # 2. All User fields in one call
        user = frappe.db.get_value(
            "User",
            frappe.session.user,
            ["full_name", "email", "mobile_no"],
            as_dict=True,
        ) or {}

        # ---------------------------------------------------------------------

        cart_data = get_cart()

        # Payment config from Pharmacy Settings
        upi_id = frappe.db.get_single_value("Pharmacy Settings", "upi_id") or ""
        upi_holder = frappe.db.get_single_value("Pharmacy Settings", "upi_holder_name") or ""
        razorpay_key = frappe.db.get_single_value("Pharmacy Settings", "razorpay_key_id") or ""

        user_email = frappe.db.get_value("User", frappe.session.user, "email") or frappe.session.user
        user_info = {
            "full_name": frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user,
            "email": user_email,
            "mobile": frappe.db.get_value("User", frappe.session.user, "mobile_no") or "",
        }

        # Fetch saved addresses
        addresses = []
        customer = frappe.db.get_value("Customer", {"email_id": user_email}, "name")
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
                            "address_title": addr.address_title,
                            "address_type": addr.address_type,
                            "address_line1": addr.address_line1,
                            "address_line2": addr.address_line2,
                            "city": addr.city,
                            "state": addr.state,
                            "country": addr.country,
                            "pincode": addr.pincode,
                            "phone": addr.phone,
                            "email_id": addr.email_id,
                            "is_shipping": getattr(addr, "is_shipping_address", 0),
                        })
                    except Exception:
                        continue
            except Exception:
                pass

        checkout_data = {
            "cart": _make_json_safe(cart_data),
            "user": user_info,
            "addresses": addresses,
            "payment_config": {
                "upi_id":         settings.get("upi_id", ""),
                "upi_holder_name": settings.get("upi_holder_name", ""),
                "razorpay_key_id": settings.get("razorpay_key_id", ""),
            },
        })

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Pharmacy Checkout: get_context failed")
        # Never leak internal error strings to the browser
        context.checkout_data = json.dumps({"error": "Unable to load checkout data. Please try again."})
