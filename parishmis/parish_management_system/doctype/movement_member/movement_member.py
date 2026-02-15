import frappe
from frappe.model.document import Document

class MovementMember(Document):
    def validate(self):
        self.validate_dates()
        self.check_duplicate_active_membership()
        if self.date_left:
            self.status = "Inactive"

    def validate_dates(self):
        if self.date_joined and self.date_left:
            if frappe.utils.getdate(self.date_left) < frappe.utils.getdate(self.date_joined):
                frappe.throw("Date Left cannot be before Date Joined")

    def check_duplicate_active_membership(self):
        if self.status == "Active":
            duplicate = frappe.db.exists("Movement Member", {
                "parishioner": self.parishioner,
                "movement": self.movement,
                "status": "Active",
                "name": ["!=", self.name]
            })
            if duplicate:
                frappe.throw(f"Parishioner {self.parishioner} is already an active member of {self.movement}")
