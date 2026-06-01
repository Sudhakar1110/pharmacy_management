import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {}
    columns = [
        {"label":_("Medicine"),"fieldname":"item_code","fieldtype":"Link","options":"Item","width":180},
        {"label":_("Warehouse"),"fieldname":"warehouse","fieldtype":"Link","options":"Warehouse","width":140},
        {"label":_("Batch No"),"fieldname":"batch_no","fieldtype":"Data","width":120},
        {"label":_("Voucher Type"),"fieldname":"voucher_type","fieldtype":"Data","width":130},
        {"label":_("Voucher"),"fieldname":"voucher_no","fieldtype":"Data","width":140},
        {"label":_("Date"),"fieldname":"posting_date","fieldtype":"Date","width":100},
        {"label":_("In Qty"),"fieldname":"actual_qty_in","fieldtype":"Float","width":90},
        {"label":_("Out Qty"),"fieldname":"actual_qty_out","fieldtype":"Float","width":90},
        {"label":_("Balance Qty"),"fieldname":"qty_after_transaction","fieldtype":"Float","width":110},
        {"label":_("Rate"),"fieldname":"valuation_rate","fieldtype":"Currency","width":100},
        {"label":_("Value"),"fieldname":"stock_value_difference","fieldtype":"Currency","width":120},
    ]
    conditions = ""
    if filters.get("item_code"):
        conditions += f" AND sle.item_code = '{filters['item_code']}'"
    if filters.get("warehouse"):
        conditions += f" AND sle.warehouse = '{filters['warehouse']}'"
    if filters.get("from_date"):
        conditions += f" AND sle.posting_date >= '{filters['from_date']}'"
    if filters.get("to_date"):
        conditions += f" AND sle.posting_date <= '{filters['to_date']}'"
    data = frappe.db.sql(f"""
        SELECT sle.item_code, sle.warehouse, sle.batch_no, sle.voucher_type,
               sle.voucher_no, sle.posting_date,
               IF(sle.actual_qty > 0, sle.actual_qty, 0) as actual_qty_in,
               IF(sle.actual_qty < 0, ABS(sle.actual_qty), 0) as actual_qty_out,
               sle.qty_after_transaction, sle.valuation_rate, sle.stock_value_difference
        FROM `tabStock Ledger Entry` sle
        WHERE sle.is_cancelled = 0 {conditions}
        ORDER BY sle.posting_date DESC, sle.posting_time DESC
        LIMIT 500
    """, as_dict=True)
    return columns, data
