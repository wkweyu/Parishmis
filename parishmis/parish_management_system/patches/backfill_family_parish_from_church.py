import frappe
from frappe.model.naming import make_autoname

def execute():
    families = frappe.get_all(
        "Family",
        filters={"church": ("is", "set")},
        fields=["name", "church", "parish", "family_code"],
    )

    for fam in families:
        updates = {}
        if fam.church and not fam.parish:
            parish = frappe.db.get_value("Church", fam.church, "parish")
            if parish:
                updates["parish"] = parish
        if not fam.family_code:
            updates["family_code"] = make_autoname("FAM-.#####")
        if updates:
            frappe.db.set_value("Family", fam.name, updates)
