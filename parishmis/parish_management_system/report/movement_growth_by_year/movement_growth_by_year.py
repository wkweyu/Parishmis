# Copyright (c) 2026, TechEdVictor and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{
			"label": "Year",
			"fieldname": "year",
			"fieldtype": "Int",
			"width": 100
		},
		{
			"label": "New Members",
			"fieldname": "new_members",
			"fieldtype": "Int",
			"width": 120
		},
		{
			"label": "Growth Rate (%)",
			"fieldname": "growth_rate",
			"fieldtype": "Percent",
			"width": 120
		}
	]

def get_data(filters):
	query = """
		SELECT 
			YEAR(date_joined) as year,
			COUNT(name) as new_members
		FROM `tabMovement Member`
		WHERE docstatus < 2
	"""
	
	if filters.get("movement"):
		query += f" AND movement = {frappe.db.escape(filters.get('movement'))}"
		
	query += " GROUP BY YEAR(date_joined) ORDER BY year ASC"
	
	raw_data = frappe.db.sql(query, as_dict=True)
	
	data = []
	prev_count = 0
	
	for d in raw_data:
		growth = 0
		if prev_count > 0:
			growth = ((d.new_members - prev_count) / prev_count) * 100
		
		data.append({
			"year": d.year,
			"new_members": d.new_members,
			"growth_rate": growth
		})
		prev_count = d.new_members
		
	return data
