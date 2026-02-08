import frappe
from frappe import _
from frappe.utils import add_days, now_datetime


def ensure_portal_user(parishioner, user_email, first_name=None, last_name=None):
    if not parishioner or not user_email:
        frappe.throw(_("parishioner and user_email are required"))

    parishioner_doc = frappe.get_doc("Parishioner", parishioner)
    full_name = parishioner_doc.full_name or ""
    name_segments = [segment for segment in full_name.split(" ") if segment]
    fallback_first = name_segments[0] if name_segments else "Parishioner"
    fallback_last = name_segments[-1] if name_segments else "Member"
    first_name = first_name or parishioner_doc.first_name or fallback_first
    last_name = last_name or parishioner_doc.last_name or fallback_last

    if frappe.db.exists("User", user_email):
        user = frappe.get_doc("User", user_email)
        user.first_name = first_name or user.first_name
        user.last_name = last_name or user.last_name
        user.user_type = "Website User"
        user.enabled = 1
    else:
        user = frappe.new_doc("User")
        user.email = user_email
        user.first_name = first_name
        user.last_name = last_name
        user.user_type = "Website User"
        user.send_welcome_email = 0
        user.enabled = 1
        user.new_password = frappe.generate_hash(length=12)

    if not any(role.role == "Portal User" for role in user.roles):
        user.append("roles", {"role": "Portal User"})
    user.save(ignore_permissions=True)

    parishioner_doc.user_account = user.name
    if not parishioner_doc.email:
        parishioner_doc.email = user_email
    parishioner_doc.save(ignore_permissions=True)

    return {
        "user": user.name,
        "roles": [role.role for role in user.roles],
        "parishioner": parishioner_doc.name,
    }


def populate_collection_type_descriptions():
    category_descriptions = {
        "Tithes": "Monthly 10% tithe remitted through the parish portal.",
        "Offering": "Sunday and weekday offertory contributions recorded digitally.",
        "Building Fund": "Capital campaign / construction support for parish infrastructure.",
        "Sacrament Fee": "Payments tied to sacrament preparation or administration fees.",
        "Donation": "Free-will donations supporting parish ministries.",
        "Dues": "Association or guild membership dues.",
        "Other": "General gifts not categorized elsewhere."
    }

    updated = []
    rows = frappe.get_all(
        "Collection Type",
        fields=["name", "collection_type", "category", "description"],
    )
    for row in rows:
        target_text = row.description or category_descriptions.get(row.category) or (
            f"{row.collection_type} contributions recorded via the parish portal."
        )
        if row.description == target_text:
            continue
        frappe.db.set_value("Collection Type", row.name, "description", target_text)
        updated.append({"name": row.name, "description": target_text})
    return updated


def seed_upcoming_church_activities(parish=None, church=None):
    if not parish:
        parish = frappe.db.get_value("Parish", {}, "name")
    if not parish:
        frappe.throw(_("No Parish records found to seed activities."))

    if not church:
        church = frappe.db.get_value("Church", {"parish": parish}, "name")
    if not church:
        frappe.throw(_("No Church records found for the selected parish."))

    today = now_datetime()
    activities = [
        {
            "title": "Family Day Eucharist",
            "category": "Mass",
            "audience_scope": "Parish",
            "status": "Scheduled",
            "start_datetime": add_days(today, 7),
            "end_datetime": add_days(today, 7),
            "location": "Main Church",
            "description": "Combined parish Mass with family blessings and testimonies.",
        },
        {
            "title": "Youth Formation Workshop",
            "category": "Formation",
            "audience_scope": "Church",
            "status": "Scheduled",
            "start_datetime": add_days(today, 14),
            "end_datetime": add_days(today, 14),
            "location": "Community Hall",
            "description": "Half-day workshop on leadership and digital discipleship.",
        },
        {
            "title": "Charity Food Drive",
            "category": "Community",
            "audience_scope": "Parish",
            "status": "Scheduled",
            "start_datetime": add_days(today, 21),
            "end_datetime": add_days(today, 21),
            "location": "Parish Grounds",
            "description": "Receiving dry food donations to support vulnerable families.",
        },
    ]

    created = []
    for payload in activities:
        exists = frappe.db.exists(
            "Church Activity",
            {
                "title": payload["title"],
                "start_datetime": payload["start_datetime"],
                "parish": parish,
            },
        )
        if exists:
            continue
        doc = frappe.get_doc({
            "doctype": "Church Activity",
            "parish": parish,
            "church": church,
            **payload,
        })
        doc.insert(ignore_permissions=True)
        created.append(doc.name)
    return created
