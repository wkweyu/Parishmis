frappe.query_reports["Parishioners per Group"] = {
	"filters": [
		{
			"fieldname": "group_type",
			"label": __("Group Type"),
			"fieldtype": "Select",
			"options": "\nSCC\nCWA\nCMA\nLegion\nOther",
			"on_change": function() {
				frappe.query_report.set_filter_value('group', "");
			}
		},
		{
			"fieldname": "group",
			"label": __("Group"),
			"fieldtype": "Link",
			"options": "Group",
			"get_query": function() {
				const group_type = frappe.query_report.get_filter_value('group_type');
				if (group_type) {
					return {
						filters: {
							"group_type": group_type
						}
					};
				}
			}
		},
		{
			"fieldname": "parish",
			"label": __("Parish"),
			"fieldtype": "Link",
			"options": "Parish"
		},
		{
			"fieldname": "status",
			"label": __("Membership Status"),
			"fieldtype": "Select",
			"options": "\nActive\nInactive"
		}
	]
};
