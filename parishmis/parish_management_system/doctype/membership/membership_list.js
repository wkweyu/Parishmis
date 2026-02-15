frappe.listview_settings['Membership'] = {
	onload(listview) {
		const groupField = listview.page.add_field({
			fieldname: 'group_filter',
			label: 'Group',
			fieldtype: 'Link',
			options: 'Group',
		});

		groupField.on('change', () => {
			const value = groupField.get_value();
			if (value) {
				listview.filter_area.add([['Membership', 'group', '=', value]]);
			} else {
				listview.filter_area.remove('Membership', 'group');
			}
			listview.refresh();
		});
	},
};
