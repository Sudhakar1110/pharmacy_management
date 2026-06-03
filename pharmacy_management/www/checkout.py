import frappe
import json
from urllib.parse import quote

no_cache = 1

def get_context(context):
    """Render the checkout page."""
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login#login?redirect_to=/checkout"
        raise frappe.Redirect

    if frappe.request.method == "POST":
        return place_order(context)

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
            "cart": cart_data,
            "user": {"full_name": full_name, "email": email, "mobile": frappe.db.get_value("User", user, "mobile_no") or ""},
            "addresses": addresses,
        }
        context.checkout_data = json.dumps(checkout_data)
    except Exception as e:
        frappe.log_error(f"Checkout data error: {e}", "Pharmacy Checkout")
        context.checkout_data = json.dumps({"error": str(e)})

    return context


def place_order(context):
    """Process order placement directly (no import from api/checkout.py)."""
    from pharmacy_management.api.cart import get_cart_data, clear_cart

    address_name = frappe.form_dict.get("address_name")
    payment_method = frappe.form_dict.get("payment_method", "COD")
    notes = frappe.form_dict.get("notes", "")
    prescription_ref = frappe.form_dict.get("prescription_ref")

    try:
        cart = get_cart_data()
        if not cart.get("items"):
            raise ValueError("Your cart is empty")

        user = frappe.session.user
        email = frappe.db.get_value("User", user, "email") or user
        full_name = frappe.db.get_value("User", user, "full_name") or user

        # Ensure customer exists
        customer = frappe.db.get_value("Customer", {"email_id": email}, "name")
        if not customer:
            customer = frappe.new_doc("Customer")
            customer.customer_name = full_name
            customer.customer_type = "Individual"
            customer.email_id = email
            customer.flags.ignore_permissions = True
            customer.insert(ignore_permissions=True)

        # Validate address
        if not address_name or not frappe.db.exists("Address", address_name):
            addresses = frappe.get_all("Address",
                filters={"email_id": email}, fields=["name"], limit=1)
            if addresses:
                address_name = addresses[0].name
            else:
                raise ValueError("Please provide a shipping address")

        # Validate prescription
        rx_required = any(item.get("requires_prescription") for item in cart["items"])
        if rx_required and not prescription_ref:
            raise ValueError("Some medicines require a valid prescription. Please upload one.")

        # Check stock
        for item in cart["items"]:
            stock = frappe.db.get_value("Bin", {"item_code": item["medicine"]}, "actual_qty") or 0
            if stock < item["qty"]:
                raise ValueError(f"Insufficient stock for {item['medicine_name']}. Available: {int(stock)}, Requested: {item['qty']}")

        # Create Sales Order
        so = frappe.new_doc("Sales Order")
        so.customer = customer
        so.transaction_date = frappe.utils.today()
        so.delivery_date = frappe.utils.add_days(frappe.utils.today(), 3)
        so.company = frappe.defaults.get_defaults().get("company") or frappe.db.get_single_value("Global Defaults", "default_company")
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

        so.db_set("custom_order_source", "Website", update_modified=False)
        so.db_set("custom_payment_method", payment_method, update_modified=False)

        if payment_method == "COD":
            so.submit()
            create_order_status(so, "Confirmed")
            clear_cart()
            frappe.local.flags.redirect_location = f"/track-order/{so.name}"
            raise frappe.Redirect
        else:
            create_order_status(so, "Pending Payment")
            clear_cart()
            frappe.local.flags.redirect_location = f"/track-order/{so.name}"
            raise frappe.Redirect

    except frappe.Redirect:
        raise
    except ValueError as e:
        frappe.log_error(f"Order error: {e}", "Pharmacy Checkout")
        frappe.local.flags.redirect_location = f"/checkout?order_error={quote(str(e))}"
        raise frappe.Redirect
    except Exception as e:
        frappe.log_error(f"Order error: {e}", "Pharmacy Checkout")
        frappe.local.flags.redirect_location = f"/checkout?order_error={quote(str(e))}"
        raise frappe.Redirect


def create_order_status(so, status):
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
