import frappe


def _has_index(table: str, index_name: str) -> bool:
    return bool(
        frappe.db.sql(
            """SHOW INDEX FROM `{table}` WHERE Key_name=%s""".format(table=table),
            index_name,
        )
    )


def _add_index(table: str, index_name: str, columns: list[str], unique: bool = False):
    if _has_index(table, index_name):
        return
    column_sql = ", ".join(f"`{col}`" for col in columns)
    unique_sql = "UNIQUE " if unique else ""
    frappe.db.sql_ddl(
        f"ALTER TABLE `{table}` ADD {unique_sql}INDEX `{index_name}` ({column_sql})"
    )


def execute():
    _resolve_scc_duplicates()
    _add_index("tabSCC", "scc_name_church", ["church", "scc_name"], unique=True)

    # Reporting indexes
    _add_index("tabParishioner", "parishioner_church", ["church"])
    _add_index("tabParishioner", "parishioner_scc", ["scc"])
    _add_index("tabParishioner", "parishioner_gender", ["gender"])
    _add_index("tabGroup", "group_type", ["group_type"])
    _add_index("tabMembership", "membership_group", ["group"])


def _resolve_scc_duplicates():
    duplicates = frappe.db.sql(
        """
        SELECT church, scc_name, COUNT(name) AS cnt
        FROM `tabSCC`
        WHERE church IS NOT NULL AND scc_name IS NOT NULL
        GROUP BY church, scc_name
        HAVING COUNT(name) > 1
        """,
        as_dict=True,
    )

    for row in duplicates:
        members = frappe.db.get_all(
            "SCC",
            filters={"church": row["church"], "scc_name": row["scc_name"]},
            fields=["name", "scc_name"],
            order_by="creation asc",
        )
        # Keep the first record as-is, suffix the rest to ensure uniqueness.
        for idx, doc in enumerate(members[1:], start=2):
            new_name = f"{doc['scc_name']} ({idx})"
            frappe.db.set_value("SCC", doc["name"], "scc_name", new_name)
