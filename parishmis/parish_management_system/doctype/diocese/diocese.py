# Copyright (c) 2025, Concoct Systems and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document

class Diocese(Document):
    def validate(self):
        if not self.diocese_name:
            frappe.throw("Diocese Name is required.")
        if self.status not in ["Active", "Inactive"]:
            frappe.throw("Status must be Active or Inactive.")