frappe.ui.form.on("Sacrament Record", {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Print Certificate'), function() {
                frm.trigger('print_certificate');
            }, __("Actions"));
        }
    },
    
    print_certificate: function(frm) {
        // Fetch the default certificate template from Sacrament Type if not cached
        frappe.db.get_value("Sacrament Type", frm.doc.sacrament_type, "default_certificate_template", (r) => {
            let print_format = r.default_certificate_template;
            
            // Fallback strategy if no template is assigned to the type
            if (!print_format) {
                const label = (frm.doc.sacrament_type_label || "").toLowerCase();
                if (label.includes("bapt")) print_format = "Sacrament Certificate - Baptism";
                else if (label.includes("conf")) print_format = "Sacrament Certificate - Confirmation";
                else if (label.includes("euch")) print_format = "Sacrament Certificate - Eucharist";
                else if (label.includes("pen") || label.includes("reconc")) print_format = "Sacrament Certificate - Penance";
                else if (label.includes("anoint")) print_format = "Sacrament Certificate - Anointing of the Sick";
                else if (label.includes("holy orders")) print_format = "Sacrament Certificate - Holy Orders";
                else if (label.includes("matr") || label.includes("marr")) print_format = "Sacrament Certificate - Matrimony";
            }

            if (print_format) {
                frappe.utils.print(
                    frm.doc.doctype,
                    frm.doc.name,
                    print_format,
                    frm.doc.docstatus,
                    frm.doc.language
                );
            } else {
                frappe.msgprint(__("Please assign a Default Certificate Template in the Sacrament Type: {0}", [frm.doc.sacrament_type]));
            }
        });
    }
});
