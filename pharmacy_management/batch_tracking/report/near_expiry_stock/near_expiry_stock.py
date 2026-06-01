import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {}
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    return columns, data, None, chart

def get_columns():
    return [
        {"label":_("Medicine"),"fieldname":"medicine","fieldtype":"Link","options":"Medicine Master","width":200},
        {"label":_("Medicine Name"),"fieldname":"medicine_name","fieldtype":"Data","width":180},
        {"label":_("Batch No"),"fieldname":"batch_no","fieldtype":"Data","width":130},
        {"label":_("Expiry Date"),"fieldname":"expiry_date","fieldtype":"Date","width":110},
        {"label":_("Days to Expiry"),"fieldname":"days_to_expiry","fieldtype":"Int","width":120},
        {"label":_("Qty"),"fieldname":"current_qty","fieldtype":"Float","width":80},
        {"label":_("MRP"),"fieldname":"mrp","fieldtype":"Currency","width":100},
        {"label":_("Value"),"fieldname":"value","fieldtype":"Currency","width":120},
        {"label":_("Warehouse"),"fieldname":"warehouse","fieldtype":"Link","options":"Warehouse","width":140},
        {"label":_("Status"),"fieldname":"batch_status","fieldtype":"Data","width":110},
    ]

def get_data(filters):
    threshold = filters.get("days_threshold") or 180
    return frappe.db.sql(f"""
        SELECT
            b.medicine, m.medicine_name, b.batch_no, b.expiry_date,
            DATEDIFF(b.expiry_date, CURDATE()) as days_to_expiry,
            b.current_qty, b.mrp,
            (b.current_qty * b.mrp) as value,
            b.warehouse, b.batch_status
        FROM `tabMedicine Batch` b
        JOIN `tabMedicine Master` m ON m.name = b.medicine
        WHERE DATEDIFF(b.expiry_date, CURDATE()) <= {threshold}
          AND b.batch_status != 'Disposed'
          AND b.current_qty > 0
        ORDER BY days_to_expiry ASC
    """, as_dict=True)

def get_chart(data):
    labels = [d.medicine_name[:20] for d in data[:10]]
    values = [d.days_to_expiry for d in data[:10]]
    return {
        "data": {"labels": labels, "datasets": [{"name": "Days to Expiry", "values": values}]},
        "type": "bar", "colors": ["#e74c3c"]
    }
