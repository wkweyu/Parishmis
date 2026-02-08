import frappe


def execute():
	"""Merge existing Sub Parish records into Church with type Sub-Parish.

	Steps:
	- Ensure each Parish has at least one Main Church (creates one if missing)
	- Create a Church entry for every Sub Parish, linked to the Parish and its Main Church
	- Remap references from Sub Parish -> Church on Family and Sacrament Record
	"""

	if not frappe.db.table_exists("Sub Parish"):
		return

	# Cache parish -> main church name
	main_church_cache = {}

	def get_or_create_main_church(parish: str) -> str | None:
		if not parish:
			return None
		if parish in main_church_cache:
			return main_church_cache[parish]
		main = frappe.db.get_value("Church", {"parish": parish, "type": "Main"})
		if not main:
			main_doc = frappe.get_doc({
				"doctype": "Church",
				"church_name": f"{parish} Main Church",
				"type": "Main",
				"parish": parish,
				"active": 1,
			})
			main_doc.insert(ignore_permissions=True)
			main = main_doc.name
		main_church_cache[parish] = main
		return main

	# Migrate Sub Parish -> Church
	sp_to_church = {}
	for sp in frappe.get_all("Sub Parish", fields=["name", "sub_parish_name", "parish", "status", "address", "phone", "catechist"]):
		parish = sp.parish
		main = get_or_create_main_church(parish)
		church_name = sp.sub_parish_name or sp.name
		if frappe.db.exists("Church", church_name):
			# Already migrated or name conflict; reuse existing
			new_church_name = church_name
		else:
			church_doc = frappe.get_doc({
				"doctype": "Church",
				"church_name": church_name,
				"type": "Sub-Parish",
				"parish": parish,
				"parent_church": main,
				"active": 1 if (sp.status or "Active") == "Active" else 0,
				"address": sp.address,
			})
			church_doc.insert(ignore_permissions=True)
			new_church_name = church_doc.name
		sp_to_church[sp.name] = new_church_name

	# Remap Family.sub_parish -> church
	if sp_to_church and frappe.db.table_exists("Family"):
		for fam in frappe.get_all("Family", fields=["name", "sub_parish", "church", "parish"], filters={"sub_parish": ("in", list(sp_to_church.keys()))}):
			new_church = sp_to_church.get(fam.sub_parish)
			if not new_church:
				continue
			parish = frappe.db.get_value("Church", new_church, "parish")
			frappe.db.set_value("Family", fam.name, {
				"church": fam.church or new_church,
				"parish": fam.parish or parish,
				"sub_parish": None,
			})

	# Remap Sacrament Record sub_parish -> church
	if sp_to_church and frappe.db.table_exists("Sacrament Record"):
		for rec in frappe.get_all("Sacrament Record", fields=["name", "sub_parish", "church", "parish"], filters={"sub_parish": ("in", list(sp_to_church.keys()))}):
			new_church = sp_to_church.get(rec.sub_parish)
			if not new_church:
				continue
			parish = frappe.db.get_value("Church", new_church, "parish")
			frappe.db.set_value("Sacrament Record", rec.name, {
				"church": rec.church or new_church,
				"parish": rec.parish or parish,
				"sub_parish": None,
			})

	frappe.db.commit()
