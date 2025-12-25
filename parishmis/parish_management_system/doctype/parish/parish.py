# Copyright (c) 2025, Concoct Systems and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document

class Parish(Document):
    def validate(self):
        if not self.diocese:
            frappe.throw("A Parish must belong to a Diocese.")
        if self.status not in ["Active", "Inactive"]:
            frappe.throw("Invalid status for Parish.")
