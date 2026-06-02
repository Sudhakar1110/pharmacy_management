import frappe

no_cache = 1

def get_context(context):
    context.title = "Test Page"
    context.message = "Hello! If you can see this, Frappe www pages are working."
    context.doctypes = frappe.get_all("DocType", pluck="name", limit=5)
    return context
