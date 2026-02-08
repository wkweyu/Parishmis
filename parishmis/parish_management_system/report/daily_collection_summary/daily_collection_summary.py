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
			"label": _("Date"),
			"fieldname": "collection_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": _("Collection Type"),
			"fieldname": "collection_type",
			"fieldtype": "Link",
			"options": "Collection Type",
			"width": 150
		},
		{
			"label": _("Mode"),
			"fieldname": "mode_of_receipt",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Parishioner"),
			"fieldname": "parishioner_name",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Amount"),
			"fieldname": "amount",
			"fieldtype": "Currency",
			"width": 120
		},
        {
			"label": _("Journal Entry"),
			"fieldname": "journal_entry",
			"fieldtype": "Link",
			"options": "Journal Entry",
			"width": 120
		}
	]

def get_data(filters):
    conditions = {"docstatus": 1}
    if filters.get("from_date") and filters.get("to_date"):
        conditions["collection_date"] = ["between", [filters.get("from_date"), filters.get("to_date")]]
    
    collections = frappe.get_all(
        "Collection",
        fields=["collection_date", "collection_type", "mode_of_receipt", "parishioner_name", "amount", "journal_entry"],
        filters=conditions,
        order_by="collection_date desc"
    )
    return collections
