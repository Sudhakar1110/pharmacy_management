import frappe

def check_reorder_levels():
    """Daily: check stock vs reorder levels and create purchase requests"""
    medicines = frappe.get_all(
        "Medicine Master",
        filters={"is_active": 1, "reorder_level": [">", 0]},
        fields=["name", "medicine_name", "reorder_level", "reorder_qty"],
    )
    needs_reorder = []
    for med in medicines:
        stock = frappe.db.get_value("Bin", {"item_code": med.name}, "actual_qty") or 0
        if stock <= med.reorder_level:
            needs_reorder.append(med)
    if needs_reorder:
        pr = frappe.new_doc("Purchase Request")
        pr.title = f"Auto Reorder - {frappe.utils.today()}"
        pr.request_date = frappe.utils.today()
        pr.priority = "High"
        pr.status = "Pending Approval"
        for med in needs_reorder:
            pr.append("items", {
                "medicine": med.name,
                "qty": med.reorder_qty or med.reorder_level * 2,
            })
        pr.insert(ignore_permissions=True)
        frappe.db.commit()
