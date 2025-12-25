# ParishMIS  
**Catholic Parish Management Information System for Frappe / ERPNext**

ParishMIS is a comprehensive Church Management System built on the **Frappe Framework** and **ERPNext**, designed to support Catholic parishes and dioceses in managing parishioners, church structures, SCCs, sacraments, events, and collections — including **M-Pesa (Daraja API) integration** for digital giving.

---

## ✝️ Purpose

ParishMIS provides a unified, secure, and scalable platform to manage:

- Church administrative hierarchy
- Parishioner and family records
- Small Christian Communities (SCCs)
- Sacraments and certificates
- Events and attendance
- Collections and offerings
- M-Pesa online giving
- Parishioner self-service portal

The system is designed to work at **Parish and Diocese level**, supporting multiple parishes per installation.

---

## 🏛️ Church Hierarchy Supported

Diocese
└── Parish
└── Sub-Parish
└── Church / Outstation
└── SCC (Small Christian Community)


This hierarchy is enforced through linked DocTypes and business rules.

---

## ⚙️ Technology Stack

| Component | Technology |
|----------|------------|
| Framework | Frappe Framework (Python) |
| ERP Base | ERPNext |
| Database | MariaDB 10.x |
| Frontend | Frappe Desk + Web Portal |
| Background Jobs | Redis + Frappe Workers |
| Payments | Safaricom Daraja API (M-Pesa) |
| Web Server | Nginx |
| OS | Ubuntu 22.04 LTS |
| Version Control | Git |

---

## 📦 Core Modules

### 1. Parish Management
- Diocese
- Parish
- Sub-Parish
- Church / Outstation

### 2. Parishioner Management
- Individual parishioner records
- Family linking
- SCC / Church / Association membership
- Transfer history
- Portal user linking

### 3. Family Management
- Household grouping
- Head of family
- Family-level participation and contributions

### 4. SCC Management
- SCC registration under churches
- Membership and leadership roles
- Meeting tracking (future phase)

### 5. Sacrament Management
- Baptism
- Confirmation
- Marriage
- Certificate printing
- Priest assignment

### 6. Events
- Parish and SCC events
- Attendance tracking

### 7. Finance & Collections
- Offertory, tithe, donations
- Cash, bank, and M-Pesa payments
- Collection categorization
- ERPNext accounting integration

### 8. M-Pesa Integration
- STK Push (Lipa na M-Pesa Online)
- Automatic callback handling
- Transaction reconciliation
- Secure credential storage

### 9. Parishioner Portal
- View profile and family
- Contribution history
- Initiate M-Pesa payments
- View sacraments and announcements

---

## 🧱 Key DocTypes

| Doctype | Description |
|-------|-------------|
| Diocese | Top-level church authority |
| Parish | Administrative parish unit |
| Sub-Parish | Sub-division of a parish |
| Church | Parish church or outstation |
| Parishioner | Individual member |
| Family | Household grouping |
| SCC | Small Christian Community |
| SCC Member | Parishioner–SCC mapping |
| Sacrament Type | Sacrament definitions |
| Sacrament Record | Sacrament administration |
| Collection Type | Offering categories |
| Collection Record | Financial contribution |
| M-Pesa Transaction | Payment gateway logs |
| Event | Parish or SCC event |

---

## 🔐 Roles & Permissions

| Role | Access Scope |
|----|-------------|
| System Manager | Full system access |
| Parish Admin | Parish-level management |
| Finance Officer | Collections & payments |
| Priest | Sacraments & parishioners |
| SCC Leader | SCC membership |
| Parishioner | Portal access only |

Permissions are enforced using standard Frappe Role-based Access Control.

---

## 💳 M-Pesa Configuration

Credentials are stored securely in `site_config.json`:

```json
{
  "mpesa_consumer_key": "xxxx",
  "mpesa_consumer_secret": "xxxx",
  "mpesa_shortcode": "xxxx",
  "mpesa_passkey": "xxxx",
  "mpesa_callback_url": "https://yourdomain/api/method/..."
}

Only M-Pesa payments can be initiated from the portal.
Cash and bank payments are recorded by authorized staff.
🚀 Installation
Prerequisites

    Frappe Framework (v14+)

    ERPNext installed

    Bench CLI

Install App

bench get-app parishmis https://github.com/your-org/parishmis.git
bench --site parish.local install-app parishmis

Apply Updates

bench update --patch

🧰 Developer Guidelines

    Follow standard Frappe app structure

    No ERPNext core modifications

    Use fixtures for:

        Roles

        Sacrament Types

        Collection Types

    Add schema changes via patches

    Maintain backward compatibility

🛡️ Security & Compliance

    HTTPS enforced

    Role-based access

    Audit logs enabled

    Daily backups recommended

    Designed to comply with Kenya Data Protection Act, 2019

📊 Reporting (Planned & Implemented)

    Parishioner demographics

    Family contributions

    SCC participation

    Sacrament statistics

    Collection summaries

    M-Pesa reconciliation reports

🌍 Localization

    English (default)

    Swahili (planned)

📜 License

MIT License
© 2025 – ParishMIS Contributors
🤝 Contributions

Contributions are welcome.
Please fork the repository, create a feature branch, and submit a pull request.
🙏 Acknowledgements

Built with:

    Frappe Framework

    ERPNext

    Safaricom Daraja API

For the service of the Church.


---

### ✅ Next Logical Steps
1. Commit this README to GitHub  
2. Add **fixtures** for:
   - Roles
   - Sacrament Types
   - Collection Types  
3. Proceed to **SCC & SCC Member DocTypes**  
4. Then **Family → Sacraments → Collections**

If you want, I can next:
- Review this README for public/open-source release, **or**
- Generate **fixtures JSON** for initial church setup (roles, sacraments, associations).