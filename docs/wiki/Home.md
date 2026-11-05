# OriginPass

**Prove where a product came from, without having to trust the seller.**

OriginPass is a web application that issues a verifiable digital passport for every physical product and records each change of custody along its journey. A buyer scans a QR code and sees whether the product is genuine, who made it, and the path it took to reach the shelf. No account is needed to check.

The project is being built for ST0251 Proyecto Integrador 1, 2026-2, at Universidad EAFIT.

## Wiki index

| Page | Contents |
|---|---|
| [Team](Team) | Who is working on the project and in which role |
| [Project Overview](Project-Overview) | What the product is, who it serves, and how it works |
| [Product Vision Board](Product-Vision-Board) | Vision, target group, needs, product and business goals |
| [Elevator Pitch](Elevator-Pitch) | The pitch, in one minute |
| [Problem Validation](Problem-Validation) | Evidence collected to confirm the problem is real |
| [Primary Research Plan](Primary-Research-Plan) | The survey, the interview channels and the message to send |
| [Requirements Specification](Requirements-Specification) | Functional, usability and logical database requirements |
| [Requirements Prioritisation](Requirements-Prioritisation) | MoSCoW prioritisation and sprint assignment |
| [Domain Model](Domain-Model) | Entities, relationships and state machines |
| [Deliverable 1](Deliverable-1) | Project definition and software requirements specification |
| [Deliverable 1 Video](Deliverable-1-Video) | Script, timing and the walkthrough to record |
| [Deliverable 2](Deliverable-2) | Solution design and functionality preview |
| [Deliverable 3](Deliverable-3) | The MVP: architecture, corporate image, repository, video and project management |
| [Deliverable 4](Deliverable-4) | The PMV and its documentation: validation against the vision and the requirements, the deployment on AWS, the design, usability, the infographic, limitations and project management |
| [Videos](Videos) | The Deliverable 3 walkthrough and the five launch videos, narrated by Emmanuel |
| [Daily Log](Daily-Log) | The individual day-by-day log the professor asked for in place of meeting minutes |
| [Sprint 1 Review](Sprint-1-Review) | What was committed, what was delivered and how it was verified |
| [Sprint 2 Plan](Sprint-2-Plan) | Sprint goal, scope, build order and risks |
| [Sprint 2 Review](Sprint-2-Review) | What was committed, what was delivered and how it was verified |
| [Sprint 3 Review](Sprint-3-Review) | What was committed, what was delivered and how it was verified |
| [Development Log](Development-Log) | What was built each week, what came next, what stood in the way |
| [Retrospectives](Retrospectives) | What to continue, start and stop doing |
| [Activities and Homeworks](Activities-and-Homeworks) | Class assignments |

## Current status

Sprint 4 is the last sprint of the course. The application is deployed on AWS EC2 with HTTPS, and of its 62 functional requirements 54 are developed, 5 in part and 3 not, verified by 349 automated tests on PostgreSQL 17 in the last full run (5 November 2026). [Deliverable 4](Deliverable-4) holds the validation against the vision and the requirements, the deployment, the design, the usability analysis, the infographic, the limitations and the project management.

A formal company or an informal workshop registers each unit and prints its QR passport, with a photo. The product passes from hand to hand along a signed chain of custody; a buyer scans the code and reads the verdict and the journey without an account; a new holder claims the piece by reading its QR with the phone's camera; and the company sees where its products are verified and is warned when one of its codes turns up in two places at once. A verdict certifies the state of the record, not by itself the physical piece. Anchoring the integrity chain on Monad (FR56) was the Sprint 4 goal and is not built.

The largest open item is the primary research on the [Problem Validation](Problem-Validation) page, carried for five sprints and not carried out, so no part of the product has been validated with its users.

The sprint calendar set by the course is:

| Sprint | Dates | Review |
|---|---|---|
| 1 | 15 July – 11 August 2026 | 11 August |
| 2 | 12 August – 8 September 2026 | 8 September |
| 3 | 9 September – 13 October 2026 | 13 October |
| 4 | 14 October – 10 November 2026 | Final presentations, 3 and 10 November |
