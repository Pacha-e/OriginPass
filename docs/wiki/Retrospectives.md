# Retrospectives

One entry per sprint, answering three questions:

- **Continue** — practices that worked and are worth keeping
- **Start** — improvements to the process
- **Stop** — problems and bottlenecks to remove

---

## Sprint 1 — 15 July to 11 August 2026

Eighteen of eighteen committed requirements delivered, verified by eighty automated tests. The detail is on the [Sprint 1 Review](Sprint-1-Review) page.

**Continue**

- Deriving requirements from the product rather than from a required count. The specification ended up covering the whole product, and the required minimum was passed without padding.
- Checking the Must set against available hours before committing to it. That check changed the plan, which is what a check is for.
- Writing a test for each acceptance criterion instead of clicking through the application. At the end of the sprint the question "is this done" had an answer that did not depend on my memory, and the time bounds the requirements state were measured rather than assumed.
- Taking the business rules from the prototype contracts rather than rewriting them from the requirement text. They had already been thought through once, and porting them was faster and produced fewer gaps than starting from prose.

**Start**

- Writing each artefact in the week it belongs to. Batching a sprint's documentation into its final days is what made this sprint tight.
- Recording the reason for a scope decision next to the decision itself, so that a choice made in August can still be explained in November.
- Treating primary research as scheduled work with a date, not as something to fit in around the code. It was on the plan for four weeks and did not happen, because nothing forced it to.

**Stop**

- Leaving the whole sprint's code to the final days. Every requirement was delivered, but the schedule left no room for anything to go wrong, and the risk was carried rather than managed.
- Postponing decisions that block other work. The database engine, the styling approach and the scope of the first migration were all settled on the last day; each of them could have been settled in week one at no cost.
- Filling tracking pages retroactively. Weeks 1 to 3 of the [Development Log](Development-Log) hold no account of the work, because the entries were not written as the weeks passed and the repository did not exist yet to be read back. They are closed by saying so; what happened in them is now harder to reconstruct honestly than it would have been to record.

**Carried into the next sprint**

- Run the producer interviews and the buyer survey. This is the largest open item in the project and it does not depend on the code.
- Write the weekly entry at the end of each week rather than at the end of the sprint.
- Start Sprint 2 work in its first week, so that the last week is spare capacity rather than the plan.

---

## Sprint 2 — 12 August to 8 September 2026

Twenty-two of twenty-two committed requirements delivered, verified by one hundred and seventy-nine automated tests. The detail is on the [Sprint 2 Review](Sprint-2-Review) page.

**Continue**

- Deciding the build order by what each step unblocks rather than by requirement number. Internationalisation went first, so the interface written afterwards was written translated once instead of twice.
- Writing the reason for a decision beside the decision. The one place the project writes Spanish at the source, `500.html`, says in the file why it is the exception, and that will still answer the question in November.
- Measuring the requirements that state a time bound instead of assuming them.
- Fixing the class of a bug rather than the instance. A comment served as text last sprint became a check over every template; a translation left empty became a check over every catalogue entry.

**Start**

- Running the suite before the last day of the sprint. The local database was unavailable for the whole of the closing work, and continuous integration was the first thing that actually ran the tests. That worked, but only because the pipeline existed; it was luck that it did.
- Keeping the deliverable template open while working, not at the end. Two sections of Deliverable 2, the mockups and the video, were only read as requirements once the code was finished.
- Reading the requirement text before the sprint rather than during it. UR04 was known from the start and was still the largest single piece of work in the sprint.

**Stop**

- Letting a refactor and a feature land in one commit. The reorganisation and the Spanish interface touched the same files, so they could not be separated afterwards, and the history is worse for it. The reorganisation should have gone first, on its own, while the suite was green.
- Depending on one machine for verification. Docker's engine failed for the whole closing period and there was no second way to run the tests locally.
- Carrying the primary research. It has now been carried for three sprints, which is no longer a slip; it is a decision that has never been taken deliberately.

**Carried into the next sprint**

- Run the producer interviews and the buyer survey. Third sprint carried.
- Produce the Sprint 2 mockups and record the deliverable video.
- Export the three architecture diagrams to PNG and attach them to the wiki.

---

## Sprint 3 — 9 September to 13 October 2026

Twenty-two of twenty-two committed requirements delivered, and fourteen of the eighteen
planned for Sprint 4, verified by three hundred and fourteen automated tests. The detail
is on the [Sprint 3 Review](Sprint-3-Review) page.

**Continue**

- Auditing the work against the requirements before calling it done. The first report on
  Sprint 3 said done; the audit found an approval that failed, a public page that showed
  the buyers' emails and a claim that moved nothing, and each was fixed with a test
  written first.
- Answering feedback the day it arrives. The professor's point about the rural artisan on
  1 October was in the interface the same day.
- Putting a rule in the database whenever the database can hold it. One open offer per
  product is a partial unique index, so two simultaneous requests cannot sell a product
  twice.
- Letting continuous integration decide the merge. Sprint 3 reached `main` only once the
  run on its pull request passed.

**Start**

- Watching the integration runs on the sprint branch, not only on `main`. The Sprint 3
  pull request failed five times on lint before anyone looked.
- Checking each issue against the code when closing it. Thirty-seven issues closed in
  three minutes with one generic comment included FR34, which had not been built.
- Keeping generated files out of the repository from the start. The presentation archive,
  which carries a rendered video, was committed six times in one evening before it moved
  to a release.

**Stop**

- Letting a sprint's code land in its last two days. Weeks 12 and 13 have no commit; it is
  the third sprint with the same shape.
- Carrying the primary research. Fourth sprint carried.

**Carried into the next sprint**

- FR56, publishing the head of the integrity chain outside the server, with Monad as the
  target; FR34, FR27 and UR05; the deployment.
- Run the producer interviews and the buyer survey.
- Rehearse the presentation kit on the machine used in class before each review.

---

## Sprint 4 — 14 October to 10 November 2026

Written on 5 November, before the Sprint Review; what the review brings up is added
below it. The application is deployed on AWS EC2 with HTTPS. Four requirements were added
and built (FR59 to FR62), the five defects of the external audit were fixed with a
regression test each, and the suite reached 349 tests. FR27, FR34, FR56 and UR05 remain
open. The detail is on the [Deliverable 4](Deliverable-4) page.

**Continue**

- Writing the test that fails before the fix. Each of the five audit defects has one, and
  it was run without the fix to see it fail.
- Using the product the way its users would. Printing the QR sheet and claiming a product
  on a phone found what no test had: a QR far too large for a hat, a passport code nobody
  would type, photos that did not load and a file button that only opened the camera.
- Turning every repeated step into a script: the update of the instance, the QR sheets,
  the diagrams and the infographic are rebuilt by a command, not by hand.
- Writing a limitation down the day it is found, with the reason: the scans that carry no
  region without a CDN, the photographs of a screen that are not read.

**Start**

- Deploying in the first week of a sprint. The deployment is what exposed the uploaded
  images, the camera that needs HTTPS and the mixed languages, all cheap to fix earlier.
- Giving a deployment a fixed address from its first day, an Elastic IP or a domain, so
  the address written in the documentation does not go stale.
- Testing browser code in a browser. The tests of the QR reader check the HTML of the
  page, so none of them saw that the message for a refused camera is hidden.
- Taking a copy of the database, the uploaded files and the key before any change to the
  instance.

**Stop**

- Letting weeks pass without a commit. Nothing reached `main` from 16 October to
  3 November, and the sprint's work landed in its last days for the fourth time.
- Carrying the primary research. Fifth sprint carried: the course ends with the product
  built and deployed and no producer or buyer consulted.
- Writing a version or a status in a document before checking it. Two documents gave the
  server's PostgreSQL as 16, and the deployment guide called itself pending after the
  deployment had run.

**Carried into the next sprint**

- FR56, publishing the head of the integrity chain outside the server, with Monad as the
  target; FR27, FR34 and UR05.
- The findings of the external audit that remain open: signatures of custody transfers,
  concurrency, the installer.
- The producer interviews, the buyer survey and the usability protocol.

---

## Template for later sprints

```
## Sprint N — dates

**Continue**
-

**Start**
-

**Stop**
-

**Carried into the next sprint**
-
```
