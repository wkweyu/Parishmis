from frappe import _

def get_data():
    return {
        "fieldname": "sacrament_candidate",
        "transactions": [
            {
                "label": _("Finance"),
                "items": ["Collection"]
            }
        ]
    }
