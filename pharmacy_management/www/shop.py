import frappe
from frappe import _

no_cache = 1

def get_context(context):
    """Shop homepage - list all medicines with filters."""
    context.title = "Shop Medicines"
    context.page = "shop"
    
    # Get path for medicine detail
    path = frappe.local.request.path
    parts = path.strip('/').split('/')
    
    if len(parts) >= 2 and parts[1] != '' and parts[1] != 'shop':
        # This is a medicine detail page
        medicine_name = parts[1]
        return get_medicine_detail(context, medicine_name)
    
    # Get categories for filter
    try:
        context.categories = frappe.get_all(
            "Medicine Category",
            filters={"is_active": 1},
            fields=["name", "category_name"],
            order_by="category_name asc",
        )
        # Get medicine count
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
    
    # Check for query param
    context.selected_category = frappe.form_dict.get("category", "")
    
    context.no_sidebar = True
    context.no_breadcrumbs = True
    
    return context


def get_medicine_detail(context, medicine_name):
    """Render medicine detail page."""
    from pharmacy_management.api.medicine import get_medicine_details as get_details
    
    try:
        result = get_details(medicine_name)
        context.medicine = result["medicine"]
        context.stock = result["stock"]
        context.in_stock = result["in_stock"]
        context.batches = result["batches"]
        context.related_medicines = result["related_medicines"]
        context.manufacturer = result["manufacturer"]
        
        # Calculate discount
        med = context.medicine
        if med.mrp and med.selling_rate and med.mrp > med.selling_rate:
            context.discount = round((1 - med.selling_rate / med.mrp) * 100, 1)
        else:
            context.discount = 0
        
        # Get composition
        if med.composition:
            try:
                context.composition = frappe.get_doc("Drug Composition", med.composition)
            except Exception:
                context.composition = None
        else:
            context.composition = None
        
        # Check wishlist
        from pharmacy_management.api.wishlist import is_in_wishlist
        context.in_wishlist = is_in_wishlist(medicine_name)["in_wishlist"]
        
        context.title = f"{med.medicine_name} - Buy Online"
        context.page = "medicine_detail"
        context.template = "templates/pages/medicine_detail.html"
        context.no_sidebar = True
        context.no_breadcrumbs = True
        
        return context
    except Exception as e:
        frappe.local.flags.redirect_location = "/shop"
        raise frappe.Redirect
