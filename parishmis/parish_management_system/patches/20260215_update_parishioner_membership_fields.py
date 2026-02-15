import frappe


def execute():
	frappe.reload_doc("parish_management_system", "doctype", "parishioner")

	frappe.db.sql(
		"""
			UPDATE `tabParishioner`
			SET membership_status = 'Registered'
			WHERE IFNULL(membership_status, '') = ''
		"""
	)

	frappe.db.sql(
		"""
			UPDATE `tabParishioner`
			SET is_minor = 0
			WHERE is_minor IS NULL
		"""
	)

	frappe.db.sql(
		"""
			UPDATE `tabParishioner`
			SET guardian = NULL
			WHERE IFNULL(is_minor, 0) = 0 AND guardian IS NOT NULL
		"""
	)

	frappe.db.sql(
		"""
			UPDATE `tabParishioner`
			SET family = NULL,
				scc = NULL
			WHERE membership_status NOT IN ('Registered', '')
				AND (family IS NOT NULL OR scc IS NOT NULL)
		"""
	)
