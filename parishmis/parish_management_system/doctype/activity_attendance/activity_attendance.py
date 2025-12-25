# Copyright (c) 2025, Concoct Systems and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe

class ActivityAttendance(Document):
    def validate(self):
        # Auto-fill group and date from the linked activity
        if self.activity:
            activity_doc = frappe.get_doc("Activity", self.activity)
            self.group = activity_doc.group
            self.attendance_date = activity_doc.date

        # Prevent duplicate attendance entries for the same activity + parishioner
        if frappe.db.exists("Activity Attendance", {"activity": self.activity, "parishioner": self.parishioner}):
            existing = frappe.db.get_value("Activity Attendance", {"activity": self.activity, "parishioner": self.parishioner}, "name")
            if existing != self.name:
                frappe.throw(f"{self.parishioner} is already marked for this activity.")
