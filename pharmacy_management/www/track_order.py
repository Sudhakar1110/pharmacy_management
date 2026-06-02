import frappe

no_cache = 1

def get_context(context):
    """Render the order tracking page."""
    context.no_sidebar = True
    context.no_breadcrumbs = True
    context.title = "Track Order"
    context.success = frappe.form_dict.get("success") == "1"
    
    # Get order_id from URL path
    path = frappe.local.request.path
    parts = path.strip('/').split('/')
    
    context.order = None
    context.items = []
    context.statuses = []
    context.payments = []
    
    if len(parts) >= 2 and parts[1] != '' and parts[1] != 'track-order':
        order_id = parts[1]
        
        if frappe.db.exists("Sales Order", order_id):
            try:
                from pharmacy_management.api.customer import track_order
                result = track_order(order_id)
                context.order = frappe.get_doc("Sales Order", order_id)
                context.items = result["items"]
                context.statuses = result["statuses"]
                
                # Get payments
                context.payments = frappe.get_all(
                    "Payment Entry",
                    filters={"reference_doctype": "Sales Order", "reference_name": order_id, "docstatus": 1},
                    fields=["name", "paid_amount", "mode_of_payment", "posting_date"],
                )
            except Exception:
                pass
    
    return context
