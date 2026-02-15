frappe.ui.form.on("SCC", {
    refresh: function(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__("Add Leader"), function() {
                frappe.new_doc("Leadership Assignment", {
                    reference_doctype: "SCC",
                    reference_name: frm.doc.name
                });
            }, __("Actions"));
        }
    },
    church: function(frm) {
        if (frm.doc.church) {
            frappe.db.get_value("Church", frm.doc.church, "parish", (r) => {
                if (r && r.parish) {
                    frm.set_value("parish", r.parish);
                }
            });
        } else {
            frm.set_value("parish", "");
        }
    }
});
