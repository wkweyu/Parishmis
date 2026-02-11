// Copyright (c) 2025, Concoct Systems and contributors
// For license information, please see license.txt

frappe.ui.form.on("Parishioner", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		if (frm.doc.user_account) {
			frm.add_custom_button("Open Portal User", () => {
				frappe.set_route("Form", "User", frm.doc.user_account);
			});
			frm.add_custom_button("Send Welcome Email", () => {
				frappe.call({
					method:
						"parishmis.parish_management_system.doctype.parishioner.parishioner.send_portal_welcome_email",
					args: {
						parishioner: frm.doc.name,
					},
					freeze: true,
					callback: (res) => {
						if (res && res.message) {
							frappe.show_alert({
								message: `Welcome email sent to ${res.message.recipient}.`,
								indicator: "green",
							});
						}
					},
				});
			});
		}

		frm.add_custom_button("Create Portal User", () => {
			const proceed = (email) => {
				frappe.call({
					method:
						"parishmis.parish_management_system.doctype.parishioner.parishioner.create_portal_user",
					args: {
						parishioner: frm.doc.name,
						user_email: email,
					},
					freeze: true,
					callback: (res) => {
						if (res && res.message) {
							frappe.show_alert({
								message: "Portal user created successfully.",
								indicator: "green",
							});
							frm.reload_doc();
						}
					},
				});
			};

			if (frm.doc.email) {
				proceed(frm.doc.email);
				return;
			}

			frappe.prompt(
				[
					{
						fieldname: "email",
						fieldtype: "Data",
						label: "Portal Email",
						reqd: 1,
						options: "Email",
					},
				],
				(values) => {
					proceed(values.email);
				},
				"Create Portal User",
				"Create"
			);
		});
	},
});
