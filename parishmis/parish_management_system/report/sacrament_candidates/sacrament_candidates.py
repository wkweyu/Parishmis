import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": _("Candidate"), "fieldname": "name", "fieldtype": "Link", "options": "Sacrament Candidate", "width": 140},
        {"label": _("Parishioner"), "fieldname": "parishioner", "fieldtype": "Link", "options": "Parishioner", "width": 160},
        {"label": _("Sacrament"), "fieldname": "sacrament_type", "fieldtype": "Link", "options": "Sacrament Type", "width": 140},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 110},
        {"label": _("Enrollment Date"), "fieldname": "enrollment_date", "fieldtype": "Date", "width": 110},
        {"label": _("Expected Date"), "fieldname": "expected_date", "fieldtype": "Date", "width": 110},
        {"label": _("Completion Date"), "fieldname": "completion_date", "fieldtype": "Date", "width": 110},
        {"label": _("Church"), "fieldname": "church", "fieldtype": "Link", "options": "Church", "width": 140},
        {"label": _("Parish"), "fieldname": "parish", "fieldtype": "Link", "options": "Parish", "width": 140},
        {"label": _("Fee"), "fieldname": "fee_amount", "fieldtype": "Currency", "width": 100},
        {"label": _("Paid"), "fieldname": "paid_amount", "fieldtype": "Currency", "width": 100},
        {"label": _("Payment Ref"), "fieldname": "payment_reference", "fieldtype": "Data", "width": 140},
    ]

    conditions = ["1=1"]
    params = {}

    if filters.get("status"):
        conditions.append("status = %(status)s")
        params["status"] = filters["status"]
    if filters.get("sacrament_type"):
        conditions.append("sacrament_type = %(sacrament_type)s")
        params["sacrament_type"] = filters["sacrament_type"]
    if filters.get("church"):
        conditions.append("church = %(church)s")
        params["church"] = filters["church"]
    if filters.get("parish"):
        conditions.append("parish = %(parish)s")
        params["parish"] = filters["parish"]
    if filters.get("from_date"):
        conditions.append("enrollment_date >= %(from_date)s")
        params["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions.append("enrollment_date <= %(to_date)s")
        params["to_date"] = filters["to_date"]

    query = f"""
        SELECT
            name,
            parishioner,
            sacrament_type,
            status,
            enrollment_date,
            expected_date,
            completion_date,
            church,
            parish,
            fee_amount,
            paid_amount,
            payment_reference
        FROM `tabSacrament Candidate`
        WHERE {' AND '.join(conditions)}
        ORDER BY modified DESC
    """

    data = frappe.db.sql(query, params, as_dict=True)
    return columns, data
