import frappe
from frappe.model.document import Document

class POSInvoiceExt(Document):
    def validate(self):
        self.calculate_totals()
        self.validate_payment()

    def calculate_totals(self):
        subtotal = sum((item.qty or 0) * (item.rate or 0) for item in self.items)
        tax = sum((item.qty or 0) * (item.rate or 0) * (item.gst_rate or 0) / 100 for item in self.items)
        discount = self.discount_amount or 0
        if self.discount_percent:
            discount = subtotal * self.discount_percent / 100
        loyalty_amt = self.loyalty_amount or 0
        self.subtotal = subtotal
        self.tax_amount = tax
        self.grand_total = subtotal + tax - discount - loyalty_amt
        if self.paid_amount:
            self.change_amount = max(0, self.paid_amount - self.grand_total)

    def validate_payment(self):
        if self.paid_amount and self.paid_amount < self.grand_total:
            if self.payment_mode not in ["Insurance", "Mixed"]:
                frappe.throw(f"Paid amount must be at least {self.grand_total}")

    def on_submit(self):
        self.status = "Paid"
        if self.patient and self.loyalty_points_used:
            patient = frappe.get_doc("Patient", self.patient)
            patient.loyalty_points = (patient.loyalty_points or 0) - self.loyalty_points_used
            patient.save(ignore_permissions=True)
        self.create_erpnext_invoice()

    def create_erpnext_invoice(self):
        si = frappe.new_doc("Sales Invoice")
        si.customer = self.patient or "Walk-in Customer"
        si.posting_date = self.posting_date
        si.is_pos = 1
        for item in self.items:
            si.append("items", {
                "item_code": item.medicine,
                "qty": item.qty,
                "rate": item.rate,
            })
        si.insert(ignore_permissions=True)

def on_submit(doc, method=None):
    doc.on_submit()
