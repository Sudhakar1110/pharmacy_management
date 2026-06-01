import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": _("Invoice"), "fieldname": "name", "fieldtype": "Link", "options": "POS Invoice Ext", "width": 140},
        {"label": _("Patient"), "fieldname": "patient_name", "fieldtype": "Data", "width": 150},
        {"label": _("Items"), "fieldname": "total_items", "fieldtype": "Int", "width": 80},
        {"label": _("Subtotal"), "fieldname": "subtotal", "fieldtype": "Currency", "width": 120},
        {"label": _("Discount"), "fieldname": "discount_amount", "fieldtype": "Currency", "width": 100},
        {"label": _("Tax"), "fieldname": "tax_amount", "fieldtype": "Currency", "width": 100},
        {"label": _("Grand Total"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 130},
        {"label": _("Payment Mode"), "fieldname": "payment_mode", "fieldtype": "Data", "width": 120},
        {"label": _("Cashier"), "fieldname": "cashier", "fieldtype": "Link", "options": "User", "width": 120},
    ]

def get_data(filters):
    conditions = "docstatus = 1"
    if filters.get("from_date"):
        conditions += f" AND posting_date >= '{filters['from_date']}'"
    if filters.get("to_date"):
        conditions += f" AND posting_date <= '{filters['to_date']}'"
    if filters.get("payment_mode"):
        conditions += f" AND payment_mode = '{filters['payment_mode']}'"
    return frappe.db.sql(f"""
        SELECT
            p.posting_date, p.name, p.patient_name,
            (SELECT COUNT(*) FROM `tabPOS Invoice Item Ext` WHERE parent=p.name) as total_items,
            p.subtotal, p.discount_amount, p.tax_amount, p.grand_total,
            p.payment_mode, p.cashier
        FROM `tabPOS Invoice Ext` p
        WHERE {conditions}
        ORDER BY p.posting_date DESC, p.creation DESC
    """, as_dict=True)
