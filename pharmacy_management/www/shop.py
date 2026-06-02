import frappe
from frappe import _

no_cache = 1

def get_context(context):
    """Shop homepage - list all medicines with filters."""
    context.title = "Shop Medicines"
    context.page = "shop"
    
    # Get categories for filter
    try:
        context.categories = frappe.get_all(
            "Medicine Category",
            filters={"is_active": 1},
            fields=["name", "category_name"],
            order_by="category_name asc",
        )
        for cat in context.categories:
            cat.medicine_count = frappe.db.count("Medicine Master", {"category": cat.name, "is_active": 1})
    except Exception:
        context.categories = []
    
    # Get dosage forms
    try:
        context.dosage_forms = frappe.db.sql("""
            SELECT DISTINCT dosage_form
            FROM `tabMedicine Master`
            WHERE is_active = 1 AND dosage_form IS NOT NULL AND dosage_form != ''
            ORDER BY dosage_form ASC
        """, as_dict=True)
    except Exception:
        context.dosage_forms = []
    
    # Get schedules
    try:
        context.schedules = frappe.db.sql("""
            SELECT DISTINCT schedule
            FROM `tabMedicine Master`
            WHERE is_active = 1 AND schedule IS NOT NULL AND schedule != ''
            ORDER BY schedule ASC
        """, as_dict=True)
    except Exception:
        context.schedules = []
    
    context.selected_category = frappe.form_dict.get("category", "")
    context.no_sidebar = True
    context.no_breadcrumbs = True
    
    return context
