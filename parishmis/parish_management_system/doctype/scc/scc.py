# Copyright (c) 2025, Concoct Systems and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class SCC(Document):
    def validate(self):
        self._format_names()
        if not self.church:
            frappe.throw("Please select a Church / Outstation for this SCC.")
        self._set_parish_from_church()
        self._ensure_code()

    def _format_names(self):
        """Format SCC name and location to Title Case"""
        if self.scc_name:
            self.scc_name = self.scc_name.strip().title()
        if self.location:
            self.location = self.location.strip().title()

    def _set_parish_from_church(self):
        parish = frappe.db.get_value("Church", self.church, "parish") if self.church else None
        if parish:
            self.parish = parish
        else:
            frappe.throw("Selected church is missing a linked Parish; fix the church record first.")

    def _ensure_code(self):
        if not getattr(self, "code", None):
            self.code = make_autoname("SCC-.#####")
