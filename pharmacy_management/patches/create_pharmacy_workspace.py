import frappe
import json


def execute():
	"""Create Pharmacy Management workspace and clear cache.

	This patch runs as [post_model_sync] — after schema sync so the Workspace
	doctype is guaranteed to exist.  It ensures the Module Def is created,
	the Workspace document is present with all child records, and the
	bootinfo / global cache are flushed so the sidebar picks up the change.
	"""

	workspace_name = "Pharmacy Management"
	app_name = "pharmacy_management"

	# ------------------------------------------------------------------ #
	#  1. Ensure Module Def exists
	# ------------------------------------------------------------------ #
	if not frappe.db.exists("Module Def", workspace_name):
		mod = frappe.get_doc({
			"doctype": "Module Def",
			"module_name": workspace_name,
			"app_name": app_name,
		})
		mod.insert(ignore_permissions=True, ignore_mandatory=True)
		print(f"  ✓ Created Module Def '{workspace_name}'")

	# ------------------------------------------------------------------ #
	#  2. Build child-table data
	# ------------------------------------------------------------------ #

	links = [
		{"label": "Medicine Master",           "link_to": "Medicine Master",      "link_type": "DocType", "onboard": 1, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Medicine Batch",            "link_to": "Medicine Batch",       "link_type": "DocType", "onboard": 1, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Stock Adjustment",          "link_to": "Stock Adjustment",     "link_type": "DocType", "onboard": 1, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Patient",                   "link_to": "Patient",              "link_type": "DocType", "onboard": 1, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Drug Composition",          "link_to": "Drug Composition",     "link_type": "DocType", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Drug Manufacturer",         "link_to": "Drug Manufacturer",    "link_type": "DocType", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Medicine Category",         "link_to": "Medicine Category",    "link_type": "DocType", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Drug Composition Item",     "link_to": "Drug Composition Item","link_type": "DocType", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Expiry Alert",              "link_to": "Expiry Alert",         "link_type": "DocType", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Stock Transfer",            "link_to": "Stock Transfer",       "link_type": "DocType", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Stock Adjustment Item",     "link_to": "Stock Adjustment Item","link_type": "DocType", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Stock Transfer Item",       "link_to": "Stock Transfer Item",  "link_type": "DocType", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Audit Log",                 "link_to": "Audit Log",            "link_type": "DocType", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Drug License",              "link_to": "Drug License",         "link_type": "DocType", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Pharmacist",                "link_to": "Pharmacist",           "link_type": "DocType", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Shift Assignment",          "link_to": "Shift Assignment",     "link_type": "DocType", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Insurance Claim",           "link_to": "Insurance Claim",      "link_type": "DocType", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Insurance Provider",        "link_to": "Insurance Provider",   "link_type": "DocType", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Loyalty Program",           "link_to": "Loyalty Program",      "link_type": "DocType", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "POS Invoice Ext",           "link_to": "POS Invoice Ext",      "link_type": "DocType", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "POS Invoice Item Ext",      "link_to": "POS Invoice Item Ext", "link_type": "DocType", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Near Expiry Stock",         "link_to": "Near Expiry Stock",    "link_type": "Report",  "onboard": 0, "is_query_report": 1, "hidden": 0, "dependencies": ""},
		{"label": "Stock Ledger Medicine",     "link_to": "Stock Ledger Medicine","link_type": "Report",  "onboard": 0, "is_query_report": 1, "hidden": 0, "dependencies": ""},
	]

	shortcuts = [
		{"label": "Medicine Master",   "link_to": "Medicine Master",  "type": "DocType", "doc_view": "List"},
		{"label": "Medicine Batch",    "link_to": "Medicine Batch",   "type": "DocType", "doc_view": "List"},
		{"label": "Stock Adjustment",  "link_to": "Stock Adjustment", "type": "DocType", "doc_view": "List"},
		{"label": "Patient",           "link_to": "Patient",          "type": "DocType", "doc_view": "List"},
		{"label": "Prescription",      "link_to": "Prescription",     "type": "DocType", "doc_view": "List"},
		{"label": "POS Invoice",       "link_to": "POS Invoice Ext",  "type": "DocType", "doc_view": "List"},
		{"label": "Purchase Request",  "link_to": "Purchase Request", "type": "DocType", "doc_view": "List"},
	]

	roles = [
		{"role": "System Manager"},
		{"role": "Pharmacy Administrator"},
		{"role": "Pharmacist"},
		{"role": "Store Manager"},
		{"role": "Purchase Officer"},
		{"role": "Pharmacy Cashier"},
		{"role": "Pharmacy Auditor"},
	]

	# content – JSON array of card / section / shortcut widgets  ----------
	content = json.dumps([
		{"id": "a1b2c3d4", "type": "section",    "data": {"label": "Quick Actions", "col": 12}},
		{"id": "b2c3d4e5", "type": "shortcut",   "data": {"shortcut_name": "Medicine Master", "col": 3}},
		{"id": "c3d4e5f6", "type": "shortcut",   "data": {"shortcut_name": "Medicine Batch", "col": 3}},
		{"id": "d4e5f6g7", "type": "shortcut",   "data": {"shortcut_name": "Stock Adjustment", "col": 3}},
		{"id": "e5f6g7h8", "type": "shortcut",   "data": {"shortcut_name": "Patient", "col": 3}},
		{"id": "f6g7h8i9", "type": "section",    "data": {"label": "Pharmacy Operations", "col": 12}},
		{"id": "g7h8i9j0", "type": "card",       "data": {"card_name": "Drug Catalog", "col": 4, "links": [
			{"type": "link", "label": "Medicine Master", "link_to": "Medicine Master", "link_type": "DocType"},
			{"type": "link", "label": "Medicine Category", "link_to": "Medicine Category", "link_type": "DocType"},
			{"type": "link", "label": "Drug Manufacturer", "link_to": "Drug Manufacturer", "link_type": "DocType"},
			{"type": "link", "label": "Drug Composition", "link_to": "Drug Composition", "link_type": "DocType"},
			{"type": "link", "label": "Drug Composition Item", "link_to": "Drug Composition Item", "link_type": "DocType"},
		]}},
		{"id": "h8i9j0k1", "type": "card",       "data": {"card_name": "Inventory", "col": 4, "links": [
			{"type": "link", "label": "Medicine Batch", "link_to": "Medicine Batch", "link_type": "DocType"},
			{"type": "link", "label": "Stock Adjustment", "link_to": "Stock Adjustment", "link_type": "DocType"},
			{"type": "link", "label": "Stock Adjustment Item", "link_to": "Stock Adjustment Item", "link_type": "DocType"},
			{"type": "link", "label": "Stock Transfer", "link_to": "Stock Transfer", "link_type": "DocType"},
			{"type": "link", "label": "Stock Transfer Item", "link_to": "Stock Transfer Item", "link_type": "DocType"},
		]}},
		{"id": "i9j0k1l2", "type": "card",       "data": {"card_name": "Batch Tracking", "col": 4, "links": [
			{"type": "link", "label": "Expiry Alert", "link_to": "Expiry Alert", "link_type": "DocType"},
		]}},
		{"id": "j0k1l2m3", "type": "section",    "data": {"label": "Patient & CRM", "col": 12}},
		{"id": "k1l2m3n4", "type": "card",       "data": {"card_name": "Pharmacy CRM", "col": 4, "links": [
			{"type": "link", "label": "Patient", "link_to": "Patient", "link_type": "DocType"},
			{"type": "link", "label": "Loyalty Program", "link_to": "Loyalty Program", "link_type": "DocType"},
			{"type": "link", "label": "Insurance Provider", "link_to": "Insurance Provider", "link_type": "DocType"},
		]}},
		{"id": "l2m3n4o5", "type": "card",       "data": {"card_name": "Insurance", "col": 4, "links": [
			{"type": "link", "label": "Insurance Claim", "link_to": "Insurance Claim", "link_type": "DocType"},
			{"type": "link", "label": "Insurance Provider", "link_to": "Insurance Provider", "link_type": "DocType"},
		]}},
		{"id": "m3n4o5p6", "type": "card",       "data": {"card_name": "Point of Sale", "col": 4, "links": [
			{"type": "link", "label": "POS Invoice Ext", "link_to": "POS Invoice Ext", "link_type": "DocType"},
			{"type": "link", "label": "POS Invoice Item Ext", "link_to": "POS Invoice Item Ext", "link_type": "DocType"},
		]}},
		{"id": "n4o5p6q7", "type": "section",    "data": {"label": "Compliance & HR", "col": 12}},
		{"id": "o5p6q7r8", "type": "card",       "data": {"card_name": "Compliance", "col": 6, "links": [
			{"type": "link", "label": "Drug License", "link_to": "Drug License", "link_type": "DocType"},
			{"type": "link", "label": "Audit Log", "link_to": "Audit Log", "link_type": "DocType"},
		]}},
		{"id": "p6q7r8s9", "type": "card",       "data": {"card_name": "Employee Operations", "col": 6, "links": [
			{"type": "link", "label": "Pharmacist", "link_to": "Pharmacist", "link_type": "DocType"},
			{"type": "link", "label": "Shift Assignment", "link_to": "Shift Assignment", "link_type": "DocType"},
		]}},
		{"id": "q7r8s9t0", "type": "section",    "data": {"label": "Reports", "col": 12}},
		{"id": "r8s9t0u1", "type": "card",       "data": {"card_name": "Reports", "col": 12, "links": [
			{"type": "link", "label": "Near Expiry Stock", "link_to": "Near Expiry Stock", "link_type": "Report"},
			{"type": "link", "label": "Stock Ledger Medicine", "link_to": "Stock Ledger Medicine", "link_type": "Report"},
		]}},
	])

	# ------------------------------------------------------------------ #
	#  3. Create / update the Workspace
	# ------------------------------------------------------------------ #

	if frappe.db.exists("Workspace", workspace_name):
		ws = frappe.get_doc("Workspace", workspace_name)
		# Re-create from scratch so child tables are refreshed properly
		frappe.delete_doc("Workspace", workspace_name, force=True)
		frappe.db.commit()

	ws = frappe.new_doc("Workspace")
	ws.name = workspace_name
	ws.title = workspace_name
	ws.label = workspace_name
	ws.module = workspace_name
	ws.icon = "medicine"
	ws.public = 1
	ws.is_hidden = 0
	ws.sequence_id = 1
	ws.content = content
	ws.extends_another_page = 0
	ws.hide_custom = 0

	for row in links:
		ws.append("links", row)

	for row in shortcuts:
		ws.append("shortcuts", row)

	for row in roles:
		ws.append("roles", row)

	ws.insert(ignore_permissions=True, ignore_mandatory=True)
	print(f"  ✓ Created / updated Workspace '{workspace_name}'")

	# ------------------------------------------------------------------ #
	#  4. Flush cache so sidebar picks up the workspace
	# ------------------------------------------------------------------ #
	frappe.cache.delete_key("bootinfo")
	frappe.clear_cache()
	print("  ✓ Cleared cache")
