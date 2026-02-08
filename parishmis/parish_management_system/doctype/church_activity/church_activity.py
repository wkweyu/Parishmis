import frappe
from frappe import _
from frappe.model.document import Document

class ChurchActivity(Document):
    def validate(self):
        self._set_parish_from_references()
        self._validate_scope_requirements()
        self._validate_schedule()

    def _set_parish_from_references(self):
        if self.church:
            parish = frappe.db.get_value("Church", self.church, "parish")
            if parish:
                self.parish = parish
        if not self.parish and self.scc:
            self.parish = frappe.db.get_value("SCC", self.scc, "parish")

    def _validate_scope_requirements(self):
        scope = (self.audience_scope or "Global").lower()
        if scope == "parish" and not self.parish:
            frappe.throw(_("Parish is required when Audience Scope is Parish."))
        if scope == "church" and not self.church:
            frappe.throw(_("Church is required when Audience Scope is Church."))
        if scope == "scc" and not self.scc:
            frappe.throw(_("SCC is required when Audience Scope is SCC."))

    def _validate_schedule(self):
        if self.end_datetime and self.start_datetime and self.end_datetime < self.start_datetime:
            frappe.throw(_("End time cannot be earlier than Start time."))
