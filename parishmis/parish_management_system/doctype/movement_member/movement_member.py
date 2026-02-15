import frappe
from frappe.model.document import Document

class MovementMember(Document):
    def validate(self):
        self.validate_dates()
        # Logic for status auto-setting is better handled here if it's a standalone doc
        # but since it's a child table, we'll ensure it's called.
        if self.date_left:
            self.status = "Inactive"

    def validate_dates(self):
        if self.date_joined and self.date_left:
            if frappe.utils.getdate(self.date_left) < frappe.utils.getdate(self.date_joined):
                frappe.throw("Date Left cannot be before Date Joined")
