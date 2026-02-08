import frappe
from frappe.utils import add_days, now_datetime, nowdate


def ensure_portal_user(parishioner_name: str, user_email: str | None = None, password: str | None = None):
    """Link a Parishioner to a Portal User role (creates user if needed)."""
    parishioner = frappe.get_doc("Parishioner", parishioner_name)

    email = user_email or parishioner.email or f"{parishioner.name}@portal.local"
    if not frappe.db.exists("User", email):
        user = frappe.get_doc(
            {
                "doctype": "User",
                "email": email,
                "first_name": parishioner.first_name or parishioner.full_name or "Parishioner",
                "send_welcome_email": 0,
                "user_type": "Website User",
            }
        ).insert(ignore_permissions=True)
    else:
        user = frappe.get_doc("User", email)

    if "Portal User" not in frappe.get_roles(user.name):
        user.add_roles("Portal User")

    if password:
        frappe.utils.password.update_password(user.name, password)

    frappe.db.set_value("Parishioner", parishioner.name, "user_account", user.name)
    frappe.db.commit()

    return {
        "parishioner": parishioner.name,
        "user": user.name,
    }


def bulk_assign_portal_users(limit: int | None = None):
    """Assign portal roles for parishioners lacking user_account."""
    filters = {"user_account": ("is", "not set")}
    names = [row.name for row in frappe.get_all("Parishioner", filters=filters, fields=["name"], limit=limit)]

    results = []
    for name in names:
        results.append(ensure_portal_user(name))
    return results


def seed_collection_type_details():
    """Populate descriptive copy for Collection Types to improve portal dropdown."""
    copy_map = {
        "Tithes": "Monthly 10% tithe offering.",
        "Offering": "Sunday loose offering for parish operations.",
        "Building Fund": "Capital drive for parish infrastructure projects.",
        "Sacrament Fee": "Fees tied to sacramental preparation and administration.",
        "Donation": "General one-time donation.",
        "Dues": "Association or ministry dues.",
    }

    updated = []
    rows = frappe.get_all("Collection Type", fields=["name", "collection_type", "description"])
    for row in rows:
        target_copy = copy_map.get(row.collection_type)
        if target_copy and (row.description or "").strip() != target_copy:
            frappe.db.set_value("Collection Type", row.name, "description", target_copy)
            updated.append(row.name)

    frappe.db.commit()
    return updated


def create_sample_church_activities(church: str | None = None, count: int = 3):
    """Seed upcoming activities for testing calendar feed."""
    if not church:
        church = frappe.db.get_value("Church", {}, "name")
    if not church:
        frappe.throw("Create at least one Church before seeding activities.")

    parish = frappe.db.get_value("Church", church, "parish")
    titles = [
        "Youth Praise Night",
        "Family Catechesis Workshop",
        "Community Outreach Drive",
    ]
    created = []
    for idx in range(count):
        title = titles[idx % len(titles)]
        start = add_days(now_datetime(), 3 + (idx * 2))
        doc = frappe.get_doc(
            {
                "doctype": "Church Activity",
                "title": f"{title} #{idx + 1}",
                "category": "Community" if idx % 2 else "Mass",
                "status": "Scheduled",
                "audience_scope": "Church",
                "parish": parish,
                "church": church,
                "start_datetime": start,
                "end_datetime": add_days(start, 0.1),
                "location": "Main Sanctuary",
                "description": "Auto-seeded portal test activity.",
                "is_published": 1,
            }
        ).insert(ignore_permissions=True)
        created.append(doc.name)

    return created
