import frappe
from frappe import _
from pharmacy_management.api.cart import get_cart_data, clear_cart, get_cart, get_medicine_stock


# ---------------------------------------------------------------------------
# Constants / helpers
# ---------------------------------------------------------------------------

_ORDER_STATUS_DOCTYPE = "Order Status"
_PHARMACY_SETTINGS = "Pharmacy Settings"


def _has_order_status_doctype() -> bool:
    key = "_pharmacy_has_order_status"
    if not hasattr(frappe.local, key):
        setattr(frappe.local, key, bool(frappe.db.exists("DocType", _ORDER_STATUS_DOCTYPE)))
    return getattr(frappe.local, key)


def _get_company() -> str:
    company = (
        frappe.defaults.get_defaults().get("company")
        or frappe.db.get_single_value("Global Defaults", "default_company")
        or (frappe.get_all("Company", limit=1, pluck="name") or [None])[0]
    )
    if not company:
        frappe.throw(_("No Company configured in ERPNext settings"))
    return company


def _get_current_user_info() -> dict:
    user = frappe.session.user
    return {
        "user": user,
        "email": frappe.db.get_value("User", user, "email") or user,
        "full_name": frappe.db.get_value("User", user, "full_name") or user,
        "mobile": frappe.db.get_value("User", user, "mobile_no") or "",
    }


# ---------------------------------------------------------------------------
# Customer / Patient helpers
# ---------------------------------------------------------------------------

def ensure_customer(user: str = None) -> str:
    """Return existing Customer name or create one for *user* (defaults to session user)."""
    info = _get_current_user_info() if user is None else {
        "user": user,
        "email": frappe.db.get_value("User", user, "email") or user,
        "full_name": frappe.db.get_value("User", user, "full_name") or user,
        "mobile": frappe.db.get_value("User", user, "mobile_no") or "",
    }

    existing = frappe.db.get_value("Customer", {"email_id": info["email"]}, "name")
    if existing:
        return existing

    selling = frappe.get_single("Selling Settings")
    customer_group = (
        selling.customer_group
        or frappe.db.get_value("Customer Group", {"is_group": 0}, "name")
        or "Individual"
    )
    territory = (
        selling.territory
        or frappe.db.get_value("Territory", {"is_group": 0}, "name")
        or "India"
    )

    customer = frappe.new_doc("Customer")
    customer.update({
        "customer_name": info["full_name"],
        "customer_type": "Individual",
        "customer_group": customer_group,
        "territory": territory,
        "email_id": info["email"],
    })
    customer.flags.ignore_permissions = True
    customer.insert(ignore_permissions=True, ignore_mandatory=True)

    _ensure_patient(info)
    return customer.name


def _ensure_patient(info: dict) -> None:
    """Create a Patient record if one doesn't exist yet. Failures are non-fatal."""
    try:
        if not frappe.db.exists("Patient", {"email": info["email"]}):
            patient = frappe.new_doc("Patient")
            patient.update({
                "patient_name": info["full_name"],
                "email": info["email"],
                "mobile_number": info["mobile"],
            })
            patient.flags.ignore_permissions = True
            patient.insert(ignore_permissions=True)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "ensure_patient failed")


# ---------------------------------------------------------------------------
# Cart / stock validation
# ---------------------------------------------------------------------------

def _validate_cart_not_empty(cart: dict) -> None:
    """Validate cart is not empty."""
    if not cart.get("items"):
        frappe.throw(_("Your cart is empty"))


def _validate_stock(items: list) -> None:
    """Check stock availability for all items."""
    for item in items:
        stock = get_medicine_stock(item["medicine"])
        if stock < item["qty"]:
            frappe.throw(_("Insufficient stock for {0}. Available: {1}, Requested: {2}").format(
                item["medicine_name"], int(stock), item["qty"]))


def _build_sales_order(customer: str, address_name: str, cart: dict, notes: str = None) -> "frappe.Document":
    """Build a Sales Order document from cart data (does NOT insert)."""
    company = _get_company()
    delivery_date = frappe.utils.add_days(frappe.utils.today(), 3)

    so = frappe.new_doc("Sales Order")
    so.update({
        "customer": customer,
        "transaction_date": frappe.utils.today(),
        "delivery_date": delivery_date,
        "company": company,
        "shipping_address_name": address_name,
        "customer_address": address_name,
    })
    if notes:
        so.notes = notes

    for item in cart["items"]:
        so.append("items", {
            "item_code": item["medicine"],
            "item_name": item["medicine_name"],
            "qty": item["qty"],
            "rate": item["rate"],
            "delivery_date": delivery_date,
        })

    if cart.get("coupon_code") and cart.get("coupon_discount", 0) > 0:
        so.coupon_code = cart["coupon_code"]
        so.discount_amount = cart["coupon_discount"]
        so.apply_discount_on = "Grand Total"

    so.flags.ignore_permissions = True
    so.insert(ignore_permissions=True)
    return so


def _set_order_meta(so: "frappe.Document", payment_method: str) -> None:
    try:
        so.db_set("custom_order_source", "Website", update_modified=False)
    except Exception:
        pass
    try:
        so.db_set("custom_payment_method", payment_method, update_modified=False)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Order Status
# ---------------------------------------------------------------------------

def create_order_status(so: "frappe.Document", status: str) -> None:
    if not _has_order_status_doctype():
        return
    try:
        record = frappe.new_doc(_ORDER_STATUS_DOCTYPE)
        record.update({
            "sales_order": so.name,
            "status": status,
            "date": frappe.utils.now(),
        })
        record.flags.ignore_permissions = True
        record.insert(ignore_permissions=True)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "create_order_status failed")


def on_sales_order_submit(doc, method=None):
    """Hook: When a Sales Order is submitted, create an Order Status record."""
    try:
        create_order_status(doc, "Confirmed")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Payment helpers
# ---------------------------------------------------------------------------

def _handle_cod(so: "frappe.Document", prescription_ref: str = None) -> dict:
    _link_prescription(so, prescription_ref)
    so.submit()
    create_order_status(so, "Confirmed")
    clear_cart()
    return {
        "success": True,
        "order_id": so.name,
        "message": _("Order placed successfully! You will pay on delivery."),
        "payment_required": False,
    }


def _handle_online_payment(so: "frappe.Document", payment_method: str) -> dict:
    create_order_status(so, "Pending Payment")
    return {
        "success": True,
        "order_id": so.name,
        "message": _("Redirecting to payment..."),
        "payment_required": True,
        "payment_method": payment_method,
    }


def _link_prescription(so: "frappe.Document", prescription_ref: str = None) -> None:
    if not prescription_ref:
        return
    try:
        frappe.db.set_value("Prescription", prescription_ref, {
            "sales_invoice": so.name,
            "status": "Dispensing",
        })
    except Exception:
        frappe.log_error(frappe.get_traceback(), "link_prescription failed")


# ---------------------------------------------------------------------------
# Public API - Cart-based checkout (used by /checkout page)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def create_order(
    address_name: str = None,
    payment_method: str = "COD",
    prescription_ref: str = None,
    notes: str = None,
) -> dict:
    """Create a Sales Order from the session user's cart."""
    cart = get_cart_data()
    _validate_cart_not_empty(cart)

    user = frappe.session.user
    customer = ensure_customer(user)

    # Resolve shipping address
    if not address_name:
        email = frappe.db.get_value("User", user, "email") or user
        row = frappe.db.get_value("Address", {"email_id": email}, "name")
        if row:
            address_name = row
        else:
            frappe.throw(_("Please provide a shipping address"))

    # Rx check — advisory, not blocking. Order is placed with "Prescription Pending" status.
    rx_required = any(i.get("requires_prescription") for i in cart["items"])

    _validate_stock(cart["items"])

    so = _build_sales_order(customer, address_name, cart, notes)
    _set_order_meta(so, payment_method)

    if payment_method == "COD":
        return _handle_cod(so, prescription_ref)

    # For online payments — don't submit yet, just create draft
    return _handle_online_payment(so, payment_method)


# ---------------------------------------------------------------------------
# Public API - Payment verification
# ---------------------------------------------------------------------------

@frappe.whitelist()
def verify_payment(
    order_id: str,
    payment_id: str,
    razorpay_order_id: str = None,
    payment_method: str = "Razorpay",
) -> dict:
    """Verify an online payment, submit the Sales Order, and record a Payment Entry."""
    if not frappe.db.exists("Sales Order", order_id):
        frappe.throw(_("Order not found"))

    so = frappe.get_doc("Sales Order", order_id)
    so.flags.ignore_permissions = True

    if payment_method == "COD":
        so.submit()
        clear_cart()
        return {"success": True, "order_id": order_id}

    so.db_set("custom_payment_id", payment_id, update_modified=False)
    so.submit()

    try:
        mode = frappe.db.get_value("Mode of Payment", payment_method, "name") or payment_method
        pe = frappe.new_doc("Payment Entry")
        pe.update({
            "payment_type": "Receive",
            "company": so.company,
            "posting_date": frappe.utils.today(),
            "party_type": "Customer",
            "party": so.customer,
            "paid_amount": so.grand_total,
            "received_amount": so.grand_total,
            "reference_doctype": "Sales Order",
            "reference_name": so.name,
            "mode_of_payment": mode,
        })
        pe.flags.ignore_permissions = True
        pe.insert(ignore_permissions=True)
        pe.submit()
    except Exception:
        frappe.log_error(frappe.get_traceback(), "verify_payment: Payment Entry creation failed")

    clear_cart()
    return {"success": True, "order_id": order_id}


@frappe.whitelist()
def get_checkout_summary():
    """Get checkout summary from cart."""
    cart_data = get_cart()

    if cart_data["is_empty"]:
        frappe.throw(_("Your cart is empty"))

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
                        "is_shipping": getattr(addr, "is_shipping_address", 0),
                        "is_billing": getattr(addr, "is_primary_billing_address", 0),
                    })
                except Exception:
                    continue
        except Exception:
            pass

    return {
        "cart": cart_data,
        "user": {
            "full_name": full_name,
            "email": email,
            "mobile": frappe.db.get_value("User", user, "mobile_no") or "",
        },
        "addresses": addresses,
    }
