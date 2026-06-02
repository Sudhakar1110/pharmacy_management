import frappe
from frappe import _
import json


@frappe.whitelist(allow_guest=True)
def search_medicines(query=None, category=None, manufacturer=None, min_price=None, max_price=None, sort_by=None, page=1, limit=12):
    """Public API to search and list medicines with filters."""
    filters = {"is_active": 1}
    
    if query:
        filters["medicine_name"] = ["like", f"%{query}%"]
    if category:
        filters["category"] = category
    if manufacturer:
        filters["manufacturer"] = manufacturer
    
    page = int(page)
    limit = int(limit)
    offset = (page - 1) * limit
    
    # Sorting
    order_by = "medicine_name asc"
    if sort_by == "price_low":
        order_by = "selling_rate asc"
    elif sort_by == "price_high":
        order_by = "selling_rate desc"
    elif sort_by == "name_asc":
        order_by = "medicine_name asc"
    elif sort_by == "name_desc":
        order_by = "medicine_name desc"
    elif sort_by == "newest":
        order_by = "creation desc"
    
    count = frappe.db.count("Medicine Master", filters=filters)
    
    medicines = frappe.get_all(
        "Medicine Master",
        filters=filters,
        fields=["name", "medicine_name", "generic_name", "brand_name", "category",
                "manufacturer", "mrp", "selling_rate", "discount_percent",
                "strength", "dosage_form", "unit_of_measure", "pack_size",
                "requires_prescription", "image", "description", "schedule"],
        order_by=order_by,
        limit=limit,
        offset=offset,
    )
    
    # Get stock availability for each medicine
    for med in medicines:
        stock = frappe.db.get_value("Bin", {"item_code": med.name}, "actual_qty") or 0
        med.available_stock = stock
        med.in_stock = stock > 0
        if med.mrp and med.selling_rate:
            med.discount_percent = round((1 - med.selling_rate / med.mrp) * 100, 1)
        else:
            med.discount_percent = 0
    
    return {
        "medicines": medicines,
        "total": count,
        "page": page,
        "pages": max(1, (count + limit - 1) // limit),
        "limit": limit,
    }


@frappe.whitelist(allow_guest=True)
def get_medicine_details(medicine_name):
    """Get full details for a single medicine."""
    medicine = frappe.get_doc("Medicine Master", medicine_name)
    if not medicine:
        frappe.throw(_("Medicine not found"), frappe.DoesNotExistError)
    
    # Get stock info
    stock = frappe.db.get_value("Bin", {"item_code": medicine.name}, "actual_qty") or 0
    
    # Get batches
    batches = frappe.get_all(
        "Medicine Batch",
        filters={"medicine": medicine.name, "batch_status": ["!=", "Disposed"], "current_qty": [">", 0]},
        fields=["batch_no", "expiry_date", "current_qty", "mrp", "selling_rate", "warehouse"],
        order_by="expiry_date asc",
    )
    
    # Get active batches stock
    total_stock = sum(b.current_qty or 0 for b in batches)
    
    # Get related medicines (same category)
    related = frappe.get_all(
        "Medicine Master",
        filters={"category": medicine.category, "is_active": 1, "name": ["!=", medicine.name]},
        fields=["name", "medicine_name", "mrp", "selling_rate", "strength", "dosage_form",
                "requires_prescription", "image"],
        limit=8,
    )
    
    for r in related:
        r_stock = frappe.db.get_value("Bin", {"item_code": r.name}, "actual_qty") or 0
        r.in_stock = r_stock > 0
        if r.mrp and r.selling_rate:
            r.discount_percent = round((1 - r.selling_rate / r.mrp) * 100, 1)
    
    # Get manufacturer info
    manufacturer_info = None
    if medicine.manufacturer:
        manufacturer_info = frappe.db.get_value(
            "Drug Manufacturer", medicine.manufacturer,
            ["manufacturer_name", "address", "contact", "email", "website"], as_dict=True
        )
    
    return {
        "medicine": medicine,
        "stock": total_stock,
        "in_stock": total_stock > 0,
        "batches": batches,
        "related_medicines": related,
        "manufacturer": manufacturer_info,
    }


@frappe.whitelist(allow_guest=True)
def get_categories():
    """Get all active medicine categories."""
    categories = frappe.get_all(
        "Medicine Category",
        filters={"is_active": 1},
        fields=["name", "category_name", "parent_category", "description"],
        order_by="category_name asc",
    )
    
    # Get medicine count per category
    for cat in categories:
        cat.medicine_count = frappe.db.count("Medicine Master", {"category": cat.name, "is_active": 1})
    
    return categories


@frappe.whitelist(allow_guest=True)
def get_brands():
    """Get distinct brands from medicine master."""
    brands = frappe.db.sql("""
        SELECT DISTINCT brand_name, COUNT(*) as count
        FROM `tabMedicine Master`
        WHERE is_active = 1 AND brand_name IS NOT NULL AND brand_name != ''
        GROUP BY brand_name
        ORDER BY brand_name ASC
    """, as_dict=True)
    return brands


@frappe.whitelist(allow_guest=True)
def get_manufacturers():
    """Get all active manufacturers."""
    manufacturers = frappe.get_all(
        "Drug Manufacturer",
        filters={"is_active": 1},
        fields=["name", "manufacturer_name", "country"],
        order_by="manufacturer_name asc",
    )
    for m in manufacturers:
        m.medicine_count = frappe.db.count("Medicine Master", {"manufacturer": m.name, "is_active": 1})
    return manufacturers


@frappe.whitelist(allow_guest=True)
def get_featured_medicines():
    """Get featured/popular medicines for homepage."""
    medicines = frappe.get_all(
        "Medicine Master",
        filters={"is_active": 1},
        fields=["name", "medicine_name", "generic_name", "mrp", "selling_rate",
                "strength", "dosage_form", "requires_prescription", "image", "category"],
        order_by="modified desc",
        limit=12,
    )
    
    for med in medicines:
        stock = frappe.db.get_value("Bin", {"item_code": med.name}, "actual_qty") or 0
        med.in_stock = stock > 0
        if med.mrp and med.selling_rate:
            med.discount_percent = round((1 - med.selling_rate / med.mrp) * 100, 1)
    
    return medicines


@frappe.whitelist(allow_guest=True)
def autocomplete_medicines(query):
    """Auto-complete search for medicines."""
    if not query or len(query) < 2:
        return []
    return frappe.get_all(
        "Medicine Master",
        filters={
            "medicine_name": ["like", f"%{query}%"],
            "is_active": 1,
        },
        fields=["name", "medicine_name", "generic_name", "strength", "dosage_form", "mrp", "selling_rate"],
        limit=10,
    )


@frappe.whitelist(allow_guest=True)
def get_dosage_forms():
    """Get distinct dosage forms used in active medicines."""
    result = frappe.db.sql("""
        SELECT DISTINCT dosage_form, COUNT(*) as count
        FROM `tabMedicine Master`
        WHERE is_active = 1 AND dosage_form IS NOT NULL AND dosage_form != ''
        GROUP BY dosage_form
        ORDER BY dosage_form ASC
    """, as_dict=True)
    return result


@frappe.whitelist(allow_guest=True)
def get_schedules():
    """Get distinct drug schedules."""
    result = frappe.db.sql("""
        SELECT DISTINCT schedule, COUNT(*) as count
        FROM `tabMedicine Master`
        WHERE is_active = 1 AND schedule IS NOT NULL AND schedule != ''
        GROUP BY schedule
        ORDER BY schedule ASC
    """, as_dict=True)
    return result
