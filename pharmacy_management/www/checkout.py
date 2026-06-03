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
    """Render the checkout page."""
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login#login?redirect_to=/checkout"
        raise frappe.Redirect

    # POST handling is done via AJAX to cart API, not form submission
    context.no_sidebar = True
    context.no_breadcrumbs = True
    context.title = "Checkout"
    context.page = "checkout"

    try:
        from pharmacy_management.api.cart import get_cart
        cart_data = get_cart()

        user = frappe.session.user
        email = frappe.db.get_value("User", user, "email") or user
        full_name = frappe.db.get_value("User", user, "full_name") or user

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
                        continue
            except Exception:
                pass

        checkout_data = {
            "cart": _make_json_safe(cart_data),
            "user": {"full_name": full_name, "email": email, "mobile": frappe.db.get_value("User", user, "mobile_no") or ""},
            "addresses": addresses,
        }
        context.checkout_data = json.dumps(checkout_data)
    except Exception as e:
        frappe.log_error(f"Checkout data error: {e}", "Pharmacy Checkout")
        context.checkout_data = json.dumps({"error": str(e)})

    return context
