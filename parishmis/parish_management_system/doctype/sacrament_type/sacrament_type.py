import frappe
from frappe.model.document import Document


class SacramentType(Document):
    def validate(self):
        if self.min_age_years is not None and self.min_age_years < 0:
            frappe.throw("Minimum Age must be zero or greater")
