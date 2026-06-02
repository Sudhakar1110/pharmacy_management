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
	#     links must have Card Break entries as group headers, followed
	#     by Link entries.  card_name in content must match Card Break labels.
	# ------------------------------------------------------------------ #

	links = [
		# Drug Catalog group
		{"label": "Drug Catalog",          "type": "Card Break", "hidden": 0, "is_query_report": 0, "onboard": 0},
		{"label": "Medicine Master",        "link_to": "Medicine Master",        "link_type": "DocType", "type": "Link", "onboard": 1, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Medicine Category",      "link_to": "Medicine Category",      "link_type": "DocType", "type": "Link", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Drug Manufacturer",      "link_to": "Drug Manufacturer",      "link_type": "DocType", "type": "Link", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Drug Composition",       "link_to": "Drug Composition",       "link_type": "DocType", "type": "Link", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		# Inventory group
		{"label": "Inventory",             "type": "Card Break", "hidden": 0, "is_query_report": 0, "onboard": 0},
		{"label": "Medicine Batch",         "link_to": "Medicine Batch",         "link_type": "DocType", "type": "Link", "onboard": 1, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Stock Adjustment",       "link_to": "Stock Adjustment",       "link_type": "DocType", "type": "Link", "onboard": 1, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Stock Transfer",         "link_to": "Stock Transfer",         "link_type": "DocType", "type": "Link", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		# Batch Tracking group
		{"label": "Batch Tracking",        "type": "Card Break", "hidden": 0, "is_query_report": 0, "onboard": 0},
		{"label": "Expiry Alert",           "link_to": "Expiry Alert",           "link_type": "DocType", "type": "Link", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		# Pharmacy CRM group
		{"label": "Pharmacy CRM",          "type": "Card Break", "hidden": 0, "is_query_report": 0, "onboard": 0},
		{"label": "Patient",                "link_to": "Patient",                "link_type": "DocType", "type": "Link", "onboard": 1, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Loyalty Program",        "link_to": "Loyalty Program",        "link_type": "DocType", "type": "Link", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Insurance Provider",     "link_to": "Insurance Provider",     "link_type": "DocType", "type": "Link", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		# Insurance group
		{"label": "Insurance",             "type": "Card Break", "hidden": 0, "is_query_report": 0, "onboard": 0},
		{"label": "Insurance Claim",        "link_to": "Insurance Claim",        "link_type": "DocType", "type": "Link", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		# Point of Sale group
		{"label": "Point of Sale",         "type": "Card Break", "hidden": 0, "is_query_report": 0, "onboard": 0},
		{"label": "POS Invoice Ext",        "link_to": "POS Invoice Ext",        "link_type": "DocType", "type": "Link", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		# Compliance group
		{"label": "Compliance",            "type": "Card Break", "hidden": 0, "is_query_report": 0, "onboard": 0},
		{"label": "Drug License",           "link_to": "Drug License",           "link_type": "DocType", "type": "Link", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Audit Log",              "link_to": "Audit Log",              "link_type": "DocType", "type": "Link", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		# Employee Operations group
		{"label": "Employee Operations",   "type": "Card Break", "hidden": 0, "is_query_report": 0, "onboard": 0},
		{"label": "Pharmacist",             "link_to": "Pharmacist",             "link_type": "DocType", "type": "Link", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		{"label": "Shift Assignment",       "link_to": "Shift Assignment",       "link_type": "DocType", "type": "Link", "onboard": 0, "is_query_report": 0, "hidden": 0, "dependencies": ""},
		# Reports group
		{"label": "Reports",               "type": "Card Break", "hidden": 0, "is_query_report": 0, "onboard": 0},
		{"label": "Near Expiry Stock",      "link_to": "Near Expiry Stock",      "link_type": "Report",  "type": "Link", "onboard": 0, "is_query_report": 1, "hidden": 0, "dependencies": ""},
		{"label": "Stock Ledger Medicine",  "link_to": "Stock Ledger Medicine",  "link_type": "Report",  "type": "Link", "onboard": 0, "is_query_report": 1, "hidden": 0, "dependencies": ""},
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
	]

	# content: card_name must match the Card Break label in links above
	content = json.dumps([
		{"id": "aa1", "type": "header",   "data": {"text": "Quick Actions", "level": 4, "col": 12}},
		{"id": "ab1", "type": "shortcut", "data": {"shortcut_name": "Medicine Master", "col": 3}},
		{"id": "ab2", "type": "shortcut", "data": {"shortcut_name": "Medicine Batch", "col": 3}},
		{"id": "ab3", "type": "shortcut", "data": {"shortcut_name": "Stock Adjustment", "col": 3}},
		{"id": "ab4", "type": "shortcut", "data": {"shortcut_name": "Patient", "col": 3}},
		{"id": "ab5", "type": "shortcut", "data": {"shortcut_name": "Prescription", "col": 3}},
		{"id": "ab6", "type": "shortcut", "data": {"shortcut_name": "POS Invoice", "col": 3}},
		{"id": "ab7", "type": "shortcut", "data": {"shortcut_name": "Purchase Request", "col": 3}},
		{"id": "ba1", "type": "header",   "data": {"text": "Pharmacy Operations", "level": 4, "col": 12}},
		{"id": "bb1", "type": "card",     "data": {"card_name": "Drug Catalog", "col": 4}},
		{"id": "bb2", "type": "card",     "data": {"card_name": "Inventory", "col": 4}},
		{"id": "bb3", "type": "card",     "data": {"card_name": "Batch Tracking", "col": 4}},
		{"id": "ca1", "type": "header",   "data": {"text": "Patient & CRM", "level": 4, "col": 12}},
		{"id": "cb1", "type": "card",     "data": {"card_name": "Pharmacy CRM", "col": 4}},
		{"id": "cb2", "type": "card",     "data": {"card_name": "Insurance", "col": 4}},
		{"id": "cb3", "type": "card",     "data": {"card_name": "Point of Sale", "col": 4}},
		{"id": "da1", "type": "header",   "data": {"text": "Compliance & HR", "level": 4, "col": 12}},
		{"id": "db1", "type": "card",     "data": {"card_name": "Compliance", "col": 6}},
		{"id": "db2", "type": "card",     "data": {"card_name": "Employee Operations", "col": 6}},
		{"id": "ea1", "type": "header",   "data": {"text": "Reports", "level": 4, "col": 12}},
		{"id": "eb1", "type": "card",     "data": {"card_name": "Reports", "col": 12}},
	])

	# ------------------------------------------------------------------ #
	#  3. Delete existing workspace and recreate from scratch
	# ------------------------------------------------------------------ #

	if frappe.db.exists("Workspace", workspace_name):
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
