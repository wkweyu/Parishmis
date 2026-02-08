frappe.listview_settings['SCC'] = {
	get_indicator(doc) {
		const status = doc.active ? 'Active' : 'Inactive';
		const color = doc.active ? 'green' : 'gray';
		return [__(status), color, `active,=,${doc.active ? 1 : 0}`];
	},
};
