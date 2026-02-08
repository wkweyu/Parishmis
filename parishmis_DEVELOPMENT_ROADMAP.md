# ParishMIS – Development Roadmap & AI Engineering Guide

Catholic Parish Management System built with **Frappe Framework + ERPNext**

This document is both:
1) Human development roadmap
2) AI/Copilot implementation specification

Copilot or any AI assistant MUST follow these rules when generating code.

---

# 🎯 System Goal

ParishMIS provides Catholic parishes and dioceses with a unified system for:

- Parish hierarchy management
- Parishioner & family records
- SCC (Small Christian Communities)
- Sacraments (canonical records)
- Events
- Collections & M-Pesa integration
- Parishioner self-service portal

The **Parish** is the primary operational unit.

Hierarchy:

Diocese → Parish → Church/Outstation → SCC → Parishioner

---

# 🔒 Global Engineering Rules (MANDATORY)

These apply to ALL phases.

## Architecture Rules

- Use normalized relational design
- No duplicated data
- No nested child lists where separate doctype is correct
- Never modify ERPNext core
- Never delete historical records
- Use status/docstatus instead of delete

## Frappe Rules

Every Doctype MUST include:
- .json schema
- .py controller
- permissions
- list filters
- workspace shortcut
- indexes for link fields

## Data Safety Rules

- Sacraments are append-only (never overwritten)
- Financial records immutable after submit
- Leadership must have history
- Transfers must be logged

---

# 🧱 PHASED DEVELOPMENT PLAN

Work strictly in order.
Do NOT skip phases.

Each phase must be fully complete before moving forward.

---

# 🟢 Phase 1 — Structure Layer (Church Hierarchy)

## Goal
Build stable organizational structure.

Everything else depends on this.

## Doctypes

### Diocese
Top-level grouping only.

### Parish (CORE ROOT)
All records belong to a parish.

### Church (Merged)
Single doctype for:
- Church
- Sub-Parish
- Outstation

Field:
type = Main | Sub-Parish | Outstation

### SCC
Community group under church.

### SCC Member
Parishioner ↔ SCC mapping (many-to-many).

### Leadership Assignment
Universal leadership history.

Used for:
- Parish priest
- Assistant priest
- Catechist
- SCC leaders
- Committees

Fields:
- reference_doctype (Dynamic Link)
- role
- person (Priest or Parishioner)
- from_date
- to_date
- is_current

## Logic

- parish auto-fetched from church
- SCC auto-fetched from church
- tree navigation enabled
- prevent orphan records
- leadership history preserved

## Definition of Done

✅ Full hierarchy creation works  
✅ Leaders assignable with history  
✅ Tree view navigation  
✅ Workspace shortcuts  

---

# 🟡 Phase 2 — People Layer (Membership Core)

## Goal
Stable parishioner registry.

NO sacraments or payments yet.

## Doctypes

- Parishioner
- Family
- Association (CWA, CMA, Youth, etc.)
- Association Member
- Parishioner Transfer History

## Parishioner stores ONLY

- identity info
- contact
- current church/SCC/family
- status

Never store:
❌ sacraments
❌ payments
❌ leadership
❌ historical logs

## Logic

- unique phone validation
- auto full name
- church mandatory
- transfer auto-logs history
- portal user linking
- status lifecycle

## Definition of Done

✅ register members  
✅ move between churches  
✅ filters by parish/church  
✅ clean reports  

---

# 🔵 Phase 3 — Sacrament Module (CANONICAL CORE)

⚠️ MOST CRITICAL PART OF SYSTEM

Implement Sacrament lifecycle using three doctypes:

## Doctypes

### Sacrament Type (setup)
Seed 7:
- Baptism
- Eucharist
- Confirmation
- Reconciliation
- Anointing of the Sick
- Marriage
- Holy Orders

### Sacrament Record (canonical)

Fields:

- sacrament_type
- parishioner
- church
- priest
- date_administered
- certificate_no
- register_book
- page_number
- entry_number
- remarks

### Sacrament Candidate (training + workflow + fees)
Created ONLY when:

Candidate.status == Approved
AND sacrament administered


This is:

immutable

permanent

printable

historical

Never stores training/payment.

Only canonical facts.

🔵 Now let’s address your real-world cases
🧒 Case 1 — Baptism (minor child)
Problem

Child not yet parishioner.

Correct flow
Step 1 — Register Child

Create Parishioner

mark is_minor = 1

link parents

family assigned

👉 NEVER create sacrament without parishioner first

Step 2 — Create Sacrament Candidate

Sacrament Type = Baptism
training_required = false

Step 3 — Verify parents/sponsors

documents_verified = true

Step 4 — Fee payment (optional)

Collection Record created

Step 5 — Priest administers

System:

Generate Sacrament Record automatically
status → Completed

🎓 Case 2 — Eucharist / Confirmation (training required)
Step 1

Candidate created by catechist

Step 2

Training sessions tracked

Step 3

Attendance recorded

Step 4

Catechist marks training_completed

Step 5

Priest approves

Step 6

Mass day → bulk generate Sacrament Records

💍 Case 3 — Marriage (two parishioners)
Special requirements

Marriage is:

2 people

investigation

training

banns

fees

priest approval

So:

Candidate record

Fields:

parishioner (groom)
second_parishioner (bride)


System validation:

both must exist

both active

both unmarried

Ceremony day

System:
Creates TWO Sacrament Records:

one for each spouse

(both referencing same certificate)

💰 Sacrament Fees (critical)

Never store fees inside Sacrament Record.

Instead:

Flow:

Candidate → Collection Record

So:

Sacrament Candidate
   ↳ Collection Record
         ↳ M-Pesa Transaction


This keeps finance separate.


## Rules

- no duplicates (except repeatable types)
- validate minimum age
- require priest if configured
- append-only history
- generate certificates
- visible in parishioner timeline
- Candidate handles preparation, training, fees, approval
- Record created only after completion
- minors must first be registered as Parishioners
- marriage supports two parishioners
- training required for Eucharist/Confirmation/Marriage
- integrate with Collection Record for payments
- never store sacrament info directly on Parishioner
- use workflows for Candidate

##Generate:
.json
.py controllers
validations
workflow states

## Definition of Done

✅ certificates printable  
✅ sacrament history visible  
✅ reports exportable  
✅ canonical compliance  

---

# 🟠 Phase 4 — Finance & Collections

Implement Phase 4 Finance & Collections for ParishMIS using normalized ERP design.

Create doctypes:

1. Collection Type (setup)
2. Collection Record (submittable, immutable after submit)
3. Collection Batch (groups multiple records)
4. M-Pesa Transaction (gateway log)
5. optional Pledge
6. Payment Settings


Rules:
- one Collection Record per payment
- never delete financial records
- ledger posting via ERPNext on submit
- do not mix mpesa data with collection record
- batches group cash transactions
- integrate with Sacrament Candidate via link
- add validations and indexes
- include list filters and workspace items

#Let ERPNext handle:

ledgers
trial balance
P&L
audit

ParishMIS only handles domain logic.

#Integration With Sacraments (IMPORTANT)

From Phase 3:

Sacrament Candidate should NOT store payments.

Instead:

Collection Record
   ↳ sacrament_candidate (link)


So:

candidate shows “Paid”

finance still normalized

#Clean Relationships
Collection Type → Collection Record
Collection Record → Batch
Collection Record → Parishioner
Collection Record → Sacrament Candidate
Collection Record → M-Pesa Transaction
Batch → Bank Deposit
ERPNext → Journal Entry


Generate:
.json
.py controllers
validations
auto ledger posting hooks
reports
fixtures

#Reports you MUST support

Because parish admins will demand these:

daily collection summary
per church totals
per mass totals
per collection type
per parishioner giving history
sacrament income report
mpesa vs cash comparison
deposit reconciliation
monthly income statement

#Implement Phase 4 in this order:

Step 1

Collection Type

Step 2

Collection Record

Step 3

Ledger posting

Step 4

M-Pesa integration

Step 5

Batch & reconciliation

Step 6

Reports

If you want, next I can generate for you:

---

# 🟣 Phase 5 — Portal Layer

Implement ParishMIS Phase 5 Portal Layer as a mobile-first Progressive Web App.

Requirements:
- PWA (manifest + service worker)
- Tailwind UI
- no native app
- Parishioner self-service only

Features:
1. login
2. profile view
3. family members
4. sacrament history timeline
5. contributions history
6. STK payments
7. announcements
8. Calender of church activities

Security:
- user linked to Parishioner
- server-side filtering only
- cannot view other users' data

Backend:
- use existing doctypes
- create Announcement doctype
- build REST endpoints
- integrate with M-Pesa Transaction

Deliver:
- portal routes
- templates
- API methods
- PWA setup
- role Portal User
- permission rules

---

# 🔴 Phase 6 — Hardening & Deployment

## Goal
Production readiness.

## Tasks

- fixtures export
- roles locking
- backups
- audit logs
- dashboards
- CSV import/export
- performance tuning
- documentation
- stress testing

## Definition of Done

✅ fresh install works  
✅ zero manual setup  
✅ stable under load  
✅ backups verified  

---

# 🧠 AI / Copilot Usage Instructions

When generating code, ALWAYS:

1. Follow current phase only
2. Generate:
   - .json
   - .py
   - validations
   - permissions
   - workspace items
3. Keep schema normalized
4. Avoid duplication
5. Do not touch ERPNext core

## Copilot Prompt Template

Use:

"Generate Frappe doctypes and controllers for Phase X of ParishMIS following DEVELOPMENT_ROADMAP.md. Follow all architecture rules strictly."

---

# ✅ Development Order Summary

Phase 1 → Structure  
Phase 2 → People  
Phase 3 → Sacraments  
Phase 4 → Finance  
Phase 5 → Portal  
Phase 6 → Hardening  

Never change this order.

---

# End of Spec

