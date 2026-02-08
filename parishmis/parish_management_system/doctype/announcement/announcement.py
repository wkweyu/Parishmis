import frappe
from frappe import _
from frappe.model.document import Document

class Announcement(Document):
    def validate(self):
        self._set_parish_from_scope()
        self._validate_scope_requirements()
        self._validate_dates()
        self._ensure_publish_defaults()

    def _set_parish_from_scope(self):
        if self.church:
            parish = frappe.db.get_value("Church", self.church, "parish")
            if parish:
                self.parish = parish
        if not self.parish and self.scc:
            self.parish = frappe.db.get_value("SCC", self.scc, "parish")

    def _validate_scope_requirements(self):
        scope = (self.target_scope or "Global").lower()
        if scope == "parish" and not self.parish:
            frappe.throw(_("Parish is required when Audience Scope is Parish."))
        if scope == "church" and not self.church:
            frappe.throw(_("Church is required when Audience Scope is Church."))
        if scope == "scc" and not self.scc:
            frappe.throw(_("SCC is required when Audience Scope is SCC."))

    def _validate_dates(self):
        if self.valid_from and self.valid_upto and self.valid_from > self.valid_upto:
            frappe.throw(_("Valid From cannot be later than Valid Until."))

    def _ensure_publish_defaults(self):
        if not self.published_on:
            self.published_on = frappe.utils.today()
