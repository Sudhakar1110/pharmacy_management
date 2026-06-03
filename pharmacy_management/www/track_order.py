import frappe

no_cache = 1

def get_context(context):
    """Render the order tracking page."""
    context.no_sidebar = True
    context.no_breadcrumbs = True
    context.title = "Track Order"
    context.success = frappe.form_dict.get("success") == "1"
    
    # Get order_id from URL params (set by route rule or query string)
    order_id = frappe.form_dict.get("order_id")
    
    context.order = None
    context.items = []
    context.statuses = []
    context.payments = []
    context.needs_payment = False
    context.payment_method = None
    
    if order_id and frappe.db.exists("Sales Order", order_id):
        try:
            from pharmacy_management.api.customer import track_order
            result = track_order(order_id)
            so = frappe.get_doc("Sales Order", order_id)
            context.order = so
            context.items = result["items"]
            context.statuses = result["statuses"]
            
            # Determine if payment is needed
            # Order is in Draft (docstatus=0) with status 'Pending Payment' → needs payment
            context.needs_payment = (
                so.docstatus == 0
                and result.get("statuses", [])
                and result["statuses"][0].get("status") == "Pending Payment"
            )
            
            # Get payments
            context.payments = frappe.get_all(
                "Payment Entry",
                filters={"reference_doctype": "Sales Order", "reference_name": order_id, "docstatus": 1},
                fields=["name", "paid_amount", "mode_of_payment", "posting_date"],
            )
        except Exception:
            pass
    
    return context
