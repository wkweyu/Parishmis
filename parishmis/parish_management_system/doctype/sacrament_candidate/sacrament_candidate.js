frappe.ui.form.on('Sacrament Candidate', {
    refresh(frm) {
        if (!frm.is_new() && frm.doc.status === 'Approved') {
            frm.add_custom_button(__('Administer Sacrament'), function() {
                frm.trigger('administer_sacrament');
            }, __("Actions")).addClass('btn-primary');
        }
    },

    administer_sacrament: function(frm) {
        let d = new frappe.ui.Dialog({
            title: __('Administer Sacrament'),
            fields: [
                {
                    label: __('Administering Priest'),
                    fieldname: 'priest',
                    fieldtype: 'Link',
                    options: 'User',
                    reqd: 1
                },
                {
                    label: __('Date Administered'),
                    fieldname: 'date',
                    fieldtype: 'Date',
                    default: frappe.datetime.get_today(),
                    reqd: 1
                }
            ],
            primary_action_label: __('Complete'),
            primary_action(values) {
                frm.call('complete_administration', {
                    priest: values.priest,
                    date: values.date
                }).then(r => {
                    if (!r.exc) {
                        frappe.show_alert({
                            message: __('Sacrament administered successfully. Records created.'),
                            indicator: 'green'
                        });
                        frm.reload_doc();
                    }
                });
                d.hide();
            }
        });
        d.show();
    }
});
