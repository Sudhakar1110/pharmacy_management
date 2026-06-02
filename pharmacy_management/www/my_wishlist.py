import frappe

no_cache = 1

def get_context(context):
    """Render my wishlist page."""
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login#login?redirect_to=/my-wishlist"
        raise frappe.Redirect
    
    context.no_sidebar = True
    context.no_breadcrumbs = True
    context.title = "My Wishlist"
    return context
