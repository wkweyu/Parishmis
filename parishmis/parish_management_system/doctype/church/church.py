# Copyright (c) 2025, Concoct Systems and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class Church(Document):
    def validate(self):
        self._set_parish_from_parent()
        self._validate_type_and_parent()
        self._ensure_code()

    def _set_parish_from_parent(self):
        if self.parent_church:
            parent_parish = frappe.db.get_value("Church", self.parent_church, "parish")
            if parent_parish:
                self.parish = parent_parish

    def _validate_type_and_parent(self):
        # Main churches must not have a parent; others should have a parent for hierarchy
        if self.type == "Main" and self.parent_church:
            frappe.throw("Main church cannot have a parent church")
        if self.type in {"Sub-Parish", "Outstation"} and not self.parent_church:
            frappe.throw("Sub-Parish/Outstation requires a parent church")
        if not self.parish:
            frappe.throw("Parish is required")

    def _ensure_code(self):
        if not self.code:
            self.code = make_autoname("CH-.#####")
