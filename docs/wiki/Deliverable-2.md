# Deliverable 2: Solution design and functionality preview

**Course:** ST0251 Proyecto Integrador 1, 2026-2
**Team 1 — OriginPass.** Emmanuel Hernández Melo, carried out individually.
**Sprint covered:** Sprint 2, 12 August to 8 September 2026.

Sprint 2 is the sprint in which OriginPass first does the thing it exists to do: an approved company registers a product and gets a QR code for it, and any buyer scans that code and reads a verdict without an account.

---

## 1. Architecture and data

The three diagrams are drawn in draw.io and kept in the repository under [`docs/diagrams/`](https://github.com/Pacha-e/OriginPass/tree/main/docs/diagrams), so that they are versioned alongside the code they describe rather than living only as images.

Every version and every column name in them was read from what is installed and running, not from the plan and not from the file that states what is acceptable: `pip list` and the image tags in `docker-compose.yml` for the deployment model, `views.py` and `urls.py` for the component model, and the running database itself, through `manage.py describe_schema`, for the data model.

A WSGI server belongs on the application server and there is not one yet. Sprint 4 is where the course covers deployment and it is the sprint that adds it; naming one here before it exists would describe a system that does not run.

Colour carries the same meaning in all three: blue for what Sprint 1 delivered, green for what Sprint 2 delivered, purple for what has a model but no views yet.

### 1.1. Deployment diagram

Source: [`docs/diagrams/deployment-model.drawio`](https://github.com/Pacha-e/OriginPass/blob/main/docs/diagrams/deployment-model.drawio)

The nodes the system runs on, the software installed on each with its version, and the protocol between them.

| Node | Software | Talks to |
|---|---|---|
| Buyer's phone | Any browser, a camera that reads QR codes | Application server over HTTPS |
| Company or administrator workstation | Any browser | Application server over HTTPS |
| Application server | Python 3.12, Django 5.2, and the development server Django ships | Database server over TCP 5432 |
| Database server | PostgreSQL 17 | — |

The buyer's device is drawn as a node of its own because it is the only one outside the operator's control, and the requirement that shapes the whole verification page, UR06, is a property of the link to it rather than of the server.

### 1.2. Component diagram

Source: [`docs/diagrams/components-model.drawio`](https://github.com/Pacha-e/OriginPass/blob/main/docs/diagrams/components-model.drawio)

One component per Django app, the functions each provides, and the dependencies between them.

| Component | What it provides | Depends on |
|---|---|---|
| `accounts` | Registration, session start and end, the role each account holds, and the administrator check the other components use | — |
| `companies` | The company application, its four states and the transitions between them, and the administrator's review | `accounts`, `audit` |
| `products` | The passport for one physical unit, its generated code, the QR image, and the chain of custody | `companies`, `audit` |
| `verification` | The public verdict page and the scan record behind it | `products` |
| `audit` | The append-only, signed and chained trail every state change writes to | `accounts` |
| `pages` | The landing page | — |
| `config` | Settings, root URLs and the WSGI and ASGI entry points | all of the above |

The dependencies run one way. `verification` knows about `products` because a verdict is about a passport; `products` does not know that a public page exists, which is what lets the verification page be replaced without touching the passport.

### 1.3. Data model

Source: [`docs/diagrams/data-model.drawio`](https://github.com/Pacha-e/OriginPass/blob/main/docs/diagrams/data-model.drawio)

Six tables, their columns and types, the foreign keys with their cardinality, and the check constraints.

| Table | Holds | Key relationships |
|---|---|---|
| `accounts_user` | One row per account: email, hashed password, role | One-to-one with a company, when it has one |
| `companies_company` | One row per company that has applied, whatever the outcome | Owned by one user; protects its products |
| `products_product` | One row per physical unit, with its unique passport code | Belongs to one company |
| `products_custodytransfer` | One row per handover, appended and never edited | Belongs to one product, links two users |
| `verification_scanevent` | One row per verification, including the ones that matched nothing | Optionally belongs to one product |
| `audit_auditentry` | One row per state change of a company or a product | Written by one user |

Five rules the requirements state about data are enforced twice: once in the model, so the application refuses the operation with a message a person can read, and once as a database constraint, so the rule holds even if a future view forgets it.

| Constraint | What it refuses |
|---|---|
| `company_track_matches_type` | A commercial company on the artisan track, or the reverse |
| `commercial_company_has_registry_code` | A commercial company with no registry code |
| `negative_decision_states_a_reason` | A rejection or a suspension with no reason recorded |
| `revocation_states_a_reason` | A revoked passport with no reason recorded |
| `custody_transfer_changes_holder` | A handover from a holder to themselves |

---

## 2. Mockups

Source: [`docs/diagrams/mockups.drawio`](https://github.com/Pacha-e/OriginPass/blob/main/docs/diagrams/mockups.drawio)

Six frames, drawn as wireframes rather than as a copy of the rendered pages: what the deliverable asks for is the structure and the interaction, not the styling. The last frame draws the verification verdict at 360 pixels, because UR01 is a requirement about that width specifically and a desktop frame cannot show it.

The views the Sprint 2 requirements are reflected in, and what each one has to answer:

| View | Main content groups | Structure | Interaction |
|---|---|---|---|
| Product registration (FR19, UR10) | Five fields and one action | One column, one card | Submit; a refusal is shown beside the field that caused it |
| Registration refused (FR20) | The cause, the company's status, the way back | One column, one card, one notice | Read-only; two links out |
| A company's products (FR24, FR25) | Status filter, search, table of passports | Filter row, search row, table | Filter and search are two independent GET parameters that combine |
| Passport detail (FR22) | The code, the QR, the public address | One card of detail, one row of actions | Download the QR as a PNG |
| Public verdict (FR28–FR31, UR01–UR03) | The verdict, then the product, then what the verdict means | One column, verdict first | None: the page is the answer to the scan |

The public verdict view is the one that carries the usability requirements, because it is the only page a stranger reaches: it fits a 360 pixel screen (UR01), it is reached in one interaction from the scan (UR02), and it states the verdict in words and not only in colour (UR03).

That last point is the one a wireframe shows better than a screenshot. The verdict is a word before it is a colour, so a reader who does not distinguish green from red gets the same answer as everyone else. The suite asserts both the word and the class that carries the colour, so neither can be removed on the assumption that the other is enough.

---

## 3. Repository

**Repository:** https://github.com/Pacha-e/OriginPass

The project is carried out individually, so every commit is by Emmanuel Hernández Melo. Each commit message states what changed and why, in the imperative, with the reasoning in the body where the change needed one.

**Dependencies.** [`requirements.txt`](https://github.com/Pacha-e/OriginPass/blob/main/requirements.txt) lists every library needed to run the program; [`requirements-dev.txt`](https://github.com/Pacha-e/OriginPass/blob/main/requirements-dev.txt) adds the linter, pinned, so that a release of the linter cannot turn a build red without the project changing.

**Instructions for running it** are in the [README](https://github.com/Pacha-e/OriginPass/blob/main/README.md), including the database, the environment file, the migrations, the translation catalogue and the demo dataset.

### The demo data, and how it is made

The demo dataset is a management command, [`seed_demo`](https://github.com/Pacha-e/OriginPass/blob/main/companies/management/commands/seed_demo.py), rather than a SQL dump or rows typed in by hand. That matters for three reasons: it is readable, it is versioned with the code, and it goes through the same model rules the application does, so it cannot create a row the application would refuse.

```bash
docker compose up -d db          # PostgreSQL 17 on localhost:5432
python manage.py migrate
python manage.py seed_demo       # prints every passport code and its verification path
python manage.py runserver
```

It creates:

| What | How many | Why |
|---|---|---|
| Administrator | 1 | The account that reviews applications |
| Company applications | 5 | One in each of the four states, so every branch of the review has a case |
| Passports | 4 | Issued by the two approved companies, one of them revoked so that verdict can be shown |
| Scan history | 14 | So the verification page and the Sprint 3 analytics have something to read |

The product type is never written into the data. It is derived from the company that issues the passport, exactly as the registration view derives it, so a seeded row cannot hold the crossed pair FR23 forbids. A test asserts that for every row the command writes.

Every account it creates shares one known password, which it prints, so the command refuses to run with `DEBUG` off unless it is forced.

**Looking at the database itself.** It is PostgreSQL 17 on `localhost:5432`, so any client opens it — the five check constraints are visible there under their own names, which is where the rules that the requirements state about data are enforced a second time:

```bash
docker compose exec db psql -U originpass -d originpass -c "\d+ companies_company"
```

`python manage.py verify_integrity` walks the signed and chained records and names the first one that does not hold up.

**Continuous integration** runs on every push and every pull request: the migration check, the test suite against a real PostgreSQL 17 service, the linter and the formatter.

```
Ran 179 tests in 77.723s
OK
```

---

## 4. Video

_To be attached: the link, once recorded._

Length 4 to 5 minutes, structured as the template asks:

| Part | Length | Contents |
|---|---|---|
| Pitch | 1:00 | Team, project name, problem, solution, where the project is and where it is going |
| Requirements addressed | 2:00 | The twenty-two requirements of Sprint 2, explained rather than read |
| Evidence of compliance | 2:00 | The working application: registering a product, getting its QR, scanning it, and the three verdicts |

---

## 5. Project management

**Weekly record.** [Development Log](Development-Log) — written for each week, including the two weeks of this sprint in which nothing was committed, because that gap is the fact worth recording.

**Sprint retrospective.** [Retrospectives](Retrospectives) — Sprint 2 answers what to continue, what to start and what to stop.

**Sprint review.** [Sprint 2 Review](Sprint-2-Review) — what was committed, what was delivered, how each requirement was verified, and the decisions taken during the sprint.

**Class assignments.** [Activities and Homeworks](Activities-and-Homeworks).

**Requirements with their status, sprint and responsible.** The [Backlog](https://github.com/users/Pacha-e/projects/1) holds one issue per requirement, numbered so that issue N is requirement N. Each carries its sprint, its MoSCoW priority and its kind as labels. The full specification is on the [Requirements Specification](Requirements-Specification) page and the prioritisation that assigned each one to a sprint is on [Requirements Prioritisation](Requirements-Prioritisation).

| Sprint | Requirements | Status |
|---|---|---|
| 1 | 18 | Delivered, 11 August 2026 |
| 2 | 22 | Delivered, verified by 179 automated tests |
| 3 | see the backlog | Planned |
| 4 | see the backlog | Planned |

Responsible for all of them: Emmanuel Hernández Melo.
