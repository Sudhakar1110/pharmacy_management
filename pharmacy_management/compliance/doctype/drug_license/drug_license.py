import frappe, datetime
from frappe.model.document import Document

class DrugLicense(Document):
    def validate(self):
        if self.expiry_date:
            today = datetime.date.today()
            expiry = self.expiry_date if not isinstance(self.expiry_date, str) else datetime.date.fromisoformat(str(self.expiry_date))
            days = (expiry - today).days
            if days < 0:
                self.status = "Expired"
            elif days <= (self.renewal_reminder_days or 60):
                self.status = "Expiring Soon"
            else:
                self.status = "Active"
