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


def get_hardcoded_addresses():
    """Return hardcoded sample addresses that always appear during checkout."""
    return [
        {
            "name": "home",
            "title": "Home",
            "address_line1": "42, Gandhi Nagar, 3rd Cross",
            "address_line2": "Near City Hospital",
            "city": "Bangalore",
            "state": "Karnataka",
            "pincode": "560001",
            "phone": "+91 98765 43210",
            "is_shipping": 1,
            "type": "Home"
        },
        {
            "name": "work",
            "title": "Work",
            "address_line1": "7th Floor, Tech Park Building",
            "address_line2": "MG Road, Ashok Nagar",
            "city": "Bangalore",
            "state": "Karnataka",
            "pincode": "560038",
            "phone": "+91 98765 43211",
            "is_shipping": 0,
            "type": "Work"
        },
        {
            "name": "other",
            "title": "Other",
            "address_line1": "Plot 15, Sri Ram Colony",
            "address_line2": "Near Railway Station",
            "city": "Mysore",
            "state": "Karnataka",
            "pincode": "570001",
            "phone": "+91 98765 43212",
            "is_shipping": 0,
            "type": "Other"
        }
    ]


def get_context(context):
    """Render the checkout page with hardcoded addresses and cart data."""
    context.no_sidebar = True
    context.no_breadcrumbs = True
    context.title = "Checkout"

    try:
        # Get cart via API
        from pharmacy_management.api.cart import get_cart
        cart_data = get_cart()

        # Get UPI config from Pharmacy Settings
        upi_id = frappe.db.get_single_value("Pharmacy Settings", "upi_id") or ""
        upi_holder = frappe.db.get_single_value("Pharmacy Settings", "upi_holder_name") or ""

        # Get Razorpay key for card payments
        razorpay_key = frappe.db.get_single_value("Pharmacy Settings", "razorpay_key_id") or ""

        user_info = {
            "full_name": frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user,
            "email": frappe.db.get_value("User", frappe.session.user, "email") or frappe.session.user,
            "mobile": frappe.db.get_value("User", frappe.session.user, "mobile_no") or "",
        }

        checkout_data = {
            "cart": _make_json_safe(cart_data),
            "addresses": get_hardcoded_addresses(),
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
        context.checkout_data = json.dumps({"error": str(e), "addresses": get_hardcoded_addresses()})

    return context
