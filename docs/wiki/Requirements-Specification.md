# Requirements Specification

Every requirement below is written with the specification template used in the course:

`[condition] THE <system or part> SHALL | SHOULD | COULD <activity> <object> <validation criteria>`

Identifiers are unique within their category: `FR` functional, `UR` usability, `DBR` logical database. Priority follows MoSCoW, where `SHALL` marks a Must, `SHOULD` a Should and `COULD` a Could. The sprint column records the iteration in which the requirement is developed. The reasoning behind the priorities is on the [Requirements Prioritisation](Requirements-Prioritisation) page.

---

## 2.1 Functional requirements

### Account and access management

| ID | Requirement | Priority | Sprint |
|---|---|---|---|
| FR01 | THE OriginPass system SHALL PROVIDE a visitor WITH THE ABILITY TO create an account using an email address and a password, confirming the result within 3 seconds | Must | 1 |
| FR02 | IF a visitor submits a registration form with an email address that is already registered THEN THE OriginPass system SHALL display a message stating that the address is in use, within 2 seconds | Must | 1 |
| FR03 | THE OriginPass system SHALL PROVIDE a registered user WITH THE ABILITY TO log in with an email address and a password, granting access to the account within 3 seconds | Must | 1 |
| FR04 | IF a user submits incorrect credentials during login THEN THE OriginPass system SHALL display an authentication error message that is identical for an unknown email address and for a wrong password, within 2 seconds | Must | 1 |
| FR05 | THE OriginPass system SHALL PROVIDE an authenticated user WITH THE ABILITY TO log out, ending the session within 2 seconds | Must | 1 |
| FR06 | THE OriginPass system SHOULD PROVIDE a registered user WITH THE ABILITY TO request a password reset link delivered to the registered email address, sent within 60 seconds of the request | Should | 4 |

### Company registration and verification

| ID | Requirement | Priority | Sprint |
|---|---|---|---|
| FR07 | THE OriginPass system SHALL PROVIDE an authenticated user WITH THE ABILITY TO submit a company application containing a legal name, a company type, a description, a location and a contact website, stored with the status Pending within 3 seconds | Must | 1 |
| FR08 | IF the applicant selects the commercial company type THEN THE OriginPass system SHALL require an official registry code before accepting the application | Must | 1 |
| FR09 | IF the applicant selects the artisan company type THEN THE OriginPass system SHALL accept the application without an official registry code and mark it for manual review | Must | 1 |
| FR10 | WHILE a company application holds the status Pending or the status Rejected THE OriginPass system SHALL PROVIDE its owner WITH THE ABILITY TO edit and resubmit the application | Must | 1 |
| FR11 | IF a company application holds the status Approved or the status Suspended THEN THE OriginPass system SHALL refuse an edit requested by its owner and display the reason for the refusal | Must | 1 |
| FR12 | THE OriginPass system SHALL PROVIDE the administrator WITH THE ABILITY TO list all company applications filtered by status, returning results within 3 seconds | Must | 1 |
| FR13 | THE OriginPass system SHALL PROVIDE the administrator WITH THE ABILITY TO approve a pending company application, changing its status to Approved within 3 seconds | Must | 1 |
| FR14 | THE OriginPass system SHALL PROVIDE the administrator WITH THE ABILITY TO reject a company application, storing a written reason together with the decision | Must | 1 |
| FR15 | THE OriginPass system SHALL PROVIDE the administrator WITH THE ABILITY TO suspend an approved company, storing a written reason and withdrawing the ability of that company to register products | Should | 4 |
| FR16 | THE OriginPass system SHALL PROVIDE the administrator WITH THE ABILITY TO reactivate a suspended company, restoring the ability of that company to register products | Should | 4 |
| FR17 | THE OriginPass system SHALL display to a company owner the current status of the application together with the reason stored for a rejection or a suspension | Must | 1 |
| FR18 | THE OriginPass system SHOULD display a public profile page for each approved company showing its name, type, location and verification track | Should | 3 |

FR09 and FR18 were extended on 15 October 2026 at the Product Owner's request. An artisan application now also describes the evidence of the craft — how the workshop works, its materials, its workspace and who can vouch for it — which only the reviewer reads, so that a manual review has something to review. Every applicant consents to the public profile of FR18 before applying.

### Product passports

| ID | Requirement | Priority | Sprint |
|---|---|---|---|
| FR19 | IF the requesting company holds the status Approved THEN THE OriginPass system SHALL PROVIDE the company WITH THE ABILITY TO register a product recording its name, description, category, origin and image | Must | 2 |
| FR20 | IF the requesting company holds a status other than Approved THEN THE OriginPass system SHALL refuse the product registration and display the reason for the refusal | Must | 2 |
| FR21 | AFTER a product is registered THE OriginPass system SHALL generate a passport code that is unique across all product records and that cannot be derived from another passport code | Must | 2 |
| FR22 | AFTER a product is registered THE OriginPass system SHALL generate a QR image encoding the public verification address of that product, available for download in PNG format | Must | 2 |
| FR23 | THE OriginPass system SHALL restrict a commercial company to registering products of the commercial type and an artisan company to registering products of the artisan type | Must | 2 |
| FR24 | THE OriginPass system SHALL PROVIDE a company WITH THE ABILITY TO list the products it registered filtered by status, returning results within 3 seconds | Must | 2 |
| FR25 | THE OriginPass system SHOULD PROVIDE a company WITH THE ABILITY TO search the products it registered by name, category or passport code, returning results within 2 seconds | Should | 2 |
| FR26 | THE OriginPass system SHALL PROVIDE a company WITH THE ABILITY TO edit the descriptive fields of a product it registered, leaving the passport code of that product unchanged | Should | 2 |
| FR27 | THE OriginPass system COULD PROVIDE a company WITH THE ABILITY TO register products in bulk from an uploaded CSV file, reporting one outcome per row of the file | Could | 4 |

### Public verification

| ID | Requirement | Priority | Sprint |
|---|---|---|---|
| FR28 | THE OriginPass system SHALL PROVIDE any visitor WITH THE ABILITY TO open the verification page of a product from its passport code without authenticating | Must | 2 |
| FR29 | IF a submitted passport code matches an active product THEN THE OriginPass system SHALL display the verdict Genuine together with the product data and the verified company that registered it, within 3 seconds | Must | 2 |
| FR30 | IF a submitted passport code matches a revoked product THEN THE OriginPass system SHALL display the verdict Revoked together with the date on which the product was revoked | Must | 2 |
| FR31 | IF a submitted passport code matches no product record THEN THE OriginPass system SHALL display the verdict Not found using a message that is identical for every unmatched code | Must | 2 |
| FR32 | THE OriginPass system SHALL display on the verification page the chain of custody of the product in chronological order | Must | 3 |
| FR33 | AFTER a verification page is opened THE OriginPass system SHALL record a scan event storing the timestamp, the coarse geographic region and the device category | Must | 3 |
| FR34 | THE OriginPass system SHOULD limit verification attempts received from a single origin to a defined maximum per minute, answering each attempt beyond that maximum with a wait message | Should | 4 |

### Chain of custody

| ID | Requirement | Priority | Sprint |
|---|---|---|---|
| FR35 | IF a product holds the status Active THEN THE OriginPass system SHALL PROVIDE the current holder of that product WITH THE ABILITY TO transfer custody to another registered account | Must | 3 |
| FR36 | AFTER a custody transfer is initiated THE OriginPass system SHALL PROVIDE the receiving account WITH THE ABILITY TO accept or to decline the transfer | Must | 3 |
| FR37 | AFTER a custody transfer is accepted THE OriginPass system SHALL append the transfer to the chain of custody of the product recording the origin holder, the destination holder and the timestamp | Must | 3 |
| FR38 | IF a custody transfer is requested by an account that is not the current holder of the product THEN THE OriginPass system SHALL refuse the transfer and display the reason for the refusal | Must | 3 |
| FR39 | IF a product holds the status Revoked THEN THE OriginPass system SHALL refuse each custody transfer requested for that product and display the reason for the refusal | Must | 3 |
| FR40 | THE OriginPass system SHOULD PROVIDE a buyer WITH THE ABILITY TO claim final ownership of a product using its passport code together with a transfer code issued by the seller | Should | 3 |

### Revocation and audit

| ID | Requirement | Priority | Sprint |
|---|---|---|---|
| FR41 | THE OriginPass system SHALL PROVIDE the company that registered a product WITH THE ABILITY TO revoke that product, storing a written reason together with the decision | Must | 4 |
| FR42 | THE OriginPass system SHALL PROVIDE the administrator WITH THE ABILITY TO revoke any product, storing a written reason together with the decision | Must | 4 |
| FR43 | AFTER the status of a company or of a product changes THE OriginPass system SHALL append an entry to the audit log recording the actor, the action, the affected record, the stored reason and the timestamp | Must | 4 |
| FR44 | THE OriginPass system SHOULD PROVIDE the administrator WITH THE ABILITY TO list audit log entries filtered by actor, by action or by date range, returning results within 3 seconds | Should | 4 |
| FR45 | THE OriginPass system SHALL keep each audit log entry in the state in which it was written for the retention period defined for the system | Must | 4 |

### Verification analytics

| ID | Requirement | Priority | Sprint |
|---|---|---|---|
| FR46 | THE OriginPass system SHALL display to a company the number of verification scans of its products over a selected date range, rendered within 5 seconds | Must | 3 |
| FR47 | THE OriginPass system SHALL display to a company the distribution of verification scans of its products by geographic region | Must | 3 |
| FR48 | THE OriginPass system SHOULD display to a company the products it registered ranked by number of verification scans | Should | 3 |
| FR49 | IF one passport code is scanned from more than one geographic region within a defined time window THEN THE OriginPass system SHALL raise a duplicate scan alert for the product carrying that code | Must | 3 |
| FR50 | THE OriginPass system SHALL display to the administrator the totals of companies grouped by status and of products grouped by status | Must | 3 |
| FR51 | THE OriginPass system SHOULD PROVIDE a company WITH THE ABILITY TO export the verification analytics of a selected date range as a CSV file | Should | 4 |
| FR52 | THE OriginPass system COULD display to a company the trend of verification scans measured against the preceding period of equal length | Could | 4 |

### Notifications

| ID | Requirement | Priority | Sprint |
|---|---|---|---|
| FR53 | AFTER the administrator approves or rejects a company application THE OriginPass system SHOULD send an email to the applicant stating the decision and the stored reason | Should | 4 |
| FR54 | AFTER a custody transfer is initiated THE OriginPass system SHOULD send an email to the receiving account requesting acceptance of the transfer | Should | 4 |
| FR55 | AFTER a product is revoked THE OriginPass system COULD send an email to the current holder of that product stating the stored reason | Could | 4 |

### Integrity

| ID | Requirement | Priority | Sprint |
|---|---|---|---|
| FR56 | AFTER a day on which any signed record was written THE OriginPass system SHALL publish the head of the integrity chain to a service outside the operator's control, so that a later rebuild of the chain can be shown not to match what was published | Must | 4 |

FR56 was added on 12 August 2026, after the others. Signing and chaining make tampering by anyone holding only the database detectable, but not by whoever runs the server, who holds the signing key as well. Publishing the head of the chain externally is what closes that, and the reasoning is on the [Domain Model](Domain-Model) page.

### Resistance to abuse

| ID | Requirement | Priority | Sprint |
|---|---|---|---|
| FR57 | IF more than 5 failed login attempts are submitted for one email address within 15 minutes THEN THE OriginPass system SHALL refuse each further attempt for that address for 15 minutes, answering with the same authentication error message stated in FR04 | Must | 3 |
| FR58 | THE OriginPass system SHALL record at most 60 verification scans per source address per hour, answering each verification beyond that count with the verdict and without storing a scan record | Should | 3 |

FR57 and FR58 were added on 10 September 2026. Together with FR56 they are the three requirements here that were found by attacking the system rather than by describing it, and each closes a gap the description had left open.

FR57 exists because FR03 and FR04 describe what a correct login and a wrong one do, and neither says what happens when the wrong one is repeated. Passwords are stored as salted hashes under DBR11, so a stolen database does not yield them, but nothing limits how many guesses the login page itself will accept. The refusal answers with the message FR04 already specifies, so a locked address still cannot be told apart from an unknown one.

FR58 exists because the public verification page is the one address in the system that must answer a stranger with no account, and FR28 to FR31 describe what it answers without bounding how often. DBR07 has it store a record of every scan, including the ones that matched no product, which is the signal FR49 needs to notice one code being scanned in two places. Unbounded, that same record is a way for anyone to grow the table at will. The verdict is still answered past the limit; only the record is dropped, because a buyer holding a real product must never be refused an answer.

---

## 2.2 Usability requirements

| ID | Requirement | Priority | Sprint |
|---|---|---|---|
| UR01 | THE OriginPass system SHALL display the verification result of a product on a screen 360 pixels wide with all content reachable by vertical scrolling alone | Must | 2 |
| UR02 | THE OriginPass system SHALL PROVIDE a first-time visitor WITH THE ABILITY TO complete a product verification in at most two interactions counted from the moment the QR code is scanned | Must | 2 |
| UR03 | THE OriginPass system SHALL present the authenticity verdict as a text label accompanying the colour used, so that the verdict is readable by a user who does not distinguish those colours | Must | 2 |
| UR04 | THE OriginPass system SHALL render each interface text in Spanish by default | Must | 2 |
| UR05 | THE OriginPass system COULD PROVIDE a user WITH THE ABILITY TO switch the interface language to English, applying the change within 2 seconds | Could | 4 |
| UR06 | THE OriginPass system SHALL display the verification page within 3 seconds measured over a 3G mobile connection | Must | 2 |
| UR07 | THE OriginPass system SHOULD PROVIDE a keyboard user WITH THE ABILITY TO reach each interactive element of a form using the tab key | Should | 3 |
| UR08 | IF a submitted form is refused THEN THE OriginPass system SHALL display a message stating the cause beside the field that caused the refusal | Must | 1 |
| UR09 | THE OriginPass system SHALL keep a contrast ratio of at least 4.5 to 1 between text and its background on each page | Should | 3 |
| UR10 | THE OriginPass system SHOULD PROVIDE a company owner WITH THE ABILITY TO complete a product registration filling at most five fields marked as required | Should | 2 |

---

## 2.3 Logical database requirements

| ID | Requirement | Priority | Sprint |
|---|---|---|---|
| DBR01 | THE OriginPass database SHALL store one record per company holding its legal name, type, verification track, status, description, location, website and the timestamps of submission and of the last status change | Must | 1 |
| DBR02 | THE OriginPass database SHALL store one record per product holding its passport code, owning company, type, status, descriptive fields and the timestamps of registration and of the last change | Must | 2 |
| DBR03 | THE OriginPass database SHALL enforce uniqueness of the passport code across every product record | Must | 2 |
| DBR04 | THE OriginPass database SHALL enforce that each product record references an existing company record | Must | 2 |
| DBR05 | THE OriginPass database SHALL store one record per custody transfer holding the product, the origin holder, the destination holder, the state of the transfer and its timestamp | Must | 3 |
| DBR06 | AFTER a custody transfer is accepted THE OriginPass database SHALL keep the record of that transfer in the state in which it was written | Must | 3 |
| DBR07 | THE OriginPass database SHALL store one record per verification scan holding the product, the timestamp, the coarse geographic region and the device category | Must | 3 |
| DBR08 | THE OriginPass database SHALL store one record per audit entry holding the actor, the action, the affected record, the stored reason and the timestamp | Must | 4 |
| DBR09 | THE OriginPass database SHALL retain each verification scan record for at least 24 months counted from the date of the scan | Should | 3 |
| DBR10 | THE OriginPass database SHALL provide an index on the passport code allowing a verification lookup to complete within 200 milliseconds over a table holding one million product records | Must | 2 |
| DBR11 | THE OriginPass database SHALL store each password using a one-way hash function with a salt unique to that record | Must | 1 |
| DBR12 | THE OriginPass database SHALL hold the reason text of each rejection, suspension and revocation as a required field of the corresponding record | Must | 1 |

---

## Summary

| Category | Must | Should | Could | Total |
|---|---|---|---|---|
| Functional | 41 | 14 | 3 | 58 |
| Usability | 6 | 3 | 1 | 10 |
| Logical database | 11 | 1 | 0 | 12 |
| **Total** | **58** | **18** | **4** | **80** |

The course template asks for at least 27 functional, 6 usability and 6 logical database requirements for a team of three. This specification covers the product as a whole rather than a target count, and exceeds the largest team size defined in the template.
