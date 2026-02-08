You are helping me implement the Sacrament Management module for a Frappe/ERPNext app named "parishmis".

This module is the CORE CANONICAL BACKBONE of the entire Parish Management System.
Design it carefully using proper relational modeling, audit safety, and Frappe best practices.

IMPORTANT ARCHITECTURAL RULES (MUST FOLLOW)

1. Sacraments are PERMANENT HISTORICAL RECORDS.
   - NEVER delete
   - NEVER overwrite
   - append-only
   - use docstatus (Draft → Submitted → Cancelled/Amended)

2. DO NOT store sacrament fields inside Parishioner.
   Sacraments must be separate transactional records.

3. Follow Frappe conventions strictly:
   - each doctype has .json and .py
   - validation logic in controller
   - link fields for relationships
   - use workflow
   - use print formats for certificates

4. Code must be clean, scalable, and production-ready.

-------------------------------------------------------
SYSTEM CONTEXT
-------------------------------------------------------

App: parishmis
Framework: Frappe v14+
Database: MariaDB

Existing doctypes:
- Diocese
- Parish
- Sub-Parish
- Church
- Parishioner
- Priest
- SCC
- Family

Hierarchy:
Diocese → Parish → Church/Outstation → SCC

Sacraments to support:
- Baptism
- Eucharist
- Confirmation
- Reconciliation
- Anointing of the Sick
- Marriage
- Holy Orders

-------------------------------------------------------
GOAL
-------------------------------------------------------

Implement a complete Sacrament module with:

1) Sacrament Type (setup/config doctype)
2) Sacrament Record (transaction/history doctype)
3) validations
4) workflow
5) certificate readiness
6) parishioner history integration

-------------------------------------------------------
REQUIRED DOCTYPES
-------------------------------------------------------

Create the following:

==================================
A. Sacrament Type (Setup doctype)
==================================

Purpose:
Static configuration of sacrament categories.

Fields:
- sacrament_name (Data, required, unique)
- code (Data)
- requires_priest (Check)
- requires_certificate (Check)
- repeatable (Check)
- minimum_age (Int)
- description (Small Text)

Seed default records:
Baptism, Eucharist, Confirmation, Reconciliation, Anointing of the Sick, Marriage, Holy Orders


==================================
B. Sacrament Record (Core transactional doctype)
==================================

Purpose:
Each row = ONE sacrament administered to ONE parishioner.

IMPORTANT:
- submittable = 1
- append-only history
- no delete after submit

Core fields:

Identity:
- sacrament_type (Link Sacrament Type, required)
- parishioner (Link Parishioner, required)

Event:
- date_administered (Date, required)
- church (Link Church, required)
- parish (Link Parish, fetch from church)
- scc (Link SCC, optional)

Officiant:
- priest (Link Priest)
- assistant_priest (Link Priest)

Certificate:
- certificate_no (Data)
- certificate_issued (Check)
- certificate_date (Date)

Register info (for church books):
- register_book (Data)
- page_number (Data)
- entry_number (Data)

Extra:
- sponsors (Small Text)
- remarks (Text)

System:
- docstatus
- amended_from


-------------------------------------------------------
REQUIRED BUSINESS LOGIC (implement in .py controller)
-------------------------------------------------------

Implement validations:

1. Parishioner must exist
2. date_administered cannot be future
3. If sacrament_type.repeatable == 0:
   prevent duplicate sacrament for same parishioner
4. If sacrament_type.requires_priest == 1:
   priest is mandatory
5. If minimum_age set:
   validate parishioner age
6. Prevent delete after submit
7. Only allow cancel + amend
8. Auto fetch parish from church
9. Auto set certificate_date when certificate_issued = true

Add helper methods:
- get_parishioner_sacrament_history()
- generate_certificate_data()

-------------------------------------------------------
WORKFLOW
-------------------------------------------------------

Create workflow:

Draft → Verified → Submitted

Rules:
- Catechist/Staff can create Draft
- Parish Admin verifies
- Only Priest/System Manager submits


-------------------------------------------------------
PARISHIONER INTEGRATION
-------------------------------------------------------

Make Sacrament Record appear in Parishioner:
- dashboard link
- or child table view

Parishioner should show full sacramental history timeline.


-------------------------------------------------------
OUTPUT FORMAT
-------------------------------------------------------

Generate:

1. sacrament_type.json
2. sacrament_record.json
3. sacrament_record.py
4. workflow configuration
5. example fixtures

Use correct Frappe schema structure.

Do NOT add unnecessary complexity.
Keep code clean and readable.

This module must be production-grade and canonically safe.

