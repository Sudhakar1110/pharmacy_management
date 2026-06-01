import frappe
from frappe.model.document import Document
import datetime

class MedicineBatch(Document):
    def validate(self):
        self.check_expiry()
        self.calculate_days_to_expiry()

    def check_expiry(self):
        if not self.expiry_date:
            return
        today = datetime.date.today()
        if isinstance(self.expiry_date, str):
            expiry = datetime.date.fromisoformat(self.expiry_date)
        else:
            expiry = self.expiry_date
        days = (expiry - today).days
        self.days_to_expiry = days
        threshold = self.near_expiry_threshold or 90
        if days < 0:
            self.batch_status = "Expired"
        elif days <= threshold:
            self.batch_status = "Near Expiry"
        else:
            self.batch_status = "Active"

    def calculate_days_to_expiry(self):
        if self.expiry_date:
            today = datetime.date.today()
            expiry = self.expiry_date if not isinstance(self.expiry_date, str) else datetime.date.fromisoformat(self.expiry_date)
            self.days_to_expiry = (expiry - today).days

def check_expiry(doc, method=None):
    doc.check_expiry()
