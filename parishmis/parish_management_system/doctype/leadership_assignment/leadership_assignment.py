import frappe
from frappe.model.document import Document


class LeadershipAssignment(Document):
	def validate(self):
		self._validate_role_against_reference()
		self._validate_dates()
		self._enforce_single_current_per_role()

	# Allowed leadership roles per reference doctype; "Other" is implicitly allowed for flexibility
	ROLE_MAP = {
		"Parish": {
			"Parish Priest",
			"Assistant Priest",
			"Catechist",
			"Parish Council Chair",
			"Finance Chair",
		},
		"Church": {
			"Chairperson",
			"Treasurer",
			"Secretary",
			"Catechist",
		},
		"SCC": {
			"SCC Leader",
			"Assistant Leader",
			"Secretary",
			"Treasurer",
		},
		"Association": {
			"Association Chair",
			"Secretary",
			"Treasurer",
			"Coordinator",
		},
		"Movement": {
			"Chairperson",
			"Vice-Chairperson",
			"Secretary",
			"Treasurer",
			"Coordinator",
			"Spiritual Director",
		},
	}

	def _validate_role_against_reference(self):
		if not (self.reference_doctype and self.role):
			return
		# Always allow "Other" to preserve flexibility
		if self.role.strip().lower() == "other":
			return
		allowed = self.ROLE_MAP.get(self.reference_doctype)
		if not allowed:
			return
		if self.role not in allowed:
			frappe.throw(
				frappe._(
					f"Role '{self.role}' is not allowed for {self.reference_doctype}. "
					f"Allowed: {', '.join(sorted(allowed | {'Other'}))}"
				)
			)

	def _validate_dates(self):
		if self.to_date and self.from_date and self.to_date < self.from_date:
			frappe.throw("To Date cannot be before From Date")

	def _enforce_single_current_per_role(self):
		if not self.is_current:
			return
		filters = {
			"name": ("!=", self.name),
			"reference_doctype": self.reference_doctype,
			"reference_name": self.reference_name,
			"role": self.role,
			"is_current": 1,
		}
		if frappe.db.exists("Leadership Assignment", filters):
			frappe.throw("An active assignment already exists for this role on the selected record. End the previous assignment or uncheck Current.")
