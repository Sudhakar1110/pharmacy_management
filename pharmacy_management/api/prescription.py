import frappe
from frappe import _
import json


@frappe.whitelist(allow_guest=True)
def upload_prescription(image=None, notes=None, order_id=None):
    """Upload a prescription from the website."""
    if not image:
        frappe.throw(_("Please upload a prescription image"))
    
    user = frappe.session.user
    email = frappe.db.get_value("User", user, "email") or user
    
    # Find or create patient
    patient = frappe.db.get_value("Patient", {"email": email}, "name")
    if not patient:
        full_name = frappe.db.get_value("User", user, "full_name") or user
        mobile = frappe.db.get_value("User", user, "mobile_no") or ""
        patient_doc = frappe.new_doc("Patient")
        patient_doc.patient_name = full_name
        patient_doc.email = email
        patient_doc.mobile_number = mobile
        patient_doc.flags.ignore_permissions = True
        patient_doc.insert(ignore_permissions=True)
        patient = patient_doc.name
    
    # Create Prescription
    rx = frappe.new_doc("Prescription")
    rx.patient = patient
    rx.prescription_date = frappe.utils.today()
    rx.status = "Uploaded"
    rx.prescription_image = image
    rx.notes = notes
    rx.flags.ignore_permissions = True
    rx.insert(ignore_permissions=True)
    rx.submit()
    
    # Link to order if provided
    if order_id and frappe.db.exists("Sales Order", order_id):
        frappe.db.set_value("Sales Order", order_id, "custom_prescription_ref", rx.name, update_modified=False)
        frappe.db.set_value("Prescription", rx.name, "sales_invoice", order_id, update_modified=False)
    
    return {
        "success": True,
        "prescription_id": rx.name,
        "message": _("Prescription uploaded successfully. A pharmacist will verify it shortly."),
    }


@frappe.whitelist()
def get_prescriptions():
    """Get all prescriptions for the current user."""
    user = frappe.session.user
    email = frappe.db.get_value("User", user, "email") or user
    
    patient = frappe.db.get_value("Patient", {"email": email}, "name")
    if not patient:
        return {"prescriptions": []}
    
    prescriptions = frappe.get_all(
        "Prescription",
        filters={"patient": patient},
        fields=["name", "prescription_date", "valid_till", "status", "patient_name",
                "prescription_image", "notes", "doctor", "verified_by", "sales_invoice"],
        order_by="prescription_date desc",
        limit=50,
    )
    
    for rx in prescriptions:
        # Get medicine items
        items = frappe.get_all(
            "Prescription Item",
            filters={"parent": rx.name},
            fields=["medicine", "medicine_name", "dosage", "frequency", "duration", "qty", "instructions"],
        )
        rx.medicines = items
    
    return {"prescriptions": prescriptions}


@frappe.whitelist()
def get_prescription_detail(prescription_id):
    """Get full detail of a prescription."""
    if not frappe.db.exists("Prescription", prescription_id):
        frappe.throw(_("Prescription not found"))
    
    rx = frappe.get_doc("Prescription", prescription_id)
    
    # Verify ownership
    user = frappe.session.user
    email = frappe.db.get_value("User", user, "email") or user
    patient = frappe.db.get_value("Patient", {"email": email}, "name")
    if rx.patient != patient and "Pharmacy Administrator" not in frappe.get_roles(user):
        frappe.throw(_("Access denied"))
    
    items = frappe.get_all(
        "Prescription Item",
        filters={"parent": rx.name},
        fields=["medicine", "medicine_name", "dosage", "frequency", "duration", "qty", "instructions"],
    )
    
    # Get doctor info
    doctor_info = None
    if rx.doctor:
        doctor_info = frappe.db.get_value("Doctor Master", rx.doctor,
                                           ["doctor_name", "specialization", "hospital", "registration_number"],
                                           as_dict=True)
    
    return {
        "prescription": rx,
        "medicines": items,
        "doctor": doctor_info,
    }


@frappe.whitelist()
def request_refill(prescription_id):
    """Request a refill of an existing prescription."""
    if not frappe.db.exists("Prescription", prescription_id):
        frappe.throw(_("Prescription not found"))
    
    rx = frappe.get_doc("Prescription", prescription_id)
    
    # Create a new prescription from the existing one
    new_rx = frappe.new_doc("Prescription")
    new_rx.patient = rx.patient
    new_rx.doctor = rx.doctor
    new_rx.prescription_date = frappe.utils.today()
    new_rx.status = "Uploaded"
    new_rx.notes = f"Refill request for {rx.name}"
    new_rx.flags.ignore_permissions = True
    
    # Copy medicines
    for item in frappe.get_all("Prescription Item", filters={"parent": prescription_id},
                                fields=["medicine", "dosage", "frequency", "duration", "qty", "instructions"]):
        new_rx.append("medicines", item)
    
    new_rx.insert(ignore_permissions=True)
    new_rx.submit()
    
    return {
        "success": True,
        "prescription_id": new_rx.name,
        "message": _("Refill requested successfully. Please upload a new prescription image for verification."),
    }
