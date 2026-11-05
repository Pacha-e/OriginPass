# Global programming rules

## Aplicación a OriginPass (Django)

Stack: Python 3.12, Django 5.2 (`Django>=5.2,<6.0`), PostgreSQL 17 como única base de datos (sin otro motor de respaldo) y psycopg 3. Herramientas: `pyproject.toml` y `requirements-dev.txt`. Esta sección prevalece sobre las reglas genéricas de este documento cuando hay conflicto.

**(a) Excepciones de forma.** Las piezas siguientes tienen un orden o una forma que define el framework. No se reordenan alfabéticamente ni se reescriben para cumplir G-STRUCT-01 o G-STRUCT-02:
- `INSTALLED_APPS` y `MIDDLEWARE` en `config/settings.py`: el orden es semántico, Django ejecuta el middleware en orden.
- `urlpatterns`: la precedencia de rutas es semántica; no se ordenan alfabéticamente.
- Migraciones (`*/migrations/*`): inmutables. Una migración aplicada no se edita; el cambio va en una migración nueva. `pyproject.toml` las excluye de ruff.
- Campos de modelo: el orden de declaración define columnas y orden por defecto; no se reordenan.
- Vistas basadas en función (por ejemplo `def log_in(request)`): son el contrato de Django. No se convierten en clases ni en métodos de utilidades. G-STRUCT-02 aplica a servicios y utilidades, no a vistas, señales, hooks ni comandos de gestión.
- Plantillas: el orden de `{% extends %}`, `{% load %}` y de los bloques lo fija la plantilla base; no se reordena.

**(b) Herramientas de verificación.**
- Lint: `ruff check .` con las reglas de `pyproject.toml`: E, F, I, UP, B, DJ, C4; longitud máxima de línea 100.
- Formato: `ruff format --check .`.
- Migraciones: `manage.py makemigrations --check --dry-run`; no debe haber cambios de modelo sin migración.
- Tests: `manage.py test --noinput` sobre PostgreSQL 17 (`DATABASE_URL`). La suite completa tarda unos 6 minutos; se ejecuta solo cuando el orquestador lo pida.
- Verificación agregada: `agentes\flujo\verificar.ps1 -DatabaseUrl <url>`.

**(c) Idioma.**
- Código, comentarios, docstrings, identificadores y nombres de archivo: inglés (G-NAME-02).
- Texto visible al usuario: español, mediante `gettext` y catálogos en `locale/`. No se deja texto de interfaz en inglés.
- Nombres de apps, modelos y campos: inglés.


## How to use this rulebook (precedence, exceptions)

Apply these rules to project-owned source and delivery work. Resolve conflicts in this order: the student's explicit file-ordering mandate; professor feedback; the professor's observed conventions (T08); course books (T06 and T07); general literature (T09 and T10), with the local code-quality law used as supplementary guidance. More specific project requirements and language or framework constraints must be recorded when they require an exception. The mandatory alphabetical ordering supersedes the local law's suggested order of use (reglas/calidad-de-codigo.md:86-99). Preserve semantic ordering whenever sorting would change behavior; document such exceptions in review. The English-only convention applies to developer-facing source, while localization and verbatim quotations remain intact.

The feedback states ?separar alfabateicamente, importaciones externas, luego internas, utilizar comentarios separadores, utils deben ser clases con m?todos? (referencia/professor-feedback.md:37). It also says ?Funciones por fuera de las clases, pasar a utils o a otros lados como m?todos? (referencia/professor-feedback.md:38). These observations motivate the ordering and class conventions; the more detailed ordering rule below is the student's explicit mandate.

Checks are review actions, not claims that an automated tool can establish semantic correctness alone. A counter-test names when the default does not fit; it does not waive an explicit contract without recording the reason.

## Rules

#### Structure and ordering

### G-STRUCT-01 Order source sections
- Rule: every source file is divided into sections in a fixed order (imports external, imports internal, constants, types/enums/interfaces, class or exported members, private helpers), each section introduced by a separator comment, and the NAMES inside each section (import specifiers and import lines, constants, properties, methods, functions) sorted alphabetically. Function bodies are not reordered. Exceptions where order carries meaning: CSS cascade, route declaration order, template block order, package scripts, middleware/pipeline order, decorator order.
- Why: Consistent navigation reduces search time; behavior-sensitive ordering must remain intact.
- Check: Inspect section headers and compare names with an alphabetical sort; review side-effect imports and initialization dependencies before changing order.
- Counter-test: Do not reorder declarations or imports when execution or language rules depend on their order; omit nonexistent sections and do not insert comments in formats that forbid them.
- Source: Student file-ordering mandate supplied in task; referencia/professor-feedback.md:19,34-38; reglas/calidad-de-codigo.md:86-99.
- Skill: source-ordering

### G-STRUCT-02 Place utilities in classes
- Rule: Put utility functions and service operations in appropriately named classes as methods.
- Why: The professor explicitly requires classes with methods and rejects loose functions.
- Check: Inspect utility and service files for top-level function declarations and check ownership of each method.
- Counter-test: Framework-required callbacks, language entry points, and constructs that cannot be methods retain their required form.
- Source: referencia/professor-feedback.md:16,37-38.
- Skill: source-ordering

### G-STRUCT-03 Assign code to its owning layer
- Rule: Place each definition in the folder and layer responsible for its role.
- Why: Mixed seeds, storage, services, types, and interfaces obscure ownership.
- Check: Compare changed file contents and imports with the documented folder responsibilities and architecture diagram.
- Counter-test: Keep a small, cohesive definition with its consumer when a separate layer would not clarify ownership and course rules permit it.
- Source: referencia/professor-feedback.md:13,27,37; [fuente no incluida] T08-author-correa.md:33-35,57-59.
- Skill: module-boundaries

#### Naming

### G-NAME-01 Name domain meaning
- Rule: Choose descriptive names that express domain meaning and distinguish each operation.
- Why: Meaningful names reduce lookup and prevent ambiguous calls.
- Check: Read changed identifiers as domain phrases; flag placeholders and names such as aRespuesta.
- Counter-test: Use conventional short names for local indices or mathematical variables when their meaning is immediately apparent.
- Source: referencia/professor-feedback.md:38; reglas/calidad-de-codigo.md:103-109.
- Skill: meaningful-names

### G-NAME-02 Use English in source
- Rule: Write identifiers, comments, and developer-facing source text in English.
- Why: A single language makes code and review consistent.
- Check: Inspect changed identifiers, comments, labels, and literals for mixed-language text; review exceptions explicitly.
- Counter-test: Preserve required Spanish quotations, user-provided data, localized user-facing text, and externally mandated names.
- Source: referencia/professor-feedback.md:14,20,27.
- Skill: meaningful-names

#### Design principles

### G-DESIGN-01 Keep changes minimal
- Rule: Implement the present requirement with the fewest moving parts that preserve domain distinctions.
- Why: Speculative abstractions add maintenance and can hide behavior.
- Check: Trace each changed abstraction and option to an acceptance criterion; review the diff for unrelated edits.
- Counter-test: Add a required extension point when an existing contract or demonstrated constraint needs it.
- Source: [fuente no incluida] T09-best-practices-a.md:53-65,233-243; reglas/calidad-de-codigo.md:69-80,184.
- Skill: simple-design

### G-DESIGN-02 Separate reasons for change
- Rule: Group code around decisions that change for the same actor and hide unstable details behind a small interface.
- Why: Cohesion limits the impact of a change without splitting files merely by size.
- Check: Name the actor and decision for each module; compare the number of files needed to understand a typical change.
- Counter-test: Do not split a cohesive module solely because it is long or force an interface that hides no decision.
- Source: [fuente no incluida] T09-best-practices-a.md:126-137,162-173; reglas/calidad-de-codigo.md:48-67.
- Skill: module-boundaries

### G-DESIGN-03 Share proven domain knowledge
- Rule: Consolidate repeated domain knowledge once a shared rule is established, using the third occurrence as the default abstraction trigger.
- Why: Duplicated rules drift, while premature unification can erase real differences.
- Check: Locate each occurrence, compare its business meaning and change history, and review the common abstraction.
- Counter-test: Keep lookalike cases separate when their meanings or change reasons differ; an established invariant may require one authority before three copies.
- Source: [fuente no incluida] T09-best-practices-a.md:108-119; reglas/calidad-de-codigo.md:80-84.
- Skill: simple-design

### G-DESIGN-04 Prefer composition for variable behavior
- Rule: Assemble interchangeable behavior from collaborators instead of introducing inheritance by default.
- Why: Composition limits coupling to parent internals.
- Check: Inspect new inheritance hierarchies for substitution and compare them with a collaborator-based design.
- Counter-test: Use inheritance when a stable subtype contract and framework integration make it the clearer fit.
- Source: [fuente no incluida] T09-best-practices-a.md:144-155.
- Skill: simple-design

#### Comments and documentation

### G-DOC-01 Explain non-obvious reasons
- Rule: Document rationale, constraints, and necessary section boundaries without restating obvious code.
- Why: Useful comments preserve context that code alone cannot express.
- Check: Read each changed comment against adjacent code; confirm mandatory section separators remain.
- Counter-test: Keep required API documentation, legal notices, generated annotations, and section separators even when their purpose seems obvious.
- Source: [fuente no incluida] T09-best-practices-a.md:180-208; referencia/professor-feedback.md:19,34,37; reglas/calidad-de-codigo.md:113-123.
- Skill: maintain-documentation

### G-DOC-02 Keep claims and diagrams accurate
- Rule: Update affected documentation, diagrams, and user-facing descriptions when behavior or structure changes.
- Why: Stale claims mislead reviewers and users.
- Check: Trace each changed behavior to its comments and documentation; compare architecture diagrams with current code and verify guarantees.
- Counter-test: Leave historical records intact when clearly labeled as snapshots rather than current specifications.
- Source: referencia/professor-feedback.md:9-10; [fuente no incluida] T08-author-correa.md:33-35; reglas/calidad-de-codigo.md:117-123.
- Skill: maintain-documentation

#### Error handling

### G-ERROR-01 Handle failures explicitly
- Rule: Handle expected failures at the appropriate boundary or propagate them with useful context.
- Why: Silent catches hide defects and prevent recovery.
- Check: Inspect catch blocks, failed return paths, and logs; reproduce representative failure paths.
- Counter-test: A deliberate ignored failure is acceptable only when its harmlessness is documented and observable where needed.
- Source: [fuente no incluida] T10-best-practices-b.md:93-142; reglas/calidad-de-codigo.md:127-136.
- Skill: failure-handling

### G-ERROR-02 Protect multi-step operations
- Rule: Use transactions, compensation, or a safe ordering for operations that can partially fail.
- Why: Partial writes can leave inconsistent state.
- Check: Force the second step to fail and verify rollback, compensation, or the documented safe state.
- Counter-test: Skip transactional machinery for a truly atomic single operation or an explicitly acceptable independent side effect.
- Source: reglas/calidad-de-codigo.md:131-135.
- Skill: failure-handling

### G-ERROR-03 Make retries safe
- Rule: Make repeatable operations idempotent or reject duplicate attempts consistently.
- Why: Retries and duplicate submissions must not cause unintended repeated effects.
- Check: Execute the same operation twice with the same identity and inspect state and responses.
- Counter-test: Do not deduplicate operations whose contract intentionally records each distinct invocation.
- Source: reglas/calidad-de-codigo.md:135.
- Skill: failure-handling

#### Validation and security

### G-SEC-01 Validate at trust boundaries
- Rule: Validate and bound external inputs on the authoritative server or receiving process before conversion to domain types.
- Why: Untrusted input can be malformed or exhaust resources.
- Check: Trace each external entry point to type, range, size, and authorization checks; test invalid and oversized inputs.
- Counter-test: Avoid repeating identical checks inside a trusted invariant-preserving module unless a new boundary is crossed.
- Source: [fuente no incluida] T10-best-practices-b.md:419-470; reglas/calidad-de-codigo.md:138-149.
- Skill: boundary-security

### G-SEC-02 Use context-safe output and queries
- Rule: Use parameterized queries and commands and context-appropriate escaping or safe APIs for untrusted content.
- Why: Concatenation across interpretation boundaries enables injection.
- Check: Search query, command, and HTML construction for interpolated input; test representative injection payloads.
- Counter-test: Use a documented safe API for dynamic identifiers that cannot be parameterized, with an explicit allowlist.
- Source: [fuente no incluida] T10-best-practices-b.md:419-470; reglas/calidad-de-codigo.md:142-146.
- Skill: boundary-security

### G-SEC-03 Protect secrets
- Rule: Load secrets from an appropriate secret store or environment and keep them out of source, logs, and URLs.
- Why: Exposure can grant unauthorized access and complicate rotation.
- Check: Inspect configuration and logging paths and run the available secret scanner without printing values.
- Counter-test: Public identifiers and deliberately public client configuration are not secrets; never treat a client-side secret as confidential.
- Source: [fuente no incluida] T10-best-practices-b.md:659-703; reglas/calidad-de-codigo.md:147.
- Skill: boundary-security

### G-SEC-04 Enforce shared-state invariants
- Rule: Enforce persistent invariants in the data store and protect concurrent read-modify-write operations.
- Why: Application-only checks and sequential tests can miss conflicting writers.
- Check: Inspect actual constraints and locking or conditional writes; run concurrent attempts against the relevant store.
- Counter-test: A single-writer immutable process may not need locks, but its invariant must be established.
- Source: reglas/calidad-de-codigo.md:153-158.
- Skill: safe-state-changes

### G-SEC-05 Plan data migrations
- Rule: Check existing data before tightening a constraint and provide a tested migration and recovery plan.
- Why: Existing rows can violate a new schema even when an empty database passes.
- Check: Count violating records, test on a representative safe copy, and inspect backfill and rollback steps.
- Counter-test: A new empty store with verified absence of existing data does not require a backfill.
- Source: reglas/calidad-de-codigo.md:162-170; referencia/professor-feedback.md:38.
- Skill: safe-state-changes

#### Testing

### G-TEST-01 Test behavior at the right boundary
- Rule: Add focused unit and integration tests for changed behavior and end-to-end tests for critical user flows.
- Why: Different test levels expose distinct failure modes.
- Check: Trace acceptance criteria and failure cases to assertions and run the smallest relevant suite.
- Counter-test: Do not add an end-to-end test for a trivial pure calculation when a focused test demonstrates the requirement.
- Source: [fuente no incluida] T10-best-practices-b.md:18-74; referencia/professor-feedback.md:48.
- Skill: evidence-based-testing

### G-TEST-02 Reproduce defects before fixing
- Rule: Demonstrate a defect with a failing test or repeatable reproduction before applying its fix.
- Why: A test must distinguish the faulty behavior from the corrected behavior.
- Check: Record the failing result before the fix and the passing result afterward; verify the test exercises the reported symptom.
- Counter-test: Use a documented manual or production-safe reproduction when an automated test is impractical or hazardous.
- Source: reglas/calidad-de-codigo.md:174-185.
- Skill: evidence-based-testing

#### Tooling

### G-TOOL-01 Run shared quality checks
- Rule: Run the project formatter, linter, and relevant checks using shared configuration before delivery.
- Why: Automated consistency and feedback make defects and noisy diffs easier to spot.
- Check: Inspect configuration and executed command results; review every new suppression and its reason.
- Counter-test: When a tool is unavailable or inapplicable, report the missing check and use a suitable available verification.
- Source: [fuente no incluida] T08-author-correa.md:37-45; reglas/calidad-de-codigo.md:187-190.
- Skill: quality-tooling

### G-TOOL-02 Maintain dependencies deliberately
- Rule: Pin or lock dependencies where the ecosystem supports it and review updates for compatibility and known vulnerabilities.
- Why: Reproducible dependencies reduce unexpected changes and supply-chain exposure.
- Check: Inspect dependency manifests, lockfiles, and available audit results for the changed dependency.
- Counter-test: Libraries may publish compatible version ranges while retaining a lockfile for development; do not lock out security updates indefinitely.
- Source: [fuente no incluida] T10-best-practices-b.md:606-650; [fuente no incluida] T06-book-mevn.md:356-368.
- Skill: quality-tooling

#### Version control

### G-VCS-01 Review changes before integration
- Rule: Use a feature branch and reviewed pull request with relevant checks before integrating into the shared main branch.
- Why: Review and automated checks provide an independent integration gate.
- Check: Inspect branch protection, pull request review, and check results for the proposed change.
- Counter-test: A solo offline exercise or emergency fix may use a documented alternative review process when repository policy permits it.
- Source: referencia/professor-feedback.md:49; [fuente no incluida] T10-best-practices-b.md:290-334,551-590.
- Skill: reviewed-delivery

### G-VCS-02 Keep repository history auditable
- Rule: Keep generated dependencies and build artifacts out of version control unless the project explicitly requires them.
- Why: Generated files obscure meaningful source changes and inflate history.
- Check: Inspect the staged file list and ignore rules for dependency directories and build outputs.
- Counter-test: Track generated artifacts when distribution, deployment, or course submission explicitly requires them.
- Source: referencia/professor-feedback.md:39-41.
- Skill: reviewed-delivery

#### Performance

### G-PERF-01 Measure before optimizing
- Rule: Profile a representative workload and target a measured bottleneck before adding performance complexity.
- Why: Evidence avoids optimizations that increase complexity without improving the relevant outcome.
- Check: Record baseline, workload, bottleneck, and comparable post-change measurements.
- Counter-test: Apply known necessary limits or suitable algorithms before profiling when an established resource or security constraint requires them.
- Source: [fuente no incluida] T10-best-practices-b.md:489-539; referencia/professor-feedback.md:50.
- Skill: measured-performance

## Skill map

| Skill name | Rules covered | One-line moral |
|---|---|---|
| source-ordering | G-STRUCT-01, G-STRUCT-02 | Keep source sections predictable and respect execution order. |
| module-boundaries | G-STRUCT-03, G-DESIGN-02 | Put each decision behind the right boundary. |
| meaningful-names | G-NAME-01, G-NAME-02 | Use consistent words that reveal domain meaning. |
| simple-design | G-DESIGN-01, G-DESIGN-03, G-DESIGN-04 | Model present needs without speculative complexity. |
| maintain-documentation | G-DOC-01, G-DOC-02 | Keep explanations and diagrams truthful. |
| failure-handling | G-ERROR-01, G-ERROR-02, G-ERROR-03 | Make failures and retries safe and observable. |
| boundary-security | G-SEC-01, G-SEC-02, G-SEC-03 | Treat external input and secrets as trust-boundary concerns. |
| safe-state-changes | G-SEC-04, G-SEC-05 | Preserve invariants across concurrent writes and migrations. |
| evidence-based-testing | G-TEST-01, G-TEST-02 | Verify behavior with tests that can expose failures. |
| quality-tooling | G-TOOL-01, G-TOOL-02 | Run reproducible checks and manage dependencies intentionally. |
| reviewed-delivery | G-VCS-01, G-VCS-02 | Make integration reviewable and history useful. |
| measured-performance | G-PERF-01 | Optimize demonstrated bottlenecks. |
