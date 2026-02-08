import frappe
from frappe.model.document import Document


class AssociationMember(Document):
	def validate(self):
		self._set_parish_from_parishioner()
		self._validate_dates()
		self._enforce_current_leave_consistency()
		self._enforce_single_current()

	def _set_parish_from_parishioner(self):
		if not self.parishioner:
			return
		parish = frappe.db.get_value("Parishioner", self.parishioner, "parish")
		if not parish:
			frappe.throw("Selected Parishioner is missing a Parish. Update the Parishioner first.")
		self.parish = parish

	def _validate_dates(self):
		if self.leave_date and self.join_date and self.leave_date < self.join_date:
			frappe.throw("Leave Date cannot be before Join Date")

	def _enforce_current_leave_consistency(self):
		if self.leave_date and self.is_current:
			frappe.throw("Current membership cannot have a Leave Date. Uncheck Current or clear Leave Date.")

	def _enforce_single_current(self):
		if not self.is_current:
			return
		conflict = frappe.db.exists(
			"Association Member",
			{
				"name": ("!=", self.name),
				"parishioner": self.parishioner,
				"association": self.association,
				"is_current": 1,
			},
		)
		if conflict:
			frappe.throw("This parishioner already has an active membership for this Association. End the previous one or uncheck Current.")
