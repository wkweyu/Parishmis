import frappe
from frappe import _
from frappe.utils import add_days, cint, flt, getdate, get_datetime, nowdate

from parishmis.integrations import mpesa

# ------------------------------
# Helpers
# ------------------------------


def _get_parishioner_context():
    user = frappe.session.user
    if user in ("Guest", None):
        frappe.throw(_("Please log in to access the parishioner portal."), frappe.PermissionError)

    fields = [
        "name",
        "full_name",
        "first_name",
        "middle_name",
        "last_name",
        "parish",
        "church",
        "scc",
        "family",
        "phone_number",
        "email",
        "gender",
        "date_of_birth",
    ]
    parishioner = frappe.db.get_value("Parishioner", {"user_account": user}, fields, as_dict=True)
    if not parishioner:
        frappe.throw(_("Your user account is not linked to a Parishioner record. Please contact the parish office."), frappe.PermissionError)
    return parishioner


def _matches_record_scope(record, ctx):
    scope = (record.get("target_scope") or record.get("audience_scope"))
    if not scope:
        return True
    if scope.lower() == "parish":
        return bool(ctx.get("parish") and record.get("parish") == ctx.get("parish"))
    if scope.lower() == "church":
        return bool(ctx.get("church") and record.get("church") == ctx.get("church"))
    if scope.lower() == "scc":
        return bool(ctx.get("scc") and record.get("scc") == ctx.get("scc"))
    return True


def _dates_are_active(record):
    today = getdate(nowdate())
    start = record.get("valid_from")
    end = record.get("valid_upto")
    published_on = record.get("published_on")
    if published_on and getdate(published_on) > today:
        return False
    if start and getdate(start) > today:
        return False
    if end and getdate(end) < today:
        return False
    return True


def _build_profile(ctx):
    doc = frappe.db.get_value(
        "Parishioner",
        ctx.get("name"),
        [
            "name",
            "full_name",
            "first_name",
            "middle_name",
            "last_name",
            "gender",
            "date_of_birth",
            "phone_number",
            "email",
            "address",
            "parish",
            "church",
            "scc",
            "family",
            "current_status",
        ],
        as_dict=True,
    ) or {}

    if doc.get("parish"):
        doc["parish_name"] = frappe.db.get_value("Parish", doc.get("parish"), "parish_name")
    if doc.get("church"):
        doc["church_name"] = frappe.db.get_value("Church", doc.get("church"), "church_name")

    memberships = frappe.db.get_all(
        "SCC Member",
        filters={"parishioner": ctx.get("name"), "is_active": 1},
        fields=[
            "name",
            "scc",
            "role",
            "join_date",
            "leave_date",
        ],
        order_by="join_date asc",
        ignore_permissions=True,
    )

    if memberships:
        scc_ids = [row.get("scc") for row in memberships if row.get("scc")]
        scc_names = {}
        if scc_ids:
            scc_names = {
                rec.name: rec.scc_name
                for rec in frappe.db.get_all(
                    "SCC",
                    filters={"name": ("in", scc_ids)},
                    fields=["name", "scc_name"],
                    ignore_permissions=True,
                )
            }

        for row in memberships:
            row["scc_name"] = scc_names.get(row.get("scc"))

    if memberships and not doc.get("scc"):
        doc["scc"] = memberships[0].get("scc")

    if doc.get("scc"):
        doc["scc_name"] = frappe.db.get_value("SCC", doc.get("scc"), "scc_name")

    family_details = None
    if doc.get("family"):
        family_details = frappe.db.get_value(
            "Family",
            doc.get("family"),
            ["name", "family_name", "phone_number", "email", "address", "church"],
            as_dict=True,
        )
        if family_details:
            doc.setdefault("family_name", family_details.get("family_name"))

    return {
        "parishioner": doc,
        "family": family_details,
        "scc_memberships": memberships,
    }


def _build_family_members(ctx):
    if not ctx.get("family"):
        return {"members": []}
    members = frappe.db.get_all(
        "Parishioner",
        filters={"family": ctx.get("family")},
        fields=[
            "name",
            "full_name",
            "gender",
            "date_of_birth",
            "phone_number",
            "email",
            "current_status",
            "church",
        ],
        order_by="full_name asc",
        ignore_permissions=True,
    )
    return {"family": ctx.get("family"), "members": members}


def _build_sacrament_history(ctx, limit=None):
    limit = cint(limit) or 50
    records = frappe.db.get_all(
        "Sacrament Record",
        filters={"parishioner": ctx.get("name"), "docstatus": 1},
        fields=[
            "name",
            "sacrament_type",
            "sacrament_type_label",
            "sacrament_date",
            "church",
            "priest",
            "certificate_no",
            "register_book",
            "page_number",
            "entry_number",
            "remarks",
            "verification_hash",
        ],
        order_by="sacrament_date desc",
        limit=limit,
        ignore_permissions=True,
    )
    return {"records": records}


def _build_contribution_history(ctx, limit=None):
    limit = cint(limit) or 50
    filters = {"parishioner": ctx.get("name"), "docstatus": 1}
    entries = frappe.db.get_all(
        "Collection",
        filters=filters,
        fields=["name", "date", "collection_type", "amount", "payment_method", "journal_entry"],
        order_by="date desc",
        limit=limit,
        ignore_permissions=True,
    )
    aggregate = frappe.db.get_all(
        "Collection",
        filters=filters,
        fields=["sum(amount) as total_amount", "max(date) as last_payment_on"],
        limit=1,
        ignore_permissions=True,
    )
    summary_row = aggregate[0] if aggregate else {}
    summary = {
        "total_amount": flt(summary_row.get("total_amount") or 0),
        "last_payment_on": summary_row.get("last_payment_on"),
    }
    return {"entries": entries, "summary": summary}


def _build_announcements(ctx, limit=None):
    limit = cint(limit) or 20
    raw = frappe.db.get_all(
        "Announcement",
        filters={"is_published": 1},
        fields=["name", "title", "body", "published_on", "target_scope", "priority", "parish", "church", "scc", "link_url", "valid_from", "valid_upto"],
        order_by="published_on desc, modified desc",
        limit=limit * 3,
        ignore_permissions=True,
    )
    filtered = [row for row in raw if _matches_record_scope(row, ctx) and _dates_are_active(row)]
    return filtered[:limit]


def _build_church_activities(ctx, from_date=None, to_date=None, limit=None):
    limit = cint(limit) or 50
    from_date = getdate(from_date) if from_date else getdate(nowdate())
    to_date = getdate(to_date) if to_date else getdate(add_days(nowdate(), 45))

    records = frappe.db.get_all(
        "Church Activity",
        filters={"is_published": 1},
        fields=[
            "name",
            "title",
            "category",
            "status",
            "audience_scope",
            "parish",
            "church",
            "scc",
            "start_datetime",
            "end_datetime",
            "location",
            "link_url",
            "description"
        ],
        order_by="start_datetime asc",
        limit=limit * 3,
        ignore_permissions=True,
    )

    def within_range(row):
        start = getdate(row.get("start_datetime")) if row.get("start_datetime") else None
        end = getdate(row.get("end_datetime")) if row.get("end_datetime") else start
        if not start:
            return False
        end = end or start
        return not (end < from_date or start > to_date)

    filtered = [row for row in records if _matches_record_scope(row, ctx) and within_range(row)]
    return filtered[:limit]


# ------------------------------
# Whitelisted API
# ------------------------------

@frappe.whitelist()
def get_profile():
    ctx = _get_parishioner_context()
    return _build_profile(ctx)


@frappe.whitelist()
def get_family_members():
    ctx = _get_parishioner_context()
    return _build_family_members(ctx)


@frappe.whitelist()
def get_sacrament_history(limit=50):
    ctx = _get_parishioner_context()
    return _build_sacrament_history(ctx, limit)


@frappe.whitelist()
def get_contribution_history(limit=50):
    ctx = _get_parishioner_context()
    return _build_contribution_history(ctx, limit)


@frappe.whitelist()
def get_announcements(limit=20):
    ctx = _get_parishioner_context()
    return _build_announcements(ctx, limit)


@frappe.whitelist()
def get_church_activities(from_date=None, to_date=None, limit=50):
    ctx = _get_parishioner_context()
    return _build_church_activities(ctx, from_date, to_date, limit)


@frappe.whitelist()
def get_portal_bootstrap():
    ctx = _get_parishioner_context()
    return {
        "profile": _build_profile(ctx),
        "family": _build_family_members(ctx),
        "sacraments": _build_sacrament_history(ctx, limit=25),
        "contributions": _build_contribution_history(ctx, limit=25),
        "announcements": _build_announcements(ctx, limit=10),
        "activities": _build_church_activities(ctx, limit=10),
    }


@frappe.whitelist()
def start_mpesa_payment(collection_type, amount, remarks=None):
    ctx = _get_parishioner_context()

    if not collection_type or not frappe.db.exists("Collection Type", collection_type):
        frappe.throw(_("Please select a valid collection type."))

    amount = flt(amount)
    if amount <= 0:
        frappe.throw(_("Amount must be greater than zero."))

    phone = ctx.get("phone_number")
    if not phone:
        frappe.throw(_("Your parishioner profile is missing a phone number. Contact the parish office to update it."))

    if not ctx.get("church"):
        frappe.throw(_("Your parishioner profile is missing a Church. Contact the parish office."))

    collection = frappe.new_doc("Collection")
    collection.naming_series = collection.naming_series or "COL-.YYYY.-.#####"
    collection.collection_type = collection_type
    collection.parishioner = ctx.get("name")
    collection.parish = ctx.get("parish")
    collection.church = ctx.get("church")
    collection.payment_method = "M-Pesa"
    collection.date = nowdate()
    collection.amount = amount
    collection.remarks = remarks or _("Portal payment initiated by {0}").format(ctx.get("full_name"))
    collection.insert(ignore_permissions=True)

    response = mpesa.initiate_stk_push(collection=collection.name, amount=amount, phone=phone)

    return {
        "collection": collection.name,
        "mpesa": response,
    }


@frappe.whitelist()
def get_collection_types():
    _get_parishioner_context()
    return frappe.db.get_all(
        "Collection Type",
        filters={"is_active": 1},
        fields=["name", "collection_type", "category", "description", "is_sacrament_fee"],
        order_by="collection_type asc",
        ignore_permissions=True,
    )
