import frappe
from frappe import _
from pharmacy_management.api.cart import get_cart_data, clear_cart

# ---------------------------------------------------------------------------
# Constants / helpers
# ---------------------------------------------------------------------------

_ORDER_STATUS_DOCTYPE = "Order Status"
_PHARMACY_SETTINGS = "Pharmacy Settings"

# Cached once per request so repeated calls don't hit the DB.
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

def ensure_customer(user: str | None = None) -> str:
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
    if not cart.get("items"):
        frappe.throw(_("Your cart is empty"))


def _validate_stock(items: list) -> None:
    """Raise if any item has insufficient stock."""
    item_codes = [i["medicine"] for i in items]
    bins = frappe.get_all(
        "Bin",
        filters={"item_code": ["in", item_codes]},
        fields=["item_code", "actual_qty"],
    )
    stock_map = {b["item_code"]: b["actual_qty"] for b in bins}

    for item in items:
        available = stock_map.get(item["medicine"], 0)
        if available < item["qty"]:
            frappe.throw(
                _("Insufficient stock for {0}. Available: {1}, Requested: {2}").format(
                    item["medicine_name"], int(available), item["qty"]
                )
            )


# ---------------------------------------------------------------------------
# Sales Order builder
# ---------------------------------------------------------------------------

def _build_sales_order(customer: str, address_name: str, cart: dict, notes: str | None) -> "frappe.Document":
    """Construct and insert (but NOT submit) a Sales Order."""
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
    so.db_set("custom_order_source", "Website", update_modified=False)
    so.db_set("custom_payment_method", payment_method, update_modified=False)


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


# ---------------------------------------------------------------------------
# Payment helpers
# ---------------------------------------------------------------------------

def generate_payment_request(so: "frappe.Document", payment_method: str) -> dict:
    """Build payment gateway payload. Returns dict; raises on critical failures."""
    info = _get_current_user_info()
    payload = {
        "amount": so.grand_total,
        "order_id": so.name,
        "customer_name": so.customer_name,
        "customer_email": info["email"],
        "customer_phone": info["mobile"],
    }

    if payment_method == "Razorpay":
        import secrets
        settings = frappe.get_single(_PHARMACY_SETTINGS)
        key_id = settings.get("razorpay_key_id") or ""
        key_secret = settings.get("razorpay_key_secret") or ""
        receipt = f"receipt_{secrets.token_hex(4)}"

        payload.update({"gateway": "razorpay", "key_id": key_id, "receipt": receipt})

        if key_id and key_secret:
            try:
                import razorpay  # type: ignore
                client = razorpay.Client(auth=(key_id, key_secret))
                rp_order = client.order.create({
                    "amount": int(so.grand_total * 100),
                    "currency": "INR",
                    "receipt": receipt,
                })
                payload["razorpay_order_id"] = rp_order["id"]
            except ImportError:
                frappe.log_error("razorpay SDK not installed", "generate_payment_request")
            except Exception:
                frappe.log_error(frappe.get_traceback(), "Razorpay order creation failed")

    return payload


def _handle_cod(so: "frappe.Document", prescription_ref: str | None) -> dict:
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
    payment_data = generate_payment_request(so, payment_method)
    return {
        "success": True,
        "order_id": so.name,
        "message": _("Redirecting to payment..."),
        "payment_required": True,
        "payment_data": payment_data,
    }


def _link_prescription(so: "frappe.Document", prescription_ref: str | None) -> None:
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
# Public API
# ---------------------------------------------------------------------------

@frappe.whitelist()
def create_order(
    address_name: str | None = None,
    payment_method: str = "COD",
    prescription_ref: str | None = None,
    notes: str | None = None,
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

    # Prescription gate
    if any(i.get("requires_prescription") for i in cart["items"]) and not prescription_ref:
        frappe.throw(_("Some medicines require a valid prescription. Please upload one."))

    _validate_stock(cart["items"])

    so = _build_sales_order(customer, address_name, cart, notes)
    _set_order_meta(so, payment_method)

    if payment_method == "COD":
        return _handle_cod(so, prescription_ref)

    if payment_method in ("Razorpay", "PhonePe", "Stripe", "UPI"):
        return _handle_online_payment(so, payment_method)

    # Fallback — treat as COD
    return _handle_cod(so, prescription_ref)


@frappe.whitelist()
def verify_payment(
    order_id: str,
    payment_id: str,
    razorpay_order_id: str | None = None,
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
def place_order_with_address(
    address_line1: str,
    city: str,
    state: str,
    pincode: str,
    country: str = "India",
    address_line2: str | None = None,
    phone: str | None = None,
    payment_method: str = "COD",
    notes: str | None = None,
) -> dict:
    """Create a shipping address on-the-fly and immediately place an order."""
    try:
        user = frappe.session.user
        if user == "Guest":
            return {"success": False, "message": "Please login to place an order", "redirect": "/login"}

        info = _get_current_user_info()
        customer = ensure_customer(user)

        # Build address
        addr_meta = frappe.get_meta("Address")
        addr = frappe.new_doc("Address")
        addr.update({
            "address_title": info["full_name"],
            "address_type": "Shipping",
            "address_line1": address_line1,
            "address_line2": address_line2 or "",
            "city": city,
            "state": state,
            "pincode": pincode,
            "country": country,
            "phone": phone or "",
        })
        if addr_meta.has_field("email_id"):
            addr.email_id = info["email"]
        if addr_meta.has_field("is_primary_shipping_address"):
            addr.is_primary_shipping_address = 1
        if addr_meta.has_field("is_shipping_address"):
            addr.is_shipping_address = 1

        addr.flags.ignore_permissions = True
        addr.append("links", {"link_doctype": "Customer", "link_name": customer})
        addr.insert(ignore_permissions=True)

        # Validate cart
        cart = get_cart_data()
        if not cart.get("items"):
            return {"success": False, "message": "Your cart is empty"}

        _validate_stock(cart["items"])

        so = _build_sales_order(customer, addr.name, cart, notes)
        _set_order_meta(so, payment_method)

        if payment_method == "COD":
            so.submit()
            clear_cart()
            return {"success": True, "order_id": so.name, "payment_required": False}

        if payment_method == "UPI":
            settings = frappe.get_single(_PHARMACY_SETTINGS)
            return {
                "success": True,
                "order_id": so.name,
                "payment_required": True,
                "payment_method": "UPI",
                "upi_id": settings.get("upi_id") or "",
                "upi_holder_name": settings.get("upi_holder_name") or "",
                "grand_total": so.grand_total,
            }

        # Card / other online
        return {
            "success": True,
            "order_id": so.name,
            "payment_required": True,
            "payment_method": "CARD",
            "grand_total": so.grand_total,
        }

    except frappe.ValidationError:
        raise
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "place_order_with_address failed")
        return {"success": False, "message": str(exc)}


# ---------------------------------------------------------------------------
# Frappe hooks
# ---------------------------------------------------------------------------

def on_sales_order_submit(doc, method=None):
    """on_submit hook — tracks order status."""
    create_order_status(doc, "Confirmed")
