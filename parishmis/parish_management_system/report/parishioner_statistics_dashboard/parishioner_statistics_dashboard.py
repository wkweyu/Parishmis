import frappe


def execute(filters=None):
    totals = frappe.db.sql(
        """
        SELECT
            COUNT(name) AS total_members,
            SUM(CASE WHEN gender = 'Male' THEN 1 ELSE 0 END) AS total_male,
            SUM(CASE WHEN gender = 'Female' THEN 1 ELSE 0 END) AS total_female
        FROM `tabParishioner`
        WHERE membership_status = 'Registered'
        """,
        as_dict=True,
    )
    totals = totals[0] if totals else {}

    total_sccs = frappe.db.count("SCC")
    total_churches = frappe.db.count("Church")

    columns = [
        {"label": "Metric", "fieldname": "metric", "fieldtype": "Data", "width": 200},
        {"label": "Value", "fieldname": "value", "fieldtype": "Int", "width": 120},
    ]

    data = [
        {"metric": "Total Members", "value": totals.get("total_members") or 0},
        {"metric": "Total Male", "value": totals.get("total_male") or 0},
        {"metric": "Total Female", "value": totals.get("total_female") or 0},
        {"metric": "Total SCCs", "value": total_sccs},
        {"metric": "Total Churches", "value": total_churches},
    ]

    return columns, data
