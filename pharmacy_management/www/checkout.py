import frappe

no_cache = 1

def get_context(context):
    """Render the checkout page."""
    # Check if user is logged in
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login#login?redirect_to=/checkout"
        raise frappe.Redirect
    
    context.no_sidebar = True
    context.no_breadcrumbs = True
    context.title = "Checkout"
    context.page = "checkout"
    return context
