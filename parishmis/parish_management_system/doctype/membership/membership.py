# Copyright (c) 2025, Concoct Systems and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class Membership(Document):
    def validate(self):
        # Ensure a parishioner is not duplicated in the same group if active
        if frappe.db.exists("Membership", {"parishioner": self.parishioner, "group": self.group, "status": "Active"}):
            frappe.throw("Parishioner is already an active member of this group")
