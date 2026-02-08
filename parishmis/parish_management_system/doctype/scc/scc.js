frappe.ui.form.on("SCC", {
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
