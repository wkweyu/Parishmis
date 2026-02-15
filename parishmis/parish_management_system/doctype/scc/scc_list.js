frappe.listview_settings['SCC'] = {
	onload(listview) {
		const churchField = listview.page.add_field({
			fieldname: 'church_filter',
			label: 'Church',
			fieldtype: 'Link',
			options: 'Church',
		});

		churchField.on('change', () => {
			const value = churchField.get_value();
			if (value) {
				listview.filter_area.add([['SCC', 'church', '=', value]]);
			} else {
				listview.filter_area.remove('SCC', 'church');
			}
			listview.refresh();
		});
	},
	get_indicator(doc) {
		const status = doc.active ? 'Active' : 'Inactive';
		const color = doc.active ? 'green' : 'gray';
		return [__(status), color, `active,=,${doc.active ? 1 : 0}`];
	},
};
