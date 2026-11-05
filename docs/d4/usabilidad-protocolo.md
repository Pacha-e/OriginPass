# Usability protocol with potential users (Deliverable 4, section 3)

**Status: PENDING: not carried out (PENDIENTE: no realizado).** No usability sessions are recorded in `docs/wiki`. The interviews and survey from the earlier research have not been run either: `docs/wiki/Retrospectives.md:36`; `docs/wiki/Sprint-2-Review.md:81`.

## 1. Objective

Check with potential users whether verifying a product and registering a company meet usability requirements UR01 to UR03, UR07, UR08 and UR10 (`docs/wiki/Requirements-Specification.md:137-146`). Without sessions, this protocol produces no findings.

## 2. Participant profile

| Group | Inclusion criteria | Proposed size | Recruitment channel |
|---|---|---|---|
| Buyers | Bought artisan or branded goods in the last year. Has no OriginPass account. Uses a mobile phone. | 5 | University groups outside Systems Engineering; family and neighbourhood groups; craft shops in Medellín (`docs/wiki/Primary-Research-Plan.md:41-43`) |
| Producers | Makes crafts or manufactures on a small scale. May have no origin registration. | 3 | Resguardo Zenú, Feria Tuchín, Artesanías de Colombia, Alcaldía de Tuchín (`docs/wiki/Primary-Research-Plan.md:53-59`) |

- Sizes are design proposals, not results.
- Producers are approached through institutions, not individual artisans (`docs/wiki/Primary-Research-Plan.md:61`).
- Sessions use the demo environment (`seed_demo`, see `analitica.md`). No real people's data is used.

## 3. Tasks

| ID | Profile | Task | Requirement | Success if |
|---|---|---|---|---|
| T1 | Buyer | With a demo code, decide whether the product is genuine and explain why. | UR02, FR28, FR29 | Reaches the verdict in 2 interactions or fewer from the scan, and identifies it correctly |
| T2 | Buyer | Explain in their own words what the Revoked and Not found verdicts mean, using demo codes. | UR03, FR30, FR31 | Explains both without help |
| T3 | Buyer | Read the full result on a 360 px phone without zooming. | UR01 | Reaches all content by vertical scrolling |
| T4 | Producer | Submit an artisan company application with their details. | FR07, FR09, UR08 | Submits the application. If an error appears, identifies the field |
| T5 | Producer | Register a demo product and download its QR as PNG. | FR19, FR22, UR10 | Registers with 5 required fields or fewer and downloads the PNG |
| T6 | Anyone | Go through the registration form using only the Tab key. (Optional) | UR07 | Reaches every interactive field with Tab |

UR06 (3 s over 3G) is measured with a technical tool, not with users. It is not part of this protocol.

## 4. Questions

**Before the task (profile).** These mirror two survey questions, so the answers can be compared. Participants answer in Spanish:
1. "En el último año, ¿compraste alguna artesanía o producto de marca sin estar seguro de que fuera original?" (Sí / No / No estoy seguro). Mirrors survey question 1 (`docs/wiki/Primary-Research-Plan.md:24`).
2. "¿Cómo verificas hoy que un producto es original, si es que lo haces?" Mirrors survey question 5 (`docs/wiki/Primary-Research-Plan.md:28`).

**After each task:**
3. What did you expect to see at that step?
4. What was confusing or made you hesitate?

**At the end (optional):**
5. SUS questionnaire, 10 items (Brooke, 1996). Score from 0 to 100.

## 5. Informed consent (participant-facing text)

The text below is kept in Spanish because participants are Spanish speakers. It must be read to them in Spanish.

> Estás invitado a probar una aplicación web de demostración para verificar productos artesanales. Evaluamos la aplicación, no a ti. Puedes detener la sesión en cualquier momento sin consecuencias.
>
> La sesión no graba audio ni video sin una autorización aparte. Tus notas se identifican con un código de participante (P-01, P-02...) y no contienen datos personales. Tu nombre no se publica.
>
> La aplicación de prueba registra, por cada escaneo, la fecha, una región gruesa y el tipo de dispositivo (`verification/models.py:27-41`). Si te registras como productor, la cuenta de prueba guarda el correo que indiques; usa uno de prueba.
>
> Contacto: ehernandem@eafit.edu.co.

| Field | Value |
|---|---|
| Verbal or signed acceptance | ________ |
| Date | ________ |
| Participant code | ________ |
| Compensation | PENDING decision |
| Personal data processing under Colombian data protection law (`docs/wiki/Deliverable-1.md`, section 1.4; the statute number is not cited in the repository) | PENDING legal review |

## 6. Metrics

| Metric | Definition | How it is measured |
|---|---|---|
| Task success | Completed without help, with help, or not completed | Moderator log |
| Task time | Seconds from start until the participant states the result | Moderator stopwatch |
| Errors | Actions that do not lead to the goal: wrong route, wrong field | Moderator count |
| Interactions (UR02) | Taps or clicks from the scan to the verdict | Moderator count |
| SUS (optional) | Score from 0 to 100 | Final questionnaire |

Thresholds are those of the requirements: UR02 (2 interactions or fewer), UR01 (360 px), UR10 (5 required fields or fewer). No additional time thresholds are set.

## 7. Severity

| Severity | Proposed criterion |
|---|---|
| High | Prevents completing the task |
| Medium | Forces repeated steps or causes an error that can be recovered from |
| Low | Annoyance with no effect on the task result |

## 8. Results

Usability issues table (format from the brief):

| Usability Issue | Severity (High / Medium / Low) | Improvement implemented |
|---|---|---|
| PENDING: not carried out (PENDIENTE: no realizado) | — | — |

Session table:

| Participant | Profile | Task | Success | Time (s) | Errors | Status |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | PENDING: not carried out (PENDIENTE: no realizado) |

## 9. Limits

- With 5 buyers and 3 producers, results would be qualitative. They have no statistical value.
- Tasks use demo data. The verdict for a real code is not tested against the production registry.
