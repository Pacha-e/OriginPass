# Deliverable 1 Video

Script and production notes for the presentation video required by Deliverable 1.

**Length:** five to seven minutes.
**Required content, in the order the deliverable template sets:** project and team name, the problem, team members, the proposed solution and its value proposition, and the ten highest-priority functional requirements.

> **Confirm with the professor before recording:** the pedagogical agreement requires deliverables and artefacts to be *written* in English. Whether the narration is spoken in English or in Spanish is not stated. This script is written in English; the spoken language is a decision to take before recording, not after.

## Timing

| From | To | Section | On screen |
|---|---|---|---|
| 0:00 | 0:30 | Project and team | Title card |
| 0:30 | 2:00 | The problem | Photographs, the competitive review table |
| 2:00 | 2:20 | Team | Team slide |
| 2:20 | 4:10 | Solution and value | **Live application** |
| 4:10 | 6:00 | The ten highest-priority requirements | Requirements slide |
| 6:00 | 6:30 | Close | Repository and wiki addresses |

## Script

### 1. Project and team name — 0:00 to 0:30

> This is OriginPass, team one, for Proyecto Integrador 1.
>
> OriginPass gives every physical product a passport that a buyer can check for themselves, and records every hand it passes through on the way to them.

### 2. The problem — 0:30 to 2:00

> Buying something genuine means trusting whoever is selling it. Standing in front of a product, a buyer has no way to tell an original from a copy.
>
> This hits protected-origin crafts hardest. A machine-made imitation of a sombrero vueltiao sells beside one woven in Tuchín, costs a fraction to produce, and looks close enough at arm's length. Three things follow. The producer loses the sale, and when the copy is poor, the reputation attached to the craft. The buyer pays a genuine-article price for something that may not be one. And the denomination of origin, which exists to protect a region's work, stops carrying information a buyer can act on.
>
> The options that exist today do not close this. Printed certificates and holograms can be reproduced in bulk, and nothing ties one certificate to one unit. Brand-owned checking apps cost more than a small producer can pay, and would need one app per brand. Marketplace guarantees do not reach the informal point of sale, which is where the problem is worst. Origin seals prove that a producer qualifies, not that the piece in your hand came from them.
>
> The gap is the same in all four: they say something about the producer, and nothing about the unit.

### 3. Team — 2:00 to 2:20

> The project is carried out individually by Emmanuel Hernández Melo, holding the roles of Scrum Master, Product Owner and developer. Working alone across the three roles was raised with the professor and approved before this deliverable, and the working agreement that guards against those roles blurring is recorded on the wiki.

### 4. The solution and its value — 2:20 to 4:10

Switch to the running application here. The walkthrough below is the one to follow.

> OriginPass issues one passport per physical unit, not per product line. A code covering a whole batch would legitimise every copy of it, so the unit is the thing being identified.
>
> A company applies through one of two tracks. A commercial company is verified through an official registry code. An artisan workshop, which usually has no such code, is verified by a person reviewing the application. Only an approved company can issue passports.
>
> *(Show: the application form, submitted without a registry code, refused with the cause beside the field. Add the code, submit, status Pending.)*
>
> The administrator sees every application and can filter by status. Approving takes effect at once. Rejecting requires a written reason, and that reason is stored with the decision and shown to the applicant, so a refusal is never silent.
>
> *(Show: the review list filtered by Pending, a rejection with its reason, then the applicant's own page showing that reason, then editing and resubmitting, then approval.)*
>
> What makes this different from a certificate is that the buyer checks it, not the seller. Verification takes a scan, no account and no app install, and it shows the chain of custody from the workshop to the shelf. And because a QR code can be photographed and reprinted, OriginPass records every scan, so one passport appearing in two distant places within a short window is something the system can see.

### 5. The ten highest-priority requirements — 4:10 to 6:00

Taken from the MoSCoW prioritisation on the [Requirements Prioritisation](Requirements-Prioritisation) page.

| # | Requirement | Sprint | State |
|---|---|---|---|
| 1 | FR07 Submit a company application with name, type, description, location and website | 1 | Delivered |
| 2 | FR08 Require an official registry code from commercial companies | 1 | Delivered |
| 3 | FR09 Accept artisan companies without a registry code, marked for manual review | 1 | Delivered |
| 4 | FR13 Administrator approves a pending company application | 1 | Delivered |
| 5 | FR14 Administrator rejects an application, storing a written reason | 1 | Delivered |
| 6 | FR19 An approved company registers a product | 2 | Planned |
| 7 | FR20 Refuse product registration from a company that is not approved | 2 | Planned |
| 8 | FR21 Generate a passport code that cannot be derived from another code | 2 | Planned |
| 9 | FR22 Generate a downloadable QR image for the verification address | 2 | Planned |
| 10 | FR23 Match product type to company type | 2 | Planned |

> These ten came out of a MoSCoW prioritisation of seventy-seven requirements, checked against the hours actually available rather than against an ideal feature list. The first five are built and covered by tests. The next five are the Sprint 2 goal: registering a product and getting a QR code for it.

### 6. Close — 6:00 to 6:30

> The code, the backlog and the documentation are on GitHub. Everything shown here is running against PostgreSQL with eighty automated tests behind it.
>
> Because buying something authentic should not depend only on trust.

## The walkthrough to record

Prepare the data first, so the interface has something in it:

```bash
docker compose up -d db
python manage.py migrate
python manage.py seed_demo      # five companies, one in each state, and an administrator
python manage.py runserver
```

`seed_demo` prints the administrator address and the shared password for the demo accounts.

Then, on screen, in this order:

1. Open the home page.
2. Create an account, then log in with it.
3. Open the company application form. Choose the commercial type, fill everything **except** the registry code, and submit. The refusal appears beside the registry code field.
4. Add the code and submit. The status reads Pending.
5. Log out. Log in as the administrator.
6. Open the applications list. Filter by Pending, then by Approved, then by Rejected.
7. Open the pending application. Try to reject it with the reason box empty; the rejection is refused. Write a reason and reject it.
8. Log back in as the company. The rejection and its reason are on the page.
9. Edit the application, correct it and resubmit. The status returns to Pending.
10. As the administrator, approve it.
11. As the company, try to edit again. The edit is refused and the refusal says why.

Steps 3, 7 and 11 are the ones worth pausing on: each is a requirement the video names.

## How it is produced

The slides and the walkthrough are built by a script; **the narration is recorded by me**. `tools/video/` in the code repository holds the pipeline and `tools/video/README.md` explains each part.

| Stage | What it does |
|---|---|
| `slides.py` | Builds each slide as HTML and renders it in a headless browser at 1920×1080 |
| `record_demo.py` | Drives the real application through a browser and records the walkthrough |
| `reference.py` | Writes the recording guide: what to read per section and roughly how long it should take |
| `voiceover.py` | Measures my recordings and writes the timing everything else follows |
| `assemble.py` | Composites the three and writes the MP4 and a subtitle file |

### Recording it

`python tools/video/reference.py` writes `build/recording-guide.md` — twelve sections, the text to read in each, and a target length. Record one file per section into `tools/video/voice/`, named after the section id. One file per section rather than a single take, so a section can be redone without re-recording the rest.

### Building it

```bash
docker compose up -d db && python manage.py migrate && python manage.py seed_demo
python manage.py runserver 8765          # in one terminal

python tools/video/build.py --preview    # silent, to check the visuals first
python tools/video/build.py              # the finished video, with my narration
```

**No duration is written by hand.** Each recording is measured, and every slide is then held for exactly as long as the sentence spoken over it; the walkthrough is stretched or compressed to fit the narration that plays over it. Re-recording a section re-times the video on the next build. That is the reason for building it this way rather than editing a timeline: the video can be regenerated whenever the product, the script or a recording changes, at no cost.

## The plan

| | |
|---|---|
| Sections | 11 slides and one recorded walkthrough of the running application |
| Length at the reference pace | about 6 minutes, inside the five to seven the deliverable asks for |
| Resolution | 1920×1080, 30 fps, H.264 with AAC audio |
| Subtitles | generated from the script text across each section's measured duration |

### One known gap

The narration is in Spanish and the interface shown in the walkthrough is still in English. Rendering the interface in Spanish is UR04, which belongs to Sprint 2, so this is the state the product is genuinely in rather than something hidden. Once that requirement is delivered, rebuilding picks up the translated interface without the narration or the slides being touched.

## Before submitting

Watch it once at full length. Check that the walkthrough segment still matches what is said over it, since the two are timed independently and re-recording that section moves the alignment.

## Link

*To be added once uploaded.*
