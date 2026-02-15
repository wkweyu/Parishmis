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
    frappe.db.sql(
        f"ALTER TABLE `{table}` ADD {unique_sql}INDEX `{index_name}` ({column_sql})"
    )


def execute():
    _add_index("tabSCC", "scc_name_church", ["church", "scc_name"], unique=True)

    # Reporting indexes
    _add_index("tabParishioner", "parishioner_church", ["church"])
    _add_index("tabParishioner", "parishioner_scc", ["scc"])
    _add_index("tabParishioner", "parishioner_gender", ["gender"])
    _add_index("tabGroup", "group_type", ["group_type"])
    _add_index("tabMembership", "membership_group", ["group"])
