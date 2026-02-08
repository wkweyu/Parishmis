import json

import frappe


def execute():
	"""Ensure Parish Management System workspace has shortcuts matching its content.

	This parses the workspace's content JSON, finds all `shortcut` blocks, and creates
	missing Workspace Shortcut child rows so that the cards render correctly.
	"""

	workspace_name = "Parish Management System"

	if not frappe.db.exists("Workspace", workspace_name):
		return

	workspace = frappe.get_doc("Workspace", workspace_name)

	# Some instances have the Workspace linked to an old module name; realign it
	if workspace.module != workspace_name:
		workspace.module = workspace_name

	# Content is stored as JSON string
	try:
		blocks = json.loads(workspace.content or "[]")
	except Exception:
		# If content is invalid, do nothing; validation will handle it elsewhere
		return

	# Keep only shortcuts pointing to existing doctypes to avoid save failures
	valid_shortcuts = []
	existing_labels = set()
	for s in workspace.get("shortcuts"):
		if s.type == "DocType" and not frappe.db.exists("DocType", s.link_to):
			continue
		valid_shortcuts.append(s)
		existing_labels.add(s.label)
	workspace.set("shortcuts", valid_shortcuts)

	# Likewise, drop links that target missing doctypes/reports
	valid_links = []
	for link in workspace.get("links"):
		link_type = link.get("link_type") or link.get("type")
		link_to = link.get("link_to")
		if link_type == "DocType" and link_to and not frappe.db.exists("DocType", link_to):
			continue
		valid_links.append(link)
	workspace.set("links", valid_links)

	for block in blocks:
		if block.get("type") != "shortcut":
			continue

		data = block.get("data") or {}
		label = data.get("shortcut_name")
		if not label or label in existing_labels:
			continue

		# Only add if the DocType exists; otherwise skip to avoid LinkValidationError
		if frappe.db.exists("DocType", label):
			workspace.append(
				"shortcuts",
				{
					"label": label,
					"link_to": label,
					"type": "DocType",
				},
			)
			existing_labels.add(label)

	workspace.save(ignore_permissions=True)
