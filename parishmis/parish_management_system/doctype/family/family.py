import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class Family(Document):
    def validate(self):
        self._require_church()
        self._set_parish_from_church()
        self._ensure_code()
        self._validate_head_membership()
        self._validate_scc_alignment()

    def _require_church(self):
        if not self.church:
            frappe.throw("Church / Outstation is required for a Family.")

    def _set_parish_from_church(self):
        if not self.church:
            return
        parish = frappe.db.get_value("Church", self.church, "parish")
        if not parish:
            frappe.throw("Selected church is missing a linked Parish; fix the church record first.")
        self.parish = parish

    def _validate_head_membership(self):
        if self.head and self.church:
            p_church = frappe.db.get_value("Parishioner", self.head, "church")
            if p_church and p_church != self.church:
                frappe.throw("Household Head must belong to the same Church as the Family.")

    def _validate_scc_alignment(self):
        if not self.scc:
            return
        scc_parish = frappe.db.get_value("SCC", self.scc, "parish")
        if scc_parish and scc_parish != self.parish:
            frappe.throw("Selected SCC belongs to a different Parish than the Family.")

    def _ensure_code(self):
        if not getattr(self, "family_code", None):
            self.family_code = make_autoname("FAM-.#####")
