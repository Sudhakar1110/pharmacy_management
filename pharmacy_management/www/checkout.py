import frappe
import json
from decimal import Decimal
from datetime import date, datetime

no_cache = 1


def _make_json_safe(obj):
    """Recursively convert non-JSON-safe types to plain JSON-compatible types."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _make_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_make_json_safe(v) for v in obj]
    return obj


def get_context(context):
    """Render the checkout page with cart data and payment config (no hardcoded addresses)."""
    context.no_sidebar = True
    context.no_breadcrumbs = True
    context.title = "Checkout"
    
    # Pass the CSRF token to the template
    context.csrf_token = frappe.session.csrf_token

    try:
        from pharmacy_management.api.cart import get_cart
        cart_data = get_cart()

        # Payment config from Pharmacy Settings
        upi_id = frappe.db.get_single_value("Pharmacy Settings", "upi_id") or ""
        upi_holder = frappe.db.get_single_value("Pharmacy Settings", "upi_holder_name") or ""
        razorpay_key = frappe.db.get_single_value("Pharmacy Settings", "razorpay_key_id") or ""

        user_info = {
            "full_name": frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user,
            "email": frappe.db.get_value("User", frappe.session.user, "email") or frappe.session.user,
            "mobile": frappe.db.get_value("User", frappe.session.user, "mobile_no") or "",
        }

        checkout_data = {
            "cart": _make_json_safe(cart_data),
            "user": user_info,
            "payment_config": {
                "upi_id": upi_id,
                "upi_holder_name": upi_holder,
                "razorpay_key_id": razorpay_key,
            }
        }
        context.checkout_data = json.dumps(checkout_data)

    except Exception as e:
        frappe.log_error(f"Checkout page error: {e}", "Pharmacy Checkout")
        context.checkout_data = json.dumps({"error": str(e)})

    return context
