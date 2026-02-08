import frappe
from frappe.model.document import Document


class SCCMember(Document):
	def validate(self):
		self._set_church_from_scc()
		self._validate_dates()
		self._enforce_active_leave_consistency()
		self._enforce_single_active_per_parishioner()

	def _set_church_from_scc(self):
		if not self.scc:
			return
		church = frappe.db.get_value("SCC", self.scc, "church")
		if not church:
			frappe.throw("Selected SCC is missing a linked Church; update the SCC record first.")
		self.church = church

	def _validate_dates(self):
		if self.leave_date and self.join_date and self.leave_date < self.join_date:
			frappe.throw("Leave Date cannot be before Join Date")

	def _enforce_active_leave_consistency(self):
		if self.leave_date and self.is_active:
			frappe.throw("An active membership cannot have a Leave Date. Clear Leave Date or uncheck Active.")
		if not self.is_active and not self.leave_date:
			# Auto-close with today's date to keep history consistent
			self.leave_date = frappe.utils.today()

	def _enforce_single_active_per_parishioner(self):
		if not self.is_active:
			return
		conflict = frappe.db.exists(
			"SCC Member",
			{
				"name": ("!=", self.name),
				"parishioner": self.parishioner,
				"is_active": 1,
			},
		)
		if conflict:
			frappe.throw("This parishioner already has an active SCC membership. Close the previous membership before creating a new one.")
