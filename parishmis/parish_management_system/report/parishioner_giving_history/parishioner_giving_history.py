# Copyright (c) 2025, Parish Management System and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{
			"label": _("Parishioner"),
			"fieldname": "parishioner",
			"fieldtype": "Link",
			"options": "Parishioner",
			"width": 150
		},
		{
			"label": _("Total Amount"),
			"fieldname": "total_amount",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Last Contribution Date"),
			"fieldname": "last_date",
			"fieldtype": "Date",
			"width": 150
		},
		{
			"label": _("Count"),
			"fieldname": "count",
			"fieldtype": "Int",
			"width": 80
		}
	]

def get_data(filters):
    # Grouped by parishioner
    query = """
        SELECT
            parishioner,
            SUM(amount) as total_amount,
            MAX(collection_date) as last_date,
            COUNT(name) as count
        FROM
            `tabCollection`
        WHERE
            docstatus = 1
        GROUP BY
            parishioner
        ORDER BY
            total_amount DESC
    """
    return frappe.db.sql(query, as_dict=1)
