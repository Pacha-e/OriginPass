HOW TO WRITE A PROJECT SKILL (OriginPass):
- One folder per skill: `agentes\habilidades\<skill-name>\` with a SKILL.md that follows `fmt\skill.md`.
- Project-specific rules (Django apps, PostgreSQL schema, migrations, rendering) belong to the skill whose name names the concern (for example `safe-state-changes` for migrations and constraints). Do not add rules that duplicate `reglas\global-rules.md`; cite its identifiers instead.
- Every rule states what the code must do in Django terms: model field, view, form, template, migration or management command.
- Give each rule an identifier with a project prefix (`OP-<AREA>-NN`) and list its source in `reglas\` or in the task.
- Professor-derived rules are hard rules and say so.
- Do not add a rule that conflicts with the Django section of `reglas\global-rules.md` without recording the exception there first.