# Deliverable 1: Project definition and Software Requirements Specification

Project: **OriginPass**
Team 1 — Emmanuel Hernández Melo (ehernandem@eafit.edu.co)
Course: ST0251 Proyecto Integrador 1, 2026-2, Universidad EAFIT

This specification follows ISO/IEC/IEEE 29148:2011.

---

## 1. Introduction

### 1.1 Product perspective

OriginPass is a self-contained web application. It is not a component of a larger system and does not require another product to be installed before it can be used. It does, however, sit inside a wider chain of trust that it does not own: the official registries that certify that a company exists, and the certifying bodies that grant denominations of origin. OriginPass consumes the outcome of those processes, in the form of a registry code supplied by the applicant, and does not replace them.

**System interfaces.** The application runs as a Django project served by an application server, backed by a PostgreSQL database. No integration with an external system is required for the product to function. Registry codes are entered by the applicant and reviewed by the administrator rather than validated against an external registry, which is a deliberate limitation recorded in section 1.4.

**User interfaces.** Three interfaces are served from the same application:

- A public interface, reachable without authentication, which handles product verification. This is the interface that receives the most traffic and the one with the least tolerance for friction, since it is opened by a buyer standing in a shop.
- A company interface, for authenticated company accounts, covering application submission, product registration, custody transfers and analytics.
- An administrative interface, for the platform administrator, covering company review, product revocation and the audit log.

All three are rendered server-side with Django templates and styled for screens from 360 pixels wide upwards.

**Hardware interfaces.** The product uses the camera of the buyer's device indirectly: the QR code is read by whatever camera or scanning application the device already provides, and the result is a plain web address. OriginPass therefore requires no hardware access of its own, and no permission prompt.

**Software interfaces.** The application requires a modern web browser on the client side. On the server side it depends on Python 3.12, Django 5, PostgreSQL and a QR generation library. Outbound email is sent through an SMTP provider.

**Communications interfaces.** All traffic is served over HTTPS. Verification addresses are ordinary URLs so that any QR reader can open them.

**Memory.** No unusual memory constraints apply. The largest stored objects are product images, which are bounded by an upload size limit.

**Operations.** The administrator carries out company review and product revocation through the application itself. Database backups and log rotation are operational tasks of the hosting environment rather than functions of the product.

**Site adaptation.** Deployment requires environment-specific configuration: database credentials, the secret key, the mail provider and the allowed host names. No per-site code changes are needed.

### 1.2 Product functions

| Area | Functions |
|---|---|
| Accounts and access | Account creation, login, logout, password reset |
| Company verification | Application submission with two verification tracks, editing while pending or rejected, administrator review, approval, rejection, suspension and reactivation, all negative decisions carrying a written reason |
| Product passports | Product registration by approved companies, generation of a unique passport code, QR image generation and download, listing, searching and editing of the company's own products |
| Public verification | Verification of a product from its passport code with no account, returning one of three verdicts, together with the product data, the company that registered it and the chain of custody |
| Chain of custody | Transfer of custody between accounts, acceptance or refusal by the receiving account, an append-only chronological record, and refusal of transfers that are invalid or that concern a revoked product |
| Verification analytics | Recording of every scan, scan counts over time and by region, ranking of products by scan volume, alerting when one passport code appears in distant regions within a short window, and platform totals for the administrator |
| Revocation and audit | Revocation of a product by its company or by the administrator with a written reason, and an append-only audit log of every status change |
| Notifications | Email on application decisions, on incoming custody transfers and on revocation |

The full specification of these functions is on the [Requirements Specification](Requirements-Specification) page, and their priority and sprint assignment on the [Requirements Prioritisation](Requirements-Prioritisation) page.

### 1.3 User characteristics

| User | Characteristics relevant to design |
|---|---|
| **Buyer** | The widest and least predictable group. No training, no account, no prior knowledge of the product. Often standing in a shop or a market, on a mobile phone, on a slow connection, deciding within seconds. May have limited formal education and may not read English. The verification result must be legible at a glance and expressed in Spanish, in plain words, without relying on colour alone. |
| **Artisan producer** | Frequently operates informally, without a trademark or a registry code. Technical experience varies widely and may be limited to a smartphone. Registration must work without paperwork the producer does not have, and forms must be short. |
| **Commercial company staff** | Works from a desktop, has a registry code available, and is comfortable with business software. Registers products in larger volumes, so listing, searching and bulk entry matter more than for artisans. |
| **Distributor or retailer** | Handles products belonging to others. Interacts with the product mainly through custody transfers, occasionally and under time pressure. Needs the transfer flow to be unambiguous about who currently holds what. |
| **Administrator** | The most technically capable user and the only one who is trained. Reviews applications in batches and needs filtering, context and a record of past decisions. Accountability matters more than speed: every negative decision is written down and can be reviewed later. |

### 1.4 Limitations

**Regulatory policies.** The product stores personal data of registered users and coarse location data of anonymous scans, and therefore falls under Colombian personal data protection law. Scan records keep a coarse geographic region rather than a precise position, and no personal data of anonymous buyers is stored. A denomination of origin is granted by a competent authority; OriginPass records that a company claims one and that an administrator reviewed the claim, and does not itself grant or certify origin.

**Hardware limitations.** Verification depends on the buyer's own device and connection. The verification page is therefore designed to work on a low-end phone over a mobile connection, which constrains page weight and rules out heavy client-side rendering.

**Interfaces to other applications.** Registry codes are not validated against the chamber of commerce or any other external registry, because access to those systems is outside the scope of this project. Verification of a commercial company consequently rests on administrator review of a code supplied by the applicant, not on an automated check.

**Parallel operation.** The product does not need to run alongside an earlier version or another system.

**Audit functions.** Every change of status of a company or a product is written to an append-only audit log with the actor, the reason and the timestamp. Custody transfers, once accepted, are likewise preserved unchanged. Both are constraints on the design, not optional features: a traceability product that can quietly rewrite its own history is worth nothing.

**Control functions.** Only an approved company may register products. Only the current holder may transfer custody. Only the administrator may approve, reject, suspend or reactivate a company.

**Quality requirements.** The verification path is the part of the product that must not fail, since it is used by people the project has no way to contact and no chance to support. It is the simplest path in the system by design, and depends on the smallest number of components.

**Criticality.** A wrong verdict causes real harm in both directions: declaring a counterfeit genuine misleads a buyer into paying for it, and declaring a genuine product counterfeit damages a producer who did nothing wrong. The design favours refusing to answer over guessing, which is why an unmatched code returns Not found rather than an inference.

**Safety and security considerations.** Passport codes must not be guessable from one another, otherwise one leaked code would let a counterfeiter generate valid-looking codes for a whole batch. Passwords are stored as salted one-way hashes. Verification is rate limited to make bulk probing of the code space impractical. Unmatched codes return an identical message so the response cannot be used to map which codes exist.

**Physical and mental considerations.** The verification result is conveyed by a text label as well as a colour, so that it is readable by users who do not distinguish those colours. Forms are reachable by keyboard and text keeps a contrast ratio of at least 4.5 to 1.

---

## 2. Specific requirements

The requirements are maintained on the [Requirements Specification](Requirements-Specification) page so that a single copy stays authoritative. They are summarised here:

| Section | Category | Count | Identifier |
|---|---|---|---|
| 2.1 | Functional requirements | 55 | FR01 – FR55 |
| 2.2 | Usability requirements | 10 | UR01 – UR10 |
| 2.3 | Logical database requirements | 12 | DBR01 – DBR12 |

Each requirement is written with the six-slot template taught in the course, carries a unique identifier, states its priority through `SHALL`, `SHOULD` or `COULD`, and ends with a validation criterion that can be tested.

The Must requirements are recorded as issues in the [project Backlog](https://github.com/users/Pacha-e/projects/1), each with its description, the person responsible and the iteration in which it is developed.

---

## 3. Video

The script, the timing, the walkthrough to record against the running application and the production notes are on the [Deliverable 1 Video](Deliverable-1-Video) page.

Content, in order:

1. Project and team name
2. The problem, who has it, and what it costs them
3. Team members
4. The proposed solution and its value proposition, demonstrated against the running application
5. The ten highest-priority functional requirements, taken from the [Requirements Prioritisation](Requirements-Prioritisation) page

Length: between five and seven minutes.

Link: *to be added once recorded.*

---

## 4. Project management

The project is managed in GitHub at https://github.com/Pacha-e/OriginPass.

| Tool | Use |
|---|---|
| Code | The Django application, with commit messages describing what changed and why |
| Projects (Backlog) | One issue per requirement, carrying its description, responsible person, iteration and status |
| Wiki | Deliverables, weekly records, retrospectives and class activities |

Requirements for Sprint 1 are recorded in the Backlog with their acceptance criteria. Weekly progress is recorded on the [Development Log](Development-Log) page, answering what was done, what comes next and what is blocking. Each sprint closes with an entry on the [Retrospectives](Retrospectives) page covering what to continue, what to start and what to stop.
