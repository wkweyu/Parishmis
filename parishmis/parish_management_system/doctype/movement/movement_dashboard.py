from frappe import _

def get_data():
	return {
		"fieldname": "reference_name",
		"non_standard_fieldnames": {
			"Leadership Assignment": "reference_name",
			"Movement Member": "movement"
		},
		"transactions": [
			{
				"label": _("Members"),
				"items": ["Movement Member"]
			},
			{
				"label": _("Leadership"),
				"items": ["Leadership Assignment"]
			}
		]
	}
