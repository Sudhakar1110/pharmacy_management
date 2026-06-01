import frappe
from frappe.model.document import Document

class MedicineMaster(Document):
    def validate(self):
        self.validate_pricing()
        self.set_item_defaults()

    def validate_pricing(self):
        if self.purchase_rate and self.mrp:
            if self.purchase_rate > self.mrp:
                frappe.throw("Purchase Rate cannot be greater than MRP")
        if self.selling_rate and self.mrp:
            if self.selling_rate > self.mrp:
                frappe.msgprint("Selling Rate exceeds MRP", indicator="orange")

    def set_item_defaults(self):
        if not self.selling_rate and self.mrp and self.discount_percent:
            self.selling_rate = self.mrp * (1 - self.discount_percent / 100)

    def on_update(self):
        self.sync_with_item()

    def sync_with_item(self):
        """Sync Medicine Master data with ERPNext Item"""
        if frappe.db.exists("Item", self.name):
            item = frappe.get_doc("Item", self.name)
            item.item_name = self.medicine_name
            item.description = self.generic_name
            item.standard_rate = self.selling_rate or self.mrp
            item.save(ignore_permissions=True)

@frappe.whitelist()
def get_medicine_stock(medicine, warehouse=None):
    filters = {"item_code": medicine}
    if warehouse:
        filters["warehouse"] = warehouse
    return frappe.db.get_value("Bin", filters, "actual_qty") or 0

@frappe.whitelist()
def search_medicine(query, filters=None):
    return frappe.get_all(
        "Medicine Master",
        filters={"medicine_name": ["like", f"%{query}%"], "is_active": 1},
        fields=["name", "medicine_name", "generic_name", "mrp", "selling_rate", "dosage_form", "strength"],
        limit=20,
    )
