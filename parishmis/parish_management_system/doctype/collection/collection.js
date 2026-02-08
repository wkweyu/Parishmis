// Copyright (c) 2025, Concoct Systems and contributors
// For license information, please see license.txt

frappe.ui.form.on("Collection", {
    refresh: function(frm) {
        if (frm.doc.docstatus === 0 && frm.doc.mode_of_receipt === "M-Pesa" && !frm.doc.reference_no) {
            frm.add_custom_button(__('Initiate M-Pesa STK Push'), function() {
                frm.trigger('initiate_stk_push');
            }).addClass("btn-primary");
        }
    },
    
    initiate_stk_push: function(frm) {
        if (!frm.doc.amount || frm.doc.amount <= 0) {
            frappe.throw(__("Please enter a valid amount"));
        }
        
        frappe.call({
            method: "parishmis.integrations.mpesa.initiate_stk_push",
            args: {
                collection: frm.doc.name,
                amount: frm.doc.amount,
                phone: frm.doc.parishioner_phone
            },
            callback: function(r) {
                if (r.message && r.message.ResponseCode == "0") {
                    frappe.msgprint(__("STK Push initiated successfully. Please check your phone."));
                }
            }
        });
    }
});
