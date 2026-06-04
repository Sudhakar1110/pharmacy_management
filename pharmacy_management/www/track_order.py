import frappe

no_cache = 1

def get_context(context, **kwargs):
    """Render the order tracking page."""
    context.no_sidebar = True
    context.no_breadcrumbs = True
    context.title = "Track Order"
    context.success = frappe.form_dict.get("success") == "1"
    context.order_id = ""

    # Try to get order_id from multiple sources
    # 1. URL path kwargs (/track-order/<order_id>) - primary for Frappe routing
    order_id = kwargs.get("order_id")
    source = "route_kwargs" if order_id else None

    # 2. Query parameter (?order_id=XXX) - fallback
    if not order_id:
        order_id = frappe.form_dict.get("order_id")
        source = "query_param" if order_id else None

    # 3. Parse from URL path (/track-order/ORDER-ID) - for direct URL access
    if not order_id:
        path = frappe.local.request.path.strip("/")
        parts = path.split("/")
        if len(parts) >= 2 and parts[0] == "track-order" and parts[1]:
            order_id = parts[1]
            source = "url_path"

    context.order_id = order_id or ""

    context.order = None
    context.items = []
    context.statuses = []
    context.payments = []
    context.needs_payment = False

    if order_id:
        exists = frappe.db.exists("Sales Order", order_id)
        if not exists:
            frappe.log_error(
                f"Track Order: Sales Order '{order_id}' not found (source: {source}, path: {frappe.local.request.path})",
                "Pharmacy Track Order"
            )

        if exists:
            try:
                so = frappe.get_doc("Sales Order", order_id)
                context.order = so
                context.needs_payment = so.docstatus == 0
            except Exception as e:
                frappe.log_error(
                    f"Track Order: Failed to load Sales Order '{order_id}': {e}",
                    "Pharmacy Track Order"
                )

            # Get items directly (independent try/except)
            if context.order:
                try:
                    context.items = frappe.get_all(
                        "Sales Order Item",
                        filters={"parent": context.order.name},
                        fields=["item_code", "item_name", "qty", "rate", "amount"],
                    )
                except Exception:
                    pass

                # Order Status timeline (independent try/except)
                try:
                    context.statuses = frappe.get_all(
                        "Order Status",
                        filters={"sales_order": context.order.name},
                        fields=["status", "date", "notes"],
                        order_by="date asc",
                    ) or [{"status": "Pending", "date": context.order.transaction_date}]
                except Exception:
                    pass

                # Payments (independent try/except)
                try:
                    context.payments = frappe.get_all(
                        "Payment Entry",
                        filters={"reference_doctype": "Sales Order", "reference_name": context.order.name, "docstatus": 1},
                        fields=["name", "paid_amount", "mode_of_payment", "posting_date"],
                    )
                except Exception:
                    pass

    return context
