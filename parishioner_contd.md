Continue development of parishmis.

We must support 3 categories of people:
1) Registered parishioners (full members)
2) Visitors/transit faithful
3) External Catholics receiving sacramental services only

We should NOT create separate doctypes.

Instead extend Parishioner doctype with membership status logic.

========================================
PART 1 — DOCTYPE UPDATE
========================================

Update Parishioner:

Add fields:

- membership_status (Select)
    Registered
    Visitor
    Transit
    External Catholic
    Inactive

- is_minor (Check)
- guardian (Link → Parishioner)
- home_parish (Data)
- visit_start (Date)
- visit_end (Date)

========================================
PART 2 — VALIDATIONS
========================================

Rules:

If membership_status = Registered:
    church required
    SCC allowed
    family allowed

If Visitor/Transit/External:
    church optional
    SCC hidden
    family hidden

If is_minor:
    guardian required

========================================
PART 3 — REPORT LOGIC
========================================

All statistical reports must count ONLY:

membership_status = "Registered"

========================================
PART 4 — UI BEHAVIOR
========================================

Client script:
Hide SCC and family fields for non-registered statuses.

========================================
PART 5 — SACRAMENTS
========================================

Allow Sacrament Records to link to ANY Parishioner regardless of status.

========================================
Deliver:
- updated doctype
- validations
- client script
- migration patch

