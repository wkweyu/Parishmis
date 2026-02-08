frappe.listview_settings['Sacrament Record'] = {
	filters: [
		['docstatus', '=', 1],
	],
	get_indicator(doc) {
		return [__('Submitted'), 'green', 'docstatus,=,1'];
	},
};
