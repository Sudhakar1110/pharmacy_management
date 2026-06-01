import frappe
import datetime

def send_expiry_alerts():
    """Daily task to check batch expiry and create/update alerts"""
    today = datetime.date.today()
    batches = frappe.get_all(
        "Medicine Batch",
        filters={"batch_status": ["in", ["Active", "Near Expiry"]]},
        fields=["name", "medicine", "batch_no", "expiry_date", "current_qty", "warehouse"],
    )
    for batch in batches:
        if not batch.expiry_date:
            continue
        expiry = batch.expiry_date if not isinstance(batch.expiry_date, str) else datetime.date.fromisoformat(str(batch.expiry_date))
        days = (expiry - today).days
        if days <= 180:
            level = "Critical" if days <= 30 else "Warning" if days <= 90 else "Info"
            existing = frappe.db.exists("Expiry Alert", {"batch_no": batch.name, "is_resolved": 0})
            if not existing:
                alert = frappe.new_doc("Expiry Alert")
                alert.medicine = batch.medicine
                alert.batch_no = batch.name
                alert.expiry_date = batch.expiry_date
                alert.days_to_expiry = days
                alert.qty = batch.current_qty
                alert.warehouse = batch.warehouse
                alert.alert_level = level
                alert.insert(ignore_permissions=True)
            else:
                frappe.db.set_value("Expiry Alert", existing, {"days_to_expiry": days, "alert_level": level})
    frappe.db.commit()

def dispose_expired_stock():
    """Weekly: mark expired batches"""
    today = datetime.date.today()
    expired = frappe.get_all(
        "Medicine Batch",
        filters={"expiry_date": ["<", today], "batch_status": ["!=", "Disposed"]},
        fields=["name"],
    )
    for b in expired:
        frappe.db.set_value("Medicine Batch", b.name, "batch_status", "Expired")
    frappe.db.commit()
