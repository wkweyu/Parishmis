Continue development of my Frappe app "parishmis".

We already have SCCs for geographic grouping.

Now implement Lay Apostolate & Church Movements (CWA, CMA, Youth, PMC, Choir, Catechists, etc).

These are NOT geographic like SCC.
They are MANY-TO-MANY memberships.

Design a scalable, generic solution.

========================================
PART 1 — DOCTYPES
========================================

Create Doctype: Movement
Fields:
- movement_name (Data, required)
- parish (Link → Parish)
- church (Link → Church, optional)
- scope (Select: Parish, Church, SCC)
- is_active (Check)

----------------------------------------

Create Doctype: Movement Member
Fields:
- parishioner (Link → Parishioner, required)
- movement (Link → Movement, required)
- role (Select: Member, Chair, Secretary, Treasurer)
- date_joined (Date)
- date_left (Date)
- status (Select: Active, Inactive)

Rules:
- one active membership per parishioner per movement
- validate duplicates
- auto-set inactive when date_left is filled

----------------------------------------

Update Parishioner doctype:
Add child table:
- movement_memberships (Table → Movement Member)

========================================
PART 2 — LISTING
========================================

Implement:
- list parishioners per movement
- list movements per church
- list leaders only
- filters

========================================
PART 3 — REPORTS
========================================

Create Query Reports:

1) Movement Member Count
Columns:
- Movement
- Total Members
- Male
- Female

2) Leaders Report
Columns:
- Movement
- Role
- Parishioner

3) Parishioners without any movement

4) Movement Growth by Year

----------------------------------------

Create Dashboard charts:
- Members per movement (bar)
- Gender split per movement (pie)

========================================
PART 4 — WORKSPACE
========================================

Add "Lay Movements" section to Parish Management workspace
Shortcuts:
- Movements
- Movement Members
- Movement Reports

========================================
Deliver:
- doctypes
- validations
- reports
- charts
- workspace updates

