frappe.listview_settings['Parishioner'] = {
	get_indicator(doc) {
		const colors = {
			'Active': 'green',
			'Transferred': 'orange',
			'Deceased': 'red',
			'Inactive': 'gray',
		};
		const status = doc.current_status || 'Unknown';
		return [__(status), colors[status] || 'gray', `current_status,=,${status}`];
	},
};
