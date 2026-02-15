import frappe


def execute(filters=None):
    filters = filters or {}
    church = filters.get("church")

    where = ""
    params = {}
    if church:
        where = " WHERE scc.church = %(church)s"
        params["church"] = church

    data = frappe.db.sql(
        f"""
        SELECT
            scc.church AS church,
            scc.name AS scc,
            COUNT(p.name) AS total_members,
            SUM(CASE WHEN p.gender = 'Male' THEN 1 ELSE 0 END) AS male,
            SUM(CASE WHEN p.gender = 'Female' THEN 1 ELSE 0 END) AS female
        FROM `tabSCC` scc
        LEFT JOIN `tabParishioner` p
            ON p.scc = scc.name AND p.membership_status = 'Registered'
        {where}
        GROUP BY scc.church, scc.name
        ORDER BY scc.church, scc.name
        """,
        params,
        as_dict=True,
    )

    columns = [
        {"label": "Church", "fieldname": "church", "fieldtype": "Link", "options": "Church", "width": 180},
        {"label": "SCC", "fieldname": "scc", "fieldtype": "Link", "options": "SCC", "width": 180},
        {"label": "Total Members", "fieldname": "total_members", "fieldtype": "Int", "width": 130},
        {"label": "Male", "fieldname": "male", "fieldtype": "Int", "width": 100},
        {"label": "Female", "fieldname": "female", "fieldtype": "Int", "width": 100},
    ]
    return columns, data
