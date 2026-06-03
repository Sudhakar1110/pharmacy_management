import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def get_customer_orders(page=1, limit=10):
    """Get orders for the current customer."""
    user = frappe.session.user
    email = frappe.db.get_value("User", user, "email") or user
    customer = frappe.db.get_value("Customer", {"email_id": email}, "name")
    
    if not customer:
        return {"orders": [], "total": 0, "page": 1, "pages": 1}
    
    page = int(page)
    limit = int(limit)
    offset = (page - 1) * limit
    
    count = frappe.db.count("Sales Order", {"customer": customer, "docstatus": ["!=", 2]})
    
    orders = frappe.get_all(
        "Sales Order",
        filters={"customer": customer, "docstatus": ["!=", 2]},
        fields=["name", "transaction_date", "delivery_date", "grand_total", 
                "status", "docstatus", "total_qty", "total"],
        order_by="transaction_date desc",
        limit=limit,
        offset=offset,
    )
    
    for order in orders:
        # Get items
        items = frappe.get_all(
            "Sales Order Item",
            filters={"parent": order.name},
            fields=["item_code", "item_name", "qty", "rate", "amount"],
        )
        order.items = items
        
        # Get tracking status
        order_status = frappe.db.get_value("Order Status", {"sales_order": order.name}, 
                                           ["status", "date", "estimated_delivery"], as_dict=True)
        order.tracking_status = order_status.status if order_status else None
        order.tracking_date = order_status.date if order_status else None
        order.estimated_delivery = order_status.estimated_delivery if order_status else None
    
    return {
        "orders": orders,
        "total": count,
        "page": page,
        "pages": max(1, (count + limit - 1) // limit),
    }


@frappe.whitelist(allow_guest=True)
def get_order_detail(order_id):
    """Get full details of a single order."""
    if not frappe.db.exists("Sales Order", order_id):
        frappe.throw(_("Order not found"))
    
    so = frappe.get_doc("Sales Order", order_id)
    
    # Verify ownership
    user = frappe.session.user
    email = frappe.db.get_value("User", user, "email") or user
    customer = frappe.db.get_value("Customer", {"email_id": email}, "name")
    
    if so.customer != customer and "System Manager" not in frappe.get_roles(user):
        frappe.throw(_("Access denied"))
    
    items = frappe.get_all(
        "Sales Order Item",
        filters={"parent": so.name},
        fields=["item_code", "item_name", "qty", "rate", "amount", "delivery_date"],
    )
    
    # Get tracking statuses
    tracking = frappe.get_all(
        "Order Status",
        filters={"sales_order": so.name},
        fields=["status", "date", "estimated_delivery", "notes"],
        order_by="date desc",
    )
    
    # Get payment info
    payments = frappe.get_all(
        "Payment Entry",
        filters={"reference_doctype": "Sales Order", "reference_name": so.name, "docstatus": 1},
        fields=["name", "paid_amount", "mode_of_payment", "posting_date"],
    )
    
    # Delivery Note
    delivery_notes = frappe.get_all(
        "Delivery Note Item",
        filters={"against_sales_order": so.name},
        fields=["parent", "qty"],
    )
    
    return {
        "order": so,
        "items": items,
        "tracking": tracking,
        "payments": payments,
        "delivery_notes": delivery_notes,
    }


@frappe.whitelist(allow_guest=True)
def get_customer_profile():
    """Get customer profile info."""
    user = frappe.session.user
    email = frappe.db.get_value("User", user, "email") or user
    full_name = frappe.db.get_value("User", user, "full_name") or user
    mobile = frappe.db.get_value("User", user, "mobile_no") or ""
    
    customer = frappe.db.get_value("Customer", {"email_id": email}, "name")
    
    profile = {
        "full_name": full_name,
        "email": email,
        "mobile": mobile,
    }
    
    if customer:
        customer_doc = frappe.get_doc("Customer", customer)
        profile["customer_name"] = customer_doc.customer_name
        profile["customer_type"] = customer_doc.customer_type
    
    # Get Patient info
    patient = frappe.db.get_value("Patient", {"email": email}, 
                                   ["name", "patient_name", "date_of_birth", "gender", "blood_group",
                                    "allergies", "loyalty_points", "total_purchases"], as_dict=True)
    if patient:
        profile["patient"] = patient
    
    # Get order stats
    if customer:
        profile["total_orders"] = frappe.db.count("Sales Order", {"customer": customer, "docstatus": 1})
        profile["total_spent"] = frappe.db.get_value("Sales Order", 
                                                      {"customer": customer, "docstatus": 1}, "sum(grand_total)") or 0
    
    return profile


@frappe.whitelist(allow_guest=True)
def update_profile(full_name=None, mobile=None, date_of_birth=None, gender=None, blood_group=None):
    """Update customer profile."""
    user = frappe.session.user
    
    if full_name:
        frappe.db.set_value("User", user, "full_name", full_name)
    if mobile:
        frappe.db.set_value("User", user, "mobile_no", mobile)
    
    # Update Patient if exists
    email = frappe.db.get_value("User", user, "email") or user
    patient = frappe.db.get_value("Patient", {"email": email}, "name")
    if patient:
        updates = {}
        if date_of_birth:
            updates["date_of_birth"] = date_of_birth
        if gender:
            updates["gender"] = gender
        if blood_group:
            updates["blood_group"] = blood_group
        if updates:
            frappe.db.set_value("Patient", patient, updates, update_modified=False)
    
    frappe.db.commit()
    return {"success": True, "message": _("Profile updated successfully")}


@frappe.whitelist(allow_guest=True)
def get_addresses():
    """Get all addresses for the current customer."""
    user = frappe.session.user
    email = frappe.db.get_value("User", user, "email") or user
    customer = frappe.db.get_value("Customer", {"email_id": email}, "name")
    
    if not customer:
        return {"addresses": []}
    
    addresses = []
    address_links = frappe.get_all("Dynamic Link", 
        filters={"link_doctype": "Customer", "link_name": customer, "parenttype": "Address"},
        fields=["parent"])
    
    for link in address_links:
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
            "is_shipping": addr.is_primary_shipping_address,
            "is_billing": addr.is_primary_billing_address,
        })
    
    return {"addresses": addresses}


@frappe.whitelist(allow_guest=True)
def save_address(address_line1, city, state, pincode, country="India", address_line2=None, phone=None, is_shipping=0, address_name=None):
    """Create or update a customer address."""
    try:
        user = frappe.session.user
        email = frappe.db.get_value("User", user, "email") or user
        full_name = frappe.db.get_value("User", user, "full_name") or user

        customer = frappe.db.get_value("Customer", {"email_id": email}, "name")
        if not customer:
            customer = ensure_customer_from_user(user)

        if address_name and frappe.db.exists("Address", address_name):
            # Update existing
            addr = frappe.get_doc("Address", address_name)
            addr.address_line1 = address_line1
            addr.address_line2 = address_line2
            addr.city = city
            addr.state = state
            addr.pincode = pincode
            addr.country = country
            addr.phone = phone or addr.phone
            addr.is_primary_shipping_address = int(is_shipping)
            addr.flags.ignore_permissions = True
            addr.save()
            return {"success": True, "address_id": addr.name, "message": _("Address updated")}

        # Create new
        addr = frappe.new_doc("Address")
        addr.address_title = f"{full_name} - {city}"
        addr.address_type = "Shipping"
        addr.address_line1 = address_line1
        addr.address_line2 = address_line2
        addr.city = city
        addr.state = state
        addr.pincode = pincode
        addr.country = country
        addr.phone = phone or ""
        addr.email_id = email
        addr.is_primary_shipping_address = int(is_shipping)
        addr.flags.ignore_permissions = True
        addr.append("links", {
            "link_doctype": "Customer",
            "link_name": customer,
        })
        addr.insert(ignore_permissions=True)

        return {"success": True, "address_id": addr.name, "message": _("Address added successfully")}
    except Exception as e:
        frappe.log_error(f"Save address failed: {e}", "Pharmacy Address")
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def delete_address(address_name):
    """Delete a customer address."""
    if not frappe.db.exists("Address", address_name):
        frappe.throw(_("Address not found"))
    
    frappe.delete_doc("Address", address_name, ignore_permissions=True)
    return {"success": True, "message": _("Address deleted")}


@frappe.whitelist(allow_guest=True)
def track_order(order_id):
    """Track order delivery status."""
    if not frappe.db.exists("Sales Order", order_id):
        frappe.throw(_("Order not found"))
    
    so = frappe.get_doc("Sales Order", order_id)
    
    # Verify ownership
    user = frappe.session.user
    email = frappe.db.get_value("User", user, "email") or user
    customer = frappe.db.get_value("Customer", {"email_id": email}, "name")
    allow_guest = frappe.form_dict.get("guest") == "1"
    
    if not allow_guest and so.customer != customer and "System Manager" not in frappe.get_roles(user):
        frappe.throw(_("Access denied"))
    
    # Collect tracking info
    statuses = frappe.get_all(
        "Order Status",
        filters={"sales_order": so.name},
        fields=["status", "date", "notes"],
        order_by="date asc",
    )
    
    items = frappe.get_all(
        "Sales Order Item",
        filters={"parent": so.name},
        fields=["item_code", "item_name", "qty", "rate", "amount"],
    )
    
    return {
        "order_id": so.name,
        "status": so.status,
        "transaction_date": so.transaction_date,
        "delivery_date": so.delivery_date,
        "grand_total": so.grand_total,
        "customer_name": so.customer_name,
        "items": items,
        "statuses": statuses or [{"status": "Pending", "date": so.transaction_date}],
    }


def ensure_customer_from_user(user):
    """Create a Customer for the current user if none exists."""
    email = frappe.db.get_value("User", user, "email") or user
    full_name = frappe.db.get_value("User", user, "full_name") or user
    
    existing = frappe.db.get_value("Customer", {"email_id": email}, "name")
    if existing:
        return existing
    
    customer = frappe.new_doc("Customer")
    customer.customer_name = full_name
    customer.customer_type = "Individual"
    customer.email_id = email
    customer.flags.ignore_permissions = True
    customer.insert(ignore_permissions=True)
    return customer.name
