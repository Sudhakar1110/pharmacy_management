import frappe
import json
from decimal import Decimal
from datetime import date, datetime

no_cache = 1


def _make_json_safe(obj):
    """Recursively convert non-JSON-safe types to plain JSON-compatible types."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _make_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_make_json_safe(v) for v in obj]
    return obj


def get_context(context):
    """Render the order confirmation page."""
    context.no_sidebar = True
    context.no_breadcrumbs = True
    context.title = "Order Confirmation"

    order_id = frappe.form_dict.get("order_id", "")

    if not order_id:
        context.order_data = json.dumps({"error": "No order ID provided"})
        return context

    try:
        if not frappe.db.exists("Sales Order", order_id):
            context.order_data = json.dumps({"error": "Order not found"})
            return context

        so = frappe.get_doc("Sales Order", order_id)

        # Get address details
        address_name = so.shipping_address_name or so.customer_address
        address_info = {}
        if address_name and frappe.db.exists("Address", address_name):
            try:
                addr = frappe.get_doc("Address", address_name)
                address_info = {
                    "address_line1": addr.address_line1,
                    "address_line2": addr.address_line2,
                    "city": addr.city,
                    "state": addr.state,
                    "pincode": addr.pincode,
                    "phone": addr.phone,
                }
            except Exception:
                pass

        # Get order status
        order_status = "Pending"
        try:
            if frappe.db.exists("DocType", "Order Status"):
                status_record = frappe.get_all("Order Status",
                    filters={"sales_order": order_id},
                    fields=["status", "date"],
                    order_by="date desc",
                    limit=1)
                if status_record:
                    order_status = status_record[0].status
        except Exception:
            pass

        # Get payment method
        payment_method = "COD"
        try:
            pm = so.get("custom_payment_method")
            if pm:
                payment_method = pm
        except Exception:
            # Check if order status record has payment info
            try:
                if frappe.db.exists("DocType", "Order Status"):
                    os_doc = frappe.get_all("Order Status",
                        filters={"sales_order": order_id},
                        fields=["status"],
                        order_by="date desc",
                        limit=1)
                    if os_doc:
                        payment_method = os_doc[0].status
            except Exception:
                pass

        order_data = {
            "order_id": order_id,
            "customer_name": so.customer_name,
            "transaction_date": so.transaction_date.isoformat() if hasattr(so.transaction_date, 'isoformat') else str(so.transaction_date),
            "delivery_date": so.delivery_date.isoformat() if hasattr(so.delivery_date, 'isoformat') else str(so.delivery_date),
            "grand_total": float(so.grand_total),
            "total_qty": float(so.total_qty),
            "status": order_status,
            "payment_method": payment_method,
            "docstatus": so.docstatus,
            "address": address_info,
            "items": [
                {
                    "item_code": item.item_code,
                    "item_name": item.item_name,
                    "qty": item.qty,
                    "rate": float(item.rate),
                    "amount": float(item.amount),
                }
                for item in so.items
            ],
        }

        context.order_data = json.dumps(_make_json_safe(order_data))

    except Exception as e:
        frappe.log_error(f"Order confirmation page error: {e}", "Pharmacy Confirmation")
        context.order_data = json.dumps({"error": str(e)})

    return context
