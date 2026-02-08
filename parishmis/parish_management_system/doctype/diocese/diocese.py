# Copyright (c) 2025, Concoct Systems and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class Diocese(Document):
    def validate(self):
        if not self.diocese_name:
            frappe.throw("Diocese Name is required.")
        if self.status not in ["Active", "Inactive"]:
            frappe.throw("Status must be Active or Inactive.")
        self._ensure_code()

    def _ensure_code(self):
        if not self.code:
            self.code = make_autoname("DIO-.#####")