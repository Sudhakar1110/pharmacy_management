"""
Pharmacy Management Demo Data Fixture
======================================
Run via: bench execute pharmacy_management.fixtures.demo_data.create_demo_data

Creates 5-10 demo records per doctype with realistic pharmacy data.
All records are created with ignore_permissions and ignore_mandatory where applicable.
"""

import frappe
from frappe.utils import today, add_days, add_months, now_datetime, getdate, flt
from datetime import datetime, timedelta
import random


# =============================================================================
# Helper functions
# =============================================================================

def _insert(doc_dict, ignore_permissions=True, ignore_mandatory=False):
    """Insert a document and return its name."""
    doc = frappe.get_doc(doc_dict)
    doc.insert(
        ignore_permissions=ignore_permissions,
        ignore_mandatory=ignore_mandatory,
    )
    return doc.name


def _exists(doctype, name):
    """Check if a document exists."""
    return frappe.db.exists(doctype, name)


def _ensure_warehouse():
    """Find or create default warehouses. Always returns a dict with 3 keys."""
    existing_wh = frappe.db.get_all("Warehouse", fields=["name", "warehouse_name"],
                                    filters={"is_group": 0}, limit=5)

    desired_names = ["Pharmacy Main Store", "Pharmacy Warehouse B", "Cold Storage"]
    warehouses = {}

    for desired in desired_names:
        matched = [w for w in existing_wh
                   if desired.lower() in (w.warehouse_name or "").lower()
                   or desired.lower() in w.name.lower()]
        warehouses[desired] = matched[0].name if matched else None

    # If we found at least one warehouse, fill gaps with the first one
    first_available = next((v for v in warehouses.values() if v), None)
    if first_available:
        for k, v in warehouses.items():
            if not v:
                warehouses[k] = first_available
        return warehouses

    # No warehouses exist at all — create one
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
        wh_name = doc.name
        for k in warehouses:
            warehouses[k] = wh_name
        return warehouses
    except Exception as e:
        print(f"  ⚠ Could not create warehouse: {e}")
        return warehouses


def _get_warehouse():
    """Get ANY valid warehouse from the system. Falls back to None."""
    wh = _ensure_warehouse()
    for v in wh.values():
        if v:
            return v
    # Last-resort: try to find ANY warehouse in the system
    try:
        whs = frappe.db.get_all("Warehouse", filters={"is_group": 0}, limit=1)
        if whs:
            return whs[0].name
    except Exception:
        pass
    return None


def _ensure_user():
    """Get or create a demo user."""
    if _exists("User", "admin@pharmacy.com"):
        return "admin@pharmacy.com"
    try:
        doc = frappe.get_doc({
            "doctype": "User",
            "email": "admin@pharmacy.com",
            "first_name": "Pharmacy",
            "last_name": "Admin",
            "send_welcome_email": 0,
            "roles": [{"role": "System Manager"}],
        })
        doc.insert(ignore_permissions=True)
        return doc.name
    except Exception:
        return "Administrator"


# =============================================================================
# Demo data creation
# =============================================================================

def create_medicine_categories():
    """Create 8 Medicine Categories."""
    if _exists("Medicine Category", "Antibiotics"):
        print("Medicine Categories already exist, skipping...")
        return

    categories = [
        {"category_name": "Antibiotics", "description": "Antibacterial medications", "gst_rate": "12", "is_active": 1},
        {"category_name": "Cardiovascular", "description": "Heart & blood pressure medications", "gst_rate": "12", "is_active": 1},
        {"category_name": "Pain Relief", "description": "Analgesics and anti-inflammatory drugs", "gst_rate": "18", "is_active": 1},
        {"category_name": "Respiratory", "description": "Asthma and respiratory medications", "gst_rate": "12", "is_active": 1},
        {"category_name": "Gastrointestinal", "description": "Digestive system medications", "gst_rate": "12", "is_active": 1},
        {"category_name": "Vitamins & Supplements", "description": "Nutritional supplements and vitamins", "gst_rate": "5", "is_active": 1},
        {"category_name": "Diabetes Care", "description": "Anti-diabetic medications", "gst_rate": "12", "is_active": 1},
        {"category_name": "Dermatology", "description": "Skin care medications", "gst_rate": "18", "is_active": 1},
    ]

    for cat in categories:
        _insert({"doctype": "Medicine Category", **cat})
    print(f"✓ Created {len(categories)} Medicine Categories")


def create_drug_manufacturers():
    """Create 6 Drug Manufacturers."""
    if _exists("Drug Manufacturer", "Sun Pharma"):
        print("Drug Manufacturers already exist, skipping...")
        return

    manufacturers = [
        {
            "manufacturer_name": "Sun Pharma", "short_name": "Sun",
            "drug_license": "DL-MH-2023-001", "gst_number": "27AAACS1234A1Z5",
            "address": "Sun House, CTS No. 201 B/1, Western Express Highway, Goregaon East, Mumbai - 400063",
            "contact": "022-67777777", "email": "info@sunpharma.com", "website": "www.sunpharma.com",
            "country": "India", "is_active": 1,
        },
        {
            "manufacturer_name": "Cipla Ltd", "short_name": "Cipla",
            "drug_license": "DL-MH-2023-002", "gst_number": "27AAACC1234A1Z5",
            "address": "Cipla House, Peninsula Business Park, Ganpatrao Kadam Marg, Lower Parel, Mumbai - 400013",
            "contact": "022-62184000", "email": "info@cipla.com", "website": "www.cipla.com",
            "country": "India", "is_active": 1,
        },
        {
            "manufacturer_name": "Dr. Reddy's Labs", "short_name": "DRL",
            "drug_license": "DL-TS-2023-003", "gst_number": "36AABCD1234A1Z5",
            "address": "8-2-337, Road No. 3, Banjara Hills, Hyderabad - 500034",
            "contact": "040-49002900", "email": "info@drreddys.com", "website": "www.drreddys.com",
            "country": "India", "is_active": 1,
        },
        {
            "manufacturer_name": "Abbott India Ltd", "short_name": "Abbott",
            "drug_license": "DL-MH-2023-004", "gst_number": "27AAACA1234A1Z5",
            "address": "Abbott House, Godrej One, 4th Floor, Pirojshanagar, Vikhroli East, Mumbai - 400079",
            "contact": "022-50314100", "email": "info@abbott.com", "website": "www.abbott.co.in",
            "country": "India", "is_active": 1,
        },
        {
            "manufacturer_name": "Mankind Pharma", "short_name": "Mankind",
            "drug_license": "DL-DL-2023-005", "gst_number": "07AAACM1234A1Z5",
            "address": "Plot No. 505, Udyog Vihar, Phase III, Gurugram - 122016",
            "contact": "0124-4116565", "email": "info@mankindpharma.com", "website": "www.mankindpharma.com",
            "country": "India", "is_active": 1,
        },
        {
            "manufacturer_name": "GSK Pharma Ltd", "short_name": "GSK",
            "drug_license": "DL-MH-2023-006", "gst_number": "27AAACG1234A1Z5",
            "address": "GSK House, Dr. Annie Besant Road, Worli, Mumbai - 400030",
            "contact": "022-24959595", "email": "info@gsk.com", "website": "www.gsk-india.com",
            "country": "India", "is_active": 1,
        },
    ]

    for mfr in manufacturers:
        _insert({"doctype": "Drug Manufacturer", **mfr})
    print(f"✓ Created {len(manufacturers)} Drug Manufacturers")


def create_drug_compositions():
    """Create 5 Drug Compositions with child items."""
    try:
        existing = frappe.db.get_all("Drug Composition", limit=1)
        if existing:
            print("Drug Compositions already exist, skipping...")
            return
    except Exception:
        pass

    compositions = [
        {
            "composition_name": "Amoxicillin + Clavulanic Acid",
            "therapeutic_class": "Penicillin Antibiotics",
            "drug_class": "Beta-lactam Antibiotic",
            "mechanism_of_action": "Inhibits bacterial cell wall synthesis",
            "contraindications": "Penicillin allergy, Hepatic impairment",
            "side_effects": "Diarrhea, Nausea, Skin rash",
            "active_ingredients": [
                {"ingredient_name": "Amoxicillin Trihydrate", "strength": "500mg", "unit": "mg"},
                {"ingredient_name": "Clavulanic Acid", "strength": "125mg", "unit": "mg"},
            ],
        },
        {
            "composition_name": "Paracetamol",
            "therapeutic_class": "Analgesic / Antipyretic",
            "drug_class": "NSAID",
            "mechanism_of_action": "COX-2 inhibition in CNS",
            "contraindications": "Severe hepatic impairment",
            "side_effects": "Nausea, Allergic skin reactions",
            "active_ingredients": [
                {"ingredient_name": "Paracetamol IP", "strength": "500mg", "unit": "mg"},
            ],
        },
        {
            "composition_name": "Metformin HCl",
            "therapeutic_class": "Anti-diabetic",
            "drug_class": "Biguanide",
            "mechanism_of_action": "Decreases hepatic glucose production",
            "contraindications": "Renal impairment, Metabolic acidosis",
            "side_effects": "GI upset, Lactic acidosis (rare)",
            "active_ingredients": [
                {"ingredient_name": "Metformin Hydrochloride", "strength": "500mg", "unit": "mg"},
            ],
        },
        {
            "composition_name": "Atorvastatin",
            "therapeutic_class": "Lipid-lowering Agent",
            "drug_class": "Statin",
            "mechanism_of_action": "HMG-CoA reductase inhibition",
            "contraindications": "Active liver disease, Pregnancy",
            "side_effects": "Muscle pain, Elevated liver enzymes",
            "active_ingredients": [
                {"ingredient_name": "Atorvastatin Calcium", "strength": "10mg", "unit": "mg"},
            ],
        },
        {
            "composition_name": "Omeprazole",
            "therapeutic_class": "Proton Pump Inhibitor",
            "drug_class": "PPI",
            "mechanism_of_action": "Inhibits gastric acid secretion",
            "contraindications": "Long-term use without assessment",
            "side_effects": "Headache, abdominal pain, nausea",
            "active_ingredients": [
                {"ingredient_name": "Omeprazole", "strength": "20mg", "unit": "mg"},
            ],
        },
    ]

    for comp in compositions:
        items = comp.pop("active_ingredients")
        doc_dict = {"doctype": "Drug Composition", **comp}
        for item in items:
            doc_dict.setdefault("active_ingredients", []).append(item)
        _insert(doc_dict)

    print(f"✓ Created {len(compositions)} Drug Compositions")


def create_insurance_providers():
    """Create 5 Insurance Providers."""
    if _exists("Insurance Provider", "Star Health Insurance"):
        print("Insurance Providers already exist, skipping...")
        return

    providers = [
        {
            "provider_name": "Star Health Insurance",
            "tpa_name": "Star Health TPA",
            "contact_person": "Rajesh Kumar", "contact_phone": "1800-123-4567",
            "contact_email": "claims@starhealth.in", "coverage_percentage": 80,
            "claim_submission_days": 30, "is_active": 1,
        },
        {
            "provider_name": "New India Assurance",
            "tpa_name": "New India TPA",
            "contact_person": "Suresh Iyer", "contact_phone": "1800-234-5678",
            "contact_email": "support@newindia.co.in", "coverage_percentage": 75,
            "claim_submission_days": 45, "is_active": 1,
        },
        {
            "provider_name": "ICICI Lombard",
            "tpa_name": "ICICI Lombard TPA",
            "contact_person": "Priya Sharma", "contact_phone": "1800-345-6789",
            "contact_email": "claims@icicilombard.com", "coverage_percentage": 85,
            "claim_submission_days": 30, "is_active": 1,
        },
        {
            "provider_name": "Bajaj Allianz",
            "tpa_name": "Bajaj Allianz TPA",
            "contact_person": "Amit Patel", "contact_phone": "1800-456-7890",
            "contact_email": "health@bajajallianz.in", "coverage_percentage": 80,
            "claim_submission_days": 30, "is_active": 1,
        },
        {
            "provider_name": "HDFC ERGO",
            "tpa_name": "HDFC ERGO TPA",
            "contact_person": "Neha Gupta", "contact_phone": "1800-567-8901",
            "contact_email": "support@hdfcergo.com", "coverage_percentage": 70,
            "claim_submission_days": 60, "is_active": 1,
        },
    ]

    for prov in providers:
        _insert({"doctype": "Insurance Provider", **prov})
    print(f"✓ Created {len(providers)} Insurance Providers")


def create_loyalty_programs():
    """Create 3 Loyalty Programs."""
    if _exists("Loyalty Program", "Silver Health Rewards"):
        print("Loyalty Programs already exist, skipping...")
        return

    programs = [
        {"program_name": "Silver Health Rewards", "points_per_rupee": 1, "min_purchase_for_points": 100,
         "redemption_value": 0.10, "min_points_to_redeem": 100, "validity_days": 365, "is_active": 1},
        {"program_name": "Gold Wellness Club", "points_per_rupee": 2, "min_purchase_for_points": 200,
         "redemption_value": 0.15, "min_points_to_redeem": 200, "validity_days": 365, "is_active": 1},
        {"program_name": "Platinum Care Plus", "points_per_rupee": 3, "min_purchase_for_points": 500,
         "redemption_value": 0.20, "min_points_to_redeem": 300, "validity_days": 730, "is_active": 1},
    ]

    for prog in programs:
        _insert({"doctype": "Loyalty Program", **prog})
    print(f"✓ Created {len(programs)} Loyalty Programs")


def create_doctor_masters():
    """Create 6 Doctor Masters."""
    if _exists("Doctor Master", "DR-"):
        # Check by partial name since autoname adds series
        try:
            existing = frappe.db.get_all("Doctor Master", limit=1)
            if existing:
                print("Doctor Masters already exist, skipping...")
                return
        except Exception:
            pass

    doctors = [
        {"doctor_name": "Dr. Rajesh Mehta", "registration_number": "MCI-12345", "specialization": "Cardiologist",
         "qualification": "MD (Cardiology)", "hospital": "Apollo Hospital", "mobile": "9876543210", "email": "rajesh.mehta@apollo.in", "is_active": 1},
        {"doctor_name": "Dr. Sunita Gupta", "registration_number": "MCI-23456", "specialization": "General Physician",
         "qualification": "MD (Internal Medicine)", "hospital": "Fortis Hospital", "mobile": "9876543211", "email": "sunita.gupta@fortis.in", "is_active": 1},
        {"doctor_name": "Dr. Arvind Patel", "registration_number": "MCI-34567", "specialization": "Pediatrician",
         "qualification": "MD (Pediatrics)", "hospital": "Children's Care Clinic", "mobile": "9876543212", "email": "arvind.patel@cccare.in", "is_active": 1},
        {"doctor_name": "Dr. Priya Singh", "registration_number": "MCI-45678", "specialization": "Dermatologist",
         "qualification": "MD (Dermatology)", "hospital": "Skin Care Center", "mobile": "9876543213", "email": "priya.singh@scc.in", "is_active": 1},
        {"doctor_name": "Dr. Venkatesh Iyer", "registration_number": "MCI-56789", "specialization": "Orthopedic",
         "qualification": "MS (Orthopedics)", "hospital": "Bone & Joint Hospital", "mobile": "9876543214", "email": "venkatesh.iyer@bjh.in", "is_active": 1},
        {"doctor_name": "Dr. Ananya Krishnan", "registration_number": "MCI-67890", "specialization": "Endocrinologist",
         "qualification": "DM (Endocrinology)", "hospital": "Diabetic Care Center", "mobile": "9876543215", "email": "ananya.krishnan@dcc.in", "is_active": 1},
    ]

    for doc in doctors:
        _insert({"doctype": "Doctor Master", **doc})
    print(f"✓ Created {len(doctors)} Doctor Masters")


def create_patients():
    """Create 8 Patients."""
    if _exists("Patient", "PAT-"):
        try:
            existing = frappe.db.get_all("Patient", limit=1)
            if existing:
                print("Patients already exist, skipping...")
                return
        except Exception:
            pass

    providers = frappe.db.get_all("Insurance Provider", pluck="name")
    loyalty = frappe.db.get_all("Loyalty Program", pluck="name")

    patients_data = [
        {"patient_name": "Amit Sharma", "mobile_number": "9876500001", "email": "amit.sharma@gmail.com",
         "date_of_birth": "1985-06-15", "gender": "Male", "blood_group": "A+",
         "allergies": "Penicillin", "chronic_conditions": "Hypertension, Diabetes Type 2",
         "address": "42, Green Park Colony", "city": "Delhi", "state": "Delhi", "pincode": "110016",
         "insurance_provider": random.choice(providers) if providers else None,
         "loyalty_program": random.choice(loyalty) if loyalty else None,
         "loyalty_points": 250, "total_purchases": 12500},
        {"patient_name": "Meena Reddy", "mobile_number": "9876500002", "email": "meena.reddy@yahoo.com",
         "date_of_birth": "1990-12-20", "gender": "Female", "blood_group": "B+",
         "allergies": "Sulfa drugs", "chronic_conditions": "Asthma",
         "address": "12, Jubilee Hills", "city": "Hyderabad", "state": "Telangana", "pincode": "500033",
         "insurance_provider": random.choice(providers) if providers else None,
         "loyalty_program": random.choice(loyalty) if loyalty else None,
         "loyalty_points": 120, "total_purchases": 5200},
        {"patient_name": "Rajesh Patil", "mobile_number": "9876500003", "email": "rajesh.patil@hotmail.com",
         "date_of_birth": "1978-03-10", "gender": "Male", "blood_group": "O+",
         "allergies": "None", "chronic_conditions": "Arthritis",
         "address": "55, Koregaon Park", "city": "Pune", "state": "Maharashtra", "pincode": "411001",
         "insurance_provider": random.choice(providers) if providers else None,
         "loyalty_points": 75, "total_purchases": 3400},
        {"patient_name": "Sneha Joshi", "mobile_number": "9876500004", "email": "sneha.joshi@gmail.com",
         "date_of_birth": "1995-08-25", "gender": "Female", "blood_group": "AB+",
         "allergies": "Aspirin", "chronic_conditions": "Migraine",
         "address": "7, Banashankari Stage II", "city": "Bangalore", "state": "Karnataka", "pincode": "560070",
         "insurance_provider": random.choice(providers) if providers else None,
         "loyalty_points": 310, "total_purchases": 15000},
        {"patient_name": "Vikram Singh", "mobile_number": "9876500005", "email": "vikram.singh@outlook.com",
         "date_of_birth": "1965-11-30", "gender": "Male", "blood_group": "B-",
         "allergies": "Codeine", "chronic_conditions": "COPD, Hypertension",
         "address": "88, Civil Lines", "city": "Lucknow", "state": "Uttar Pradesh", "pincode": "226001",
         "insurance_provider": random.choice(providers) if providers else None,
         "loyalty_points": 500, "total_purchases": 25000},
        {"patient_name": "Lakshmi Nair", "mobile_number": "9876500006", "email": "lakshmi.nair@gmail.com",
         "date_of_birth": "2000-01-14", "gender": "Female", "blood_group": "A-",
         "allergies": "None", "chronic_conditions": "",
         "address": "33, Marine Drive", "city": "Kochi", "state": "Kerala", "pincode": "682031",
         "loyalty_points": 45, "total_purchases": 1800},
        {"patient_name": "Dr. Farhan Qureshi", "mobile_number": "9876500007", "email": "farhan.q@yahoo.com",
         "date_of_birth": "1982-07-22", "gender": "Male", "blood_group": "O-",
         "allergies": "Latex", "chronic_conditions": "Diabetes Type 1",
         "address": "9, Park Street", "city": "Kolkata", "state": "West Bengal", "pincode": "700016",
         "insurance_provider": random.choice(providers) if providers else None,
         "loyalty_points": 180, "total_purchases": 8900},
        {"patient_name": "Anita Deshmukh", "mobile_number": "9876500008", "email": "anita.deshmukh@gmail.com",
         "date_of_birth": "1975-09-08", "gender": "Female", "blood_group": "AB-",
         "allergies": "Penicillin", "chronic_conditions": "Hypothyroidism",
         "address": "15, Model Town", "city": "Nagpur", "state": "Maharashtra", "pincode": "440001",
         "insurance_provider": random.choice(providers) if providers else None,
         "loyalty_program": random.choice(loyalty) if loyalty else None,
         "loyalty_points": 90, "total_purchases": 4200},
    ]

    for pt in patients_data:
        _insert({"doctype": "Patient", **pt})
    print(f"✓ Created {len(patients_data)} Patients")


def create_medicine_masters():
    """Create 10 Medicine Masters."""
    if _exists("Medicine Master", "MED-"):
        try:
            existing = frappe.db.get_all("Medicine Master", limit=1)
            if existing:
                print("Medicine Masters already exist, skipping...")
                return
        except Exception:
            pass

    categories = {c["name"]: c["name"] for c in frappe.get_all("Medicine Category", fields=["name"])}
    manufacturers = frappe.db.get_all("Drug Manufacturer", pluck="name")
    compositions = frappe.db.get_all("Drug Composition", pluck="name")

    medicines = [
        {"medicine_name": "Augmentin 625 Duo", "generic_name": "Amoxicillin + Clavulanic Acid",
         "brand_name": "Augmentin", "category": categories.get("Antibiotics", "Antibiotics"),
         "manufacturer": "Sun Pharma" if "Sun Pharma" in manufacturers else (manufacturers[0] if manufacturers else None),
         "composition": compositions[0] if len(compositions) > 0 else None,
         "strength": "625mg", "dosage_form": "Tablet", "unit_of_measure": "Strip", "pack_size": 10,
         "barcode": "8901234567890", "hsn_code": "30041090", "gst_rate": "12",
         "schedule": "H", "requires_prescription": 1,
         "mrp": 245.00, "purchase_rate": 185.00, "selling_rate": 235.00, "discount_percent": 5,
         "reorder_level": 50, "reorder_qty": 100, "min_stock_qty": 20,
         "storage_condition": "Room Temperature", "shelf_life_months": 24, "cold_chain": 0,
         "is_active": 1},
        {"medicine_name": "Paracetamol 500mg", "generic_name": "Paracetamol IP",
         "brand_name": "Calpol", "category": categories.get("Pain Relief", "Pain Relief"),
         "manufacturer": "GSK Pharma Ltd" if "GSK Pharma Ltd" in manufacturers else (manufacturers[1] if len(manufacturers) > 1 else None),
         "composition": compositions[1] if len(compositions) > 1 else None,
         "strength": "500mg", "dosage_form": "Tablet", "unit_of_measure": "Strip", "pack_size": 15,
         "barcode": "8901234567891", "hsn_code": "30049011", "gst_rate": "18",
         "schedule": "OTC", "requires_prescription": 0,
         "mrp": 35.00, "purchase_rate": 22.00, "selling_rate": 32.00, "discount_percent": 10,
         "reorder_level": 200, "reorder_qty": 500, "min_stock_qty": 100,
         "storage_condition": "Room Temperature", "shelf_life_months": 36, "cold_chain": 0,
         "is_active": 1},
        {"medicine_name": "Glycomet 500 SR", "generic_name": "Metformin HCl SR",
         "brand_name": "Glycomet", "category": categories.get("Diabetes Care", "Diabetes Care"),
         "manufacturer": "Sun Pharma" if "Sun Pharma" in manufacturers else (manufacturers[0] if manufacturers else None),
         "composition": compositions[2] if len(compositions) > 2 else None,
         "strength": "500mg", "dosage_form": "Tablet", "unit_of_measure": "Strip", "pack_size": 10,
         "barcode": "8901234567892", "hsn_code": "30049099", "gst_rate": "12",
         "schedule": "H", "requires_prescription": 1,
         "mrp": 98.00, "purchase_rate": 72.00, "selling_rate": 92.00, "discount_percent": 5,
         "reorder_level": 100, "reorder_qty": 200, "min_stock_qty": 30,
         "storage_condition": "Room Temperature", "shelf_life_months": 36, "cold_chain": 0,
         "is_active": 1},
        {"medicine_name": "Atorva 10", "generic_name": "Atorvastatin Calcium",
         "brand_name": "Atorva", "category": categories.get("Cardiovascular", "Cardiovascular"),
         "manufacturer": "Cipla Ltd" if "Cipla Ltd" in manufacturers else (manufacturers[1] if len(manufacturers) > 1 else None),
         "composition": compositions[3] if len(compositions) > 3 else None,
         "strength": "10mg", "dosage_form": "Tablet", "unit_of_measure": "Strip", "pack_size": 15,
         "barcode": "8901234567893", "hsn_code": "30049099", "gst_rate": "12",
         "schedule": "H", "requires_prescription": 1,
         "mrp": 156.00, "purchase_rate": 118.00, "selling_rate": 148.00, "discount_percent": 5,
         "reorder_level": 80, "reorder_qty": 150, "min_stock_qty": 20,
         "storage_condition": "Room Temperature", "shelf_life_months": 24, "cold_chain": 0,
         "is_active": 1},
        {"medicine_name": "Omez 20", "generic_name": "Omeprazole",
         "brand_name": "Omez", "category": categories.get("Gastrointestinal", "Gastrointestinal"),
         "manufacturer": "Dr. Reddy's Labs" if "Dr. Reddy's Labs" in manufacturers else (manufacturers[2] if len(manufacturers) > 2 else None),
         "composition": compositions[4] if len(compositions) > 4 else None,
         "strength": "20mg", "dosage_form": "Capsule", "unit_of_measure": "Strip", "pack_size": 10,
         "barcode": "8901234567894", "hsn_code": "30049099", "gst_rate": "12",
         "schedule": "H", "requires_prescription": 1,
         "mrp": 112.00, "purchase_rate": 82.00, "selling_rate": 105.00, "discount_percent": 5,
         "reorder_level": 100, "reorder_qty": 200, "min_stock_qty": 30,
         "storage_condition": "Room Temperature", "shelf_life_months": 24, "cold_chain": 0,
         "is_active": 1},
        {"medicine_name": "Azithral 500", "generic_name": "Azithromycin",
         "brand_name": "Azithral", "category": categories.get("Antibiotics", "Antibiotics"),
         "manufacturer": "Mankind Pharma" if "Mankind Pharma" in manufacturers else (manufacturers[4] if len(manufacturers) > 4 else None),
         "strength": "500mg", "dosage_form": "Tablet", "unit_of_measure": "Strip", "pack_size": 3,
         "barcode": "8901234567895", "hsn_code": "30041090", "gst_rate": "12",
         "schedule": "H", "requires_prescription": 1,
         "mrp": 189.00, "purchase_rate": 142.00, "selling_rate": 180.00, "discount_percent": 3,
         "reorder_level": 60, "reorder_qty": 120, "min_stock_qty": 15,
         "storage_condition": "Room Temperature", "shelf_life_months": 24, "cold_chain": 0,
         "is_active": 1},
        {"medicine_name": "Eltroxin 50mcg", "generic_name": "Thyroxine Sodium",
         "brand_name": "Eltroxin", "category": categories.get("Vitamins & Supplements", "Vitamins & Supplements"),
         "manufacturer": "Abbott India Ltd" if "Abbott India Ltd" in manufacturers else (manufacturers[3] if len(manufacturers) > 3 else None),
         "strength": "50mcg", "dosage_form": "Tablet", "unit_of_measure": "Strip", "pack_size": 10,
         "barcode": "8901234567896", "hsn_code": "30049099", "gst_rate": "5",
         "schedule": "H", "requires_prescription": 1,
         "mrp": 65.00, "purchase_rate": 45.00, "selling_rate": 60.00, "discount_percent": 5,
         "reorder_level": 100, "reorder_qty": 200, "min_stock_qty": 30,
         "storage_condition": "Room Temperature", "shelf_life_months": 36, "cold_chain": 0,
         "is_active": 1},
        {"medicine_name": "Levocetrizine 5mg", "generic_name": "Levocetrizine",
         "brand_name": "Levocet", "category": categories.get("Respiratory", "Respiratory"),
         "manufacturer": "Mankind Pharma" if "Mankind Pharma" in manufacturers else (manufacturers[4] if len(manufacturers) > 4 else None),
         "strength": "5mg", "dosage_form": "Tablet", "unit_of_measure": "Strip", "pack_size": 10,
         "barcode": "8901234567897", "hsn_code": "30049099", "gst_rate": "12",
         "schedule": "H", "requires_prescription": 0,
         "mrp": 42.00, "purchase_rate": 28.00, "selling_rate": 39.00, "discount_percent": 10,
         "reorder_level": 150, "reorder_qty": 300, "min_stock_qty": 50,
         "storage_condition": "Room Temperature", "shelf_life_months": 24, "cold_chain": 0,
         "is_active": 1},
        {"medicine_name": "Betnovate C Cream", "generic_name": "Betamethasone + Clotrimazole",
         "brand_name": "Betnovate", "category": categories.get("Dermatology", "Dermatology"),
         "manufacturer": "GSK Pharma Ltd" if "GSK Pharma Ltd" in manufacturers else (manufacturers[5] if len(manufacturers) > 5 else None),
         "strength": "0.05% + 1%", "dosage_form": "Cream", "unit_of_measure": "Tube", "pack_size": 1,
         "barcode": "8901234567898", "hsn_code": "30049099", "gst_rate": "18",
         "schedule": "H", "requires_prescription": 1,
         "mrp": 78.00, "purchase_rate": 55.00, "selling_rate": 73.00, "discount_percent": 5,
         "reorder_level": 40, "reorder_qty": 80, "min_stock_qty": 10,
         "storage_condition": "Room Temperature", "shelf_life_months": 24, "cold_chain": 0,
         "is_active": 1},
        {"medicine_name": "Shelcal 500", "generic_name": "Calcium Carbonate + Vitamin D3",
         "brand_name": "Shelcal", "category": categories.get("Vitamins & Supplements", "Vitamins & Supplements"),
         "manufacturer": "Mankind Pharma" if "Mankind Pharma" in manufacturers else (manufacturers[4] if len(manufacturers) > 4 else None),
         "strength": "500mg + 400IU", "dosage_form": "Tablet", "unit_of_measure": "Strip", "pack_size": 15,
         "barcode": "8901234567899", "hsn_code": "21069099", "gst_rate": "5",
         "schedule": "OTC", "requires_prescription": 0,
         "mrp": 195.00, "purchase_rate": 148.00, "selling_rate": 185.00, "discount_percent": 8,
         "reorder_level": 80, "reorder_qty": 160, "min_stock_qty": 20,
         "storage_condition": "Room Temperature", "shelf_life_months": 24, "cold_chain": 0,
         "is_active": 1},
    ]

    for med in medicines:
        _insert({"doctype": "Medicine Master", **med})
    print(f"✓ Created {len(medicines)} Medicine Masters")


def create_pharmacists():
    """Create 5 Pharmacists."""
    if _exists("Pharmacist", "PH-"):
        try:
            existing = frappe.db.get_all("Pharmacist", limit=1)
            if existing:
                print("Pharmacists already exist, skipping...")
                return
        except Exception:
            pass

    pharmacists = [
        {"pharmacist_name": "Sandeep Verma", "registration_number": "PHAR-2023-001",
         "qualification": "B.Pharm", "specialization": "Clinical Pharmacy",
         "experience_years": 8, "license_expiry": add_months(today(), 18), "is_active": 1},
        {"pharmacist_name": "Pooja Desai", "registration_number": "PHAR-2023-002",
         "qualification": "M.Pharm", "specialization": "Hospital Pharmacy",
         "experience_years": 5, "license_expiry": add_months(today(), 24), "is_active": 1},
        {"pharmacist_name": "Mohammed Ali", "registration_number": "PHAR-2023-003",
         "qualification": "Pharm.D", "specialization": "Community Pharmacy",
         "experience_years": 12, "license_expiry": add_months(today(), 6), "is_active": 1},
        {"pharmacist_name": "Kavita Sharma", "registration_number": "PHAR-2023-004",
         "qualification": "B.Pharm", "specialization": "Retail Pharmacy",
         "experience_years": 3, "license_expiry": add_months(today(), 30), "is_active": 1},
        {"pharmacist_name": "Ravi Kumar", "registration_number": "PHAR-2023-005",
         "qualification": "M.Pharm", "specialization": "Pharmaceutical Analysis",
         "experience_years": 7, "license_expiry": add_months(today(), 15), "is_active": 1},
    ]

    for ph in pharmacists:
        _insert({"doctype": "Pharmacist", **ph})
    print(f"✓ Created {len(pharmacists)} Pharmacists")


def create_medicine_batches():
    """Create 8 Medicine Batches."""
    if _exists("Medicine Batch", "BATCH-"):
        try:
            existing = frappe.db.get_all("Medicine Batch", limit=1)
            if existing:
                print("Medicine Batches already exist, skipping...")
                return
        except Exception:
            pass

    warehouses = _ensure_warehouse()
    wh_list = [v for v in warehouses.values() if v] or [_get_warehouse()]
    wh_list = [w for w in wh_list if w]
    medicines = frappe.db.get_all("Medicine Master", fields=["name", "mrp", "purchase_rate", "selling_rate"])

    if not medicines:
        print("  ⚠ No Medicine Masters found, skipping batches...")
        return

    # Map medicine data
    med_map = {m.name: m for m in medicines}
    med_names = [m.name for m in medicines]
    manufacturers = frappe.db.get_all("Drug Manufacturer", pluck="name")

    batches_data = [
        {"batch_no": "B2024001", "medicine": med_names[0] if len(med_names) > 0 else med_names[0],
         "manufacturer": manufacturers[0] if manufacturers else None,
         "manufacturing_date": add_months(today(), -14), "expiry_date": add_months(today(), 10),
         "warehouse": wh_list[0] if wh_list else None, "received_qty": 500, "current_qty": 423,
         "purchase_rate": med_map[med_names[0]].purchase_rate if len(med_names) > 0 else 185.00,
         "mrp": med_map[med_names[0]].mrp if len(med_names) > 0 else 245.00,
         "selling_rate": med_map[med_names[0]].selling_rate if len(med_names) > 0 else 235.00,
         "batch_status": "Active", "days_to_expiry": None,
         "near_expiry_threshold": 90, "notes": "Initial procurement batch"},
        {"batch_no": "B2024002", "medicine": med_names[1] if len(med_names) > 1 else med_names[0],
         "manufacturer": manufacturers[1] if len(manufacturers) > 1 else None,
         "manufacturing_date": add_months(today(), -6), "expiry_date": add_months(today(), 30),
         "warehouse": wh_list[0] if wh_list else None, "received_qty": 1000, "current_qty": 845,
         "purchase_rate": med_map[med_names[1]].purchase_rate if len(med_names) > 1 else 22.00,
         "mrp": med_map[med_names[1]].mrp if len(med_names) > 1 else 35.00,
         "selling_rate": med_map[med_names[1]].selling_rate if len(med_names) > 1 else 32.00,
         "batch_status": "Active", "days_to_expiry": None,
         "near_expiry_threshold": 90, "notes": ""},
        {"batch_no": "B2024003", "medicine": med_names[2] if len(med_names) > 2 else med_names[0],
         "manufacturer": manufacturers[0] if manufacturers else None,
         "manufacturing_date": add_months(today(), -8), "expiry_date": add_months(today(), 28),
         "warehouse": wh_list[1] if len(wh_list) > 1 else (wh_list[0] if wh_list else None),
         "received_qty": 300, "current_qty": 256,
         "purchase_rate": med_map[med_names[2]].purchase_rate if len(med_names) > 2 else 72.00,
         "mrp": med_map[med_names[2]].mrp if len(med_names) > 2 else 98.00,
         "selling_rate": med_map[med_names[2]].selling_rate if len(med_names) > 2 else 92.00,
         "batch_status": "Active", "days_to_expiry": None,
         "near_expiry_threshold": 90, "notes": ""},
        {"batch_no": "B2024004", "medicine": med_names[4] if len(med_names) > 4 else med_names[0],
         "manufacturer": manufacturers[2] if len(manufacturers) > 2 else None,
         "manufacturing_date": add_months(today(), -10), "expiry_date": add_months(today(), 14),
         "warehouse": wh_list[0] if wh_list else None, "received_qty": 400, "current_qty": 312,
         "purchase_rate": med_map[med_names[4]].purchase_rate if len(med_names) > 4 else 82.00,
         "mrp": med_map[med_names[4]].mrp if len(med_names) > 4 else 112.00,
         "selling_rate": med_map[med_names[4]].selling_rate if len(med_names) > 4 else 105.00,
         "batch_status": "Active", "days_to_expiry": None,
         "near_expiry_threshold": 90, "notes": ""},
        {"batch_no": "B2024005", "medicine": med_names[5] if len(med_names) > 5 else med_names[0],
         "manufacturer": manufacturers[4] if len(manufacturers) > 4 else None,
         "manufacturing_date": add_months(today(), -4), "expiry_date": add_months(today(), 20),
         "warehouse": wh_list[1] if len(wh_list) > 1 else (wh_list[0] if wh_list else None),
         "received_qty": 200, "current_qty": 167,
         "purchase_rate": med_map[med_names[5]].purchase_rate if len(med_names) > 5 else 142.00,
         "mrp": med_map[med_names[5]].mrp if len(med_names) > 5 else 189.00,
         "selling_rate": med_map[med_names[5]].selling_rate if len(med_names) > 5 else 180.00,
         "batch_status": "Active", "days_to_expiry": None,
         "near_expiry_threshold": 90, "notes": ""},
        {"batch_no": "B2024006", "medicine": med_names[3] if len(med_names) > 3 else med_names[0],
         "manufacturer": manufacturers[1] if len(manufacturers) > 1 else None,
         "manufacturing_date": add_months(today(), -12), "expiry_date": add_months(today(), 12),
         "warehouse": wh_list[0] if wh_list else None, "received_qty": 350, "current_qty": 289,
         "purchase_rate": med_map[med_names[3]].purchase_rate if len(med_names) > 3 else 118.00,
         "mrp": med_map[med_names[3]].mrp if len(med_names) > 3 else 156.00,
         "selling_rate": med_map[med_names[3]].selling_rate if len(med_names) > 3 else 148.00,
         "batch_status": "Active", "days_to_expiry": None,
         "near_expiry_threshold": 90, "notes": ""},
        {"batch_no": "B2024007", "medicine": med_names[6] if len(med_names) > 6 else med_names[0],
         "manufacturer": manufacturers[3] if len(manufacturers) > 3 else None,
         "manufacturing_date": add_months(today(), -3), "expiry_date": add_months(today(), 33),
         "warehouse": wh_list[0] if wh_list else None,
         "received_qty": 250, "current_qty": 218,
         "purchase_rate": med_map[med_names[6]].purchase_rate if len(med_names) > 6 else 45.00,
         "mrp": med_map[med_names[6]].mrp if len(med_names) > 6 else 65.00,
         "selling_rate": med_map[med_names[6]].selling_rate if len(med_names) > 6 else 60.00,
         "batch_status": "Active", "days_to_expiry": None,
         "near_expiry_threshold": 90, "notes": ""},
        {"batch_no": "B2024008", "medicine": med_names[9] if len(med_names) > 9 else med_names[0],
         "manufacturer": manufacturers[4] if len(manufacturers) > 4 else None,
         "manufacturing_date": add_months(today(), -2), "expiry_date": add_months(today(), 22),
         "warehouse": wh_list[2] if len(wh_list) > 2 else (wh_list[0] if wh_list else None),
         "received_qty": 180, "current_qty": 153,
         "purchase_rate": med_map[med_names[9]].purchase_rate if len(med_names) > 9 else 148.00,
         "mrp": med_map[med_names[9]].mrp if len(med_names) > 9 else 195.00,
         "selling_rate": med_map[med_names[9]].selling_rate if len(med_names) > 9 else 185.00,
         "batch_status": "Active", "days_to_expiry": None,
         "near_expiry_threshold": 90, "notes": "Cold chain maintained"},
    ]

    for batch in batches_data:
        b = frappe.get_doc({"doctype": "Medicine Batch", **batch})
        b.insert(ignore_permissions=True)
        # Manually update current_qty since it's read_only
        frappe.db.set_value("Medicine Batch", b.name, "current_qty", batch["current_qty"])

    print(f"✓ Created {len(batches_data)} Medicine Batches")


def create_prescriptions():
    """Create 6 Prescriptions with child items."""
    try:
        existing = frappe.db.get_all("Prescription", limit=1)
        if existing:
            print("Prescriptions already exist, skipping...")
            return
    except Exception:
        pass

    patients = frappe.db.get_all("Patient", pluck="name")
    doctors = frappe.db.get_all("Doctor Master", pluck="name")
    medicines = frappe.db.get_all("Medicine Master", pluck="name")

    if not patients or not doctors or not medicines:
        print("  ⚠ Missing dependencies (Patients/Doctors/Medicines), skipping prescriptions...")
        return

    prescriptions_data = [
        {"patient": patients[0] if len(patients) > 0 else patients[0],
         "doctor": doctors[0], "prescription_date": add_days(today(), -5), "valid_till": add_days(today(), 25),
         "status": "Completed", "notes": "Patient responded well to treatment.",
         "medicines": [
             {"medicine": medicines[0], "dosage": "1-0-1", "frequency": "Twice Daily", "duration": "5 Days", "qty": 10, "instructions": "After meals"},
             {"medicine": medicines[4], "dosage": "0-1-0", "frequency": "Once Daily", "duration": "5 Days", "qty": 5, "instructions": "Before breakfast"},
         ]},
        {"patient": patients[1] if len(patients) > 1 else patients[0],
         "doctor": doctors[1], "prescription_date": add_days(today(), -3), "valid_till": add_days(today(), 27),
         "status": "Dispensing",
         "medicines": [
             {"medicine": medicines[1], "dosage": "1-1-1", "frequency": "Thrice Daily", "duration": "3 Days", "qty": 9, "instructions": "With water"},
             {"medicine": medicines[7], "dosage": "0-0-1", "frequency": "Once Daily", "duration": "7 Days", "qty": 7, "instructions": "At bedtime"},
         ]},
        {"patient": patients[2] if len(patients) > 2 else patients[0],
         "doctor": doctors[2], "prescription_date": add_days(today(), -7), "valid_till": add_days(today(), 23),
         "status": "Completed",
         "medicines": [
             {"medicine": medicines[2], "dosage": "1-0-1", "frequency": "Twice Daily", "duration": "30 Days", "qty": 60, "instructions": "After meals"},
         ]},
        {"patient": patients[3] if len(patients) > 3 else patients[0],
         "doctor": doctors[0], "prescription_date": add_days(today(), -1), "valid_till": add_days(today(), 29),
         "status": "Verification",
         "medicines": [
             {"medicine": medicines[3], "dosage": "0-0-1", "frequency": "Once Daily", "duration": "30 Days", "qty": 30, "instructions": "At bedtime"},
             {"medicine": medicines[1], "dosage": "SOS", "frequency": "SOS", "duration": "3 Days", "qty": 6, "instructions": "When headache occurs"},
         ]},
        {"patient": patients[4] if len(patients) > 4 else patients[0],
         "doctor": doctors[3], "prescription_date": today(), "valid_till": add_days(today(), 30),
         "status": "Uploaded", "notes": "New patient, needs allergy screening.",
         "medicines": [
             {"medicine": medicines[8], "dosage": "Apply twice daily", "frequency": "Twice Daily", "duration": "14 Days", "qty": 2, "instructions": "Apply on affected area"},
         ]},
        {"patient": patients[5] if len(patients) > 5 else patients[0],
         "doctor": doctors[4], "prescription_date": add_days(today(), -2), "valid_till": add_days(today(), 28),
         "status": "Completed",
         "medicines": [
             {"medicine": medicines[6], "dosage": "1-0-0", "frequency": "Once Daily", "duration": "30 Days", "qty": 30, "instructions": "Empty stomach"},
             {"medicine": medicines[9], "dosage": "0-0-1", "frequency": "Once Daily", "duration": "60 Days", "qty": 60, "instructions": "After dinner"},
         ]},
    ]

    for rx in prescriptions_data:
        items = rx.pop("medicines")
        rx_doc = frappe.get_doc({"doctype": "Prescription", **rx})
        for item in items:
            rx_doc.append("medicines", item)
        rx_doc.insert(ignore_permissions=True)

    print(f"✓ Created {len(prescriptions_data)} Prescriptions")


def create_purchase_requests():
    """Create 5 Purchase Requests with items."""
    try:
        existing = frappe.db.get_all("Purchase Request", limit=1)
        if existing:
            print("Purchase Requests already exist, skipping...")
            return
    except Exception:
        pass

    user = _ensure_user()
    warehouses = _ensure_warehouse()
    wh_list = [v for v in warehouses.values() if v] or [_get_warehouse()]
    wh_list = [w for w in wh_list if w]
    medicines = frappe.db.get_all("Medicine Master", fields=["name", "medicine_name", "purchase_rate"])

    if not medicines:
        print("  ⚠ No Medicine Masters found, skipping purchase requests...")
        return

    pr_data = [
        {"title": "Monthly Antibiotics Restock", "request_date": add_days(today(), -5), "required_by": add_days(today(), 10),
         "requested_by": user, "warehouse": wh_list[0] if wh_list else None, "priority": "High",
         "status": "Approved", "notes": "Monthly replenishment order",
         "items": [
             {"medicine": medicines[0].name, "qty": 100, "last_purchase_rate": medicines[0].purchase_rate if len(medicines) > 0 else 180.00},
             {"medicine": medicines[5].name if len(medicines) > 5 else medicines[0].name, "qty": 50, "last_purchase_rate": medicines[5].purchase_rate if len(medicines) > 5 else 140.00},
         ]},
        {"title": "Diabetes Care Stock", "request_date": add_days(today(), -3), "required_by": add_days(today(), 7),
         "requested_by": user, "warehouse": wh_list[0] if wh_list else None, "priority": "Medium",
         "status": "Pending Approval",
         "items": [
             {"medicine": medicines[2].name if len(medicines) > 2 else medicines[0].name, "qty": 200, "last_purchase_rate": medicines[2].purchase_rate if len(medicines) > 2 else 70.00},
         ]},
        {"title": "Pain Relief Medicines", "request_date": add_days(today(), -2), "required_by": add_days(today(), 14),
         "requested_by": user, "warehouse": wh_list[1] if len(wh_list) > 1 else (wh_list[0] if wh_list else None),
         "priority": "Low", "status": "Draft",
         "items": [
             {"medicine": medicines[1].name if len(medicines) > 1 else medicines[0].name, "qty": 500, "last_purchase_rate": medicines[1].purchase_rate if len(medicines) > 1 else 22.00},
             {"medicine": medicines[7].name if len(medicines) > 7 else medicines[0].name, "qty": 300, "last_purchase_rate": medicines[7].purchase_rate if len(medicines) > 7 else 28.00},
         ]},
        {"title": "Cardiovascular Meds Order", "request_date": today(), "required_by": add_days(today(), 7),
         "requested_by": user, "warehouse": wh_list[0] if wh_list else None, "priority": "Urgent",
         "status": "Approved",
         "items": [
             {"medicine": medicines[3].name if len(medicines) > 3 else medicines[0].name, "qty": 150, "last_purchase_rate": medicines[3].purchase_rate if len(medicines) > 3 else 118.00},
         ]},
        {"title": "Vitamin & Supplement Order", "request_date": add_days(today(), -1), "required_by": add_days(today(), 21),
         "requested_by": user, "warehouse": wh_list[0] if wh_list else None, "priority": "Low",
         "status": "PO Created",
         "items": [
             {"medicine": medicines[9].name if len(medicines) > 9 else medicines[0].name, "qty": 100, "last_purchase_rate": medicines[9].purchase_rate if len(medicines) > 9 else 148.00},
             {"medicine": medicines[6].name if len(medicines) > 6 else medicines[0].name, "qty": 200, "last_purchase_rate": medicines[6].purchase_rate if len(medicines) > 6 else 45.00},
         ]},
    ]

    for pr in pr_data:
        items = pr.pop("items")
        pr_doc = frappe.get_doc({"doctype": "Purchase Request", **pr})
        for item in items:
            pr_doc.append("items", item)
        pr_doc.insert(ignore_permissions=True)

    print(f"✓ Created {len(pr_data)} Purchase Requests")


def create_shift_assignments():
    """Create 6 Shift Assignments."""
    try:
        existing = frappe.db.get_all("Shift Assignment", limit=1)
        if existing:
            print("Shift Assignments already exist, skipping...")
            return
    except Exception:
        pass

    pharmacists = frappe.db.get_all("Pharmacist", pluck="name")
    warehouses = _ensure_warehouse()
    wh_list = [v for v in warehouses.values() if v] or [_get_warehouse()]
    wh_list = [w for w in wh_list if w]

    if not pharmacists:
        print("  ⚠ No Pharmacists found, skipping shift assignments...")
        return

    shifts_data = [
        {"pharmacist": pharmacists[0], "shift_date": today(), "shift_type": "Morning",
         "start_time": "06:00:00", "end_time": "14:00:00", "warehouse": wh_list[0] if wh_list else None, "notes": ""},
        {"pharmacist": pharmacists[1], "shift_date": today(), "shift_type": "Afternoon",
         "start_time": "14:00:00", "end_time": "22:00:00", "warehouse": wh_list[0] if wh_list else None, "notes": "Covering for leave"},
        {"pharmacist": pharmacists[2], "shift_date": add_days(today(), 1), "shift_type": "Morning",
         "start_time": "06:00:00", "end_time": "14:00:00", "warehouse": wh_list[1] if len(wh_list) > 1 else (wh_list[0] if wh_list else None), "notes": ""},
        {"pharmacist": pharmacists[3], "shift_date": add_days(today(), 1), "shift_type": "Afternoon",
         "start_time": "14:00:00", "end_time": "22:00:00", "warehouse": wh_list[0] if wh_list else None, "notes": ""},
        {"pharmacist": pharmacists[4], "shift_date": add_days(today(), -1), "shift_type": "Night",
         "start_time": "22:00:00", "end_time": "06:00:00", "warehouse": wh_list[0] if wh_list else None, "notes": "Night shift"},
        {"pharmacist": pharmacists[0], "shift_date": add_days(today(), 2), "shift_type": "Evening",
         "start_time": "16:00:00", "end_time": "24:00:00", "warehouse": wh_list[0] if wh_list else None, "notes": ""},
    ]

    for shift in shifts_data:
        _insert({"doctype": "Shift Assignment", **shift})
    print(f"✓ Created {len(shifts_data)} Shift Assignments")


def create_stock_adjustments():
    """Create 4 Stock Adjustments with items."""
    try:
        existing = frappe.db.get_all("Stock Adjustment", limit=1)
        if existing:
            print("Stock Adjustments already exist, skipping...")
            return
    except Exception:
        pass

    user = _ensure_user()
    warehouses = _ensure_warehouse()
    wh_list = [v for v in warehouses.values() if v] or [_get_warehouse()]
    wh_list = [w for w in wh_list if w]
    medicines = frappe.db.get_all("Medicine Master", fields=["name", "purchase_rate"])

    if not medicines:
        print("  ⚠ No Medicine Masters found, skipping stock adjustments...")
        return

    adjustments = [
        {"posting_date": add_days(today(), -10), "adjustment_type": "Damage",
         "warehouse": wh_list[0] if wh_list else None, "reason": "Syrup bottles damaged during shelf collapse",
         "approved_by": user,
         "items": [
             {"medicine": medicines[0].name, "qty": -5, "rate": medicines[0].purchase_rate},
             {"medicine": medicines[5].name if len(medicines) > 5 else medicines[0].name, "qty": -3, "rate": medicines[5].purchase_rate if len(medicines) > 5 else medicines[0].purchase_rate},
         ]},
        {"posting_date": add_days(today(), -7), "adjustment_type": "Expiry Disposal",
         "warehouse": wh_list[0] if wh_list else None, "reason": "Batch nearing expiry - returned to supplier",
         "approved_by": user,
         "items": [
             {"medicine": medicines[4].name if len(medicines) > 4 else medicines[0].name, "qty": -25, "rate": medicines[4].purchase_rate if len(medicines) > 4 else medicines[0].purchase_rate},
         ]},
        {"posting_date": add_days(today(), -3), "adjustment_type": "Count Adjustment",
         "warehouse": wh_list[1] if len(wh_list) > 1 else (wh_list[0] if wh_list else None),
         "reason": "Physical inventory count variance",
         "approved_by": user,
         "items": [
             {"medicine": medicines[2].name if len(medicines) > 2 else medicines[0].name, "qty": 2, "rate": medicines[2].purchase_rate if len(medicines) > 2 else medicines[0].purchase_rate},
             {"medicine": medicines[7].name if len(medicines) > 7 else medicines[0].name, "qty": -1, "rate": medicines[7].purchase_rate if len(medicines) > 7 else medicines[0].purchase_rate},
         ]},
        {"posting_date": add_days(today(), -1), "adjustment_type": "Write Off",
         "warehouse": wh_list[0] if wh_list else None, "reason": "Expired stock written off",
         "approved_by": user,
         "items": [
             {"medicine": medicines[1].name if len(medicines) > 1 else medicines[0].name, "qty": -15, "rate": medicines[1].purchase_rate if len(medicines) > 1 else medicines[0].purchase_rate},
         ]},
    ]

    for adj in adjustments:
        items = adj.pop("items")
        adj_doc = frappe.get_doc({"doctype": "Stock Adjustment", **adj})
        for item in items:
            adj_doc.append("items", item)
        adj_doc.insert(ignore_permissions=True)

    print(f"✓ Created {len(adjustments)} Stock Adjustments")


def create_stock_transfers():
    """Create 3 Stock Transfers with items."""
    try:
        existing = frappe.db.get_all("Stock Transfer", limit=1)
        if existing:
            print("Stock Transfers already exist, skipping...")
            return
    except Exception:
        pass

    user = _ensure_user()
    warehouses = _ensure_warehouse()
    wh_list = [v for v in warehouses.values() if v] or [_get_warehouse()]
    wh_list = [w for w in wh_list if w]
    medicines = frappe.db.get_all("Medicine Master", fields=["name", "medicine_name"])

    if not medicines or len(wh_list) < 2:
        print("  ⚠ Not enough warehouses/medicines, skipping stock transfers...")
        return

    transfers = [
        {"posting_date": add_days(today(), -4), "from_warehouse": wh_list[0], "to_warehouse": wh_list[1],
         "reason": "Replenish branch store stock", "requested_by": user,
         "items": [
             {"medicine": medicines[1].name, "qty": 50, "uom": "Strip"},
             {"medicine": medicines[7].name if len(medicines) > 7 else medicines[1].name, "qty": 30, "uom": "Strip"},
         ]},
        {"posting_date": add_days(today(), -2), "from_warehouse": wh_list[0],
         "to_warehouse": wh_list[2] if len(wh_list) > 2 else wh_list[1],
         "reason": "Transfer to cold storage", "requested_by": user,
         "items": [
             {"medicine": medicines[9].name if len(medicines) > 9 else medicines[0].name, "qty": 20, "uom": "Bottle"},
         ]},
        {"posting_date": today(), "from_warehouse": wh_list[1], "to_warehouse": wh_list[0],
         "reason": "Return excess stock to main store", "requested_by": user,
         "items": [
             {"medicine": medicines[5].name if len(medicines) > 5 else medicines[1].name, "qty": 10, "uom": "Strip"},
         ]},
    ]

    for tr in transfers:
        items = tr.pop("items")
        tr_doc = frappe.get_doc({"doctype": "Stock Transfer", **tr})
        for item in items:
            tr_doc.append("items", item)
        tr_doc.insert(ignore_permissions=True)

    print(f"✓ Created {len(transfers)} Stock Transfers")


def create_insurance_claims():
    """Create 5 Insurance Claims."""
    try:
        existing = frappe.db.get_all("Insurance Claim", limit=1)
        if existing:
            print("Insurance Claims already exist, skipping...")
            return
    except Exception:
        pass

    patients = frappe.db.get_all("Patient", fields=["name", "patient_name"])
    providers = frappe.db.get_all("Insurance Provider", pluck="name")

    if not patients or not providers:
        print("  ⚠ Missing dependencies (Patients/Providers), skipping insurance claims...")
        return

    claims = [
        {"patient": patients[0].name, "patient_name": patients[0].patient_name,
         "insurance_provider": providers[0],
         "policy_number": "POL-NIA-2024-001", "claim_date": add_days(today(), -15),
         "status": "Settled", "invoice_amount": 12500, "claimed_amount": 10000,
         "approved_amount": 9500, "settled_amount": 9500,
         "deductible": 500, "patient_liability": 3000,
         "settlement_date": add_days(today(), -5), "notes": "Claim settled in full"},
        {"patient": patients[1].name if len(patients) > 1 else patients[0].name,
         "patient_name": patients[1].patient_name if len(patients) > 1 else patients[0].patient_name,
         "insurance_provider": providers[1] if len(providers) > 1 else providers[0],
         "policy_number": "POL-ICICI-2024-002", "claim_date": add_days(today(), -7),
         "status": "Approved", "invoice_amount": 5200, "claimed_amount": 4160,
         "approved_amount": 4000, "deductible": 200, "patient_liability": 1200,
         "notes": "Awaiting settlement"},
        {"patient": patients[2].name if len(patients) > 2 else patients[0].name,
         "patient_name": patients[2].patient_name if len(patients) > 2 else patients[0].patient_name,
         "insurance_provider": providers[2] if len(providers) > 2 else providers[0],
         "policy_number": "POL-BA-2024-003", "claim_date": add_days(today(), -3),
         "status": "Under Review", "invoice_amount": 3400, "claimed_amount": 2700,
         "deductible": 0, "patient_liability": 700, "notes": "Documents verification pending"},
        {"patient": patients[3].name if len(patients) > 3 else patients[0].name,
         "patient_name": patients[3].patient_name if len(patients) > 3 else patients[0].patient_name,
         "insurance_provider": providers[3] if len(providers) > 3 else providers[0],
         "policy_number": "POL-HDFC-2024-004", "claim_date": add_days(today(), -1),
         "status": "Submitted", "invoice_amount": 15000, "claimed_amount": 12000,
         "deductible": 500, "patient_liability": 3500, "notes": "New claim - yet to be processed"},
        {"patient": patients[4].name if len(patients) > 4 else patients[0].name,
         "patient_name": patients[4].patient_name if len(patients) > 4 else patients[0].patient_name,
         "insurance_provider": providers[0],
         "policy_number": "POL-NIA-2024-005", "claim_date": add_days(today(), -30),
         "status": "Rejected", "invoice_amount": 25000, "claimed_amount": 20000,
         "deductible": 1000, "patient_liability": 6000,
         "rejection_reason": "Policy expired at time of treatment",
         "notes": "Patient informed to resubmit after policy renewal"},
    ]

    for claim in claims:
        _insert({"doctype": "Insurance Claim", **claim})
    print(f"✓ Created {len(claims)} Insurance Claims")


def create_pos_invoices():
    """Create 5 POS Invoice Ext records with items."""
    try:
        existing = frappe.db.get_all("POS Invoice Ext", limit=1)
        if existing:
            print("POS Invoice Ext already exist, skipping...")
            return
    except Exception:
        pass

    patients = frappe.db.get_all("Patient", fields=["name", "patient_name"])
    medicines = frappe.db.get_all("Medicine Master", fields=["name", "medicine_name", "mrp", "selling_rate", "requires_prescription", "gst_rate"])
    user = _ensure_user()

    if not patients or not medicines:
        print("  ⚠ Missing dependencies (Patients/Medicines), skipping POS invoices...")
        return

    invoices = [
        {"posting_date": add_days(today(), -5), "posting_time": "10:30:00",
         "patient": patients[0].name, "patient_name": patients[0].patient_name,
         "cashier": user, "discount_amount": 50, "discount_percent": 0,
         "subtotal": 450, "tax_amount": 54, "grand_total": 504, "paid_amount": 504, "change_amount": 0,
         "payment_mode": "UPI", "upi_reference": "UPI-REF-001", "status": "Paid",
         "items": [
             {"medicine": medicines[0].name, "medicine_name": medicines[0].medicine_name,
              "qty": 1, "uom": "Strip", "rate": medicines[0].selling_rate, "mrp": medicines[0].mrp,
              "discount_percent": 5, "gst_rate": float(medicines[0].gst_rate or 12),
              "amount": medicines[0].selling_rate, "requires_prescription": medicines[0].requires_prescription},
             {"medicine": medicines[1].name if len(medicines) > 1 else medicines[0].name,
              "medicine_name": medicines[1].medicine_name if len(medicines) > 1 else medicines[0].medicine_name,
              "qty": 2, "uom": "Strip", "rate": medicines[1].selling_rate if len(medicines) > 1 else medicines[0].selling_rate,
              "mrp": medicines[1].mrp if len(medicines) > 1 else medicines[0].mrp,
              "discount_percent": 10, "gst_rate": float(medicines[1].gst_rate or 18) if len(medicines) > 1 else 18,
              "amount": 2 * (medicines[1].selling_rate if len(medicines) > 1 else medicines[0].selling_rate),
              "requires_prescription": 0},
         ]},
        {"posting_date": add_days(today(), -3), "posting_time": "14:45:00",
         "patient": patients[2].name if len(patients) > 2 else patients[0].name,
         "patient_name": patients[2].patient_name if len(patients) > 2 else patients[0].patient_name,
         "cashier": user, "discount_amount": 0, "discount_percent": 0,
         "subtotal": 780, "tax_amount": 93.60, "grand_total": 873.60, "paid_amount": 875, "change_amount": 1.40,
         "payment_mode": "Cash", "status": "Paid",
         "items": [
             {"medicine": medicines[2].name if len(medicines) > 2 else medicines[0].name,
              "medicine_name": medicines[2].medicine_name if len(medicines) > 2 else medicines[0].medicine_name,
              "qty": 5, "uom": "Strip", "rate": medicines[2].selling_rate if len(medicines) > 2 else medicines[0].selling_rate,
              "mrp": medicines[2].mrp if len(medicines) > 2 else medicines[0].mrp,
              "discount_percent": 0, "gst_rate": float(medicines[2].gst_rate or 12) if len(medicines) > 2 else 12,
              "amount": 5 * (medicines[2].selling_rate if len(medicines) > 2 else medicines[0].selling_rate),
              "requires_prescription": medicines[2].requires_prescription if len(medicines) > 2 else 1},
             {"medicine": medicines[9].name if len(medicines) > 9 else medicines[0].name,
              "medicine_name": medicines[9].medicine_name if len(medicines) > 9 else medicines[0].medicine_name,
              "qty": 2, "uom": "Bottle", "rate": medicines[9].selling_rate if len(medicines) > 9 else medicines[0].selling_rate,
              "mrp": medicines[9].mrp if len(medicines) > 9 else medicines[0].mrp,
              "discount_percent": 5, "gst_rate": float(medicines[9].gst_rate or 5) if len(medicines) > 9 else 5,
              "amount": 2 * (medicines[9].selling_rate if len(medicines) > 9 else medicines[0].selling_rate),
              "requires_prescription": 0},
         ]},
        {"posting_date": add_days(today(), -1), "posting_time": "18:30:00",
         "patient": patients[4].name if len(patients) > 4 else patients[0].name,
         "patient_name": patients[4].patient_name if len(patients) > 4 else patients[0].patient_name,
         "cashier": user, "discount_amount": 100, "discount_percent": 0,
         "loyalty_points_used": 200, "loyalty_amount": 20,
         "subtotal": 1200, "tax_amount": 144, "grand_total": 1344, "paid_amount": 1224, "change_amount": 0,
         "payment_mode": "Mixed", "status": "Paid",
         "items": [
             {"medicine": medicines[3].name if len(medicines) > 3 else medicines[0].name,
              "medicine_name": medicines[3].medicine_name if len(medicines) > 3 else medicines[0].medicine_name,
              "qty": 3, "uom": "Strip", "rate": medicines[3].selling_rate if len(medicines) > 3 else medicines[0].selling_rate,
              "mrp": medicines[3].mrp if len(medicines) > 3 else medicines[0].mrp,
              "discount_percent": 5, "gst_rate": float(medicines[3].gst_rate or 12) if len(medicines) > 3 else 12,
              "amount": 3 * (medicines[3].selling_rate if len(medicines) > 3 else medicines[0].selling_rate),
              "requires_prescription": medicines[3].requires_prescription if len(medicines) > 3 else 1},
         ]},
        {"posting_date": add_days(today(), -7), "posting_time": "09:15:00",
         "patient": patients[1].name if len(patients) > 1 else patients[0].name,
         "patient_name": patients[1].patient_name if len(patients) > 1 else patients[0].patient_name,
         "cashier": user, "discount_amount": 25, "discount_percent": 0,
         "subtotal": 320, "tax_amount": 57.60, "grand_total": 377.60, "paid_amount": 377.60, "change_amount": 0,
         "payment_mode": "Card", "upi_reference": "CARD-REF-004", "status": "Paid",
         "items": [
             {"medicine": medicines[1].name if len(medicines) > 1 else medicines[0].name,
              "medicine_name": medicines[1].medicine_name if len(medicines) > 1 else medicines[0].medicine_name,
              "qty": 3, "uom": "Strip", "rate": medicines[1].selling_rate if len(medicines) > 1 else medicines[0].selling_rate,
              "mrp": medicines[1].mrp if len(medicines) > 1 else medicines[0].mrp,
              "discount_percent": 0, "gst_rate": float(medicines[1].gst_rate or 18) if len(medicines) > 1 else 18,
              "amount": 3 * (medicines[1].selling_rate if len(medicines) > 1 else medicines[0].selling_rate),
              "requires_prescription": 0},
             {"medicine": medicines[7].name if len(medicines) > 7 else medicines[0].name,
              "medicine_name": medicines[7].medicine_name if len(medicines) > 7 else medicines[0].medicine_name,
              "qty": 1, "uom": "Strip", "rate": medicines[7].selling_rate if len(medicines) > 7 else medicines[0].selling_rate,
              "mrp": medicines[7].mrp if len(medicines) > 7 else medicines[0].mrp,
              "discount_percent": 10, "gst_rate": float(medicines[7].gst_rate or 12) if len(medicines) > 7 else 12,
              "amount": medicines[7].selling_rate if len(medicines) > 7 else medicines[0].selling_rate,
              "requires_prescription": 0},
         ]},
        {"posting_date": today(), "posting_time": "11:00:00",
         "patient": patients[5].name if len(patients) > 5 else patients[0].name,
         "patient_name": patients[5].patient_name if len(patients) > 5 else patients[0].patient_name,
         "cashier": user, "discount_amount": 0, "discount_percent": 0,
         "subtotal": 285, "tax_amount": 34.20, "grand_total": 319.20, "paid_amount": 319.20, "change_amount": 0,
         "payment_mode": "UPI", "upi_reference": "UPI-REF-005", "status": "Draft",
         "items": [
             {"medicine": medicines[6].name if len(medicines) > 6 else medicines[0].name,
              "medicine_name": medicines[6].medicine_name if len(medicines) > 6 else medicines[0].medicine_name,
              "qty": 2, "uom": "Strip", "rate": medicines[6].selling_rate if len(medicines) > 6 else medicines[0].selling_rate,
              "mrp": medicines[6].mrp if len(medicines) > 6 else medicines[0].mrp,
              "discount_percent": 0, "gst_rate": float(medicines[6].gst_rate or 5) if len(medicines) > 6 else 5,
              "amount": 2 * (medicines[6].selling_rate if len(medicines) > 6 else medicines[0].selling_rate),
              "requires_prescription": medicines[6].requires_prescription if len(medicines) > 6 else 1},
         ]},
    ]

    for inv in invoices:
        items = inv.pop("items")
        inv_doc = frappe.get_doc({"doctype": "POS Invoice Ext", **inv})
        for item in items:
            inv_doc.append("items", item)
        inv_doc.insert(ignore_permissions=True)

    print(f"✓ Created {len(invoices)} POS Invoice Ext")


def create_expiry_alerts():
    """Create 5 Expiry Alerts."""
    try:
        existing = frappe.db.get_all("Expiry Alert", limit=1)
        if existing:
            print("Expiry Alerts already exist, skipping...")
            return
    except Exception:
        pass

    medicines = frappe.db.get_all("Medicine Master", pluck="name")
    batches = frappe.db.get_all("Medicine Batch", fields=["name", "expiry_date"])
    warehouses = _ensure_warehouse()
    wh_list = [v for v in warehouses.values() if v] or [_get_warehouse()]
    wh_list = [w for w in wh_list if w]

    if not medicines or not batches:
        print("  ⚠ Missing dependencies (Medicines/Batches), skipping expiry alerts...")
        return

    wh = wh_list[0] if wh_list else None

    alerts = [
        {"medicine": medicines[0], "batch_no": batches[0].name if len(batches) > 0 else None,
         "expiry_date": batches[0].expiry_date if len(batches) > 0 else add_months(today(), 2),
         "days_to_expiry": 60, "qty": 45, "warehouse": wh,
         "alert_level": "Warning", "is_resolved": 0},
        {"medicine": medicines[5] if len(medicines) > 5 else medicines[0],
         "batch_no": batches[4].name if len(batches) > 4 else (batches[0].name if batches else None),
         "expiry_date": add_months(today(), 1),
         "days_to_expiry": 30, "qty": 22, "warehouse": wh,
         "alert_level": "Critical", "is_resolved": 0},
        {"medicine": medicines[4] if len(medicines) > 4 else medicines[0],
         "batch_no": batches[3].name if len(batches) > 3 else (batches[0].name if batches else None),
         "expiry_date": add_months(today(), 5),
         "days_to_expiry": 150, "qty": 78, "warehouse": wh,
         "alert_level": "Info", "is_resolved": 0},
        {"medicine": medicines[2] if len(medicines) > 2 else medicines[0],
         "batch_no": batches[2].name if len(batches) > 2 else (batches[0].name if batches else None),
         "expiry_date": add_days(today(), 75),
         "days_to_expiry": 75, "qty": 120, "warehouse": wh,
         "alert_level": "Warning", "is_resolved": 0},
        {"medicine": medicines[1] if len(medicines) > 1 else medicines[0],
         "batch_no": batches[1].name if len(batches) > 1 else (batches[0].name if batches else None),
         "expiry_date": add_months(today(), 10),
         "days_to_expiry": 300, "qty": 500, "warehouse": wh,
         "alert_level": "Info", "is_resolved": 1},
    ]

    for alert in alerts:
        _insert({"doctype": "Expiry Alert", **alert})
    print(f"✓ Created {len(alerts)} Expiry Alerts")


def create_drug_licenses():
    """Create 5 Drug Licenses."""
    if _exists("Drug License", "DL-"):
        try:
            existing = frappe.db.get_all("Drug License", limit=1)
            if existing:
                print("Drug Licenses already exist, skipping...")
                return
        except Exception:
            pass

    licenses = [
        {"license_name": "Pharmacy Retail License", "license_number": "DL-2024-MH-001",
         "license_type": "Drug License", "issue_date": add_months(today(), -12),
         "expiry_date": add_months(today(), 24), "issuing_authority": "FDA Maharashtra",
         "status": "Active", "renewal_reminder_days": 60, "notes": "Main pharmacy retail license"},
        {"license_name": "Narcotic Drug License", "license_number": "NDL-2024-MH-001",
         "license_type": "Narcotic License", "issue_date": add_months(today(), -6),
         "expiry_date": add_months(today(), 60), "issuing_authority": "Narcotics Control Bureau",
         "status": "Active", "renewal_reminder_days": 90, "notes": "For Schedule X drugs"},
        {"license_name": "GST Registration", "license_number": "27AABCD1234E1Z5",
         "license_type": "GST Registration", "issue_date": add_months(today(), -24),
         "expiry_date": add_months(today(), 60), "issuing_authority": "GST Department",
         "status": "Active", "renewal_reminder_days": 60, "notes": "GSTIN for pharmacy operations"},
        {"license_name": "Shop & Establishment Act", "license_number": "S&E-2024-002",
         "license_type": "Shop Act", "issue_date": add_months(today(), -18),
         "expiry_date": add_months(today(), 3), "issuing_authority": "Municipal Corporation",
         "status": "Expiring Soon", "renewal_reminder_days": 45,
         "notes": "Needs renewal within 90 days"},
        {"license_name": "FSSAI Basic License", "license_number": "FSSAI-2024-001",
         "license_type": "FSSAI", "issue_date": add_months(today(), -10),
         "expiry_date": add_months(today(), 2), "issuing_authority": "FSSAI",
         "status": "Expiring Soon", "renewal_reminder_days": 30,
         "notes": "For health supplements section"},
    ]

    for lic in licenses:
        _insert({"doctype": "Drug License", **lic})
    print(f"✓ Created {len(licenses)} Drug Licenses")


def create_audit_logs():
    """Create 8 Audit Logs."""
    try:
        existing = frappe.db.get_all("Audit Log", limit=1)
        if existing:
            print("Audit Logs already exist, skipping...")
            return
    except Exception:
        pass

    user = _ensure_user()

    logs = [
        {"action": "Created", "doctype_name": "Medicine Master", "document": "Augmentin 625 Duo",
         "user": user, "timestamp": now_datetime(), "ip_address": "192.168.1.100",
         "details": "New medicine added to catalog"},
        {"action": "Updated", "doctype_name": "Medicine Master", "document": "Paracetamol 500mg",
         "user": user, "timestamp": add_days(now_datetime(), -1), "ip_address": "192.168.1.100",
         "details": "MRP updated from 33 to 35"},
        {"action": "Submitted", "doctype_name": "Purchase Request", "document": "Monthly Antibiotics Restock",
         "user": user, "timestamp": add_days(now_datetime(), -3), "ip_address": "192.168.1.101",
         "details": "Purchase request submitted for approval"},
        {"action": "Approved", "doctype_name": "Purchase Request", "document": "Monthly Antibiotics Restock",
         "user": user, "timestamp": add_days(now_datetime(), -2), "ip_address": "192.168.1.100",
         "details": "Approved by Pharmacy Administrator"},
        {"action": "Created", "doctype_name": "Patient", "document": "Amit Sharma",
         "user": user, "timestamp": add_days(now_datetime(), -10), "ip_address": "192.168.1.102",
         "details": "New patient registration"},
        {"action": "Submitted", "doctype_name": "Prescription", "document": "RX-",
         "user": user, "timestamp": add_days(now_datetime(), -4), "ip_address": "192.168.1.101",
         "details": "Prescription verified and submitted"},
        {"action": "Created", "doctype_name": "Insurance Claim", "document": "IC-",
         "user": user, "timestamp": add_days(now_datetime(), -5), "ip_address": "192.168.1.100",
         "details": "Insurance claim filed for patient"},
        {"action": "Stock Adjusted", "doctype_name": "Stock Adjustment", "document": "SA-",
         "user": user, "timestamp": add_days(now_datetime(), -6), "ip_address": "192.168.1.101",
         "details": "Damage adjustment for syrup bottles"},
    ]

    for log in logs:
        _insert({"doctype": "Audit Log", **log})
    print(f"✓ Created {len(logs)} Audit Logs")


# =============================================================================
# Main entry point
# =============================================================================

def create_demo_data():
    """Create all demo data for Pharmacy Management System."""
    print("=" * 60)
    print("🏥 Pharmacy Management - Demo Data Creation")
    print("=" * 60)

    # Base / independent doctypes first
    create_medicine_categories()
    create_drug_manufacturers()
    create_drug_compositions()
    create_insurance_providers()
    create_loyalty_programs()
    create_doctor_masters()

    # Dependent doctypes
    create_patients()
    create_medicine_masters()
    create_pharmacists()

    # Transactional doctypes
    create_medicine_batches()
    create_prescriptions()
    create_purchase_requests()
    create_shift_assignments()
    create_stock_adjustments()
    create_stock_transfers()
    create_insurance_claims()
    create_pos_invoices()

    # Compliance & monitoring
    create_expiry_alerts()
    create_drug_licenses()
    create_audit_logs()

    frappe.db.commit()

    print("=" * 60)
    print("✅ Demo data creation completed successfully!")
    print("=" * 60)
    print()
    print("You can verify the data by going to:")
    for doctype in [
        "Medicine Category", "Drug Manufacturer", "Drug Composition",
        "Insurance Provider", "Loyalty Program", "Doctor Master",
        "Patient", "Medicine Master", "Pharmacist",
        "Medicine Batch", "Prescription", "Purchase Request",
        "Shift Assignment", "Stock Adjustment", "Stock Transfer",
        "Insurance Claim", "POS Invoice Ext",
        "Expiry Alert", "Drug License", "Audit Log",
    ]:
        print(f"  • {doctype}")


if __name__ == "__main__":
    create_demo_data()
