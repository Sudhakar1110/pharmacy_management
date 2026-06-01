import frappe
from frappe.model.document import Document

class Patient(Document):
    def validate(self):
        self.validate_mobile()
        self.validate_insurance_expiry()

    def validate_mobile(self):
        if self.mobile_number and not self.mobile_number.isdigit():
            frappe.throw("Mobile Number must contain only digits")
        if self.mobile_number and len(self.mobile_number) != 10:
            frappe.throw("Mobile Number must be 10 digits")

    def validate_insurance_expiry(self):
        import datetime
        if self.insurance_expiry:
            if isinstance(self.insurance_expiry, str):
                expiry = datetime.date.fromisoformat(self.insurance_expiry)
            else:
                expiry = self.insurance_expiry
            if expiry < datetime.date.today():
                frappe.msgprint("Insurance policy has expired", indicator="orange", alert=True)

    def add_loyalty_points(self, points):
        self.loyalty_points = (self.loyalty_points or 0) + points
        self.save(ignore_permissions=True)

@frappe.whitelist()
def get_patient_purchase_history(patient):
    return frappe.get_all(
        "Sales Invoice",
        filters={"patient": patient, "docstatus": 1},
        fields=["name", "posting_date", "grand_total", "status"],
        order_by="posting_date desc",
        limit=50,
    )
