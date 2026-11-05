SKILLS (obligatorias, leer PRIMERO): `agentes\habilidades\source-ordering\SKILL.md`, `agentes\habilidades\meaningful-names\SKILL.md`, más las habilidades que liste la tarea. Lee un `references\` solo si tocas esa tecnología.
RULE LOOKUP (no leas el archivo completo; busca el id que necesitas): `agentes\reglas\global-rules.md`. La sección "Aplicación a OriginPass (Django)" prevalece sobre las reglas genéricas.
CODE QUALITY BAR:
- Every Python file: section separator comments (`# --- Section ---`), standard-library imports, then third-party, then first-party, alphabetical names inside each section (imports, constants, classes, methods). Function bodies keep their logic order. Semantic-order exceptions per the Django section of global-rules.md.
- English only: identifiers, comments, docstrings, file names. UI text goes through gettext and locale/.
- No dead code, no commented-out code, no `Any` in annotations, no generic helper utilities, no loose functions outside classes in services or utilities. Django views, signals and framework hooks are the documented exception.
- Behavior preserved unless the task demands a change; list every behavior change in the report.
- Touch only OWNED paths.
DONE = verification commands pass; put their final summary lines and a file-by-file change list in the report.