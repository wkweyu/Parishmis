frappe.listview_settings['Family'] = {
	get_indicator(doc) {
		const colors = {
			'Active': 'green',
			'Inactive': 'gray',
		};
		const status = doc.status || 'Active';
		return [__(status), colors[status] || 'gray', `status,=,${status}`];
	},
};
