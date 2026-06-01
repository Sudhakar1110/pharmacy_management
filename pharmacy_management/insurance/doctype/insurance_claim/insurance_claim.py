import frappe
from frappe.model.document import Document

class InsuranceClaim(Document):
    def validate(self):
        if self.deductible and self.claimed_amount:
            self.patient_liability = self.deductible
        if self.approved_amount:
            self.patient_liability = (self.invoice_amount or 0) - (self.approved_amount or 0)
