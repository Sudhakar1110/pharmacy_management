"""
Pharmacy Management - Add More Demo Medicines
===============================================
Run via: bench execute pharmacy_management.fixtures.add_more_medicines.add_more_medicines

Adds 15+ new medicines with batches and stock to make the e-commerce shop
look comprehensive. Adds 4 new categories and additional medicines to
existing categories.
"""

import frappe
from frappe.utils import today, add_days, add_months


def _insert(doc_dict):
    doc = frappe.get_doc(doc_dict)
    doc.insert(ignore_permissions=True)
    return doc.name


# =============================================================================
# New Categories
# =============================================================================

NEW_CATEGORIES = [
    {"category_name": "Nervous System", "description": "Neurology and CNS medications", "gst_rate": "12", "is_active": 1},
    {"category_name": "Eye Care", "description": "Eye drops and ophthalmic preparations", "gst_rate": "12", "is_active": 1},
    {"category_name": "Women's Health", "description": "Gynecological and prenatal medications", "gst_rate": "12", "is_active": 1},
    {"category_name": "Cold & Flu", "description": "Cold, cough, and allergy medications", "gst_rate": "18", "is_active": 1},
]

# =============================================================================
# New Medicines (15+)
# =============================================================================

NEW_MEDICINES = [
    # --- Antibiotics ---
    {
        "medicine_name": "Cefixime 200mg",
        "generic_name": "Cefixime",
        "brand_name": "Cefspan",
        "category": "Antibiotics",
        "manufacturer": "Sun Pharma",
        "strength": "200mg", "dosage_form": "Tablet", "unit_of_measure": "Strip", "pack_size": 10,
        "barcode": "8901234567810", "hsn_code": "30041090", "gst_rate": "12",
        "schedule": "H", "requires_prescription": 1,
        "mrp": 285.00, "purchase_rate": 215.00, "selling_rate": 270.00, "discount_percent": 5,
        "reorder_level": 40, "reorder_qty": 80, "min_stock_qty": 10,
        "storage_condition": "Room Temperature", "shelf_life_months": 24, "cold_chain": 0,
        "batch_qty": 180, "batch_no": "B2025001",
    },
    {
        "medicine_name": "Doxycycline 100mg",
        "generic_name": "Doxycycline Hyclate",
        "brand_name": "Doxi",
        "category": "Antibiotics",
        "manufacturer": "Cipla Ltd",
        "strength": "100mg", "dosage_form": "Capsule", "unit_of_measure": "Strip", "pack_size": 10,
        "barcode": "8901234567811", "hsn_code": "30041090", "gst_rate": "12",
        "schedule": "H", "requires_prescription": 1,
        "mrp": 89.00, "purchase_rate": 65.00, "selling_rate": 84.00, "discount_percent": 5,
        "reorder_level": 60, "reorder_qty": 120, "min_stock_qty": 15,
        "storage_condition": "Room Temperature", "shelf_life_months": 36, "cold_chain": 0,
        "batch_qty": 320, "batch_no": "B2025002",
    },
    # --- Cardiovascular ---
    {
        "medicine_name": "Telma 40mg",
        "generic_name": "Telmisartan",
        "brand_name": "Telma",
        "category": "Cardiovascular",
        "manufacturer": "Dr. Reddy's Labs",
        "strength": "40mg", "dosage_form": "Tablet", "unit_of_measure": "Strip", "pack_size": 15,
        "barcode": "8901234567812", "hsn_code": "30049099", "gst_rate": "12",
        "schedule": "H", "requires_prescription": 1,
        "mrp": 168.00, "purchase_rate": 128.00, "selling_rate": 159.00, "discount_percent": 5,
        "reorder_level": 80, "reorder_qty": 160, "min_stock_qty": 20,
        "storage_condition": "Room Temperature", "shelf_life_months": 24, "cold_chain": 0,
        "batch_qty": 245, "batch_no": "B2025003",
    },
    {
        "medicine_name": "Storvas 20mg",
        "generic_name": "Atorvastatin + Aspirin",
        "brand_name": "Storvas",
        "category": "Cardiovascular",
        "manufacturer": "Sun Pharma",
        "strength": "20mg + 75mg", "dosage_form": "Capsule", "unit_of_measure": "Strip", "pack_size": 10,
        "barcode": "8901234567813", "hsn_code": "30049099", "gst_rate": "12",
        "schedule": "H", "requires_prescription": 1,
        "mrp": 215.00, "purchase_rate": 162.00, "selling_rate": 204.00, "discount_percent": 5,
        "reorder_level": 50, "reorder_qty": 100, "min_stock_qty": 15,
        "storage_condition": "Room Temperature", "shelf_life_months": 24, "cold_chain": 0,
        "batch_qty": 198, "batch_no": "B2025004",
    },
    # --- Pain Relief ---
    {
        "medicine_name": "Diclofenac Gel 50g",
        "generic_name": "Diclofenac Sodium + Linseed",
        "brand_name": "Volini",
        "category": "Pain Relief",
        "manufacturer": "Mankind Pharma",
        "strength": "1%", "dosage_form": "Gel", "unit_of_measure": "Tube", "pack_size": 1,
        "barcode": "8901234567814", "hsn_code": "30049011", "gst_rate": "18",
        "schedule": "OTC", "requires_prescription": 0,
        "mrp": 145.00, "purchase_rate": 108.00, "selling_rate": 138.00, "discount_percent": 5,
        "reorder_level": 60, "reorder_qty": 120, "min_stock_qty": 15,
        "storage_condition": "Room Temperature", "shelf_life_months": 24, "cold_chain": 0,
        "batch_qty": 156, "batch_no": "B2025005",
    },
    {
        "medicine_name": "Combiflam Tablets",
        "generic_name": "Ibuprofen + Paracetamol",
        "brand_name": "Combiflam",
        "category": "Pain Relief",
        "manufacturer": "Abbott India Ltd",
        "strength": "400mg + 500mg", "dosage_form": "Tablet", "unit_of_measure": "Strip", "pack_size": 15,
        "barcode": "8901234567815", "hsn_code": "30049011", "gst_rate": "18",
        "schedule": "OTC", "requires_prescription": 0,
        "mrp": 118.00, "purchase_rate": 85.00, "selling_rate": 112.00, "discount_percent": 5,
        "reorder_level": 150, "reorder_qty": 300, "min_stock_qty": 40,
        "storage_condition": "Room Temperature", "shelf_life_months": 36, "cold_chain": 0,
        "batch_qty": 450, "batch_no": "B2025006",
    },
    # --- Respiratory ---
    {
        "medicine_name": "Duolin Inhaler",
        "generic_name": "Levosalbutamol + Ipratropium",
        "brand_name": "Duolin",
        "category": "Respiratory",
        "manufacturer": "Cipla Ltd",
        "strength": "50mcg + 20mcg", "dosage_form": "Inhaler", "unit_of_measure": "Piece", "pack_size": 1,
        "barcode": "8901234567816", "hsn_code": "30043900", "gst_rate": "12",
        "schedule": "H", "requires_prescription": 1,
        "mrp": 425.00, "purchase_rate": 355.00, "selling_rate": 405.00, "discount_percent": 5,
        "reorder_level": 20, "reorder_qty": 50, "min_stock_qty": 5,
        "storage_condition": "Room Temperature", "shelf_life_months": 24, "cold_chain": 0,
        "batch_qty": 65, "batch_no": "B2025007",
    },
    {
        "medicine_name": "Montair LC 10mg",
        "generic_name": "Montelukast + Levocetrizine",
        "brand_name": "Montair LC",
        "category": "Respiratory",
        "manufacturer": "Mankind Pharma",
        "strength": "10mg + 5mg", "dosage_form": "Tablet", "unit_of_measure": "Strip", "pack_size": 10,
        "barcode": "8901234567817", "hsn_code": "30049099", "gst_rate": "12",
        "schedule": "H", "requires_prescription": 1,
        "mrp": 156.00, "purchase_rate": 118.00, "selling_rate": 148.00, "discount_percent": 5,
        "reorder_level": 60, "reorder_qty": 120, "min_stock_qty": 15,
        "storage_condition": "Room Temperature", "shelf_life_months": 24, "cold_chain": 0,
        "batch_qty": 275, "batch_no": "B2025008",
    },
    # --- Nervous System ---
    {
        "medicine_name": "Neurobion Forte",
        "generic_name": "B-Complex + B12",
        "brand_name": "Neurobion",
        "category": "Nervous System",
        "manufacturer": "Abbott India Ltd",
        "strength": "Vitamin B Complex", "dosage_form": "Tablet", "unit_of_measure": "Strip", "pack_size": 15,
        "barcode": "8901234567818", "hsn_code": "21069099", "gst_rate": "12",
        "schedule": "OTC", "requires_prescription": 0,
        "mrp": 198.00, "purchase_rate": 152.00, "selling_rate": 188.00, "discount_percent": 5,
        "reorder_level": 80, "reorder_qty": 160, "min_stock_qty": 20,
        "storage_condition": "Room Temperature", "shelf_life_months": 36, "cold_chain": 0,
        "batch_qty": 320, "batch_no": "B2025009",
    },
    {
        "medicine_name": "Ultracet Tablets",
        "generic_name": "Tramadol + Paracetamol",
        "brand_name": "Ultracet",
        "category": "Nervous System",
        "manufacturer": "Sun Pharma",
        "strength": "37.5mg + 325mg", "dosage_form": "Tablet", "unit_of_measure": "Strip", "pack_size": 10,
        "barcode": "8901234567819", "hsn_code": "30049099", "gst_rate": "12",
        "schedule": "H", "requires_prescription": 1,
        "mrp": 165.00, "purchase_rate": 125.00, "selling_rate": 157.00, "discount_percent": 5,
        "reorder_level": 40, "reorder_qty": 80, "min_stock_qty": 10,
        "storage_condition": "Room Temperature", "shelf_life_months": 24, "cold_chain": 0,
        "batch_qty": 185, "batch_no": "B2025010",
    },
    # --- Eye Care ---
    {
        "medicine_name": "Moisture Eye Drops",
        "generic_name": "Polyvinyl Alcohol + Povidone",
        "brand_name": "Refresh Tears",
        "category": "Eye Care",
        "manufacturer": "GSK Pharma Ltd",
        "strength": "10ml", "dosage_form": "Drops", "unit_of_measure": "Bottle", "pack_size": 1,
        "barcode": "8901234567820", "hsn_code": "30049099", "gst_rate": "12",
        "schedule": "OTC", "requires_prescription": 0,
        "mrp": 220.00, "purchase_rate": 168.00, "selling_rate": 209.00, "discount_percent": 5,
        "reorder_level": 50, "reorder_qty": 100, "min_stock_qty": 10,
        "storage_condition": "Room Temperature", "shelf_life_months": 18, "cold_chain": 0,
        "batch_qty": 120, "batch_no": "B2025011",
    },
    {
        "medicine_name": "Gatiflox Eye Drops",
        "generic_name": "Gatifloxacin",
        "brand_name": "Gatiquin",
        "category": "Eye Care",
        "manufacturer": "Mankind Pharma",
        "strength": "0.3% w/v", "dosage_form": "Drops", "unit_of_measure": "Bottle", "pack_size": 1,
        "barcode": "8901234567821", "hsn_code": "30049099", "gst_rate": "12",
        "schedule": "H", "requires_prescription": 1,
        "mrp": 95.00, "purchase_rate": 72.00, "selling_rate": 90.00, "discount_percent": 5,
        "reorder_level": 40, "reorder_qty": 80, "min_stock_qty": 10,
        "storage_condition": "Room Temperature", "shelf_life_months": 18, "cold_chain": 0,
        "batch_qty": 88, "batch_no": "B2025012",
    },
    # --- Gastrointestinal ---
    {
        "medicine_name": "Rantac 150mg",
        "generic_name": "Ranitidine HCl",
        "brand_name": "Rantac",
        "category": "Gastrointestinal",
        "manufacturer": "Dr. Reddy's Labs",
        "strength": "150mg", "dosage_form": "Tablet", "unit_of_measure": "Strip", "pack_size": 15,
        "barcode": "8901234567822", "hsn_code": "30049099", "gst_rate": "12",
        "schedule": "H", "requires_prescription": 0,
        "mrp": 58.00, "purchase_rate": 42.00, "selling_rate": 55.00, "discount_percent": 5,
        "reorder_level": 200, "reorder_qty": 400, "min_stock_qty": 50,
        "storage_condition": "Room Temperature", "shelf_life_months": 36, "cold_chain": 0,
        "batch_qty": 580, "batch_no": "B2025013",
    },
    {
        "medicine_name": "Cremaffin Suspension",
        "generic_name": "Liquid Paraffin + Milk of Magnesia",
        "brand_name": "Cremaffin",
        "category": "Gastrointestinal",
        "manufacturer": "Abbott India Ltd",
        "strength": "100ml", "dosage_form": "Syrup", "unit_of_measure": "Bottle", "pack_size": 1,
        "barcode": "8901234567823", "hsn_code": "30049099", "gst_rate": "12",
        "schedule": "OTC", "requires_prescription": 0,
        "mrp": 92.00, "purchase_rate": 68.00, "selling_rate": 87.00, "discount_percent": 5,
        "reorder_level": 40, "reorder_qty": 80, "min_stock_qty": 10,
        "storage_condition": "Room Temperature", "shelf_life_months": 24, "cold_chain": 0,
        "batch_qty": 95, "batch_no": "B2025014",
    },
    # --- Women's Health ---
    {
        "medicine_name": "Folvite 5mg",
        "generic_name": "Folic Acid",
        "brand_name": "Folvite",
        "category": "Women's Health",
        "manufacturer": "Sun Pharma",
        "strength": "5mg", "dosage_form": "Tablet", "unit_of_measure": "Strip", "pack_size": 15,
        "barcode": "8901234567824", "hsn_code": "30049099", "gst_rate": "5",
        "schedule": "OTC", "requires_prescription": 0,
        "mrp": 38.00, "purchase_rate": 25.00, "selling_rate": 35.00, "discount_percent": 8,
        "reorder_level": 150, "reorder_qty": 300, "min_stock_qty": 40,
        "storage_condition": "Room Temperature", "shelf_life_months": 36, "cold_chain": 0,
        "batch_qty": 650, "batch_no": "B2025015",
    },
    # --- Diabetes Care ---
    {
        "medicine_name": "Glucored 2mg",
        "generic_name": "Glimepiride",
        "brand_name": "Glucored",
        "category": "Diabetes Care",
        "manufacturer": "Dr. Reddy's Labs",
        "strength": "2mg", "dosage_form": "Tablet", "unit_of_measure": "Strip", "pack_size": 10,
        "barcode": "8901234567825", "hsn_code": "30049099", "gst_rate": "12",
        "schedule": "H", "requires_prescription": 1,
        "mrp": 72.00, "purchase_rate": 52.00, "selling_rate": 68.00, "discount_percent": 5,
        "reorder_level": 100, "reorder_qty": 200, "min_stock_qty": 25,
        "storage_condition": "Room Temperature", "shelf_life_months": 36, "cold_chain": 0,
        "batch_qty": 340, "batch_no": "B2025016",
    },
    # --- Cold & Flu ---
    {
        "medicine_name": "Dolo 650mg",
        "generic_name": "Paracetamol IP",
        "brand_name": "Dolo",
        "category": "Pain Relief",
        "manufacturer": "GSK Pharma Ltd",
        "strength": "650mg", "dosage_form": "Tablet", "unit_of_measure": "Strip", "pack_size": 15,
        "barcode": "8901234567826", "hsn_code": "30049011", "gst_rate": "18",
        "schedule": "OTC", "requires_prescription": 0,
        "mrp": 48.00, "purchase_rate": 32.00, "selling_rate": 45.00, "discount_percent": 8,
        "reorder_level": 200, "reorder_qty": 500, "min_stock_qty": 50,
        "storage_condition": "Room Temperature", "shelf_life_months": 36, "cold_chain": 0,
        "batch_qty": 780, "batch_no": "B2025017",
    },
    {
        "medicine_name": "Sinarest Nasal Drops",
        "generic_name": "Xylometazoline HCl",
        "brand_name": "Sinarest",
        "category": "Cold & Flu",
        "manufacturer": "Cipla Ltd",
        "strength": "0.1% w/v", "dosage_form": "Drops", "unit_of_measure": "Bottle", "pack_size": 1,
        "barcode": "8901234567827", "hsn_code": "30049099", "gst_rate": "18",
        "schedule": "OTC", "requires_prescription": 0,
        "mrp": 75.00, "purchase_rate": 55.00, "selling_rate": 71.00, "discount_percent": 5,
        "reorder_level": 60, "reorder_qty": 120, "min_stock_qty": 15,
        "storage_condition": "Room Temperature", "shelf_life_months": 24, "cold_chain": 0,
        "batch_qty": 130, "batch_no": "B2025018",
    },
    # --- Dermatology ---
    {
        "medicine_name": "Clocip Ointment",
        "generic_name": "Clobetasol + Clotrimazole",
        "brand_name": "Clocip",
        "category": "Dermatology",
        "manufacturer": "Mankind Pharma",
        "strength": "0.05% + 1%", "dosage_form": "Ointment", "unit_of_measure": "Tube", "pack_size": 1,
        "barcode": "8901234567828", "hsn_code": "30049099", "gst_rate": "18",
        "schedule": "H", "requires_prescription": 1,
        "mrp": 88.00, "purchase_rate": 65.00, "selling_rate": 84.00, "discount_percent": 5,
        "reorder_level": 40, "reorder_qty": 80, "min_stock_qty": 10,
        "storage_condition": "Room Temperature", "shelf_life_months": 24, "cold_chain": 0,
        "batch_qty": 110, "batch_no": "B2025019",
    },
]


# =============================================================================
# Main function
# =============================================================================

def add_more_medicines():
    """Add new categories, medicines, batches, and fix stock."""
    print("=" * 60)
    print("➕ Adding More Demo Medicines")
    print("=" * 60)

    # 1. Add new categories
    cat_added = 0
    for cat in NEW_CATEGORIES:
        if not frappe.db.exists("Medicine Category", cat["category_name"]):
            _insert({"doctype": "Medicine Category", **cat})
            cat_added += 1
    if cat_added:
        print(f"✓ Added {cat_added} new Medicine Categories")
    else:
        print("  All new categories already exist, skipping...")

    # Get existing details
    categories = {c["category_name"]: c["name"] for c in frappe.get_all("Medicine Category", fields=["name", "category_name"])}
    manufacturers = frappe.db.get_all("Drug Manufacturer", pluck="name")
    warehouses = frappe.db.get_all("Warehouse", filters={"is_group": 0, "disabled": 0}, limit=3)
    warehouse = warehouses[0].name if warehouses else None
    if not warehouse:
        print("  ⚠ No warehouse found! Cannot create batches.")
        return

    # 2. Add new medicines
    med_count = 0
    batch_count = 0

    for med in NEW_MEDICINES:
        if frappe.db.exists("Medicine Master", {"medicine_name": med["medicine_name"]}):
            print(f"  ⚠ {med['medicine_name']} already exists, skipping...")
            continue

        batch_qty = med.pop("batch_qty")
        batch_no = med.pop("batch_no")
        cat_name = med.pop("category")

        # Map category
        cat = categories.get(cat_name)
        if not cat:
            print(f"  ⚠ Category '{cat_name}' not found, skipping {med['medicine_name']}...")
            continue

        # Map manufacturer
        mfr = med.pop("manufacturer")
        if mfr in manufacturers:
            med["manufacturer"] = mfr
        elif manufacturers:
            med["manufacturer"] = manufacturers[0]
        else:
            med["manufacturer"] = None

        med["category"] = cat

        # Create medicine
        try:
            doc = frappe.get_doc({"doctype": "Medicine Master", **med})
            doc.insert(ignore_permissions=True)
            med_count += 1
            med_name = doc.name
        except Exception as e:
            print(f"  ⚠ Error creating {med['medicine_name']}: {e}")
            continue

        # Create batch
        try:
            expiry = add_months(today(), 24)
            batch_doc = frappe.get_doc({
                "doctype": "Medicine Batch",
                "batch_no": batch_no,
                "medicine": med_name,
                "manufacturer": med.get("manufacturer"),
                "manufacturing_date": add_months(today(), -8),
                "expiry_date": expiry,
                "warehouse": warehouse,
                "received_qty": batch_qty,
                "current_qty": batch_qty,
                "mrp": med.get("mrp"),
                "selling_rate": med.get("selling_rate"),
                "purchase_rate": med.get("purchase_rate"),
                "batch_status": "Active",
                "near_expiry_threshold": 90,
            })
            batch_doc.insert(ignore_permissions=True)
            frappe.db.set_value("Medicine Batch", batch_doc.name, "current_qty", batch_qty)
            batch_count += 1
        except Exception as e:
            print(f"  ⚠ Error creating batch for {med['medicine_name']}: {e}")

        print(f"  ✓ {med['medicine_name']} (₹{med['selling_rate']}) — {int(batch_qty)} in stock")

    print()
    print(f"✅ Added {med_count} new medicines")
    print(f"✅ Added {batch_count} new batches")

    # 3. Fix stock (create Items and Bin records)
    print()
    print("--- Syncing stock to shop... ---")
    from pharmacy_management.fixtures.fix_stock import fix_stock
    fix_stock()

    frappe.db.commit()

    print()
    print(f"🎉 Shop now has {frappe.db.count('Medicine Master', {'is_active': 1})} active medicines!")
    print("Visit /shop to see the expanded inventory.")


if __name__ == "__main__":
    add_more_medicines()
