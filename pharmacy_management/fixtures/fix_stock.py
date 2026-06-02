"""
Pharmacy Management - Fix Stock Visibility
============================================
Run via: bench execute pharmacy_management.fixtures.fix_stock.fix_stock

Creates ERPNext Items and Bin records from Medicine Batch stock so that
the e-commerce shop correctly shows "In Stock" for medicines with available batches.
"""

import frappe
from frappe.utils import today


def fix_stock():
    """Create Items and Bin records for all Medicine Masters with batch stock."""
    print("=" * 60)
    print("🔧 Pharmacy Management - Fix Stock Visibility")
    print("=" * 60)

    medicines = frappe.get_all("Medicine Master", fields=["name", "medicine_name", "selling_rate", "mrp"])
    if not medicines:
        print("  ⚠ No Medicine Masters found!")
        return

    # Find the warehouse
    warehouse = _get_warehouse()
    if not warehouse:
        print("  ⚠ No warehouse found! Cannot create stock records.")
        return

    print(f"  Using warehouse: {warehouse}")

    created_items = 0
    created_bins = 0

    for med in medicines:
        # 1. Ensure ERPNext Item exists
        item_name = med.name
        if not frappe.db.exists("Item", item_name):
            try:
                item = frappe.get_doc({
                    "doctype": "Item",
                    "item_code": item_name,
                    "item_name": med.medicine_name or item_name,
                    "item_group": "Products",
                    "stock_uom": "Nos",
                    "is_stock_item": 1,
                    "valuation_rate": med.selling_rate or med.mrp or 0,
                    "standard_rate": med.selling_rate or med.mrp or 0,
                    "opening_stock": 0,
                })
                item.insert(ignore_permissions=True, ignore_mandatory=True)
                created_items += 1
            except Exception as e:
                print(f"  ⚠ Could not create Item for {item_name}: {e}")
                continue

        # 2. Calculate total stock from Medicine Batches
        total_stock = frappe.db.sql("""
            SELECT COALESCE(SUM(current_qty), 0) as total
            FROM `tabMedicine Batch`
            WHERE medicine = %s AND batch_status != 'Disposed'
              AND (expiry_date >= %s OR expiry_date IS NULL)
        """, (med.name, today()), as_dict=True)[0].total

        # 3. Create or update Bin record
        if total_stock > 0:
            existing_bin = frappe.db.get_value("Bin", {
                "item_code": item_name,
                "warehouse": warehouse
            }, "name")

            if existing_bin:
                frappe.db.set_value("Bin", existing_bin, "actual_qty", total_stock)
            else:
                try:
                    bin_doc = frappe.get_doc({
                        "doctype": "Bin",
                        "item_code": item_name,
                        "warehouse": warehouse,
                        "actual_qty": total_stock,
                    })
                    bin_doc.insert(ignore_permissions=True)
                    created_bins += 1
                except Exception as e:
                    print(f"  ⚠ Could not create Bin for {item_name}: {e}")

        # Print progress
        if total_stock > 0:
            print(f"  ✓ {med.medicine_name}: {int(total_stock)} units in stock")

    frappe.db.commit()

    print()
    print(f"✅ Created {created_items} new Items")
    print(f"✅ Created {created_bins} new Bin records")
    print()
    print("Stock is now visible on the e-commerce shop!")
    print("Visit /shop to see medicines marked 'In Stock'.")

    return {
        "items_created": created_items,
        "bins_created": created_bins,
    }


def _get_warehouse():
    """Get any non-group warehouse from the system."""
    wh = frappe.db.get_all("Warehouse",
        filters={"is_group": 0, "disabled": 0},
        limit=1)
    if wh:
        return wh[0].name

    # Try to create one
    company = (
        frappe.db.get_single_value("Global Defaults", "default_company")
        or frappe.db.get_value("Company", {}, "name")
        or "Your Company"
    )
    try:
        doc = frappe.get_doc({
            "doctype": "Warehouse",
            "warehouse_name": "Pharmacy Main Store",
            "company": company,
        })
        doc.insert(ignore_permissions=True)
        return doc.name
    except Exception as e:
        print(f"  ⚠ Could not create warehouse: {e}")
        return None


if __name__ == "__main__":
    fix_stock()
