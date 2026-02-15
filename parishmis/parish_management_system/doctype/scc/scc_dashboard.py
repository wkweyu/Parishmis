from frappe import _

def get_data():
	return {
		"fieldname": "reference_name",
		"non_standard_fieldnames": {
			"Leadership Assignment": "reference_name",
			"Parishioner": "scc"
		},
		"transactions": [
			{
				"label": _("Members"),
				"items": ["Parishioner"]
			},
			{
				"label": _("Leadership"),
				"items": ["Leadership Assignment"]
			}
		]
	}
