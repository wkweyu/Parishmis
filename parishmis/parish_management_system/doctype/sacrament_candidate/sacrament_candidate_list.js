frappe.listview_settings['Sacrament Candidate'] = {
	filters: [
		['status', '!=', 'Rejected'],
	],
	get_indicator(doc) {
		const status_color = {
			'Draft': 'gray',
			'In Training': 'orange',
			'Ready': 'blue',
			'Approved': 'green',
			'Rejected': 'red',
			'Administered': 'green',
		};
		return [__(doc.status), status_color[doc.status] || 'gray', `status,=,${doc.status}`];
	},
};
