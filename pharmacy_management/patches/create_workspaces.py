import frappe


def clear_workspace_cache():
    """Force clear the bootinfo cache so workspaces appear immediately.
    The Workspace controller's on_update() normally clears this, but during
    patch execution disable_saving_as_public() returns True and on_update
    returns early — so we must clear it manually.
    """
    frappe.cache.delete_key("bootinfo")
    frappe.clear_cache()


WORKSPACES = [
    {
        "name": "Pharmacy",
        "label": "Pharmacy",
        "title": "Pharmacy",
        "icon": "healthcare",
        "module": "Dashboard",
        "sequence_id": 1,
        "roles": [
            {"role": "System Manager"}, {"role": "Pharmacy Administrator"},
            {"role": "Pharmacist"}, {"role": "Store Manager"},
            {"role": "Purchase Officer"}, {"role": "Pharmacy Cashier"}, {"role": "Pharmacy Auditor"},
        ],
        "shortcuts": [
            {"doc_view": "List", "label": "Patient", "link_to": "Patient", "type": "DocType"},
            {"doc_view": "List", "label": "Prescription", "link_to": "Prescription", "type": "DocType"},
            {"doc_view": "List", "label": "POS Invoice Ext", "link_to": "POS Invoice Ext", "type": "DocType"},
            {"doc_view": "List", "label": "Purchase Request", "link_to": "Purchase Request", "type": "DocType"},
            {"doc_view": "List", "label": "Medicine Batches", "link_to": "Medicine Batch", "type": "DocType"},
            {"doc_view": "List", "label": "Stock Transfers", "link_to": "Stock Transfer", "type": "DocType"},
            {"doc_view": "List", "label": "Insurance Claims", "link_to": "Insurance Claim", "type": "DocType"},
            {"label": "Daily Sales Report", "link_to": "Daily Sales Report", "type": "Report"},
            {"label": "Near Expiry Stock", "link_to": "Near Expiry Stock", "type": "Report"},
            {"label": "Stock Ledger", "link_to": "Stock Ledger Medicine", "type": "Report"},
        ],
        "content": "[{\"id\":\"quick-actions\",\"type\":\"section\",\"data\":{\"label\":\"Quick Actions\",\"col\":12}},{\"id\":\"shortcut-patient\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Patient\",\"col\":3}},{\"id\":\"shortcut-prescription\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Prescription\",\"col\":3}},{\"id\":\"shortcut-pos\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"POS Invoice Ext\",\"col\":3}},{\"id\":\"shortcut-purchase\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Purchase Request\",\"col\":3}},{\"id\":\"section-patient\",\"type\":\"section\",\"data\":{\"label\":\"Patient & Clinical Management\",\"col\":12}},{\"id\":\"card-patient\",\"type\":\"card\",\"data\":{\"card_name\":\"Patients & CRM\",\"col\":4,\"links\":[{\"label\":\"Patient\",\"link_to\":\"Patient\",\"link_type\":\"DocType\"},{\"label\":\"Insurance Provider\",\"link_to\":\"Insurance Provider\",\"link_type\":\"DocType\"},{\"label\":\"Loyalty Program\",\"link_to\":\"Loyalty Program\",\"link_type\":\"DocType\"},{\"label\":\"Insurance Claim\",\"link_to\":\"Insurance Claim\",\"link_type\":\"DocType\"}]}},{\"id\":\"card-prescription\",\"type\":\"card\",\"data\":{\"card_name\":\"Prescriptions\",\"col\":4,\"links\":[{\"label\":\"Doctor Master\",\"link_to\":\"Doctor Master\",\"link_type\":\"DocType\"},{\"label\":\"Prescription\",\"link_to\":\"Prescription\",\"link_type\":\"DocType\"}]}},{\"id\":\"card-pos\",\"type\":\"card\",\"data\":{\"card_name\":\"Point of Sale\",\"col\":4,\"links\":[{\"label\":\"POS Invoice Ext\",\"link_to\":\"POS Invoice Ext\",\"link_type\":\"DocType\"},{\"label\":\"Daily Sales Report\",\"link_to\":\"Daily Sales Report\",\"link_type\":\"Report\"}]}},{\"id\":\"section-medicine\",\"type\":\"section\",\"data\":{\"label\":\"Medicine Catalog & Inventory\",\"col\":12}},{\"id\":\"card-catalog\",\"type\":\"card\",\"data\":{\"card_name\":\"Medicine Catalog\",\"col\":4,\"links\":[{\"label\":\"Medicine Master\",\"link_to\":\"Medicine Master\",\"link_type\":\"DocType\"},{\"label\":\"Medicine Category\",\"link_to\":\"Medicine Category\",\"link_type\":\"DocType\"},{\"label\":\"Drug Manufacturer\",\"link_to\":\"Drug Manufacturer\",\"link_type\":\"DocType\"},{\"label\":\"Drug Composition\",\"link_to\":\"Drug Composition\",\"link_type\":\"DocType\"}]}},{\"id\":\"card-inventory\",\"type\":\"card\",\"data\":{\"card_name\":\"Inventory Management\",\"col\":4,\"links\":[{\"label\":\"Medicine Batch\",\"link_to\":\"Medicine Batch\",\"link_type\":\"DocType\"},{\"label\":\"Stock Adjustment\",\"link_to\":\"Stock Adjustment\",\"link_type\":\"DocType\"},{\"label\":\"Stock Transfer\",\"link_to\":\"Stock Transfer\",\"link_type\":\"DocType\"}]}},{\"id\":\"card-expiry\",\"type\":\"card\",\"data\":{\"card_name\":\"Batch & Expiry\",\"col\":4,\"links\":[{\"label\":\"Expiry Alert\",\"link_to\":\"Expiry Alert\",\"link_type\":\"DocType\"},{\"label\":\"Near Expiry Stock\",\"link_to\":\"Near Expiry Stock\",\"link_type\":\"Report\"},{\"label\":\"Stock Ledger Medicine\",\"link_to\":\"Stock Ledger Medicine\",\"link_type\":\"Report\"}]}},{\"id\":\"section-procure\",\"type\":\"section\",\"data\":{\"label\":\"Procurement & Compliance\",\"col\":12}},{\"id\":\"card-procurement\",\"type\":\"card\",\"data\":{\"card_name\":\"Procurement\",\"col\":6,\"links\":[{\"label\":\"Purchase Request\",\"link_to\":\"Purchase Request\",\"link_type\":\"DocType\"},{\"label\":\"Purchase Analysis\",\"link_to\":\"Purchase Analysis\",\"link_type\":\"Report\"}]}},{\"id\":\"card-compliance\",\"type\":\"card\",\"data\":{\"card_name\":\"Compliance & Staff\",\"col\":6,\"links\":[{\"label\":\"Drug License\",\"link_to\":\"Drug License\",\"link_type\":\"DocType\"},{\"label\":\"Audit Log\",\"link_to\":\"Audit Log\",\"link_type\":\"DocType\"},{\"label\":\"Pharmacist\",\"link_to\":\"Pharmacist\",\"link_type\":\"DocType\"},{\"label\":\"Shift Assignment\",\"link_to\":\"Shift Assignment\",\"link_type\":\"DocType\"}]}},{\"id\":\"section-reports\",\"type\":\"section\",\"data\":{\"label\":\"Reports & Analytics\",\"col\":12}},{\"id\":\"card-reports\",\"type\":\"card\",\"data\":{\"card_name\":\"Reports\",\"col\":12,\"links\":[{\"label\":\"Daily Sales Report\",\"link_to\":\"Daily Sales Report\",\"link_type\":\"Report\"},{\"label\":\"Near Expiry Stock\",\"link_to\":\"Near Expiry Stock\",\"link_type\":\"Report\"},{\"label\":\"Stock Ledger Medicine\",\"link_to\":\"Stock Ledger Medicine\",\"link_type\":\"Report\"},{\"label\":\"Purchase Analysis\",\"link_to\":\"Purchase Analysis\",\"link_type\":\"Report\"}]}}]",
    },
    {
        "name": "Pharmacy CRM",
        "label": "Pharmacy CRM",
        "title": "Pharmacy CRM",
        "icon": "users",
        "module": "Dashboard",
        "sequence_id": 2,
        "roles": [{"role": "System Manager"}, {"role": "Pharmacy Administrator"}, {"role": "Pharmacist"}, {"role": "Pharmacy Auditor"}],
        "shortcuts": [
            {"doc_view": "List", "label": "Patient", "link_to": "Patient", "type": "DocType"},
            {"doc_view": "List", "label": "Loyalty Program", "link_to": "Loyalty Program", "type": "DocType"},
            {"doc_view": "List", "label": "Insurance Provider", "link_to": "Insurance Provider", "type": "DocType"},
            {"doc_view": "List", "label": "Insurance Claims", "link_to": "Insurance Claim", "type": "DocType"},
        ],
        "content": "[{\"id\":\"crm-quick\",\"type\":\"section\",\"data\":{\"label\":\"Quick Actions\",\"col\":12}},{\"id\":\"shortcut-patient\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Patient\",\"col\":4}},{\"id\":\"shortcut-loyalty\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Loyalty Program\",\"col\":4}},{\"id\":\"shortcut-insurance\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Insurance Provider\",\"col\":4}},{\"id\":\"section-main\",\"type\":\"section\",\"data\":{\"label\":\"Patient Management\",\"col\":12}},{\"id\":\"card-patient\",\"type\":\"card\",\"data\":{\"card_name\":\"Patients\",\"col\":6,\"links\":[{\"label\":\"Patient\",\"link_to\":\"Patient\",\"link_type\":\"DocType\"},{\"label\":\"Loyalty Program\",\"link_to\":\"Loyalty Program\",\"link_type\":\"DocType\"}]}},{\"id\":\"card-insurance\",\"type\":\"card\",\"data\":{\"card_name\":\"Insurance\",\"col\":6,\"links\":[{\"label\":\"Insurance Provider\",\"link_to\":\"Insurance Provider\",\"link_type\":\"DocType\"},{\"label\":\"Insurance Claim\",\"link_to\":\"Insurance Claim\",\"link_type\":\"DocType\"}]}}]",
    },
    {
        "name": "Catalog",
        "label": "Catalog",
        "title": "Catalog",
        "icon": "clipboard",
        "module": "Dashboard",
        "sequence_id": 3,
        "roles": [{"role": "System Manager"}, {"role": "Pharmacy Administrator"}, {"role": "Pharmacist"}, {"role": "Store Manager"}],
        "shortcuts": [
            {"doc_view": "List", "label": "Medicine Master", "link_to": "Medicine Master", "type": "DocType"},
            {"doc_view": "List", "label": "Medicine Category", "link_to": "Medicine Category", "type": "DocType"},
            {"doc_view": "List", "label": "Drug Manufacturer", "link_to": "Drug Manufacturer", "type": "DocType"},
            {"doc_view": "List", "label": "Drug Composition", "link_to": "Drug Composition", "type": "DocType"},
        ],
        "content": "[{\"id\":\"catalog-quick\",\"type\":\"section\",\"data\":{\"label\":\"Quick Actions\",\"col\":12}},{\"id\":\"shortcut-medicine\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Medicine Master\",\"col\":4}},{\"id\":\"shortcut-category\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Medicine Category\",\"col\":4}},{\"id\":\"shortcut-manufacturer\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Drug Manufacturer\",\"col\":4}},{\"id\":\"section-catalog\",\"type\":\"section\",\"data\":{\"label\":\"Medicine Catalog\",\"col\":12}},{\"id\":\"card-medicines\",\"type\":\"card\",\"data\":{\"card_name\":\"Medicines\",\"col\":6,\"links\":[{\"label\":\"Medicine Master\",\"link_to\":\"Medicine Master\",\"link_type\":\"DocType\"},{\"label\":\"Medicine Category\",\"link_to\":\"Medicine Category\",\"link_type\":\"DocType\"}]}},{\"id\":\"card-composition\",\"type\":\"card\",\"data\":{\"card_name\":\"Composition & Manufacturing\",\"col\":6,\"links\":[{\"label\":\"Drug Composition\",\"link_to\":\"Drug Composition\",\"link_type\":\"DocType\"},{\"label\":\"Drug Manufacturer\",\"link_to\":\"Drug Manufacturer\",\"link_type\":\"DocType\"}]}}]",
    },
    {
        "name": "Inventory",
        "label": "Inventory",
        "title": "Inventory",
        "icon": "cubes",
        "module": "Dashboard",
        "sequence_id": 4,
        "roles": [{"role": "System Manager"}, {"role": "Pharmacy Administrator"}, {"role": "Store Manager"}, {"role": "Pharmacist"}],
        "shortcuts": [
            {"doc_view": "List", "label": "Medicine Batch", "link_to": "Medicine Batch", "type": "DocType"},
            {"doc_view": "List", "label": "Stock Adjustment", "link_to": "Stock Adjustment", "type": "DocType"},
            {"doc_view": "List", "label": "Stock Transfer", "link_to": "Stock Transfer", "type": "DocType"},
            {"label": "Stock Ledger", "link_to": "Stock Ledger Medicine", "type": "Report"},
        ],
        "content": "[{\"id\":\"inv-quick\",\"type\":\"section\",\"data\":{\"label\":\"Quick Actions\",\"col\":12}},{\"id\":\"shortcut-batch\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Medicine Batch\",\"col\":4}},{\"id\":\"shortcut-adjust\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Stock Adjustment\",\"col\":4}},{\"id\":\"shortcut-transfer\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Stock Transfer\",\"col\":4}},{\"id\":\"section-inv\",\"type\":\"section\",\"data\":{\"label\":\"Inventory Management\",\"col\":12}},{\"id\":\"card-stock\",\"type\":\"card\",\"data\":{\"card_name\":\"Stock Operations\",\"col\":6,\"links\":[{\"label\":\"Medicine Batch\",\"link_to\":\"Medicine Batch\",\"link_type\":\"DocType\"},{\"label\":\"Stock Ledger Medicine\",\"link_to\":\"Stock Ledger Medicine\",\"link_type\":\"Report\"}]}},{\"id\":\"card-moves\",\"type\":\"card\",\"data\":{\"card_name\":\"Movements & Adjustments\",\"col\":6,\"links\":[{\"label\":\"Stock Adjustment\",\"link_to\":\"Stock Adjustment\",\"link_type\":\"DocType\"},{\"label\":\"Stock Transfer\",\"link_to\":\"Stock Transfer\",\"link_type\":\"DocType\"}]}}]",
    },
    {
        "name": "Procurement",
        "label": "Procurement",
        "title": "Procurement",
        "icon": "shopping-cart",
        "module": "Dashboard",
        "sequence_id": 5,
        "roles": [{"role": "System Manager"}, {"role": "Pharmacy Administrator"}, {"role": "Purchase Officer"}, {"role": "Store Manager"}],
        "shortcuts": [
            {"doc_view": "List", "label": "Purchase Request", "link_to": "Purchase Request", "type": "DocType"},
            {"label": "Purchase Analysis", "link_to": "Purchase Analysis", "type": "Report"},
        ],
        "content": "[{\"id\":\"proc-quick\",\"type\":\"section\",\"data\":{\"label\":\"Quick Actions\",\"col\":12}},{\"id\":\"shortcut-pr\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Purchase Request\",\"col\":6}},{\"id\":\"shortcut-analysis\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Purchase Analysis\",\"col\":6}},{\"id\":\"section-proc\",\"type\":\"section\",\"data\":{\"label\":\"Procurement\",\"col\":12}},{\"id\":\"card-requests\",\"type\":\"card\",\"data\":{\"card_name\":\"Purchase Requests\",\"col\":12,\"links\":[{\"label\":\"Purchase Request\",\"link_to\":\"Purchase Request\",\"link_type\":\"DocType\"},{\"label\":\"Purchase Request Item\",\"link_to\":\"Purchase Request Item\",\"link_type\":\"DocType\"},{\"label\":\"Purchase Analysis\",\"link_to\":\"Purchase Analysis\",\"link_type\":\"Report\"}]}}]",
    },
    {
        "name": "Prescription",
        "label": "Prescription",
        "title": "Prescription",
        "icon": "file-text",
        "module": "Dashboard",
        "sequence_id": 6,
        "roles": [{"role": "System Manager"}, {"role": "Pharmacy Administrator"}, {"role": "Pharmacist"}, {"role": "Pharmacy Auditor"}],
        "shortcuts": [
            {"doc_view": "List", "label": "Prescription", "link_to": "Prescription", "type": "DocType"},
            {"doc_view": "List", "label": "Doctor Master", "link_to": "Doctor Master", "type": "DocType"},
        ],
        "content": "[{\"id\":\"presc-quick\",\"type\":\"section\",\"data\":{\"label\":\"Quick Actions\",\"col\":12}},{\"id\":\"shortcut-presc\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Prescription\",\"col\":6}},{\"id\":\"shortcut-doctor\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Doctor Master\",\"col\":6}},{\"id\":\"section-presc\",\"type\":\"section\",\"data\":{\"label\":\"Prescription Management\",\"col\":12}},{\"id\":\"card-presc-main\",\"type\":\"card\",\"data\":{\"card_name\":\"Prescriptions\",\"col\":6,\"links\":[{\"label\":\"Prescription\",\"link_to\":\"Prescription\",\"link_type\":\"DocType\"},{\"label\":\"Prescription Item\",\"link_to\":\"Prescription Item\",\"link_type\":\"DocType\"}]}},{\"id\":\"card-doctor\",\"type\":\"card\",\"data\":{\"card_name\":\"Doctors\",\"col\":6,\"links\":[{\"label\":\"Doctor Master\",\"link_to\":\"Doctor Master\",\"link_type\":\"DocType\"}]}}]",
    },
    {
        "name": "POS",
        "label": "POS",
        "title": "POS",
        "icon": "money",
        "module": "Dashboard",
        "sequence_id": 7,
        "roles": [{"role": "System Manager"}, {"role": "Pharmacy Administrator"}, {"role": "Pharmacist"}, {"role": "Pharmacy Cashier"}],
        "shortcuts": [
            {"doc_view": "List", "label": "POS Invoice Ext", "link_to": "POS Invoice Ext", "type": "DocType"},
            {"label": "Daily Sales Report", "link_to": "Daily Sales Report", "type": "Report"},
        ],
        "content": "[{\"id\":\"pos-quick\",\"type\":\"section\",\"data\":{\"label\":\"Quick Actions\",\"col\":12}},{\"id\":\"shortcut-invoice\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"POS Invoice Ext\",\"col\":6}},{\"id\":\"shortcut-sales\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Daily Sales Report\",\"col\":6}},{\"id\":\"section-pos\",\"type\":\"section\",\"data\":{\"label\":\"Point of Sale\",\"col\":12}},{\"id\":\"card-pos\",\"type\":\"card\",\"data\":{\"card_name\":\"Sales & Invoicing\",\"col\":12,\"links\":[{\"label\":\"POS Invoice Ext\",\"link_to\":\"POS Invoice Ext\",\"link_type\":\"DocType\"},{\"label\":\"Daily Sales Report\",\"link_to\":\"Daily Sales Report\",\"link_type\":\"Report\"}]}}]",
    },
    {
        "name": "Insurance",
        "label": "Insurance",
        "title": "Insurance",
        "icon": "shield",
        "module": "Dashboard",
        "sequence_id": 8,
        "roles": [{"role": "System Manager"}, {"role": "Pharmacy Administrator"}, {"role": "Pharmacy Auditor"}],
        "shortcuts": [
            {"doc_view": "List", "label": "Insurance Claim", "link_to": "Insurance Claim", "type": "DocType"},
        ],
        "content": "[{\"id\":\"ins-quick\",\"type\":\"section\",\"data\":{\"label\":\"Quick Actions\",\"col\":12}},{\"id\":\"shortcut-claim\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Insurance Claim\",\"col\":12}},{\"id\":\"section-ins\",\"type\":\"section\",\"data\":{\"label\":\"Insurance Management\",\"col\":12}},{\"id\":\"card-claims\",\"type\":\"card\",\"data\":{\"card_name\":\"Claims\",\"col\":12,\"links\":[{\"label\":\"Insurance Claim\",\"link_to\":\"Insurance Claim\",\"link_type\":\"DocType\"}]}}]",
    },
    {
        "name": "Batch Tracking",
        "label": "Batch Tracking",
        "title": "Batch Tracking",
        "icon": "bell",
        "module": "Dashboard",
        "sequence_id": 9,
        "roles": [{"role": "System Manager"}, {"role": "Pharmacy Administrator"}, {"role": "Store Manager"}, {"role": "Pharmacist"}],
        "shortcuts": [
            {"doc_view": "List", "label": "Expiry Alert", "link_to": "Expiry Alert", "type": "DocType"},
            {"label": "Near Expiry Stock", "link_to": "Near Expiry Stock", "type": "Report"},
        ],
        "content": "[{\"id\":\"batch-quick\",\"type\":\"section\",\"data\":{\"label\":\"Quick Actions\",\"col\":12}},{\"id\":\"shortcut-alert\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Expiry Alert\",\"col\":6}},{\"id\":\"shortcut-expiry\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Near Expiry Stock\",\"col\":6}},{\"id\":\"section-batch\",\"type\":\"section\",\"data\":{\"label\":\"Batch & Expiry Tracking\",\"col\":12}},{\"id\":\"card-expiry\",\"type\":\"card\",\"data\":{\"card_name\":\"Expiry Management\",\"col\":12,\"links\":[{\"label\":\"Expiry Alert\",\"link_to\":\"Expiry Alert\",\"link_type\":\"DocType\"},{\"label\":\"Near Expiry Stock\",\"link_to\":\"Near Expiry Stock\",\"link_type\":\"Report\"}]}}]",
    },
    {
        "name": "Compliance",
        "label": "Compliance",
        "title": "Compliance",
        "icon": "check-circle",
        "module": "Dashboard",
        "sequence_id": 10,
        "roles": [{"role": "System Manager"}, {"role": "Pharmacy Administrator"}, {"role": "Pharmacy Auditor"}],
        "shortcuts": [
            {"doc_view": "List", "label": "Drug License", "link_to": "Drug License", "type": "DocType"},
            {"doc_view": "List", "label": "Audit Log", "link_to": "Audit Log", "type": "DocType"},
        ],
        "content": "[{\"id\":\"comp-quick\",\"type\":\"section\",\"data\":{\"label\":\"Quick Actions\",\"col\":12}},{\"id\":\"shortcut-license\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Drug License\",\"col\":6}},{\"id\":\"shortcut-audit\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Audit Log\",\"col\":6}},{\"id\":\"section-comp\",\"type\":\"section\",\"data\":{\"label\":\"Compliance & Regulatory\",\"col\":12}},{\"id\":\"card-licenses\",\"type\":\"card\",\"data\":{\"card_name\":\"Licenses\",\"col\":6,\"links\":[{\"label\":\"Drug License\",\"link_to\":\"Drug License\",\"link_type\":\"DocType\"}]}},{\"id\":\"card-audit\",\"type\":\"card\",\"data\":{\"card_name\":\"Audit\",\"col\":6,\"links\":[{\"label\":\"Audit Log\",\"link_to\":\"Audit Log\",\"link_type\":\"DocType\"}]}}]",
    },
    {
        "name": "Employee Ops",
        "label": "Employee Ops",
        "title": "Employee Ops",
        "icon": "user-md",
        "module": "Dashboard",
        "sequence_id": 11,
        "roles": [{"role": "System Manager"}, {"role": "Pharmacy Administrator"}, {"role": "Pharmacist"}],
        "shortcuts": [
            {"doc_view": "List", "label": "Pharmacist", "link_to": "Pharmacist", "type": "DocType"},
            {"doc_view": "List", "label": "Shift Assignment", "link_to": "Shift Assignment", "type": "DocType"},
        ],
        "content": "[{\"id\":\"emp-quick\",\"type\":\"section\",\"data\":{\"label\":\"Quick Actions\",\"col\":12}},{\"id\":\"shortcut-pharmacist\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Pharmacist\",\"col\":6}},{\"id\":\"shortcut-shift\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Shift Assignment\",\"col\":6}},{\"id\":\"section-emp\",\"type\":\"section\",\"data\":{\"label\":\"Employee Operations\",\"col\":12}},{\"id\":\"card-staff\",\"type\":\"card\",\"data\":{\"card_name\":\"Staff Management\",\"col\":12,\"links\":[{\"label\":\"Pharmacist\",\"link_to\":\"Pharmacist\",\"link_type\":\"DocType\"},{\"label\":\"Shift Assignment\",\"link_to\":\"Shift Assignment\",\"link_type\":\"DocType\"}]}}]",
    },
    {
        "name": "Vendor Portal",
        "label": "Vendor Portal",
        "title": "Vendor Portal",
        "icon": "truck",
        "module": "Dashboard",
        "sequence_id": 12,
        "roles": [{"role": "System Manager"}, {"role": "Pharmacy Administrator"}, {"role": "Purchase Officer"}, {"role": "Store Manager"}],
        "shortcuts": [
            {"doc_view": "List", "label": "Purchase Request", "link_to": "Purchase Request", "type": "DocType"},
            {"doc_view": "List", "label": "Purchase Order", "link_to": "Purchase Order", "type": "DocType"},
        ],
        "content": "[{\"id\":\"vendor-quick\",\"type\":\"section\",\"data\":{\"label\":\"Quick Actions\",\"col\":12}},{\"id\":\"shortcut-purchase\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Purchase Request\",\"col\":12}},{\"id\":\"section-vendor\",\"type\":\"section\",\"data\":{\"label\":\"Vendor Portal\",\"col\":12}},{\"id\":\"card-vendor\",\"type\":\"card\",\"data\":{\"card_name\":\"Vendor Management\",\"col\":12,\"links\":[{\"label\":\"Purchase Request\",\"link_to\":\"Purchase Request\",\"link_type\":\"DocType\"},{\"label\":\"Purchase Order\",\"link_to\":\"Purchase Order\",\"link_type\":\"DocType\"}]}}]",
    },
    {
        "name": "Finance",
        "label": "Finance",
        "title": "Finance",
        "icon": "line-chart",
        "module": "Dashboard",
        "sequence_id": 13,
        "roles": [{"role": "System Manager"}, {"role": "Pharmacy Administrator"}, {"role": "Pharmacy Auditor"}],
        "shortcuts": [
            {"label": "Daily Sales Report", "link_to": "Daily Sales Report", "type": "Report"},
            {"label": "Purchase Analysis", "link_to": "Purchase Analysis", "type": "Report"},
        ],
        "content": "[{\"id\":\"fin-quick\",\"type\":\"section\",\"data\":{\"label\":\"Quick Actions\",\"col\":12}},{\"id\":\"shortcut-sales\",\"type\":\"shortcut\",\"data\":{\"shortcut_name\":\"Daily Sales Report\",\"col\":12}},{\"id\":\"section-fin\",\"type\":\"section\",\"data\":{\"label\":\"Finance & Accounting\",\"col\":12}},{\"id\":\"card-finance\",\"type\":\"card\",\"data\":{\"card_name\":\"Reports\",\"col\":12,\"links\":[{\"label\":\"Daily Sales Report\",\"link_to\":\"Daily Sales Report\",\"link_type\":\"Report\"},{\"label\":\"Purchase Analysis\",\"link_to\":\"Purchase Analysis\",\"link_type\":\"Report\"}]}}]",
    },
]


def execute():
    """Create all pharmacy workspace documents directly in the database.
    This patch ensures workspaces are created even if the file-based
    auto-discovery mechanism doesn't pick them up.
    """
    links_map = {
        "Pharmacy": [
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Patient", "link_count": 0, "link_to": "Patient", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Insurance Provider", "link_count": 0, "link_to": "Insurance Provider", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Loyalty Program", "link_count": 0, "link_to": "Loyalty Program", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Insurance Claim", "link_count": 0, "link_to": "Insurance Claim", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Doctor Master", "link_count": 0, "link_to": "Doctor Master", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Prescription", "link_count": 0, "link_to": "Prescription", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Medicine Master", "link_count": 0, "link_to": "Medicine Master", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Medicine Category", "link_count": 0, "link_to": "Medicine Category", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Drug Manufacturer", "link_count": 0, "link_to": "Drug Manufacturer", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Drug Composition", "link_count": 0, "link_to": "Drug Composition", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Medicine Batch", "link_count": 0, "link_to": "Medicine Batch", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Stock Adjustment", "link_count": 0, "link_to": "Stock Adjustment", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Stock Transfer", "link_count": 0, "link_to": "Stock Transfer", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "POS Invoice Ext", "link_count": 0, "link_to": "POS Invoice Ext", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Purchase Request", "link_count": 0, "link_to": "Purchase Request", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Expiry Alert", "link_count": 0, "link_to": "Expiry Alert", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Drug License", "link_count": 0, "link_to": "Drug License", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Audit Log", "link_count": 0, "link_to": "Audit Log", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Pharmacist", "link_count": 0, "link_to": "Pharmacist", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Shift Assignment", "link_count": 0, "link_to": "Shift Assignment", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Daily Sales Report", "link_count": 0, "link_to": "Daily Sales Report", "link_type": "Report", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Near Expiry Stock", "link_count": 0, "link_to": "Near Expiry Stock", "link_type": "Report", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Stock Ledger Medicine", "link_count": 0, "link_to": "Stock Ledger Medicine", "link_type": "Report", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Purchase Analysis", "link_count": 0, "link_to": "Purchase Analysis", "link_type": "Report", "onboard": 0, "type": "Link"},
        ],
        "Pharmacy CRM": [
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Patient", "link_count": 0, "link_to": "Patient", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Loyalty Program", "link_count": 0, "link_to": "Loyalty Program", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Insurance Provider", "link_count": 0, "link_to": "Insurance Provider", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Insurance Claim", "link_count": 0, "link_to": "Insurance Claim", "link_type": "DocType", "onboard": 0, "type": "Link"},
        ],
        "Catalog": [
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Medicine Master", "link_count": 0, "link_to": "Medicine Master", "link_type": "DocType", "onboard": 1, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Medicine Category", "link_count": 0, "link_to": "Medicine Category", "link_type": "DocType", "onboard": 1, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Drug Manufacturer", "link_count": 0, "link_to": "Drug Manufacturer", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Drug Composition", "link_count": 0, "link_to": "Drug Composition", "link_type": "DocType", "onboard": 0, "type": "Link"},
        ],
        "Inventory": [
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Medicine Batch", "link_count": 0, "link_to": "Medicine Batch", "link_type": "DocType", "onboard": 1, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Stock Adjustment", "link_count": 0, "link_to": "Stock Adjustment", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Stock Transfer", "link_count": 0, "link_to": "Stock Transfer", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Stock Ledger Medicine", "link_count": 0, "link_to": "Stock Ledger Medicine", "link_type": "Report", "onboard": 0, "type": "Link"},
        ],
        "Procurement": [
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Purchase Request", "link_count": 0, "link_to": "Purchase Request", "link_type": "DocType", "onboard": 1, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Purchase Request Item", "link_count": 0, "link_to": "Purchase Request Item", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Purchase Analysis", "link_count": 0, "link_to": "Purchase Analysis", "link_type": "Report", "onboard": 0, "type": "Link"},
        ],
        "Prescription": [
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Prescription", "link_count": 0, "link_to": "Prescription", "link_type": "DocType", "onboard": 1, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Prescription Item", "link_count": 0, "link_to": "Prescription Item", "link_type": "DocType", "onboard": 0, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Doctor Master", "link_count": 0, "link_to": "Doctor Master", "link_type": "DocType", "onboard": 1, "type": "Link"},
        ],
        "POS": [
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "POS Invoice Ext", "link_count": 0, "link_to": "POS Invoice Ext", "link_type": "DocType", "onboard": 1, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Daily Sales Report", "link_count": 0, "link_to": "Daily Sales Report", "link_type": "Report", "onboard": 0, "type": "Link"},
        ],
        "Insurance": [
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Insurance Claim", "link_count": 0, "link_to": "Insurance Claim", "link_type": "DocType", "onboard": 1, "type": "Link"},
        ],
        "Batch Tracking": [
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Expiry Alert", "link_count": 0, "link_to": "Expiry Alert", "link_type": "DocType", "onboard": 1, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Near Expiry Stock", "link_count": 0, "link_to": "Near Expiry Stock", "link_type": "Report", "onboard": 0, "type": "Link"},
        ],
        "Compliance": [
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Drug License", "link_count": 0, "link_to": "Drug License", "link_type": "DocType", "onboard": 1, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Audit Log", "link_count": 0, "link_to": "Audit Log", "link_type": "DocType", "onboard": 0, "type": "Link"},
        ],
        "Employee Ops": [
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Pharmacist", "link_count": 0, "link_to": "Pharmacist", "link_type": "DocType", "onboard": 1, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Shift Assignment", "link_count": 0, "link_to": "Shift Assignment", "link_type": "DocType", "onboard": 0, "type": "Link"},
        ],
        "Vendor Portal": [
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Purchase Request", "link_count": 0, "link_to": "Purchase Request", "link_type": "DocType", "onboard": 1, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Purchase Order", "link_count": 0, "link_to": "Purchase Order", "link_type": "DocType", "onboard": 0, "type": "Link"},
        ],
        "Finance": [
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Daily Sales Report", "link_count": 0, "link_to": "Daily Sales Report", "link_type": "Report", "onboard": 1, "type": "Link"},
            {"dependencies": "", "hidden": 0, "is_query_report": 0, "label": "Purchase Analysis", "link_count": 0, "link_to": "Purchase Analysis", "link_type": "Report", "onboard": 0, "type": "Link"},
        ],
    }

    for ws in WORKSPACES:
        name = ws["name"]
        if frappe.db.exists("Workspace", name):
            frappe.delete_doc("Workspace", name, force=True)

        doc = frappe.get_doc({
            "doctype": "Workspace",
            "charts": [],
            "content": ws["content"],
            "extends_another_page": 0,
            "hide_custom": 0,
            "icon": ws["icon"],
            "is_hidden": 0,
            "label": ws["label"],
            "title": ws.get("title", ws["label"]),
            "module": ws["module"],
            "name": name,
            "public": 1,
            "roles": ws["roles"],
            "sequence_id": ws["sequence_id"],
            "shortcuts": ws["shortcuts"],
            "links": links_map.get(name, []),
        })
        doc.flags.ignore_permissions = True
        doc.flags.ignore_mandatory = True
        doc.flags.ignore_links = True
        doc.flags.ignore_validate = True
        doc.insert()
        print(f"Created workspace: {name}")

    clear_workspace_cache()
    print("Cache cleared — workspaces should now be visible.")
