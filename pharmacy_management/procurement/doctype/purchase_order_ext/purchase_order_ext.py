import frappe


def on_submit(doc, method=None):
	"""Hook into Purchase Order submission for pharmacy-specific processing."""
	if doc.custom_pharmacy_purchase_request:
		frappe.db.set_value("Purchase Request", doc.custom_pharmacy_purchase_request, "status", "PO Created")
