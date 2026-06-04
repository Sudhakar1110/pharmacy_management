import frappe
import json

no_cache = 1


def get_context(context):
    """Render the payment page for UPI / Card payments."""
    context.no_sidebar = True
    context.no_breadcrumbs = True
    context.title = "Payment"

    order_id = frappe.form_dict.get("order_id", "")
    method = frappe.form_dict.get("method", "UPI")

    if not order_id:
        context.payment_data = json.dumps({"error": "No order ID provided"})
        return context

    try:
        # Fetch order details
        if not frappe.db.exists("Sales Order", order_id):
            context.payment_data = json.dumps({"error": "Order not found"})
            return context

        so = frappe.get_doc("Sales Order", order_id)

        # Get UPI config from Pharmacy Settings
        upi_id = frappe.db.get_single_value("Pharmacy Settings", "upi_id") or ""
        upi_holder = frappe.db.get_single_value("Pharmacy Settings", "upi_holder_name") or ""

        # Get Razorpay config
        razorpay_key_id = frappe.db.get_single_value("Pharmacy Settings", "razorpay_key_id") or ""
        payment_data = {
            "order_id": order_id,
            "method": method,
            "grand_total": float(so.grand_total),
            "customer_name": so.customer_name,
            "items": [
                {
                    "item_name": item.item_name,
                    "qty": item.qty,
                    "rate": float(item.rate),
                    "amount": float(item.amount),
                }
                for item in so.items
            ],
            "upi_id": upi_id,
            "upi_holder_name": upi_holder,
            "razorpay_key_id": razorpay_key_id,
        }

        context.payment_data = json.dumps(payment_data)

    except Exception as e:
        frappe.log_error(f"Payment page error: {e}", "Pharmacy Payment")
        context.payment_data = json.dumps({"error": str(e)})

    return context
