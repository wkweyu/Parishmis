import frappe
from frappe.model.document import Document

class CollectionBatch(Document):
    def validate(self):
        self.calculate_total()

    def calculate_total(self):
        total = frappe.db.get_value("Collection", {"batch": self.name, "docstatus": 1}, "sum(amount)") or 0
        self.total_amount = total

    def on_submit(self):
        # Prevent further records from being added to this batch
        pass

    @frappe.whitelist()
    def get_records(self):
        return frappe.get_all("Collection", 
            filters={"batch": self.name},
            fields=["name", "parishioner", "amount", "date", "payment_method"]
        )
