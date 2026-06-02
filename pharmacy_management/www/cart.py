import frappe

no_cache = 1

def get_context(context):
    """Render the shopping cart page."""
    context.no_sidebar = True
    context.no_breadcrumbs = True
    context.title = "Shopping Cart"
    context.page = "cart"
    return context
