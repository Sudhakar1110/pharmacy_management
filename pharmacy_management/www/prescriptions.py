import frappe

no_cache = 1

def get_context(context):
    """Render the prescription upload page."""
    context.no_sidebar = True
    context.no_breadcrumbs = True
    context.title = "Upload Prescription"
    return context
