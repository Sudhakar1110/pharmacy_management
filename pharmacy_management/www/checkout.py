import frappe
import json

no_cache = 1

def get_context(context):
    """Render the checkout page."""
    # Check if user is logged in
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login#login?redirect_to=/checkout"
        raise frappe.Redirect

    # Handle order placement via POST (avoids frappe.whitelist() API issue)
    if frappe.request.method == "POST":
        return place_order(context)

    context.no_sidebar = True
    context.no_breadcrumbs = True
    context.title = "Checkout"
    context.page = "checkout"

    # Load checkout data server-side
    try:
        from pharmacy_management.api.cart import get_cart
        cart_data = get_cart()

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
                        continue
            except Exception:
                pass

        checkout_data = {
            "cart": cart_data,
            "user": {
                "full_name": full_name,
                "email": email,
                "mobile": frappe.db.get_value("User", user, "mobile_no") or "",
            },
            "addresses": addresses,
        }

        context.checkout_data = json.dumps(checkout_data)
    except Exception as e:
        frappe.log_error(f"Checkout data error: {e}", "Pharmacy Checkout")
        context.checkout_data = json.dumps({"error": str(e)})

    return context


def place_order(context):
    """Process order placement from form POST (server-side, no API call)."""
    from pharmacy_management.api.checkout import create_order as api_create_order

    address_name = frappe.form_dict.get("address_name")
    payment_method = frappe.form_dict.get("payment_method", "COD")
    notes = frappe.form_dict.get("notes", "")
    prescription_ref = frappe.form_dict.get("prescription_ref")

    try:
        result = api_create_order(
            address_name=address_name,
            payment_method=payment_method,
            prescription_ref=prescription_ref or None,
            notes=notes or None,
        )

        if result.get("success"):
            order_id = result.get("order_id")
            if result.get("payment_required"):
                # For online payments, redirect to payment page
                frappe.local.flags.redirect_location = f"/checkout/pay/{order_id}"
            else:
                # For COD, redirect to order tracking
                frappe.local.flags.redirect_location = f"/track-order/{order_id}?success=1"
            raise frappe.Redirect
        else:
            context.error = result.get("message", "Failed to place order")
    except frappe.Redirect:
        raise
    except Exception as e:
        context.error = str(e)
        frappe.log_error(f"Order placement error: {e}", "Pharmacy Checkout")

    # If there's an error, re-render the checkout page with the error
    context.no_sidebar = True
    context.no_breadcrumbs = True
    context.title = "Checkout"
    context.page = "checkout"
    context.checkout_data = json.dumps({"error": context.error, "cart": {"is_empty": False}})
    return context
