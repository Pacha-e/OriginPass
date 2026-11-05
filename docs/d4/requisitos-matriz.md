# Functional requirements matrix (Deliverable 4, section 1.3)

**Scope:** the 58 functional requirements, FR01 to FR58. Usability requirements (UR01 to UR10) and database requirements (DBR01 to DBR12) are not part of this matrix.

**Origin:**
- **Initial:** FR01 to FR55. Deliverable 1 declares 55 functional requirements in this range (`docs/wiki/Deliverable-1.md`, section 2).
- **New:** FR56, added on 12 August 2026 (`docs/wiki/Requirements-Specification.md:116`). FR57 and FR58, added on 10 September 2026 (`docs/wiki/Requirements-Specification.md:125`).
- **Modified without a new ID:** FR09 and FR18, extended on 15 October 2026 (`docs/wiki/Requirements-Specification.md:41`).

**Responsible:** Emmanuel Hernández, the only team member (`docs/wiki/Team.md`).

**Sprint:** the sprint assigned in `docs/wiki/Requirements-Specification.md`. Five requirements were built by the end of Sprint 3 although planned for Sprint 4: FR06, FR44, FR51, FR52 and FR55 (`docs/wiki/Requirements-Prioritisation.md:90`). They are marked "4 (built by end of S3)".

**Statuses:**

| Status | Definition |
|---|---|
| Implemented and tested | Code is located and a test in the repository cites the FR. The test suite was not run in this session. |
| Implemented without test | Code exists, but no test cites the FR. |
| Partial | Part of the requirement is implemented; another part is missing. |
| Pending | No code, and the repository declares the requirement open. |
| NOT VERIFIED | Could not be checked in code or tests. |

## Matrix

| ID | Description | Priority | Origin | Sprint | Status | Responsible | Evidence (file:line) |
|---|---|---|---|---|---|---|---|
| FR01 | Create an account with email and password | Must | Initial | 1 | Implemented and tested | Emmanuel Hernández | `accounts/views.py:46` (`register`); `accounts/tests/test_registration.py:25` |
| FR02 | Reject registration with an email already in use | Must | Initial | 1 | Implemented and tested | Emmanuel Hernández | `accounts/views.py:46`; `accounts/tests/test_registration.py:50` |
| FR03 | Log in with email and password | Must | Initial | 1 | Implemented and tested | Emmanuel Hernández | `accounts/views.py:63` (`log_in`); `accounts/tests/test_sessions.py:24` |
| FR04 | Identical authentication error for an unknown email and a wrong password | Must | Initial | 1 | Implemented and tested | Emmanuel Hernández | `accounts/forms.py:59` (`LoginForm`); `accounts/tests/test_sessions.py:97` |
| FR05 | Log out | Must | Initial | 1 | Implemented and tested | Emmanuel Hernández | `accounts/views.py:109` (`log_out`); `accounts/tests/test_sessions.py:134` |
| FR06 | Request a password reset link by email | Should | Initial | 4 (built by end of S3) | Implemented and tested | Emmanuel Hernández | `accounts/urls.py:17-24`; `accounts/tests/test_password_reset.py:1` |
| FR07 | Submit a company application (legal name, type, description, location, website) with status Pending | Must | Initial | 1 | Implemented and tested | Emmanuel Hernández | `companies/views.py:35` (`application_create`); `companies/forms.py:21`; `companies/tests/test_application_submission.py:20` |
| FR08 | Require an official registry code from commercial companies | Must | Initial | 1 | Implemented and tested | Emmanuel Hernández | `companies/tests/test_application_submission.py:72`; `companies/views.py:35` |
| FR09 | Accept artisan applications without a registry code, for manual review; consent to the public profile (extended 15 Oct 2026) | Must | Initial | 1 | Implemented and tested | Emmanuel Hernández | `companies/tests/test_application_submission.py:107` and `:137`; `companies/forms.py:133-136` |
| FR10 | Edit and resubmit an application in Pending or Rejected status | Must | Initial | 1 | Implemented and tested | Emmanuel Hernández | `companies/views.py:74` (`application_edit`); `companies/tests/test_application_editing.py:13` |
| FR11 | Refuse edits to Approved or Suspended applications, showing the reason | Must | Initial | 1 | Implemented and tested | Emmanuel Hernández | `companies/views.py:74`; `companies/tests/test_application_editing.py:49` |
| FR12 | Administrator lists applications filtered by status | Must | Initial | 1 | Implemented and tested | Emmanuel Hernández | `companies/views.py:106` (`review_list`); `companies/tests/test_review.py:29` |
| FR13 | Administrator approves a pending application | Must | Initial | 1 | Implemented and tested | Emmanuel Hernández | `companies/views.py:144` (`review_approve`); `companies/tests/test_review.py:80` |
| FR14 | Administrator rejects an application with a written reason | Must | Initial | 1 | Implemented and tested | Emmanuel Hernández | `companies/views.py:165` (`review_reject`); `companies/forms.py:142` (`RejectionForm`); `companies/tests/test_review.py:111` |
| FR15 | Administrator suspends an approved company with a reason | Should | Initial | 4 | Implemented and tested | Emmanuel Hernández | `companies/views.py:191` (`suspend_company`); `companies/forms.py:158` (`SuspensionForm`); `companies/tests/test_suspension_and_profile.py:1` |
| FR16 | Administrator reactivates a suspended company | Should | Initial | 4 | Implemented and tested | Emmanuel Hernández | `companies/views.py:213` (`reactivate_company`); `companies/tests/test_suspension_and_profile.py:1` |
| FR17 | The owner sees the application status and the reason for a rejection or suspension | Must | Initial | 1 | Implemented and tested | Emmanuel Hernández | `companies/views.py:26` (`application_detail`); `companies/tests/test_application_status.py:10` |
| FR18 | Public profile for each approved company (extended 15 Oct 2026) | Should | Initial | 3 | Implemented and tested | Emmanuel Hernández | `companies/views.py:228` (`public_profile`); `companies/urls.py:17`; `companies/tests/test_suspension_and_profile.py:1` |
| FR19 | An approved company registers a product (name, description, category, origin, image) | Must | Initial | 2 | Implemented and tested | Emmanuel Hernández | `products/views.py:116` (`product_create`); `products/tests/test_registration.py:25` |
| FR20 | Refuse product registration from a company that is not approved, with a reason | Must | Initial | 2 | Implemented and tested | Emmanuel Hernández | `products/views.py:68` (`_refuse`); `products/tests/test_registration.py:93` |
| FR21 | Generate a unique passport code that cannot be derived from another | Must | Initial | 2 | Implemented and tested | Emmanuel Hernández | `products/models.py:51` (`generate_passport_code`); `products/models.py:84`; `products/tests/test_passport_record.py:99` |
| FR22 | Generate a downloadable PNG QR encoding the verification address | Must | Initial | 2 | Implemented and tested | Emmanuel Hernández | `products/views.py:236` (`qr_download`); `products/tests/test_qr_code.py:1` |
| FR23 | Restrict product type according to company type | Must | Initial | 2 | Implemented and tested | Emmanuel Hernández | `products/tests/test_passport_record.py:120`; `products/views.py:116` |
| FR24 | List own products filtered by status, within 3 s | Must | Initial | 2 | Implemented and tested | Emmanuel Hernández | `products/views.py:79` (`product_list`); `products/tests/test_catalogue.py:27` and `:81` |
| FR25 | Search own products by name, category or passport code | Should | Initial | 2 | Implemented and tested | Emmanuel Hernández | `products/views.py:79`; `products/tests/test_catalogue.py:27` |
| FR26 | Edit descriptive fields without changing the product's passport code | Should | Initial | 2 | Implemented and tested | Emmanuel Hernández | `products/views.py:190` (`product_edit`); `products/tests/test_catalogue.py:89` |
| FR27 | Bulk product registration from a CSV file | Could | Initial | 4 | Pending | Emmanuel Hernández | No code: `products/views.py` has no import view; `docs/wiki/Requirements-Prioritisation.md:81` and `:90` |
| FR28 | Open the verification page without authenticating | Must | Initial | 2 | Implemented and tested | Emmanuel Hernández | `verification/views.py:106` (`verify`); `verification/tests/test_verdicts.py:43` |
| FR29 | Verdict Genuine with product and verified company data | Must | Initial | 2 | Implemented and tested | Emmanuel Hernández | `verification/views.py:106`; `verification/tests/test_verdicts.py:64` |
| FR30 | Verdict Revoked with the revocation date | Must | Initial | 2 | Implemented and tested | Emmanuel Hernández | `verification/views.py:106`; `verification/tests/test_verdicts.py:92` |
| FR31 | Verdict Not found with an identical message for every unmatched code | Must | Initial | 2 | Implemented and tested | Emmanuel Hernández | `verification/views.py:106`; `verification/tests/test_verdicts.py:119` |
| FR32 | Show the chain of custody in chronological order on the verification page | Must | Initial | 3 | Implemented and tested | Emmanuel Hernández | `verification/views.py:185` (`_public_chain`); `verification/tests/test_public_chain.py:1` |
| FR33 | Record a scan event with timestamp, coarse region and device category | Must | Initial | 3 | Implemented and tested | Emmanuel Hernández | `verification/models.py:27-41` (`ScanEvent`); `verification/views.py:45` (`_device_category`) and `:67` (`_region_for`); `verification/tests/test_public_chain.py:1` |
| FR34 | Limit verification attempts per origin to a maximum per minute, with a wait message | Should | Initial | 4 | Pending | Emmanuel Hernández | No code: `verification/views.py:37` and `:42` define only a 24 h window and a cap of 60 per hour; `docs/wiki/Requirements-Prioritisation.md:87` and `:90` |
| FR35 | The current holder transfers custody to another registered account | Must | Initial | 3 | Implemented and tested | Emmanuel Hernández | `products/views.py:284` (`transfer_initiate`); `products/models.py:184` (`current_holder`); `products/tests/test_custody_transfers.py:46` |
| FR36 | The receiving account accepts or declines the transfer | Must | Initial | 3 | Implemented and tested | Emmanuel Hernández | `products/views.py:343` (`transfer_respond`); `products/models.py:385` (`accept`) and `:388` (`decline`); `products/tests/test_custody_transfers.py:113` |
| FR37 | An accepted transfer is appended to the chain of custody | Must | Initial | 3 | Implemented and tested | Emmanuel Hernández | `products/models.py:223` (`CustodyTransfer`); `products/models.py:305` (`_append`); `products/tests/test_custody_transfers.py:113` |
| FR38 | Refuse a transfer requested by an account that is not the holder, with a reason | Must | Initial | 3 | Implemented and tested | Emmanuel Hernández | `products/views.py:284`; `products/tests/test_custody_transfers.py:69` |
| FR39 | Refuse a transfer of a revoked product, with a reason | Must | Initial | 3 | Implemented and tested | Emmanuel Hernández | `products/views.py:284`; `products/tests/test_custody_transfers.py:69` |
| FR40 | Claim final ownership with a passport code and a transfer code | Should | Initial | 3 | Implemented and tested | Emmanuel Hernández | `products/views.py:380` (`transfer_claim`); `products/tests/test_custody_transfers.py:163` |
| FR41 | The company revokes its product with a written reason | Must | Initial | 4 | Implemented and tested | Emmanuel Hernández | `products/models.py:193` (`revoke`); `products/views.py:546` (`product_revoke`); `products/tests/test_revocation.py:1` |
| FR42 | The administrator revokes any product with a written reason | Must | Initial | 4 | Implemented and tested | Emmanuel Hernández | `products/views.py:576` (`admin_revoke_product`); `products/admin.py:17`; `products/tests/test_revocation.py:1` |
| FR43 | Audit entry when the status of a company or product changes | Must | Initial | 4 | Implemented and tested | Emmanuel Hernández | `audit/models.py:35` (`AuditEntry`); `audit/tests/test_status_changes.py:8` |
| FR44 | Administrator lists audit entries filtered by actor, action or date (built by end of S3) | Should | Initial | 4 (built by end of S3) | Implemented and tested | Emmanuel Hernández | `audit/views.py:23` (`audit_log`); `audit/tests/test_log_view.py:1` |
| FR45 | Keep each audit entry unchanged for the retention period | Must | Initial | 4 | Partial | Emmanuel Hernández | `audit/models.py:84-86` (`save` refuses edits: "append-only"). The application code defines no retention policy. |
| FR46 | Number of scans of the company's products over a date range, within 5 s | Must | Initial | 3 | Implemented and tested | Emmanuel Hernández | `products/views.py:417-431` (`company_analytics`); `products/tests/test_analytics.py:1` |
| FR47 | Distribution of scans of the company's products by region | Must | Initial | 3 | Implemented and tested | Emmanuel Hernández | `products/views.py:441-443`; `products/tests/test_analytics.py:1` |
| FR48 | Ranking of products by number of scans | Should | Initial | 3 | Implemented and tested | Emmanuel Hernández | `products/views.py:444-448`; `products/tests/test_analytics.py:1` |
| FR49 | Duplicate-scan alert when a code is scanned in more than one region within the defined window | Must | Initial | 3 | Implemented and tested | Emmanuel Hernández | `verification/views.py:37` (24 h window), `:133-142` (`Alert.objects.get_or_create`); `verification/tests/test_public_chain.py:54-58`; `products/views.py:449-453` |
| FR50 | Totals of companies and products grouped by status, for the administrator | Must | Initial | 3 | Implemented and tested | Emmanuel Hernández | `products/views.py:607` (`admin_overview`); `products/tests/test_revocation.py:1` |
| FR51 | Export the analytics for the selected range as CSV (built by end of S3) | Should | Initial | 4 (built by end of S3) | Implemented and tested | Emmanuel Hernández | `products/views.py:498` (`company_analytics_csv`), `:491` (`_csv_cell`); `products/tests/test_analytics.py:58` |
| FR52 | Scan trend against the preceding period of equal length (built by end of S3) | Could | Initial | 4 (built by end of S3) | Implemented and tested | Emmanuel Hernández | `products/views.py:431-433` and `:465-467`; `products/tests/test_analytics.py:34` |
| FR53 | Email the applicant the decision and the stored reason | Should | Initial | 4 | Implemented and tested | Emmanuel Hernández | `accounts/emails.py:35` (`notify_company_decision`); `companies/tests/test_decision_email.py:1` |
| FR54 | Email the receiving account when a transfer starts | Should | Initial | 4 | Implemented and tested | Emmanuel Hernández | `accounts/emails.py:55` (`notify_transfer`); `products/tests/test_custody_transfers.py:46` |
| FR55 | Email the current holder when a product is revoked, with the reason (built by end of S3) | Could | Initial | 4 (built by end of S3) | Implemented and tested | Emmanuel Hernández | `products/views.py:541` (call); `accounts/emails.py:68` (`notify_revocation`); `products/tests/test_custody_transfers.py:1` |
| FR56 | Publish the integrity chain head to a service outside the operator's control (new, 12 Aug 2026) | Must | New (12 Aug 2026) | 4 | Partial | Emmanuel Hernández | Signing and chaining: `audit/integrity.py:1-11`. External publication not implemented: `audit/integrity.py:20-23`; `audit/management/commands/verify_integrity.py:102` |
| FR57 | Block an email address for 15 min after more than 5 failed logins within 15 min, with the FR04 message (new, 10 Sep 2026) | Must | New (10 Sep 2026) | 3 | Implemented and tested | Emmanuel Hernández | `accounts/models.py:71` (`LoginAttempt`); `accounts/tests/test_login_throttle.py:1` |
| FR58 | Store at most 60 scan records per source address per hour; verdicts are still answered (new, 10 Sep 2026) | Should | New (10 Sep 2026) | 3 | Implemented and tested | Emmanuel Hernández | `verification/views.py:42` (`SCAN_CAP_PER_HOUR = 60`), `:88` (`_under_scan_cap`); `verification/tests/test_public_chain.py:2` |

## Count by status

| Status | Count | IDs |
|---|---|---|
| Implemented and tested | 54 | FR01 to FR26; FR28 to FR33; FR35 to FR44; FR46 to FR55; FR57 and FR58 |
| Implemented without test | 0 | — |
| Partial | 2 | FR45, FR56 |
| Pending | 2 | FR27, FR34 |
| NOT VERIFIED | 0 | — |
| **Total** | **58** | |

Mapping to the template's "Developed (Yes / No)": Yes = 54. No = 4 (2 pending and 2 partial). The decision on the partial items rests with the instructor.

## Notes

- **Test execution:** the test suite was not run in this session. "Implemented and tested" means a test in the repository cites the FR. It does not mean the test passes today.
- **Pending items:** FR27 and FR34 have no code. `docs/wiki/Requirements-Prioritisation.md:87` and `:90` list them as open.
- **FR45:** immutability of entries exists (`audit/models.py:84-86`). The retention period is not defined in code.
- **FR56:** the repository states that external publication "is not implemented here" (`audit/integrity.py:23`).
- **QR (FR22 and FR28 to FR31):** the QR opens the page that queries the registry. It does not prove the physical authenticity of the object.
- **Out of this matrix:** the audit baseline (`/d/OriginPass-D4-orq/auditoria/baseline-inventario.md`) does not exist; the `auditoria/` directory is empty. It was not used.
