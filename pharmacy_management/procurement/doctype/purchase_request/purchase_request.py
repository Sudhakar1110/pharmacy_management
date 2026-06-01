import frappe
from frappe.model.document import Document
import datetime

class PurchaseRequest(Document):
    def on_submit(self):
        self.status = "Pending Approval"

    def approve(self):
        self.status = "Approved"
        self.approved_by = frappe.session.user
        self.approval_date = datetime.date.today()
        self.save()

    @frappe.whitelist()
    def create_purchase_order(self):
        po = frappe.new_doc("Purchase Order")
        po.schedule_date = self.required_by or datetime.date.today()
        for item in self.items:
            po.append("items", {
                "item_code": item.medicine,
                "qty": item.qty,
                "schedule_date": self.required_by,
            })
        po.insert(ignore_permissions=True)
        self.status = "PO Created"
        self.save()
        return po.name
