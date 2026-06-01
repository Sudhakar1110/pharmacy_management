import frappe
from frappe.model.document import Document

class Prescription(Document):
    def validate(self):
        self.validate_expiry()
        self.validate_medicines()

    def validate_expiry(self):
        import datetime
        if self.valid_till:
            vt = self.valid_till if not isinstance(self.valid_till, str) else datetime.date.fromisoformat(self.valid_till)
            if vt < datetime.date.today():
                frappe.throw("Prescription has expired")

    def validate_medicines(self):
        for item in self.medicines:
            if not item.medicine:
                frappe.throw("Medicine is required in prescription items")

    def on_submit(self):
        self.status = "Verification"
        frappe.db.set_value("Prescription", self.name, "status", "Verification")

def on_submit(doc, method=None):
    doc.on_submit()

def get_permission_query_conditions(user):
    if "Pharmacy Administrator" in frappe.get_roles(user):
        return ""
    return f"(`tabPrescription`.owner = '{user}')"
