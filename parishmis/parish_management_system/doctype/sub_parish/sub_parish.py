# Copyright (c) 2025, Concoct Systems and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document

class SubParish(Document):
    def validate(self):
        if not self.parish:
            frappe.throw("Each Sub-Parish must belong to a Parish.")
        if self.status not in ["Active", "Inactive"]:
            frappe.throw("Invalid status for Sub-Parish.")

