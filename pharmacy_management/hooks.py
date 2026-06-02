from . import __version__ as app_version

app_name = "pharmacy_management"
app_title = "Pharmacy Management"
app_publisher = "Your Company"
app_description = "Complete Pharmacy E-Commerce + Management System for ERPNext v15+"
app_email = "admin@yourcompany.com"
app_license = "MIT"
app_version = app_version

# Required Apps
required_apps = ["erpnext"]

# Includes in <head>
app_include_css = "/assets/pharmacy_management/css/pharmacy.css"
app_include_js = "/assets/pharmacy_management/js/pharmacy.js"

# Website Routes (Frappe www)
# /shop/<name> routes to medicine detail page
website_route_rules = [
    ("/shop/<name>", "medicine"),
]

# Website page titles
website_page_title = "Pharmacy Management"

# Document Events
doc_events = {
    "POS Invoice": {
        "on_submit": "pharmacy_management.pos.doctype.pos_invoice_ext.pos_invoice_ext.on_submit",
    },
    "Purchase Order": {
        "on_submit": "pharmacy_management.procurement.doctype.purchase_order_ext.purchase_order_ext.on_submit",
    },
    "Prescription": {
        "on_submit": "pharmacy_management.prescription.doctype.prescription.prescription.on_submit",
    },
    "Medicine Batch": {
        "before_save": "pharmacy_management.inventory.doctype.medicine_batch.medicine_batch.check_expiry",
    },
    "Sales Order": {
        "on_submit": "pharmacy_management.api.checkout.on_sales_order_submit",
    },
}

# Scheduled Tasks
scheduler_events = {
    "daily": [
        "pharmacy_management.batch_tracking.tasks.send_expiry_alerts",
        "pharmacy_management.inventory.tasks.check_reorder_levels",
        "pharmacy_management.compliance.tasks.check_license_expiry",
    ],
    "weekly": [
        "pharmacy_management.batch_tracking.tasks.dispose_expired_stock",
    ],
}

# Fixtures
fixtures = [
    {"dt": "Role", "filters": [["name", "in", [
        "Pharmacy Administrator",
        "Pharmacist",
        "Store Manager",
        "Purchase Officer",
        "Pharmacy Cashier",
        "Pharmacy Auditor",
    ]]]},
    {"dt": "Workspace", "filters": [["module", "=", "Pharmacy Management"]]},
    "Custom Field",
    "Property Setter",
]

# Permissions
permission_query_conditions = {
    "Prescription": "pharmacy_management.prescription.doctype.prescription.prescription.get_permission_query_conditions",
}

# Notification Config
notification_config = "pharmacy_management.notifications.get_notification_config"

# On App Install
after_install = "pharmacy_management.setup.after_install"
before_uninstall = "pharmacy_management.setup.before_uninstall"
