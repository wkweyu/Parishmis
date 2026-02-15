// Copyright (c) 2025, Concoct Systems and contributors
// For license information, please see license.txt

frappe.ui.form.on("Parishioner", {
	refresh(frm) {
		configure_membership_grid(frm);
		apply_membership_status_rules(frm);
		apply_minor_rules(frm);
		if (frm.is_new()) {
			return;
		}

		if (frm.doc.user_account) {
			frm.add_custom_button("Open Portal User", () => {
				frappe.set_route("Form", "User", frm.doc.user_account);
			});
			frm.add_custom_button("Send Welcome Email", () => {
				frappe.prompt(
					[
						{
							fieldname: "auto_generate",
							fieldtype: "Check",
							label: "Auto-generate temporary password",
							default: 1,
						},
						{
							fieldname: "temp_password",
							fieldtype: "Password",
							label: "Temporary Password",
							depends_on: "eval:!doc.auto_generate",
							description:
								"Min 10 chars with upper, lower, number, and symbol. Leave blank to auto-generate.",
						},
					],
					(values) => {
						frappe.call({
							method:
								"parishmis.parish_management_system.doctype.parishioner.parishioner.send_portal_welcome_email",
							args: {
								parishioner: frm.doc.name,
								temp_password: values.auto_generate ? null : values.temp_password,
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
					},
					"Send Welcome Email",
					"Send"
				);
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
						send_welcome_email: 1,
					},
					freeze: true,
					callback: (res) => {
						if (res && res.message) {
							frappe.show_alert({
								message: res.message.welcome_email
									? "Portal user created and welcome email sent."
									: "Portal user created successfully.",
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
	membership_status(frm) {
		apply_membership_status_rules(frm);
	},
	is_minor(frm) {
		apply_minor_rules(frm);
	},
	visit_start(frm) {
		validate_visit_dates_client(frm);
	},
	visit_end(frm) {
		validate_visit_dates_client(frm);
	},
	movement_memberships_add(frm, cdt, cdn) {
		set_membership_defaults(frm, cdt, cdn);
	},
});

frappe.ui.form.on("Movement Member", {
	form_render(frm, cdt, cdn) {
		set_membership_defaults(frm, cdt, cdn);
	},
	movement(frm, cdt, cdn) {
		set_membership_defaults(frm, cdt, cdn);
	},
	date_left(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row?.date_left) {
			frappe.model.set_value(cdt, cdn, "status", "Inactive");
		}
	},
});

function configure_membership_grid(frm) {
	const grid = frm.fields_dict?.movement_memberships?.grid;
	if (!grid) {
		return;
	}
	grid.toggle_enable("parishioner", false);
	grid.toggle_display("parishioner", false);
}

function apply_membership_status_rules(frm) {
	const status = frm.doc.membership_status || "Registered";
	const registered = status === "Registered";
	frm.set_df_property("church", "reqd", registered);
	update_field_visibility(frm, "family", registered);
	update_field_visibility(frm, "scc", registered);
	if (!registered) {
		clear_fields(frm, ["family", "scc"]);
	}
	const visitor_fields = ["home_parish", "visit_start", "visit_end"];
	visitor_fields.forEach((field) => update_field_visibility(frm, field, !registered));
	if (registered) {
		clear_fields(frm, visitor_fields);
	}
}

function apply_minor_rules(frm) {
	const isMinor = !!frm.doc.is_minor;
	frm.set_df_property("guardian", "reqd", isMinor ? 1 : 0);
	update_field_visibility(frm, "guardian", isMinor);
	if (!isMinor && frm.doc.guardian) {
		frm.set_value("guardian", null);
	}
}

function validate_visit_dates_client(frm) {
	const { visit_start: start, visit_end: end } = frm.doc;
	if (start && end && frappe.datetime.str_to_obj(end) < frappe.datetime.str_to_obj(start)) {
		frappe.msgprint(__("Visit End cannot be before Visit Start."));
		frm.set_value("visit_end", null);
	}
}

function set_membership_defaults(frm, cdt, cdn) {
	if (!frm?.doc?.name) {
		return;
	}
	frappe.model.set_value(cdt, cdn, "parishioner", frm.doc.name);
	const row = locals[cdt][cdn];
	if (!row?.status) {
		frappe.model.set_value(cdt, cdn, "status", "Active");
	}
}

function update_field_visibility(frm, fieldname, show) {
	if (!frm.get_field(fieldname)) {
		return;
	}
	frm.toggle_display(fieldname, show);
}

function clear_fields(frm, fields) {
	fields.forEach((field) => {
		if (frm.doc[field]) {
			frm.set_value(field, null);
		}
	});
}
