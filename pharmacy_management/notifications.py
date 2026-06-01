import frappe

def get_notification_config():
    return {
        "for_doctype": {
            "Expiry Alert": {"alert_level": "Critical", "is_resolved": 0},
            "Drug License": {"status": ["in", ["Expiring Soon", "Expired"]]},
            "Purchase Request": {"status": "Pending Approval"},
            "Prescription": {"status": ["in", ["Uploaded", "Verification"]]},
            "Insurance Claim": {"status": ["in", ["Submitted", "Under Review"]]},
        }
    }
