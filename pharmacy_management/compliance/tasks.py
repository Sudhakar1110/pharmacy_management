import frappe, datetime

def check_license_expiry():
    licenses = frappe.get_all("Drug License", filters={"status": ["!=", "Expired"]}, fields=["name", "license_name", "expiry_date", "renewal_reminder_days"])
    for lic in licenses:
        if not lic.expiry_date:
            continue
        today = datetime.date.today()
        expiry = lic.expiry_date if not isinstance(lic.expiry_date, str) else datetime.date.fromisoformat(str(lic.expiry_date))
        days = (expiry - today).days
        threshold = lic.renewal_reminder_days or 60
        if days <= threshold:
            frappe.db.set_value("Drug License", lic.name, "status", "Expiring Soon" if days > 0 else "Expired")
    frappe.db.commit()
