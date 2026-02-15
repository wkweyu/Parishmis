Continue development of my Frappe app "parishmis" (Parish Management Information System).

Goal:
Implement SCC data integrity, listing features, and statistical reporting for SCCs and Parishioners.

Stack:
Frappe Framework v14+
Python controllers
MariaDB
Query Reports + Script Reports + Dashboard Charts

========================================
PART 1 — DATA INTEGRITY FIXES
========================================

Update SCC doctype:

Fields:
- scc_name (Data, required)
- church (Link → Church, required)

Rules:
- SCC name must be UNIQUE per church
- Implement composite uniqueness (church + scc_name)

Tasks:
- Add DB unique constraint
- Validate in before_save()
- Show friendly error if duplicate

========================================
PART 2 — LISTING FEATURES
========================================

Create list filters and child queries:

1) List SCCs per Church
- Filter SCC list by church

2) List Parishioners per Church
- church field in Parishioner
- Filter list view by church

3) List Parishioners per SCC
- scc field
- Quick filter

4) List Parishioners per Group
- group_type (CWA/CMA/Youth)
- Filter view

========================================
PART 3 — REPORTS (IMPORTANT)
========================================

Create these reports:

A) SCC Member Count Report (Query Report)
Columns:
- Church
- SCC
- Total Members
- Male
- Female

SQL:
Group by SCC
Count gender totals

----------------------------------------

B) Parishioners per Church (Query Report)
Columns:
- Church
- Total Members

----------------------------------------

C) Parishioners per Group (Query Report)
Columns:
- Group (CWA/CMA/Youth)
- Total Members

----------------------------------------

D) Parishioner Statistics Dashboard (Script Report)
Return:
{
 total_members,
 total_male,
 total_female,
 total_sccs,
 total_churches
}

----------------------------------------

E) Church Drilldown Report (Script Report)
Input filter: church
Output:
- SCC count
- Member count
- Gender breakdown

========================================
PART 4 — DASHBOARD CHARTS
========================================

Add workspace charts:

Charts:
- Members per Church (bar)
- Members per SCC (bar)
- Gender split (pie)
- Group distribution (pie)

========================================
PART 5 — WORKSPACE
========================================

Add section "Statistics & Reports" to Parish Management workspace:

Shortcuts:
- SCC Member Count
- Parishioners per Church
- Parishioners per Group
- Church Drilldown

========================================
PART 6 — PERFORMANCE
========================================

- Use indexed fields (church, scc, group_type, gender)
- Optimize queries
- Use frappe.db.get_all with group_by

========================================
Deliver:
- Updated doctypes
- validation logic
- reports
- charts
- workspace updates
- fixtures if needed

