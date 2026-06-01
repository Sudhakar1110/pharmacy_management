import frappe

def after_install():
    """Setup roles, permissions, and default data after install"""
    create_roles()
    create_default_warehouse()
    create_default_loyalty_program()
    create_default_medicine_categories()
    frappe.db.commit()
    print("Pharmacy Management System installed successfully!")

def create_roles():
    roles = [
        "Pharmacy Administrator",
        "Pharmacist",
        "Store Manager",
        "Purchase Officer",
        "Pharmacy Cashier",
        "Pharmacy Auditor",
    ]
    for role in roles:
        if not frappe.db.exists("Role", role):
            frappe.get_doc({"doctype": "Role", "role_name": role}).insert(ignore_permissions=True)

def create_default_warehouse():
    if not frappe.db.exists("Warehouse", "Pharmacy Main Store - PM"):
        try:
            wh = frappe.new_doc("Warehouse")
            wh.warehouse_name = "Pharmacy Main Store"
            wh.company = frappe.db.get_single_value("Global Defaults", "default_company")
            wh.insert(ignore_permissions=True)
        except Exception:
            pass

def create_default_loyalty_program():
    if not frappe.db.exists("Loyalty Program", "Standard Pharmacy Loyalty"):
        lp = frappe.new_doc("Loyalty Program")
        lp.program_name = "Standard Pharmacy Loyalty"
        lp.points_per_rupee = 1
        lp.min_purchase_for_points = 100
        lp.redemption_value = 0.10
        lp.min_points_to_redeem = 100
        lp.is_active = 1
        lp.insert(ignore_permissions=True)

def create_default_medicine_categories():
    categories = [
        "Tablet", "Capsule", "Syrup", "Injection", "Cream & Ointment",
        "Drops", "Inhaler", "Surgical", "Vitamins & Supplements",
        "Ayurvedic", "Homeopathic", "Personal Care", "Baby Care",
    ]
    for cat in categories:
        if not frappe.db.exists("Medicine Category", cat):
            frappe.get_doc({
                "doctype": "Medicine Category",
                "category_name": cat,
                "is_active": 1,
            }).insert(ignore_permissions=True)

def before_uninstall():
    print("Removing Pharmacy Management System...")
