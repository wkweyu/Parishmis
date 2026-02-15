import frappe


def execute(filters=None):
    filters = filters or {}
    group_type = filters.get("group_type")

    where = ""
    params = {}
    if group_type:
        where = " WHERE g.group_type = %(group_type)s"
        params["group_type"] = group_type

    data = frappe.db.sql(
        f"""
        SELECT
            g.group_type AS group_type,
            COUNT(m.name) AS total_members
        FROM `tabMembership` m
        INNER JOIN `tabGroup` g ON g.name = m.group
        {where}
        GROUP BY g.group_type
        ORDER BY g.group_type
        """,
        params,
        as_dict=True,
    )

    columns = [
        {"label": "Group", "fieldname": "group_type", "fieldtype": "Data", "width": 200},
        {"label": "Total Members", "fieldname": "total_members", "fieldtype": "Int", "width": 140},
    ]
    return columns, data
