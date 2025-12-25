# Copyright (c) 2025, Concoct Systems and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document

class Church(Document):
    def validate(self):
        """Ensure at least one of Parish or Sub-Parish is set, and auto-fill Parish if possible."""
        if not self.parish and not self.sub_parish:
            frappe.throw("Please select either a Parish or a Sub-Parish for this Church.")
        
        # Auto-populate parish if sub-parish is selected
        if self.sub_parish and not self.parish:
            parish = frappe.db.get_value("Sub Parish", self.sub_parish, "parish")
            if parish:
                self.parish = parish
