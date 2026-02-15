import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": _("Code"), "fieldname": "parishioner_code", "fieldtype": "Data", "width": 120},
        {"label": _("Full Name"), "fieldname": "full_name", "fieldtype": "Data", "width": 200},
        {"label": _("Gender"), "fieldname": "gender", "fieldtype": "Data", "width": 100},
        {"label": _("Phone"), "fieldname": "phone_number", "fieldtype": "Data", "width": 120},
        {"label": _("Church"), "fieldname": "church", "fieldtype": "Link", "options": "Church", "width": 150},
        {"label": _("SCC"), "fieldname": "scc", "fieldtype": "Link", "options": "SCC", "width": 150},
        {"label": _("Parish"), "fieldname": "parish", "fieldtype": "Link", "options": "Parish", "width": 150},
        {"label": _("Reg. Date"), "fieldname": "creation_date", "fieldtype": "Date", "width": 110},
    ]


def get_data(filters):
    conditions = []
    params = {}

    if filters.get("parish"):
        conditions.append("p.parish = %(parish)s")
        params["parish"] = filters.get("parish")

    if filters.get("church"):
        conditions.append("p.church = %(church)s")
        params["church"] = filters.get("church")

    if filters.get("scc"):
        conditions.append("p.scc = %(scc)s")
        params["scc"] = filters.get("scc")

    if filters.get("gender"):
        conditions.append("p.gender = %(gender)s")
        params["gender"] = filters.get("gender")

    if filters.get("from_date"):
        conditions.append("DATE(p.creation) >= %(from_date)s")
        params["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions.append("DATE(p.creation) <= %(to_date)s")
        params["to_date"] = filters.get("to_date")

    # Sacrament filter (Join with Sacrament Record)
    sacrament_join = ""
    if filters.get("sacrament_type"):
        sacrament_join = """
            INNER JOIN `tabSacrament Record` sr ON sr.parishioner = p.name
        """
        conditions.append("sr.sacrament_type = %(sacrament_type)s")
        params["sacrament_type"] = filters.get("sacrament_type")

    where_clause = ""
    if conditions:
        where_clause = " WHERE " + " AND ".join(conditions)

    query = f"""
        SELECT
            p.parishioner_code,
            p.full_name,
            p.gender,
            p.phone_number,
            p.church,
            p.scc,
            p.parish,
            DATE(p.creation) as creation_date
        FROM
            `tabParishioner` p
        {sacrament_join}
        {where_clause}
        ORDER BY p.full_name ASC
    """

    return frappe.db.sql(query, params, as_dict=True)
