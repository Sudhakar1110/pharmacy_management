import frappe

no_cache = 1

def get_context(context):
    """Medicine detail page - accessed via /shop/<medicine_name> route."""
    medicine_name = frappe.form_dict.get("medicine_name")

    if not medicine_name:
        frappe.local.flags.redirect_location = "/shop"
        raise frappe.Redirect

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
        frappe.log_error(f"Medicine detail error: {str(e)}", "Pharmacy E-Commerce")
        frappe.local.flags.redirect_location = "/shop"
        raise frappe.Redirect
