frappe.ui.form.on('Leadership Assignment', {
	refresh(frm) {
		set_role_options(frm);
	},
	reference_doctype(frm) {
		set_role_options(frm);
	},
});

const ROLE_MAP = {
	Parish: [
		'Parish Priest',
		'Assistant Priest',
		'Catechist',
		'Parish Council Chair',
		'Finance Chair',
	],
	Church: ['Chairperson', 'Treasurer', 'Secretary', 'Catechist'],
	SCC: ['SCC Leader', 'Assistant Leader', 'Secretary', 'Treasurer'],
	Association: ['Association Chair', 'Secretary', 'Treasurer', 'Coordinator'],
	Movement: ['Chairperson', 'Vice-Chairperson', 'Secretary', 'Treasurer', 'Coordinator', 'Spiritual Director'],
};

function set_role_options(frm) {
	const ref = frm.doc.reference_doctype;
	const base = ROLE_MAP[ref] || [];
	const options = [...base, 'Other'];
	frm.set_df_property('role', 'options', options.join('\n'));
}
