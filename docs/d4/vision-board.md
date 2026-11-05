# Product Vision Board validation: OriginPass

Deliverable 4, section 1.1 ("Product Vision Board Validation").

**Source of the proposed content:** `docs/wiki/Product-Vision-Board.md` (current repository version; not compared with an earlier version of the board).

**Status criteria:**
- **VALIDATED:** only with real evidence about the element: interviews, surveys, or real data in the repository.
- **ASSUMED:** any other case.

**Result: 0 VALIDATED, 5 ASSUMED.**

Why no element is VALIDATED:
- The producer interviews (5 to 8 producers) and the buyer survey (30 or more buyers) have not been run: `docs/wiki/Primary-Research-Plan.md:13-15` and `:47-49`; `docs/wiki/Retrospectives.md:36`; `docs/wiki/Sprint-2-Review.md:81`.
- Assumptions A1, A2 and A4 remain open: `docs/wiki/Primary-Research-Plan.md:7-11`.
- A3 has desk research based on public sources (SIC, DIAN, El País): `docs/wiki/Problem-Validation.md:26-63`. The page itself states that this does not validate the board's elements: `docs/wiki/Problem-Validation.md:67-69`.
- The repository contains no real usage data: `git ls-files` lists no `.sql`, `.dump`, `.sqlite3`, `.csv` or `.bak` files.

## Validation by element

| Element | Proposed content for OriginPass | Achievement in the product (implementation) | Evidence (file:line) | Status |
|---|---|---|---|---|
| Vision | Make the origin of any physical product provable, so that buying a genuine product stops depending on trusting the seller. | Partial. Public verification without an account (FR28 to FR31) and one passport per unit (FR21) are implemented. The impact on counterfeiting is not measured in the repository. | `docs/wiki/Product-Vision-Board.md:11`; `verification/views.py:106` (`verify`); `products/tests/test_passport_record.py:99` | ASSUMED |
| Target group | Artisan workshops and informal producers; small and medium manufacturers; distributors and retailers; buyers; platform administrator. | Each group has a flow: company application (FR07 to FR09), verification without an account (FR28), custody (FR35 to FR40), administrative review (FR12 to FR14). | `docs/wiki/Product-Vision-Board.md:15-21`; `docs/wiki/Primary-Research-Plan.md:15` (buyer sample, not run); `:49` (producers, not run) | ASSUMED |
| Needs | Prove that a specific unit was made by a specific producer; verify at the point of sale without an account or app; tell a verified producer apart from someone who only claims to be one; show the product's route; withdraw passports; detect copies. | Covered by FR21 (code per unit), FR28 (no account), FR32 (chain of custody), FR41 and FR42 (withdrawal), FR49 (copy detection). Telling a verified producer apart depends on FR08, FR09 and FR13 (approval). | `docs/wiki/Product-Vision-Board.md:25-32`; `docs/wiki/Problem-Validation.md:67` (A3, partial support); `docs/wiki/Problem-Validation.md:69` (does not validate A1, A2 or A4) | ASSUMED |
| Product | Two verification tracks; one passport per unit; public verification without barriers; chain of custody that is not edited; scan analytics; withdrawal always with a reason. | Implemented: two tracks (`companies/models.py:22`, `VerificationTrack`); one passport per unit (`products/models.py:80`); chain that is not edited (`products/models.py:223-224`; `products/tests/test_custody_transfers.py:113`); duplicate-scan alert (`verification/views.py:133-142`); mandatory reason on revocation (`products/views.py:537`). Note: the QR opens the page that queries the registry; it does not prove the physical authenticity of the object. | `docs/wiki/Product-Vision-Board.md:38-43`; citations in the achievement column | ASSUMED |
| Business Goals | Become the origin registry that artisan sectors in Colombia adopt; protect the commercial value of denominations of origin; turn verification data into an early warning for counterfeiting; keep the cost of joining low. | Not measurable in the repository: there are no users, approved companies or real scans. Analytics data is demo data (see `analitica.md`). Payments are out of scope this semester. | `docs/wiki/Product-Vision-Board.md:47-50`; `docs/wiki/Requirements-Prioritisation.md:103` | ASSUMED |

## Notes

- The "Achievement" column describes implementation, not validation. An implemented element remains ASSUMED until real users confirm it.
- The QR queries the OriginPass registry. It does not prove the physical authenticity of the object.
- Pending for validation: producer interviews, the buyer survey, and the usability sessions described in `usabilidad-protocolo.md`.
