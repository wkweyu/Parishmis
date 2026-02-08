import frappe


def execute():
    # Populate parish on Association Member from linked Parishioner
    if not frappe.db.has_column("Association Member", "parish"):
        return

    members = frappe.get_all(
        "Association Member",
        fields=["name", "parishioner"],
        filters={"parish": ["is", "not set"]},
    )

    for member in members:
        if not member.parishioner:
            continue
        parish = frappe.db.get_value("Parishioner", member.parishioner, "parish")
        if parish:
            frappe.db.set_value("Association Member", member.name, "parish", parish)
