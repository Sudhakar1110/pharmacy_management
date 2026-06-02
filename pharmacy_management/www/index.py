import frappe

no_cache = 1
no_sidebar = 1

def get_context(context):
    """Render the homepage."""
    try:
        context.categories = frappe.get_all(
            "Medicine Category",
            filters={"is_active": 1},
            fields=["name", "category_name", "medicine_count"],
            order_by="category_name asc",
        )
        # Get medicine count per category
        for cat in context.categories:
            if not cat.medicine_count:
                cat.medicine_count = frappe.db.count("Medicine Master", {"category": cat.name, "is_active": 1})
    except Exception:
        context.categories = []
    
    context.no_sidebar = True
    context.no_breadcrumbs = True
    context.title = "Pharmacy Management - Buy Medicines Online"
    
    return context
