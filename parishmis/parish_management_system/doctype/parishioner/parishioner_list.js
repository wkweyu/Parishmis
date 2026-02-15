frappe.listview_settings['Parishioner'] = {
	onload(listview) {
		const churchField = listview.page.add_field({
			fieldname: 'church_filter',
			label: 'Church',
			fieldtype: 'Link',
			options: 'Church',
		});
		const sccField = listview.page.add_field({
			fieldname: 'scc_filter',
			label: 'SCC',
			fieldtype: 'Link',
			options: 'SCC',
		});

		churchField.on('change', () => {
			const value = churchField.get_value();
			if (value) {
				listview.filter_area.add([['Parishioner', 'church', '=', value]]);
			} else {
				listview.filter_area.remove('Parishioner', 'church');
			}
			listview.refresh();
		});

		sccField.on('change', () => {
			const value = sccField.get_value();
			if (value) {
				listview.filter_area.add([['Parishioner', 'scc', '=', value]]);
			} else {
				listview.filter_area.remove('Parishioner', 'scc');
			}
			listview.refresh();
		});
	},
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
