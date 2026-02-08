import frappe
from frappe.utils import password

TARGETS = [
    {
        "parishioner_full_name": "Victor Kweyu Weremba",
        "user_id": "victor.portal@parish.local",
    },
    {
        "parishioner_full_name": "Spouse Bride Test",
        "user_id": "bride.portal@parish.local",
    },
]

DEFAULT_PASSWORD = "Portal#2026!"


def ensure_portal_user(user_id: str, full_name: str) -> str:
    user_name = frappe.db.exists("User", user_id)
    if user_name:
        user_doc = frappe.get_doc("User", user_name)
    else:
        first, *rest = (full_name or "Portal User").split()
        user_doc = frappe.get_doc(
            {
                "doctype": "User",
                "email": user_id,
                "first_name": first,
                "last_name": " ".join(rest) if rest else "",
                "user_type": "Website User",
                "send_welcome_email": 0,
                "enabled": 1,
                "new_password": DEFAULT_PASSWORD,
            }
        )
        user_doc.insert(ignore_permissions=True)

    user_doc.enabled = 1
    user_doc.user_type = "Website User"
    existing_roles = {role.role for role in user_doc.get("roles", [])}
    if "Portal User" not in existing_roles:
        user_doc.append("roles", {"role": "Portal User"})
    user_doc.save(ignore_permissions=True)

    password.update_password(user_doc.name, DEFAULT_PASSWORD)

    return user_doc.name


def link_portal_users():
    results = []
    for target in TARGETS:
        parishioner_name = frappe.db.get_value(
            "Parishioner",
            {"full_name": target["parishioner_full_name"]},
            "name",
        )
        if not parishioner_name:
            results.append(
                {
                    "parishioner": target["parishioner_full_name"],
                    "status": "missing",
                    "message": "Parishioner not found",
                }
            )
            continue

        user_name = ensure_portal_user(target["user_id"], target["parishioner_full_name"])
        frappe.db.set_value("Parishioner", parishioner_name, "user_account", user_name)

        results.append(
            {
                "parishioner": target["parishioner_full_name"],
                "user": user_name,
                "status": "linked",
            }
        )

    frappe.db.commit()
    return results
