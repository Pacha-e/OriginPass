# Sprint 2 review — demo runbook

Local notes, not a project artefact. Not tracked.

The point of this file is that nothing in the live demo is decided on the spot.

---

## Pre-flight, 15 minutes before

Run these in order. Each line says what you should see, so you find out here rather than in front of the class.

```bash
cd "D:/Universidad/Proyecto integrador 1/OriginPass"

docker compose up -d db
# expect: Container originpass-db  Started   (and "healthy" within ~10s)

docker compose ps
# expect: STATUS = Up (healthy), PORTS = 0.0.0.0:5432->5432/tcp
```

```bash
.venv/Scripts/python.exe manage.py migrate
# expect: "No migrations to apply." or a list ending in OK
```

```bash
.venv/Scripts/python.exe manage.py seed_demo
# expect: 5 companies, then 4 passports, each printed with its /v/<code> path
# COPY THE PASSPORT PATHS SOMEWHERE. You will need one of them live.
```

If `seed_demo` says "skipped … already present", the data is already there — fine, but you need
the codes. Get them with:

```bash
.venv/Scripts/python.exe manage.py shell
>>> from products.models import Product
>>> for p in Product.objects.all(): print(p.status, p.name, "/v/" + p.passport_code)
```

```bash
.venv/Scripts/python.exe manage.py runserver
# expect: Starting development server at http://127.0.0.1:8000/
```

**Open in tabs, in this order, before you start talking:**

1. `http://127.0.0.1:8000/` — the landing page
2. `http://127.0.0.1:8000/v/<code-of-an-ACTIVE-product>` — the Genuine verdict
3. `http://127.0.0.1:8000/v/<code-of-the-REVOKED-product>` — the Revoked verdict
4. `http://127.0.0.1:8000/v/nothing-here` — the Not found verdict
5. `http://127.0.0.1:8000/admin/` — logged in as the administrator
6. The repository's Actions tab, on the green run
7. The wiki's Sprint 2 Review page

Log in beforehand. Do not type a password in front of the room.

**Accounts** (all share the password `seed_demo` prints):

| Who | Email |
|---|---|
| Administrator | `admin@originpass.co` |
| Approved commercial company | `contacto@labonga.co` |
| Approved artisan workshop | `taller@tuchin.co` |
| Pending | `info@mochilaswayuu.co` |
| Rejected | `ventas@importadoraandina.co` |
| Suspended | `contacto@ceramicaraquira.co` |

---

## The demo, in the order it should be told

Roughly seven minutes. The order is: the thing it exists to do first, the machinery second.
Do not start with the admin panel.

### 1 · What a buyer sees (2 min) — FR28, FR29, FR30, FR31, UR01–UR04

Start on tab 2, the Genuine verdict, **and make the browser window narrow first**. UR01 is
about a 360 pixel screen; showing it at desktop width throws the requirement away.

Say: *this page is the product. No account, one request from the scanned code, and the verdict
is a word before it is a colour.*

Then tab 3 (Revoked) and tab 4 (Not found), quickly. The point of tab 4: **every unmatched code
gets the same page**, because telling one kind of miss from another would leak which codes are live.

### 2 · Where the code comes from (2 min) — FR19, FR21, FR22, FR23, UR10

Log in as `taller@tuchin.co` → My products → Register a product.

Say while the form is open: *five fields. The product type is not one of them — it follows from
the company, so a workshop cannot issue a commercial original by mistake. The passport code is not
one of them either; it is generated from a cryptographically secure source, so holding one valid
code does not let you guess another.*

Submit it. On the detail page, download the QR. **Scan it with your own phone** — the QR encodes
the verification address, so the phone lands on the page from step 1. That is the whole loop, live.

### 3 · The database (2 min) — this is what was asked for

Two ways. Use the second if the projector makes a terminal unreadable.

```bash
docker compose exec db psql -U originpass -d originpass
\dt                          -- the tables
\d+ companies_company        -- columns, types, and the CHECK constraints by name
select action, target_type, target_id, left(entry_hash, 12) from audit_auditentry order by id;
```

Point at the constraint names in the `\d+` output and say: *the rules the requirements state about
data are enforced twice — once in the model so a person gets a message they can read, and once here
so the rule holds even if a future view forgets it.*

Or use the Django admin (tab 5) if a GUI reads better.

### 4 · How the demo data is made (1 min) — this is what was asked for

Open `companies/management/commands/seed_demo.py`.

Say: *the demo data is a command, not a SQL dump and not rows typed by hand. It goes through the
same model rules the application does, so it cannot create a row the application would refuse. The
product type is derived from the company here exactly as the registration view derives it — and a
test asserts that for every row this command writes.*

Scroll to `PASSPORTS`. Point out the one with `revoked` — *that is why there is a revoked verdict
to show you.*

### 5 · That it works (1 min)

Tab 6, the green CI run. Say: *185 tests against a real PostgreSQL 17, not a substitute engine.
Where a requirement states a time bound the test measures it instead of assuming it.*

If asked for the number: Sprint 1 ended with 80.

---

## If something breaks

| Symptom | Do this |
|---|---|
| `docker compose` errors or hangs | The engine died once already this week. `wsl --shutdown`, reopen Docker Desktop. **If it will not come back, do not fight it live** — go to tab 6 and demo from the green CI run and the wiki instead. |
| The page renders in English | The `.mo` is missing. It is a build artefact. Say so: the source strings are English, `locale/es` is what a visitor reads, and CI compiles it before the tests. Do not debug it live. |
| `seed_demo` refuses to run | It needs `DEBUG` on. Check `.env`. |
| A passport code 404s | You copied a code from a previous seed. Re-read them with the shell snippet above. |

---

## Questions you will be asked, and honest answers

The first three have no good answer. Do not invent one — say the true thing and say what changes.

**"You've had three sprints. Why has no artisan been interviewed?"**
There is no defence. It was planned in Sprint 1, carried in Sprint 2, carried again. It never
blocked a requirement, which is exactly why it kept slipping, and it is the item most likely to
invalidate work already built. The retrospective says so in those words. *If you do one interview
before the review, this answer changes completely — see below.*

**"Two of these four weeks have no commits."**
True, and the Sprint 1 retrospective had already said to stop batching the work. It happened again.
It is in the weekly records because leaving it out would have been worse.

**"Where is the video?"**
Not recorded. Say the date you will have it up.

**"UR06 says three seconds on 3G. Did you measure on 3G?"**
Be precise here, because the honest answer is good. The test measures the server response and
asserts it. The 3G budget is met by not spending it: no script, one stylesheet, one indexed query,
one row written — and a test asserts the page loads no script and exactly one stylesheet. A
throttled-network measurement is not yet recorded. Do not claim it is.

**"What stops someone forging a passport?"**
The code cannot be derived from another one. The row is signed with a key the database does not
hold, and the audit trail and each custody chain are linked so every record carries the signature
of the one before it. Rewriting a row invalidates its signature; removing one breaks the chain.
Neither is *prevented* — both are *detectable*. Say it that way. Claiming immutability is what the
project corrected in Sprint 2, and the reasoning is on the Domain Model wiki page.

**"So it is not immutable?"**
No, and it never was. What is open is the operator, who holds the key as well as the database.
Closing that needs the head of the chain published where the operator does not control it. That is
requirement FR56 and it is assigned to Sprint 4.

**"Why PostgreSQL and not SQLite?"**
Development and deployment run the same engine, so a constraint that holds locally holds in
production. Also `select_for_update`, which serialises the chain append, is a no-op on SQLite — the
guarantee would disappear silently.

**"What is left?"**
Custody transfers and the analytics, both with tables and invariants already in place and no views
yet. Sprint 3 is the analytics; Sprint 4 the custody and FR56.

---

## Tonight, in priority order

1. **Record the video.** It is a required section and it cannot be produced tomorrow morning.
2. **Export the four diagrams to PNG** and attach them to the wiki — open each `.drawio` at
   app.diagrams.net, File → Export as → PNG, 200 %, 10 px border. Three of the five sections become
   visible to anyone clicking through instead of downloading XML.
3. **Do one interview.** One. Fifteen minutes with one workshop or one shop, written up on the
   Problem Validation page. It converts the single most damaging answer above from "never done"
   into "started, here is what I learned", and nothing else available tonight moves the grade as
   much for as little work.

Do not refactor anything. The suite is green and the branch is reviewed; churn tonight is pure risk.
