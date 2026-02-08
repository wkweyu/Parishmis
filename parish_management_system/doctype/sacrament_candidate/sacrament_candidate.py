import frappe
from frappe.model.document import Document
from frappe import _


class SacramentCandidate(Document):
    def validate(self):
        self._set_parish_from_church()
        self._validate_requireds()
        self._validate_status_flow()
        self._validate_training_requirement()
        self._validate_fee_consistency()

    def on_update_after_submit(self):
        raise frappe.ValidationError("Submitted Sacrament Candidate cannot be modified.")

    def _set_parish_from_church(self):
        if not self.church:
            return
        parish = frappe.db.get_value("Church", self.church, "parish")
        if not parish:
            frappe.throw("Selected Church is missing a linked Parish; update the Church record first.")
        self.parish = parish

    def _validate_requireds(self):
        if not self.parishioner:
            frappe.throw("Parishioner is required.")
        if not self.sacrament_type:
            frappe.throw("Sacrament Type is required.")
        if not self.church:
            frappe.throw("Church is required.")
        if not self.enrollment_date:
            frappe.throw("Enrollment Date is required.")

    def _validate_status_flow(self):
        allowed = {"Draft", "In Training", "Ready", "Approved", "Rejected", "Administered"}
        if self.status not in allowed:
            frappe.throw("Invalid status for Sacrament Candidate.")
        if self.is_new():
            return
        prev_status = frappe.db.get_value("Sacrament Candidate", self.name, "status")
        if prev_status == "Approved" and self.status in {"Draft", "In Training", "Ready"}:
            frappe.throw("Cannot move back from Approved to an earlier training status.")
        if prev_status == "Rejected" and self.status != "Rejected":
            frappe.throw("Cannot reopen a Rejected candidate.")
        if self.status == "Administered":
            frappe.throw("Set Administered by creating a Sacrament Record.")

    def _validate_training_requirement(self):
        requires_training = frappe.db.get_value("Sacrament Type", self.sacrament_type, "requires_training")
        if requires_training and self.status in {"Ready", "Approved", "Administered"} and not self.completion_date:
            frappe.throw("Completion Date is required before marking this candidate Ready/Approved/Administered.")

    def _validate_fee_consistency(self):
        fee = self.fee_amount or 0
        paid = self.paid_amount or 0
        if paid and fee and paid > fee:
            frappe.throw("Paid Amount cannot exceed Fee Amount.")


def create_sacrament_record(candidate_name: str):
    candidate = frappe.get_doc("Sacrament Candidate", candidate_name)
    if candidate.status != "Approved":
        frappe.throw("Candidate must be Approved before creating a Sacrament Record.")
    if not candidate.parishioner or not candidate.sacrament_type or not candidate.church:
        frappe.throw("Parishioner, Sacrament Type, and Church are required to create a Sacrament Record.")
    parish = candidate.parish or frappe.db.get_value("Church", candidate.church, "parish")
    if not parish:
        frappe.throw("Selected Church is missing a linked Parish; update the Church record first.")

    record = frappe.new_doc("Sacrament Record")
    record.parishioner = candidate.parishioner
    record.sacrament_type = candidate.sacrament_type
    record.church = candidate.church
    record.parish = parish
    record.sacrament_date = candidate.expected_date or frappe.utils.today()
    record.priest = None
    record.insert(ignore_permissions=True)

    candidate.db_set("status", "Administered", update_modified=True)
    return record.name
