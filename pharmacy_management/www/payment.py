import frappe

no_cache = 1


def get_context(context):
    """Redirect to checkout — payment is handled on the checkout page via modals."""
    frappe.local.flags.redirect_location = "/checkout"
    raise frappe.Redirect
