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
    """Render the checkout page with cart data and payment config."""
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

        context.checkout_data = json.dumps({
            "cart": _make_json_safe(cart_data),
            "user": {
                "full_name": user.get("full_name") or frappe.session.user,
                "email":     user.get("email")     or frappe.session.user,
                "mobile":    user.get("mobile_no") or "",
            },
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
