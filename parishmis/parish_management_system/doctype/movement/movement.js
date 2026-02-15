// Copyright (c) 2024, Parish Management System and contributors
// For license information, please see license.txt

frappe.ui.form.on('Movement', {
	refresh: function(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Add Leader"), function() {
				frappe.new_doc("Leadership Assignment", {
					reference_doctype: "Movement",
					reference_name: frm.doc.name
				});
			}, __("Actions"));
		}
	}
});
