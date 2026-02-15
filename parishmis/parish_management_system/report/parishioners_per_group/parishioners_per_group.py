import frappe


def execute(filters=None):
    filters = filters or {}
    group_type = filters.get("group_type")
    group = filters.get("group")
    parish = filters.get("parish")
    status = filters.get("status")

    where = []
    params = {}
    if group_type:
        where.append("g.group_type = %(group_type)s")
        params["group_type"] = group_type
    if group:
        where.append("g.name = %(group)s")
        params["group"] = group
    if parish:
        where.append("g.parish = %(parish)s")
        params["parish"] = parish
    if status:
        where.append("m.status = %(status)s")
        params["status"] = status

    where_clause = f"WHERE {' AND '.join(where)}" if where else ""

    data = frappe.db.sql(
        f"""
        SELECT
            g.group_type AS group_type,
            g.name AS group_name,
            g.parish AS parish,
            m.parishioner AS parishioner_id,
            p.full_name AS parishioner_name,
            p.gender,
            m.role,
            m.status,
            m.join_date,
            m.leave_date
        FROM `tabMembership` m
        INNER JOIN `tabGroup` g ON g.name = m.group
        INNER JOIN `tabParishioner` p ON p.name = m.parishioner
        {where_clause}
        ORDER BY g.group_type, g.name, p.full_name
        """,
        params,
        as_dict=True,
    )

    columns = [
        {"label": "Group Type", "fieldname": "group_type", "fieldtype": "Data", "width": 120},
        {"label": "Group", "fieldname": "group_name", "fieldtype": "Link", "options": "Group", "width": 180},
        {"label": "Parish", "fieldname": "parish", "fieldtype": "Link", "options": "Parish", "width": 120},
        {"label": "Parishioner", "fieldname": "parishioner_id", "fieldtype": "Link", "options": "Parishioner", "width": 180},
        {"label": "Full Name", "fieldname": "parishioner_name", "fieldtype": "Data", "width": 180},
        {"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 80},
        {"label": "Role", "fieldname": "role", "fieldtype": "Data", "width": 100},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": "Join Date", "fieldname": "join_date", "fieldtype": "Date", "width": 100},
        {"label": "Leave Date", "fieldname": "leave_date", "fieldtype": "Date", "width": 100},
    ]
    return columns, data
