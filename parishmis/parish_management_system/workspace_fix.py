import json
import os

import frappe


def fix_parish_workspace() -> None:
    """Sync the Parish Management System Workspace content from the app JSON into the DB.

    This reads parish_management_system/workspace/parish_management_system/parish_management_system.json,
    takes its `content` list and stores it in the Workspace record as a JSON string,
    which is what this Frappe version expects.
    """

    app_path = frappe.get_app_path("parishmis")
    json_path = os.path.join(
        app_path,
        "parish_management_system",
        "workspace",
        "parish_management_system",
        "parish_management_system.json",
    )

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    content = data.get("content")
    if not content:
        frappe.throw("Workspace JSON has no 'content' field")

    # In this Frappe version, Workspace.content should be a JSON string, not a list
    if isinstance(content, list):
        content_str = json.dumps(content)
    else:
        content_str = str(content)

    ws = frappe.get_doc("Workspace", "Parish Management System")

    # Keep module aligned in case it was saved with an old name
    ws.module = "Parish Management System"
    ws.content = content_str
    ws.save()
    frappe.db.commit()

    print("Updated Workspace 'Parish Management System' content from JSON file.")
