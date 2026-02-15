frappe.listview_settings['Movement'] = {
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
				listview.filter_area.add([['Movement', 'church', '=', value]]);
			} else {
				listview.filter_area.remove('Movement', 'church');
			}
			listview.refresh();
		});
	}
};
