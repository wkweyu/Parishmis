import base64
import io

import frappe
import qrcode
from frappe.model.document import Document


class SacramentRecord(Document):
    def validate(self):
        self._set_parish_from_church()
        self._set_spouse_name()
        self._validate_requireds()
        self._validate_age()
        self._validate_priest_requirement()
        self._set_register_details()
        self._enforce_repeatable_rule()
        self._ensure_verification_hash()

    def _set_spouse_name(self):
        type_label = self._get_sacrament_label()
        if self.spouse_parishioner:
            self.spouse_name = frappe.db.get_value("Parishioner", self.spouse_parishioner, "full_name")
        # Require spouse (linked) for matrimony
        if type_label and any(key in type_label.lower() for key in ("matr", "marri")):
            if not self.spouse_parishioner:
                frappe.throw("Spouse (Parishioner) is required for Matrimony records.")

    def before_update_after_submit(self):
        frappe.throw("Submitted Sacrament Records are immutable.")

    def on_cancel(self):
        frappe.throw("Cancelling Sacrament Records is not allowed. Records are append-only.")

    def on_submit(self):
        # Prevent further edits after submit (standard submittable behavior)
        pass

    def _set_parish_from_church(self):
        if not self.church:
            frappe.throw("Church is required.")
        parish = frappe.db.get_value("Church", self.church, "parish")
        if not parish:
            frappe.throw("Selected Church is missing a linked Parish; update the Church record first.")
        self.parish = parish

    def _validate_requireds(self):
        if not self.parishioner:
            frappe.throw("Parishioner is required.")
        if not self.sacrament_type:
            frappe.throw("Sacrament Type is required.")
        if not self.sacrament_date:
            frappe.throw("Date Administered is required.")

    def _validate_age(self):
        min_age = frappe.db.get_value("Sacrament Type", self.sacrament_type, "min_age_years")
        if not min_age:
            return
        dob = frappe.db.get_value("Parishioner", self.parishioner, "date_of_birth")
        if not dob:
            return
        age_years = frappe.utils.date_diff(self.sacrament_date, dob) / 365.25
        if age_years < min_age:
            frappe.throw(f"Minimum age for this sacrament is {min_age} years.")

    def _validate_priest_requirement(self):
        require_priest = frappe.db.get_value("Sacrament Type", self.sacrament_type, "require_priest")
        if require_priest and not self.priest:
            frappe.throw("Priest is required for this Sacrament Type.")

    def _enforce_repeatable_rule(self):
        repeatable = frappe.db.get_value("Sacrament Type", self.sacrament_type, "repeatable")
        if repeatable:
            return
        # Non-repeatable: ensure no existing submitted record for same parishioner+type
        exists = frappe.db.exists(
            "Sacrament Record",
            {
                "name": ("!=", self.name),
                "parishioner": self.parishioner,
                "sacrament_type": self.sacrament_type,
                "docstatus": 1,
            },
        )
        if exists:
            frappe.throw("A submitted record already exists for this Sacrament Type and Parishioner.")

    def _ensure_verification_hash(self):
        if not self.verification_hash:
            seed = self.name or frappe.utils.random_string(12)
            self.verification_hash = frappe.generate_hash(seed, 10)

    def get_verification_qr_data_uri(self):
        url = frappe.utils.get_url_to_form("Sacrament Record", self.name)
        img = qrcode.make(url)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        encoded = base64.b64encode(buf.getvalue()).decode()
        return f"data:image/png;base64,{encoded}"

    def _get_sacrament_label(self):
        return frappe.db.get_value("Sacrament Type", self.sacrament_type, "sacrament_type") or self.sacrament_type

    def _is_matrimony(self):
        label = (self._get_sacrament_label() or "").lower()
        return any(key in label for key in ("matr", "marri"))

    def _set_register_details(self):
        if not self._is_matrimony():
            return
        mode = (self.registration_mode or "Auto-register").lower()
        if "manual" in mode:
            return
        if self.register_book and self.page_number and self.entry_number and self.certificate_no:
            return
        year = frappe.utils.getdate(self.sacrament_date or frappe.utils.nowdate()).year
        parish = self.parish
        if not parish:
            return
        register_name = f"{parish}-{year}"
        reg_row = frappe.db.sql(
            "select name, current_entry, current_certificate from `tabSacrament Register` where name=%s for update",
            register_name,
            as_dict=True,
        )
        if not reg_row:
            reg_doc = frappe.get_doc({
                "doctype": "Sacrament Register",
                "name": register_name,
                "parish": parish,
                "year": year,
                "current_entry": 0,
                "current_certificate": 0,
            })
            reg_doc.insert(ignore_permissions=True)
            reg_row = [
                {
                    "name": register_name,
                    "current_entry": 0,
                    "current_certificate": 0,
                }
            ]
        current_entry = reg_row[0]["current_entry"]
        current_certificate = reg_row[0]["current_certificate"]
        next_entry = (current_entry or 0) + 1
        next_cert = (current_certificate or 0) + 1
        self.register_book = self.register_book or f"MARRIAGE-{year}"
        self.page_number = self.page_number or str(next_entry)
        self.entry_number = self.entry_number or str(next_entry)
        self.certificate_no = self.certificate_no or f"MAR-{year}-{next_cert:05d}"
        frappe.db.set_value("Sacrament Register", register_name, {
            "current_entry": next_entry,
            "current_certificate": next_cert,
        })
