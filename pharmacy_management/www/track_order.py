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
        # Load the Sales Order directly
        try:
            so = frappe.get_doc("Sales Order", order_id)
            context.order = so
            context.needs_payment = so.docstatus == 0
            
            # Get items directly
            context.items = frappe.get_all(
                "Sales Order Item",
                filters={"parent": so.name},
                fields=["item_code", "item_name", "qty", "rate", "amount"],
            )
            
            # Get Order Status timeline
            context.statuses = frappe.get_all(
                "Order Status",
                filters={"sales_order": so.name},
                fields=["status", "date", "notes"],
                order_by="date asc",
            ) or [{"status": "Pending", "date": so.transaction_date}]
            
            # Get payments
            context.payments = frappe.get_all(
                "Payment Entry",
                filters={"reference_doctype": "Sales Order", "reference_name": so.name, "docstatus": 1},
                fields=["name", "paid_amount", "mode_of_payment", "posting_date"],
            )
        except Exception:
            pass
    
    return context
