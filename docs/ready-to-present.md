# Getting this project ready to present, on a machine that has never run it

One file, start to finish. Follow it in order. Every step says what you should see, so a
step that went wrong is caught here rather than in front of the room.

It is written to be handed to an agent as much as read by a person. An agent working from
this file should run each step, compare the real output against the **Expect** line, and
stop at the first mismatch rather than continuing and hoping.

Budget about twenty minutes on a machine that has none of the prerequisites, and about
four on one that has them all.

---

## 0. What you need first

| | Check with | If it is missing |
|---|---|---|
| Git | `git --version` | [git-scm.com](https://git-scm.com/downloads) |
| Python 3.12 | `python --version` | [python.org](https://www.python.org/downloads/) — tick *Add to PATH* |
| Docker Desktop, running | `docker info` | [docker.com](https://www.docker.com/products/docker-desktop/) — start it and wait for the whale to stop animating |
| gettext | `msgfmt --version` | Needed only by step 6. See that step. |

**Expect:** four version numbers and no error. `docker info` prints a long block ending in
server details; if it says *cannot connect to the Docker daemon*, Docker Desktop is not
running yet.

Commands below assume Git Bash on Windows. On Linux or macOS the only difference is
`.venv/bin/activate` instead of `.venv/Scripts/activate`.

---

## 1. Get the code

```bash
git clone https://github.com/Pacha-e/OriginPass.git
cd OriginPass
```

If the repository is already there, take the branch being presented and update it:

```bash
cd OriginPass
git fetch origin
git checkout sprint-2-completion
git pull
```

**Expect:** `git status` says *up to date* and *nothing to commit*.

> If `git status` lists changes you did not make, stop and read them before continuing.
> Do not discard them without looking; they may be work that was never pushed from the
> other machine.

---

## 2. Python environment

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements-dev.txt
```

**Expect:** the prompt is prefixed with `(.venv)`, and pip ends with *Successfully
installed* naming Django, psycopg, Pillow, qrcode, dj-database-url, python-dotenv and
ruff.

> **`python` is not recognised** — Python is not on PATH. Reinstall ticking *Add to PATH*,
> or use the full path to `python.exe`.
>
> **A wheel fails to build** — the machine is on a Python other than 3.12. Check with
> `python --version`.

---

## 3. The environment file

```bash
cp .env.example .env
python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
```

Put the printed key into `.env` as `SECRET_KEY`, replacing `replace-me`. Leave every other
value as it comes.

**Expect:** `.env` exists, `SECRET_KEY` is a 50-character string, `DATABASE_URL` points at
`localhost:5432/originpass`.

> The key is not only the Django secret: it signs every integrity record. A different key
> on this machine than on the other one means records written there will not verify here.
> That is expected and harmless for a fresh database, because step 5 creates the records
> under this key. It matters only if you copy a database between machines — then carry the
> old key across in `SECRET_KEY_FALLBACKS`.

---

## 4. The database and the window onto it

```bash
docker compose up -d
docker compose ps
```

**Expect:** two containers.

```
NAME                 STATUS                   PORTS
originpass-db        Up (healthy)             0.0.0.0:5432->5432/tcp
originpass-pgadmin   Up                       127.0.0.1:8080->80/tcp
```

`originpass-db` must say **healthy**, not just *Up*. It takes about ten seconds. If it
stays *starting* for more than a minute, read `docker compose logs db`.

> **port is already allocated** — something else holds 5432 or 8080. Find it with
> `netstat -ano | grep 5432`, or stop the other project's containers with
> `docker ps` then `docker stop <name>`.

---

## 5. Schema and data

```bash
python manage.py migrate
python manage.py seed_demo
```

**Expect:** `migrate` lists migrations ending in `OK`, or says *No migrations to apply*.
Then `seed_demo` prints five companies, four passports and the `/v/<code>` path of each.

**Copy those passport paths somewhere.** You need one of them live, and looking it up in
front of the room is the kind of pause that reads as not knowing your own project.

> **`connection timeout expired`** — step 4 is not finished. Wait for *healthy*.
>
> **`seed_demo` says it skipped, data already present** — fine, the data is there. Get the
> codes with:
> ```bash
> python manage.py shell -c "from products.models import Product; [print(p.status, p.name, '/v/' + p.passport_code) for p in Product.objects.all()]"
> ```

---

## 6. The interface in Spanish

```bash
python manage.py compilemessages
```

**Expect:** `processing file django.po in locale/es/LC_MESSAGES`.

> **`msgfmt` is not on PATH** — this is the one prerequisite Python does not bring. Without
> it the interface is served in English, and UR04 asks for Spanish.
>
> On Windows, install [gettext for Windows](https://mlocati.github.io/articles/gettext-iconv-windows.html)
> and open a new terminal. On macOS, `brew install gettext`. On Debian or Ubuntu,
> `sudo apt install gettext`.
>
> Check that it worked: `locale/es/LC_MESSAGES/django.mo` exists.

---

## 7. An administrator account

`seed_demo` already made one: `admin@originpass.co`. Every account it creates shares one
password, `OriginPass-2026`, which it prints when it runs and which is written in plain
sight in `companies/management/commands/seed_demo.py`. It is a demonstration credential and
nothing else: the command refuses to run unless `DEBUG` is on, precisely so this password
cannot reach a deployment. That is enough to present.

Make another only if you want a password you chose:

```bash
python manage.py createsuperuser
```

---

## 8. Prove it before you present it

Four checks. Each one answers a question the reviewer might ask.

```bash
python manage.py test
```
**Expect:** `OK`, with the test count. Anything else, stop and read it.

```bash
python manage.py verify_integrity
```
**Expect:** three lines saying intact, then a sentence about the signing key.

> If it says **This database is behind the code**, run `python manage.py migrate` and try
> again. It refuses to report on a database that is missing constraints it is supposed to
> be verifying.

```bash
python manage.py describe_schema
```
**Expect:** six tables with their columns, and each rule the database enforces named as a
sentence — *commercial company has registry code*, *audit entry links to one predecessor*
and the rest. This is what to show if you are asked to prove the data model is real.

```bash
ruff check . && ruff format --check .
```
**Expect:** *All checks passed!* and *N files already formatted*.

---

## 9. Start it

```bash
python manage.py runserver
```

Leave this terminal open. It is the server.

**Expect:** *Starting development server at http://127.0.0.1:8000/* and **no** line about
unapplied migrations. If that warning appears, step 5 did not finish.

---

## 10. Open the four things you will show

| What | Where | First thing to do |
|---|---|---|
| The public verification page | `http://127.0.0.1:8000/v/<code>` | Use a passport path from step 5 |
| The application | `http://127.0.0.1:8000/` | Log in as a company owner from `seed_demo` |
| Django administration | `http://127.0.0.1:8000/admin/` | Log in as `admin@originpass.co` |
| The database | `http://127.0.0.1:8080/` | See below |

**pgAdmin** opens straight on the object tree with no login of its own. Expand
**Servers → OriginPass**; it asks once for the password of the user `originpass`, which is
`originpass`. Tick *Save password*. The tables are then under
**Databases → originpass → Schemas → public → Tables**.

> The step up to the password prompt was verified; the path below it was not walked on this
> machine. Walk it once yourself while rehearsing, and correct this file if it differs.

To show a rule the database holds rather than the application:
**products_custodytransfer → Constraints**. There is
`custody_transfer_links_to_one_predecessor`, which is what keeps a chain of custody from
forking, and `custody_transfer_changes_holder`.

Open all four tabs **before** anyone is watching, and log into each one. Every password
prompt you meet now is one you do not meet live.

---

## Ready

- [ ] `docker compose ps` shows both containers, the database healthy
- [ ] `python manage.py test` ends in `OK`
- [ ] `verify_integrity` reports intact
- [ ] `runserver` is running and warns about nothing
- [ ] The four tabs are open and logged in
- [ ] The passport paths from step 5 are written down where you can see them

---

## Shutting down

```bash
# Ctrl-C in the runserver terminal, then:
docker compose down
```

The data survives in a Docker volume; `docker compose up -d` brings it back as it was.
To start from nothing, `docker compose down -v` deletes the volume too, and steps 5 and 6
rebuild everything.
