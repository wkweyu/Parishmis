import frappe
from frappe.model.document import Document

class MovementMember(Document):
    def validate(self):
        self.set_defaults_from_parent()
        self.validate_dates()
        self.apply_status_rules()
        self.check_duplicate_active_membership()

    def validate_dates(self):
        if self.date_joined and self.date_left:
            if frappe.utils.getdate(self.date_left) < frappe.utils.getdate(self.date_joined):
                frappe.throw("Date Left cannot be before Date Joined")

    def set_defaults_from_parent(self):
        if not self.parishioner and self.parenttype == "Parishioner":
            self.parishioner = self.parent

    def apply_status_rules(self):
        if self.date_left and self.status != "Inactive":
            self.status = "Inactive"

    def check_duplicate_active_membership(self):
        if self.status == "Active" and self.parishioner and self.movement:
            duplicate = frappe.db.exists("Movement Member", {
                "parishioner": self.parishioner,
                "movement": self.movement,
                "status": "Active",
                "name": ["!=", self.name]
            })
            if duplicate:
                frappe.throw(f"Parishioner {self.parishioner} is already an active member of {self.movement}")
