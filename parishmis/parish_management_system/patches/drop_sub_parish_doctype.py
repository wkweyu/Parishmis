import frappe
from frappe.utils import cint


def execute():
	"""Drop the legacy Sub Parish DocType and table after migration to Church hierarchy."""
	doctype = "Sub Parish"
	if frappe.db.exists("DocType", doctype):
		frappe.delete_doc("DocType", doctype, ignore_permissions=True, force=1)
		frappe.db.commit()

	# Drop the table if it remains
	if frappe.db.table_exists("tabSub Parish"):
		frappe.db.sql("DROP TABLE `tabSub Parish`")

	# Clean leftover records from DocType cache
	tables_to_clear = ["DocType Cache"] if frappe.db.table_exists("DocType Cache") else []
	for table in tables_to_clear:
		frappe.db.delete(table, {"name": doctype})

	frappe.clear_cache()
