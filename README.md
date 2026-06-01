# Pharmacy Management System for ERPNext v15+

A comprehensive pharmacy management application built on the **Frappe Framework** and **ERPNext v15+**, inspired by modern pharmacy platforms like PharmEasy.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Module Structure](#module-structure)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Modules & DocTypes](#modules--doctypes)
6. [Reports](#reports)
7. [Workflows](#workflows)
8. [Notifications](#notifications)
9. [Roles & Permissions](#roles--permissions)
10. [Workspace](#workspace)
11. [Scheduler Tasks](#scheduler-tasks)
12. [Customization](#customization)
13. [API Reference](#api-reference)

---

## Overview

The **Pharmacy Management System** (`pharmacy_management`) is a Frappe/ERPNext custom app providing:

- 🏥 Patient & CRM management  
- 💊 Complete medicine catalog with batch/expiry tracking  
- 🔄 Inventory control with multi-warehouse support  
- 📋 Prescription (Rx) management workflow  
- 🖥️ Point of Sale (POS) for fast billing  
- 🏥 Insurance claim processing  
- 📦 Procurement & vendor management  
- 👔 Employee & shift management  
- ⚖️ Regulatory compliance & drug license tracking  
- 📊 Executive dashboard with KPIs  

---

## Module Structure

```
pharmacy_management/
├── pharmacy_management/
│   ├── crm/                          # Pharmacy CRM Module
│   │   └── doctype/
│   │       ├── patient/
│   │       ├── loyalty_program/
│   │       └── insurance_provider/
│   ├── catalog/                      # Medicine Catalog Module
│   │   └── doctype/
│   │       ├── medicine_master/
│   │       ├── medicine_category/
│   │       ├── drug_manufacturer/
│   │       ├── drug_composition/
│   │       └── drug_composition_item/
│   ├── inventory/                    # Inventory Control Module
│   │   ├── doctype/
│   │   │   ├── medicine_batch/
│   │   │   ├── stock_adjustment/
│   │   │   ├── stock_adjustment_item/
│   │   │   ├── stock_transfer/
│   │   │   └── stock_transfer_item/
│   │   ├── report/
│   │   │   └── stock_ledger_medicine/
│   │   └── tasks.py
│   ├── procurement/                  # Procurement Management Module
│   │   ├── doctype/
│   │   │   ├── purchase_request/
│   │   │   └── purchase_request_item/
│   │   ├── report/
│   │   │   └── purchase_analysis/
│   │   └── notification/
│   │       └── purchase_request_approval.json
│   ├── prescription/                 # Prescription Management Module
│   │   ├── doctype/
│   │   │   ├── prescription/
│   │   │   ├── prescription_item/
│   │   │   └── doctor_master/
│   │   └── notification/
│   │       └── prescription_verified.json
│   ├── pos/                          # Point of Sale Module
│   │   ├── doctype/
│   │   │   ├── pos_invoice_ext/
│   │   │   └── pos_invoice_item_ext/
│   │   └── report/
│   │       └── daily_sales_report/
│   ├── insurance/                    # Insurance Processing Module
│   │   └── doctype/
│   │       └── insurance_claim/
│   ├── batch_tracking/               # Expiry & Batch Tracking Module
│   │   ├── doctype/
│   │   │   └── expiry_alert/
│   │   ├── report/
│   │   │   └── near_expiry_stock/
│   │   ├── notification/
│   │   │   └── expiry_alert_notification.json
│   │   └── tasks.py
│   ├── employee_ops/                 # Employee Operations Module
│   │   └── doctype/
│   │       ├── pharmacist/
│   │       └── shift_assignment/
│   ├── compliance/                   # Regulatory Compliance Module
│   │   ├── doctype/
│   │   │   ├── drug_license/
│   │   │   └── audit_log/
│   │   ├── notification/
│   │   │   └── drug_license_expiry.json
│   │   └── tasks.py
│   ├── dashboard/                    # Dashboard & Workspace
│   │   └── workspace/
│   │       └── pharmacy_dashboard.json
│   ├── public/
│   │   ├── js/pharmacy.js
│   │   └── css/pharmacy.css
│   ├── hooks.py
│   ├── modules.txt
│   ├── notifications.py
│   └── setup.py
├── setup.py
├── requirements.txt
└── README.md
```

---

## Installation

### Prerequisites

- Python 3.10+
- Node.js 18+
- ERPNext v15+ installed on Frappe Bench
- MariaDB 10.6+ or MySQL 8.0+

### Step 1 — Get the App

```bash
cd /path/to/frappe-bench
bench get-app pharmacy_management https://github.com/yourorg/pharmacy_management
# OR for local development:
bench get-app pharmacy_management /path/to/pharmacy_management
```

### Step 2 — Install on Site

```bash
bench --site your-site.local install-app pharmacy_management
```

### Step 3 — Run Migrations

```bash
bench --site your-site.local migrate
```

### Step 4 — Build Assets

```bash
bench build --app pharmacy_management
```

### Step 5 — Restart

```bash
bench restart
# Or in production:
sudo supervisorctl restart all
```

### Step 6 — Verify Installation

```bash
bench --site your-site.local list-apps
# Should show: pharmacy_management
```

---

## Configuration

### 1. Set Up Company

Ensure ERPNext company is configured:

```
ERPNext > Setup > Company
- Company Name: Your Pharmacy Name
- Default Currency: INR
- Country: India
```

### 2. Configure Warehouses

```
Stock > Warehouse
- Pharmacy Main Store
- Cold Storage
- Dispensing Counter
```

### 3. POS Profile Setup

```
Retail > POS Profile
- POS Profile Name: Pharmacy Counter 1
- Warehouse: Pharmacy Main Store
- Taxes: GST (as applicable)
- Payment Methods: Cash, Card, UPI
```

### 4. Drug License Setup

```
Pharmacy > Regulatory Compliance > Drug License
- Add all pharmacy licenses
- Set renewal reminder days (recommended: 60)
```

### 5. Loyalty Program

```
Pharmacy > CRM > Loyalty Program
- Program Name: Standard Pharmacy Loyalty
- Points Per Rupee: 1
- Redemption Value: ₹0.10 per point
```

---

## Modules & DocTypes

### 1. Pharmacy CRM Module

#### Patient
**Path:** `crm/doctype/patient`  
**Purpose:** Central patient registry with medical & insurance details.

| Field | Type | Description |
|-------|------|-------------|
| patient_name | Data | Full name (required) |
| mobile_number | Data | 10-digit mobile (required) |
| date_of_birth | Date | For age calculation |
| blood_group | Select | A+/A-/B+/B-/O+/O-/AB+/AB- |
| allergies | Small Text | Known drug allergies |
| insurance_provider | Link | Linked Insurance Provider |
| loyalty_program | Link | Loyalty Program |
| loyalty_points | Float | Current points balance (auto) |

**API Methods:**
```python
# Get patient purchase history
frappe.call('pharmacy_management.crm.doctype.patient.patient.get_patient_purchase_history', {
    patient: 'PAT-2025-00001'
})
```

#### Loyalty Program
**Path:** `crm/doctype/loyalty_program`

| Field | Description |
|-------|-------------|
| points_per_rupee | How many points per ₹1 spent |
| redemption_value | ₹ value per redeemed point |
| min_points_to_redeem | Minimum points to redeem |

#### Insurance Provider
**Path:** `crm/doctype/insurance_provider`

Tracks TPA details, contact info, claim coverage percentage.

---

### 2. Medicine Catalog Module

#### Medicine Master
**Path:** `catalog/doctype/medicine_master`  
**Purpose:** Complete medicine product database.

| Field | Type | Notes |
|-------|------|-------|
| medicine_name | Data | Brand name (Dolo 650) |
| generic_name | Data | INN (Paracetamol) |
| strength | Data | 650mg, 500mg/5ml |
| dosage_form | Select | Tablet/Capsule/Syrup/... |
| hsn_code | Data | For GST compliance |
| gst_rate | Select | 0/5/12/18/28 % |
| schedule | Select | H/H1/X/G/OTC |
| requires_prescription | Check | Mandatory Rx flag |
| barcode | Data | For POS scanning |
| reorder_level | Float | Auto-reorder trigger |
| mrp | Currency | Maximum Retail Price |

**Example:**
```
Medicine Name: Dolo 650
Generic Name: Paracetamol
Strength: 650 mg
Category: Tablet
Dosage Form: Tablet
HSN Code: 30049099
GST Rate: 12%
Schedule: OTC
MRP: ₹30.00
```

---

### 3. Inventory Control Module

#### Medicine Batch
**Path:** `inventory/doctype/medicine_batch`

Tracks every physical batch in stock.

| Field | Description |
|-------|-------------|
| batch_no | Manufacturer batch number |
| medicine | Linked Medicine Master |
| expiry_date | Expiry date (required) |
| current_qty | Live stock (maintained by system) |
| batch_status | Active / Near Expiry / Expired / Disposed |
| days_to_expiry | Calculated automatically |

**Batch Status Logic:**
```
days_to_expiry < 0        → Expired
days_to_expiry ≤ threshold → Near Expiry
else                       → Active
```

#### Stock Adjustment
**Path:** `inventory/doctype/stock_adjustment`  
Types: Write Off, Damage, Expiry Disposal, Count Adjustment  
On submit → creates ERPNext Stock Entry (Material Issue).

#### Stock Transfer
**Path:** `inventory/doctype/stock_transfer`  
On submit → creates ERPNext Stock Entry (Material Transfer).

---

### 4. Procurement Management Module

#### Purchase Request
**Path:** `procurement/doctype/purchase_request`

**Workflow:**
```
Draft
  ↓ Submit
Pending Approval
  ↓ Approve (Pharmacy Administrator)
Approved
  ↓ Create PO
PO Created
  ↓ Receive Goods
Completed
```

**Auto-Reorder:** Scheduler runs daily → checks reorder levels → creates Purchase Request automatically.

---

### 5. Prescription Management Module

#### Doctor Master
**Path:** `prescription/doctype/doctor_master`  
Maintains registered doctors with their MCI/state registration numbers.

#### Prescription
**Path:** `prescription/doctype/prescription`

**Workflow:**
```
Uploaded       → Patient uploads / pharmacist enters
  ↓ Submit
Verification   → Pharmacist verifies authenticity
  ↓
Dispensing     → Medicines being dispensed
  ↓
Completed      → Linked to Sales Invoice
```

**Fields include:** Doctor, Prescription Date, Valid Till, Medicine Items, Prescription Image upload.

---

### 6. Point of Sale Module

#### POS Invoice Ext
**Path:** `pos/doctype/pos_invoice_ext`

**Features:**
- Link to Patient for loyalty point tracking
- Prescription reference validation
- Batch-wise item selection with expiry date display
- Multiple payment modes: Cash, Card, UPI, Insurance, Loyalty, Mixed
- Auto GST calculation per item
- Loyalty point redemption
- On submit → creates ERPNext Sales Invoice

---

### 7. Insurance Processing Module

#### Insurance Claim
**Path:** `insurance/doctype/insurance_claim`

**Claim Status Flow:**
```
Draft → Submitted → Under Review → Approved → Settled
                                             → Rejected
```

Tracks claimed amount, approved amount, deductible, patient liability.

---

### 8. Batch Tracking Module

#### Expiry Alert
**Path:** `batch_tracking/doctype/expiry_alert`

Alert Levels:
- **Info** — 91–180 days to expiry
- **Warning** — 31–90 days to expiry
- **Critical** — 0–30 days to expiry

Dashboard widget shows count of Critical + Warning alerts.

---

### 9. Employee Operations Module

#### Pharmacist
Pharmacist registry with license details, qualification, registration number, license expiry.

#### Shift Assignment
Assigns pharmacists to shifts (Morning/Afternoon/Evening/Night) with warehouse assignment.

---

### 10. Regulatory Compliance Module

#### Drug License
Tracks all regulatory licenses:
- Drug License (Form 20/21)
- Narcotic License
- GST Registration
- FSSAI (if applicable)
- Shop Act License

Auto-updates status to "Expiring Soon" when within reminder window.

#### Audit Log
System-level audit trail for sensitive operations.

---

## Reports

| Report | Module | Description |
|--------|--------|-------------|
| Daily Sales Report | Point of Sale | Sales by date, cashier, payment mode |
| Near Expiry Stock | Batch Tracking | Medicines expiring within threshold |
| Stock Ledger Medicine | Inventory Control | Complete stock movement history |
| Purchase Analysis | Procurement | Supplier-wise purchase analytics |

### Adding Custom Filters

Reports support standard Frappe filter objects. Add filters in the JSON:

```json
"filters": [
  {
    "fieldname": "from_date",
    "label": "From Date",
    "fieldtype": "Date",
    "default": "Today"
  }
]
```

---

## Workflows

### Prescription Workflow

```
[Patient/Pharmacist]
       │
       ▼
  Prescription Created (Uploaded)
       │
       ▼ (Submit)
  Pending Verification
       │
       ▼ (Pharmacist verifies)
  Dispensing
       │
       ▼ (POS Invoice created)
  Completed ──────────────────► Linked Sales Invoice
       │
       └──(Cancel)──► Cancelled
```

### Purchase Request Workflow

```
[Store Manager / Purchase Officer]
       │
       ▼
  Purchase Request Draft
       │
       ▼ (Submit)
  Pending Approval ──► Email to Admin
       │
       ▼ (Admin approves)
  Approved
       │
       ▼ (Create PO button)
  PO Created ──────────────────► Purchase Order in ERPNext
       │
       ▼ (Goods received)
  Completed
```

---

## Notifications

| Notification | Trigger | Recipients |
|---|---|---|
| Expiry Alert Notification | Batch near/at expiry | Store Manager, Admin |
| Drug License Expiry | License status changes | Pharmacy Administrator |
| Purchase Request Approval | PR submitted | Pharmacy Administrator |
| Prescription Ready for Dispensing | Status = Dispensing | Pharmacist, Cashier |

All notifications use **Email** + **System Notification** channels.

---

## Roles & Permissions

| Role | Access Level |
|------|-------------|
| **Pharmacy Administrator** | Full access to all doctypes, reports, settings |
| **Pharmacist** | Patient, Prescription, POS, Medicine, Batch read/write |
| **Store Manager** | Inventory, Batch, Shift, Purchase Requests |
| **Purchase Officer** | Purchase Requests, Purchase Analysis |
| **Pharmacy Cashier** | POS Invoice create/submit, Prescription read |
| **Pharmacy Auditor** | Read-only access to all doctypes + reports |

### Role Setup

Roles are created automatically on app install via `setup.py`.

Manual setup:
```
Setup > Role > New Role
```

---

## Workspace

The **Pharmacy** workspace is automatically added to the sidebar with:

**Shortcuts:**
- Patients
- Medicines
- Prescriptions
- POS Billing
- Medicine Batches
- Expiry Alerts
- Insurance Claims
- Purchase Requests
- Daily Sales Report
- Near Expiry Stock

---

## Scheduler Tasks

Defined in `hooks.py`:

```python
scheduler_events = {
    "daily": [
        "pharmacy_management.batch_tracking.tasks.send_expiry_alerts",
        "pharmacy_management.inventory.tasks.check_reorder_levels",
        "pharmacy_management.compliance.tasks.check_license_expiry",
    ],
    "weekly": [
        "pharmacy_management.batch_tracking.tasks.dispose_expired_stock",
    ],
}
```

| Task | Frequency | Action |
|------|-----------|--------|
| send_expiry_alerts | Daily | Scans batches, creates Expiry Alert docs |
| check_reorder_levels | Daily | Creates auto Purchase Request for low stock |
| check_license_expiry | Daily | Updates Drug License statuses |
| dispose_expired_stock | Weekly | Marks expired batches |

### Manual Trigger

```bash
bench --site your-site.local execute pharmacy_management.batch_tracking.tasks.send_expiry_alerts
```

---

## Customization

### Adding a New DocType

```bash
bench --site your-site.local new-doctype "Your DocType" --module "Pharmacy CRM"
```

### Custom Script Example

```python
# In your_doctype.py
import frappe
from frappe.model.document import Document

class YourDocType(Document):
    def validate(self):
        # Your validation logic
        pass
```

### Custom Report

```python
# report_name.py
import frappe

def execute(filters=None):
    columns = [{"label": "Column", "fieldname": "col", "fieldtype": "Data", "width": 120}]
    data = frappe.db.sql("SELECT ...", as_dict=True)
    return columns, data
```

---

## API Reference

### Patient APIs

```python
# Get patient purchase history
frappe.call({
    method: 'pharmacy_management.crm.doctype.patient.patient.get_patient_purchase_history',
    args: { patient: 'PAT-2025-00001' }
})

# Search medicines
frappe.call({
    method: 'pharmacy_management.catalog.doctype.medicine_master.medicine_master.search_medicine',
    args: { query: 'paracetamol' }
})

# Get medicine stock
frappe.call({
    method: 'pharmacy_management.catalog.doctype.medicine_master.medicine_master.get_medicine_stock',
    args: { medicine: 'MED-2025-00001', warehouse: 'Pharmacy Main Store - PM' }
})
```

---

## ERPNext Integration Points

| Pharmacy DocType | ERPNext DocType |
|------------------|-----------------|
| POS Invoice Ext | Sales Invoice |
| Stock Adjustment | Stock Entry (Material Issue) |
| Stock Transfer | Stock Entry (Material Transfer) |
| Purchase Request | Purchase Order |
| Medicine Master | Item |
| Drug Manufacturer | Supplier |
| Patient | Customer |

---

## Troubleshooting

### App not visible after install
```bash
bench --site your-site.local clear-cache
bench build --app pharmacy_management
bench restart
```

### DocType not found
```bash
bench --site your-site.local migrate
```

### Scheduler not running
```bash
bench --site your-site.local enable-scheduler
bench scheduler status
```

### Permission errors
Check role profiles and ensure roles from `setup.py` were created:
```bash
bench --site your-site.local execute pharmacy_management.setup.create_roles
```

---

## License

MIT License — See LICENSE file for details.

---

## Support

For issues and feature requests, create a GitHub issue or contact your system administrator.
