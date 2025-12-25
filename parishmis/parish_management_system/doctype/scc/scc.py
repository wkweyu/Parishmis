# Copyright (c) 2025, Concoct Systems and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document

class SCC(Document):
    def validate(self):
        if not self.church:
            frappe.throw("Please select a Church / Outstation for this SCC.")
