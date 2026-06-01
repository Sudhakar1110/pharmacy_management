import frappe
from frappe.model.document import Document

class LoyaltyProgram(Document):
    def validate(self):
        if self.points_per_rupee <= 0:
            frappe.throw("Points per Rupee must be greater than 0")
