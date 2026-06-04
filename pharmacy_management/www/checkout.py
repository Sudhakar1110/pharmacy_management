import frappe
import json
from decimal import Decimal
from datetime import date, datetime

no_cache = 1


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


def get_context(context):
    """Render the checkout page with cart data, saved addresses, and payment config."""
    context.no_sidebar = True
    context.no_breadcrumbs = True
    context.title = "Checkout"

    try:
        from pharmacy_management.api.cart import get_cart

        # Get user info once
        user = frappe.session.user
        user_email = frappe.db.get_value("User", user, "email") or user
        user_full_name = frappe.db.get_value("User", user, "full_name") or user
        user_mobile = frappe.db.get_value("User", user, "mobile_no") or ""

        # Get cart data
        cart_data = get_cart()

        # Get payment config from Pharmacy Settings (single DB call)
        settings = frappe.db.get_singles_dict("Pharmacy Settings")
        upi_id = settings.get("upi_id", "")
        upi_holder = settings.get("upi_holder_name", "")
        razorpay_key = settings.get("razorpay_key_id", "")

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
                            "address_line1": addr.address_line1 or "",
                            "address_line2": addr.address_line2 or "",
                            "city": addr.city or "",
                            "state": addr.state or "",
                            "country": addr.country or "India",
                            "pincode": addr.pincode or "",
                            "phone": addr.phone or "",
                            "email_id": addr.email_id or "",
                            "is_shipping": getattr(addr, "is_shipping_address", 0),
                        })
                    except Exception:
                        continue
            except Exception:
                pass

        checkout_data = {
            "cart": _make_json_safe(cart_data),
            "user": {
                "full_name": user_full_name,
                "email": user_email,
                "mobile": user_mobile,
            },
            "addresses": addresses,
            "payment_config": {
                "upi_id": upi_id,
                "upi_holder_name": upi_holder,
                "razorpay_key_id": razorpay_key,
            },
        }
        context.checkout_data = json.dumps(checkout_data)

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Pharmacy Checkout: get_context failed")
        context.checkout_data = json.dumps({"error": "Unable to load checkout data. Please try again."})

    return context
