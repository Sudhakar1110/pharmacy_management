import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {}
    columns = [
        {"label":_("Supplier"),"fieldname":"supplier","fieldtype":"Link","options":"Supplier","width":180},
        {"label":_("Medicine"),"fieldname":"item_code","fieldtype":"Link","options":"Item","width":180},
        {"label":_("Total Qty"),"fieldname":"total_qty","fieldtype":"Float","width":100},
        {"label":_("Total Amount"),"fieldname":"total_amount","fieldtype":"Currency","width":130},
        {"label":_("Avg Rate"),"fieldname":"avg_rate","fieldtype":"Currency","width":110},
        {"label":_("Orders"),"fieldname":"order_count","fieldtype":"Int","width":80},
        {"label":_("Last Order"),"fieldname":"last_order","fieldtype":"Date","width":110},
    ]
    conditions = "po.docstatus = 1"
    if filters.get("from_date"):
        conditions += f" AND po.transaction_date >= '{filters['from_date']}'"
    if filters.get("to_date"):
        conditions += f" AND po.transaction_date <= '{filters['to_date']}'"
    if filters.get("supplier"):
        conditions += f" AND po.supplier = '{filters['supplier']}'"
    data = frappe.db.sql(f"""
        SELECT po.supplier, poi.item_code,
               SUM(poi.qty) as total_qty, SUM(poi.amount) as total_amount,
               AVG(poi.rate) as avg_rate, COUNT(DISTINCT po.name) as order_count,
               MAX(po.transaction_date) as last_order
        FROM `tabPurchase Order Item` poi
        JOIN `tabPurchase Order` po ON po.name = poi.parent
        WHERE {conditions}
        GROUP BY po.supplier, poi.item_code
        ORDER BY total_amount DESC
    """, as_dict=True)
    return columns, data
