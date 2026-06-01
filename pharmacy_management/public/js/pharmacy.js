// Pharmacy Management - Global JS

frappe.ui.form.on('POS Invoice Ext', {
    medicine: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.medicine) {
            frappe.db.get_value('Medicine Master', row.medicine, 
                ['medicine_name', 'selling_rate', 'mrp', 'requires_prescription'], (r) => {
                if (r) {
                    frappe.model.set_value(cdt, cdn, 'medicine_name', r.medicine_name);
                    frappe.model.set_value(cdt, cdn, 'rate', r.selling_rate || r.mrp);
                    frappe.model.set_value(cdt, cdn, 'mrp', r.mrp);
                    frappe.model.set_value(cdt, cdn, 'requires_prescription', r.requires_prescription);
                    if (r.requires_prescription && !frm.doc.prescription) {
                        frappe.msgprint({
                            title: 'Prescription Required',
                            message: `${r.medicine_name} requires a valid prescription.`,
                            indicator: 'orange'
                        });
                    }
                }
            });
        }
    },

    qty: function(frm, cdt, cdn) {
        calculate_row_amount(cdt, cdn);
        frm.trigger('calculate_totals');
    },

    rate: function(frm, cdt, cdn) {
        calculate_row_amount(cdt, cdn);
        frm.trigger('calculate_totals');
    },

    calculate_totals: function(frm) {
        let subtotal = 0, tax = 0;
        (frm.doc.items || []).forEach(item => {
            subtotal += (item.qty || 0) * (item.rate || 0);
            tax += (item.qty || 0) * (item.rate || 0) * (item.gst_rate || 0) / 100;
        });
        const discount = frm.doc.discount_amount || (subtotal * (frm.doc.discount_percent || 0) / 100);
        frm.set_value('subtotal', subtotal);
        frm.set_value('tax_amount', tax);
        frm.set_value('grand_total', subtotal + tax - discount - (frm.doc.loyalty_amount || 0));
    },

    patient: function(frm) {
        if (frm.doc.patient) {
            frappe.db.get_value('Patient', frm.doc.patient, 
                ['loyalty_points', 'insurance_provider', 'insurance_expiry'], (r) => {
                if (r) {
                    frm.set_value('patient_name', frm.doc.patient);
                    if (r.loyalty_points > 0) {
                        frappe.msgprint(`Patient has ${r.loyalty_points} loyalty points available.`, 'Loyalty Points');
                    }
                }
            });
        }
    }
});

function calculate_row_amount(cdt, cdn) {
    const row = locals[cdt][cdn];
    const disc = row.discount_percent || 0;
    const rate = (row.mrp || row.rate || 0) * (1 - disc/100);
    frappe.model.set_value(cdt, cdn, 'rate', rate);
    frappe.model.set_value(cdt, cdn, 'amount', (row.qty || 0) * rate);
}

// Medicine Batch - show color based on status
frappe.listview_settings['Medicine Batch'] = {
    get_indicator: function(doc) {
        if (doc.batch_status === 'Expired') return [__('Expired'), 'red', 'batch_status,=,Expired'];
        if (doc.batch_status === 'Near Expiry') return [__('Near Expiry'), 'orange', 'batch_status,=,Near Expiry'];
        return [__('Active'), 'green', 'batch_status,=,Active'];
    }
};

frappe.listview_settings['Prescription'] = {
    get_indicator: function(doc) {
        const map = {
            'Uploaded': 'blue', 'Verification': 'orange',
            'Dispensing': 'yellow', 'Completed': 'green', 'Cancelled': 'red'
        };
        return [__(doc.status), map[doc.status] || 'grey', `status,=,${doc.status}`];
    }
};
