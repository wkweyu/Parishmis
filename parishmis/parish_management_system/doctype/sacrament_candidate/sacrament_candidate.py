import frappe
from frappe.model.document import Document


class SacramentCandidate(Document):
    def validate(self):
        self._set_parish_from_church()
        self._validate_requireds()
        self._validate_spouse_requirement()
        self._validate_status_flow()
        self._validate_training_requirement()
        self._validate_fee_consistency()
        self.update_paid_amount()

    def update_paid_amount(self):
        total = frappe.db.get_value("Collection", {"sacrament_candidate": self.name, "docstatus": 1}, "sum(amount)") or 0
        self.paid_amount = total
        
        fee = self.fee_amount or 0
        if total >= fee and fee > 0:
            self.payment_status = "Paid"
        elif total > 0:
            self.payment_status = "Partially Paid"
        else:
            self.payment_status = "Unpaid"

    def _validate_spouse_requirement(self):
        if self._is_matrimony():
            if not self.second_parishioner:
                frappe.throw("Second Parishioner (Spouse) is required for Marriage.")
            if self.parishioner == self.second_parishioner:
                frappe.throw("Groom and Bride cannot be the same person.")
            
            # Validation: both must be active and not already married (if backfilling/strict check)
            for p in [self.parishioner, self.second_parishioner]:
                p_doc = frappe.db.get_value("Parishioner", p, ["current_status", "marital_status"], as_dict=True)
                if p_doc.current_status != "Active":
                    frappe.throw(f"Parishioner {p} must be Active to register for Marriage.")
                if p_doc.marital_status == "Married":
                    # Note: We allow this if and only if they are marrying each other 
                    # (e.g. correcting a record) or if we skip strict state check.
                    # But per roadmap "both unmarried":
                    frappe.throw(f"Parishioner {p} is already listed as Married.")

    def _is_matrimony(self):
        label = frappe.db.get_value("Sacrament Type", self.sacrament_type, "sacrament_type") or ""
        return any(key in label.lower() for key in ("matr", "marri"))

    @frappe.whitelist()
    def complete_administration(self, priest, date):
        """Administer the sacrament and generate records"""
        if self.status != "Approved":
            frappe.throw("Sacrament can only be administered once Approved.")
        
        if self.status == "Administered":
            frappe.throw("Sacrament has already been administered.")

        # Create Record 1
        rec1 = self._create_sacrament_record(self.parishioner, self.second_parishioner, self.spouse_name, priest, date)
        
        # If matrimony, create Record 2 for the spouse
        rec2_name = None
        if self._is_matrimony():
            # For the second record, share the SAME register details as record 1
            # so they both point to the same canonical entry/certificate
            spouse_full_name = frappe.db.get_value("Parishioner", self.parishioner, "full_name")
            rec2 = self._create_sacrament_record(
                self.second_parishioner, 
                self.parishioner, 
                spouse_full_name, 
                priest, 
                date,
                register_details={
                    "register_book": rec1.register_book,
                    "page_number": rec1.page_number,
                    "entry_number": rec1.entry_number,
                    "certificate_no": rec1.certificate_no
                }
            )
            rec2_name = rec2.name

        self.status = "Administered"
        self.completion_date = date
        self.save()
        
        return {
            "record1": rec1.name,
            "record2": rec2_name
        }

    def _create_sacrament_record(self, parishioner, spouse_p, spouse_n, priest, date, register_details=None):
        doc_data = {
            "doctype": "Sacrament Record",
            "parishioner": parishioner,
            "spouse_parishioner": spouse_p,
            "spouse_name": spouse_n,
            "sacrament_type": self.sacrament_type,
            "sacrament_date": date,
            "church": self.church,
            "parish": self.parish,
            "priest": priest,
            "registration_mode": "Auto-register",
            "remarks": f"Generated from Candidate {self.name}"
        }
        if register_details:
            doc_data.update(register_details)
            
        doc = frappe.get_doc(doc_data)
        doc.insert(ignore_permissions=True)
        doc.submit()
        return doc

    def on_update_after_submit(self):
        # Prevent updates after submission if ever made submittable in future
        raise frappe.ValidationError("Submitted Sacrament Candidate cannot be modified.")
    
        def before_update_after_submit(self):
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
        # Simple flow guard: cannot jump to Approved/Administered from Draft directly
        if self.is_new():
            return
        prev_status = frappe.db.get_value("Sacrament Candidate", self.name, "status")
        if prev_status == "Approved" and self.status in {"Draft", "In Training", "Ready"}:
            frappe.throw("Cannot move back from Approved to an earlier training status.")
        if prev_status == "Rejected" and self.status != "Rejected":
            frappe.throw("Cannot reopen a Rejected candidate.")
        if self.status == "Administered":
            # Gate: should only be set via Sacrament Record creation
            frappe.throw("Set Administered by creating a Sacrament Record.")

    def _validate_training_requirement(self):
        requires_training = frappe.db.get_value("Sacrament Type", self.sacrament_type, "requires_training")
        if requires_training and self.status in {"Ready", "Approved", "Administered"} and not self.completion_date:
            frappe.throw("Completion Date is required before marking this candidate Ready/Approved/Administered.")

    def _validate_fee_consistency(self):
        fee = self.fee_amount or 0
        paid = self.paid_amount or 0
        if paid and paid > fee and fee > 0:
            frappe.throw("Paid Amount cannot exceed Fee Amount.")
