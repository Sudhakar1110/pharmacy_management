import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {}
    columns = get_columns()
    conditions = get_conditions(filters)
    data = frappe.db.sql(f"""
        SELECT sle.item_code, sle.warehouse, sle.batch_no, sle.voucher_type,
               sle.voucher_no, sle.posting_date,
               IF(sle.actual_qty > 0, sle.actual_qty, 0) as actual_qty_in,
               IF(sle.actual_qty < 0, ABS(sle.actual_qty), 0) as actual_qty_out,
               sle.qty_after_transaction, sle.valuation_rate, sle.stock_value_difference
        FROM `tabStock Ledger Entry` sle
        INNER JOIN `tabItem` i ON i.name = sle.item_code
        INNER JOIN `tabMedicine Master` mm ON mm.name = sle.item_code
        WHERE sle.is_cancelled = 0 {conditions}
        ORDER BY sle.posting_date DESC, sle.posting_time DESC
        LIMIT 500
    """, filters, as_dict=True)
    return columns, data


def get_columns():
    return [
        {"label":_("Medicine"),"fieldname":"item_code","fieldtype":"Link","options":"Item","width":180},
        {"label":_("Warehouse"),"fieldname":"warehouse","fieldtype":"Link","options":"Warehouse","width":140},
        {"label":_("Batch No"),"fieldname":"batch_no","fieldtype":"Data","width":120},
        {"label":_("Voucher Type"),"fieldname":"voucher_type","fieldtype":"Data","width":130},
        {"label":_("Voucher No"),"fieldname":"voucher_no","fieldtype":"Dynamic Link","options":"voucher_type","width":140},
        {"label":_("Date"),"fieldname":"posting_date","fieldtype":"Date","width":100},
        {"label":_("In Qty"),"fieldname":"actual_qty_in","fieldtype":"Float","width":90},
        {"label":_("Out Qty"),"fieldname":"actual_qty_out","fieldtype":"Float","width":90},
        {"label":_("Balance Qty"),"fieldname":"qty_after_transaction","fieldtype":"Float","width":110},
        {"label":_("Rate"),"fieldname":"valuation_rate","fieldtype":"Currency","width":100},
        {"label":_("Value"),"fieldname":"stock_value_difference","fieldtype":"Currency","width":120},
    ]


def get_conditions(filters):
    conditions = ""
    if filters.get("item_code"):
        conditions += " AND sle.item_code = %(item_code)s"
    if filters.get("warehouse"):
        conditions += " AND sle.warehouse = %(warehouse)s"
    if filters.get("from_date"):
        conditions += " AND sle.posting_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " AND sle.posting_date <= %(to_date)s"
    if filters.get("batch_no"):
        conditions += " AND sle.batch_no = %(batch_no)s"
    if filters.get("voucher_type"):
        conditions += " AND sle.voucher_type = %(voucher_type)s"
    return conditions


@frappe.whitelist()
def get_filters():
    filters = [
        {
            "fieldname": "item_code",
            "label": _("Medicine"),
            "fieldtype": "Link",
            "options": "Item",
        },
        {
            "fieldname": "warehouse",
            "label": _("Warehouse"),
            "fieldtype": "Link",
            "options": "Warehouse",
        },
        {
            "fieldname": "batch_no",
            "label": _("Batch No"),
            "fieldtype": "Link",
            "options": "Batch",
        },
        {
            "fieldname": "voucher_type",
            "label": _("Voucher Type"),
            "fieldtype": "Select",
            "options": ["", "Stock Entry", "Purchase Receipt", "Sales Invoice", "Stock Reconciliation", "POS Invoice"],
        },
        {
            "fieldname": "from_date",
            "label": _("From Date"),
            "fieldtype": "Date",
        },
        {
            "fieldname": "to_date",
            "label": _("To Date"),
            "fieldtype": "Date",
            "default": frappe.utils.today(),
        },
    ]
    return filters
