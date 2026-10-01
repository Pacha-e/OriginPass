# OriginPass — Plan de cierre de MVP (Entregable 3) — 2026-09-30

**Mandato (Emmanuel, Discord):** terminar el MVP completamente; cerrar todas las issues posibles;
UI sustancialmente mejorada en TODAS las páginas (especialmente la pública de QR — más orgánica,
entretenida, viva, confiable); council multi-LLM; todo YOLO; calidad senior+.
**Ajuste:** Codex NO disponible → se ejecuta con Claude (arquitecto chairman) + Kimi (worker
headless de masa) + Hermes (HEAD/orquestación/QA). OR-01 se aplica: workers hacen volumen, HEAD
integra y certifica con tests reales.

---

## 1. Estado real verificado (2026-09-30)

- Repo: `D:\Universidad\Proyecto integrador 1\OriginPass` (clone gh: Pacha-e/OriginPass)
- Rama activa: `main` (origin/main al día). 158 archivos, ~8.8K LOC py+html+css.
- Stack: Django 5.2 + PostgreSQL 17 (docker) + templates i18n (es). 179 tests ✓ (Sprint 2 cerrado).
- **41 issues abiertas** del backlog (Sprint 3 completo + Sprint 4 completo + 1 fuera de sprint).
- Entregable 3 (del .docx) pide: diagramas UML mejorados (deployment, componentes, RDS),
  imagen corporativa (logo + slogan + paleta + screenshots integrados), repo sano, video 4-5 min,
  backlog actualizado, actas semanales, retrospectiva, Sprint Review.
- Wiki (`OriginPass-wiki`): Deliverable-2.md y Sprint-2-Review.md existen y son de alto nivel.
  Deliverable-3.md no existe todavía.
- UI actual: 1 stylesheet plano `static/css/originpass.css` (688 líneas), paleta sobria indigo,
  sin framework, sin JS — correcta pero plana.

## 2. Qué falta para terminar el MVP (mapa issue → entregable)

### Sprint 3 (cadena de custodia + analítica) — TODO el cuerpo funcional del MVP
- Cuentas/abuso: FR57 lockout tras 5 fallos/15 min (el login hoy es ilimitado), FR58 cap de 60 scans/hora.
- Custodia (FR35–FR40 + DBR05/06): transferir, aceptar/rechazar, append a cadena, rechazar
  a no-holder y a revocado, claim de comprador con código de transferencia. DBR05/06 ya tienen tabla+invariantes.
- Verificación pública enriquecida (FR32 cadena visible, FR33 ya contabilizado; UR01/UR06 ya medidos).
- Analítica empresa (FR46–FR50 + DBR07/09): conteos por fecha, región, top productos,
  alerta de QR clonado (un código en >1 región en ventana corta — el "wow" del pitch),
  totales admin (FR50). Retención 24 meses (DBR09).
- Usabilidad Sprint 3: UR07 tab, UR09 contraste 4.5:1 (paleta vieja fallaba — CSS nueva debe certificarlo).
- Perfil público de empresa (FR18, Should).

### Sprint 4 (revocación, auditoría dura, notificaciones, cierre)
- FR41/FR42 revocar (empresa y admin) + DBR08/FR43–FR45 auditoría append-only con cadena de firma (ya existe
  `audit/integrity.py` con hash chain — Big Win) + FR44 filtros de auditoría + FR56 publicar head de la
  cadena a servicio externo (issue #78).
- FR06 reset de contraseña por email (Should).
- FR15/16 suspender/reactivar empresa (Should).
- FR51 exportar analítica CSV (Should), FR52 tendencia vs período previo (Could).
- FR53/54/55 emails (console backend demo: se registran y se prueban; envío real es post-MVP).
- FR34 rate limit attempts (Should, complementa FR58), FR27 bulk CSV (Could), UR05 language switch (Could).

### UI overhaul transversal (lo que Emmanuel pide explícito)
- Nueva paleta orgánica (terracota/verde/canela — identidad alineada a Handoo/artesanías),
  ilustración/micro-detalle de fibra/firma, paleta contrast-safe (UR09 cuantificado).
- Rediseñar: home landing con hero + historia, login/register, dashboard empresa, registro,
  lista productos, perfil, admin review, **verdict público (la estrella)**, 403/404/500.
- Entregable 3.2 pide logo + slogan + paleta + screenshots → se produce un mini design-system en
  `docs/brand/` con capturas Playwright antes/después.

### Entregable 3 (artefactos de curso)
- 1.1 Deployment diagram actualizado (añade integrity-verify, publish-head, emails, pgAdmin).
- 1.2 Component diagram (apps Django + relationships).
- 1.3 RDS actualizado (products, custody_transfers, scan_events, audit_entries con hash chain).
- 2 Corporate image: logo + slogan + paleta + 4-6 screenshots.
- 3 Repo: README actualizado a MVP, requirements auditado, issues cerrados con refs.
- 5 Backlog actualizado, actas semanales, retrospectiva Sprint 3→4; wiki Deliverable-3.md.
- (El video 4-5min y su demo presencial son de ustedes: yo produzco runbook + capturas listas.)

## 3. Concilio LLM (cómo se orquesta)

| Rol | Agente | Qué hace |
|---|---|---|
| **HEAD / Orquestación** | Hermes (Kimi K3) | Plan, dispatch, integración, QA final, gate de commits (no commit without tests ✓) |
| **Chairman / Arquitecto** | Claude Code CLI | Decisiones de diseño senior: módulos nuevos (custody, analytics), tipos, boundaries, invariants, revisión de patrones |
| **Worker A (código volumen)** | Kimi CLI headless | Apps nuevas, vistas, tests masivos, migraciones, seeders |
| **Worker B (apariencia)** | Kimi CLI headless | CSS system, templates, i18n strings, static + screenshots previos |
| **Revisor** | Claude Code (short calls) | Security/anti-pattern scan + senior review del diff antes de commit |
| **QA realista** | Hermes + Playwright | Suite Django ✓, makemigrations --check, compilemessages, 360px + 3G budget, contrast checker, capturas |

**Protocolo:** cada fase pasa por plan(claude)→implementar(kimi)→review(claude)→tests(Hermes)→fix si rojo.
Sin fase que cierre sin suite en verde. Pre-commit scanning lo hace Claude (no se corre codex).

## 4. Fases (min 1 commit legible por fase)

| # | Fase | Issues cerradas | Tool principal |
|---|---|---|---|
| **B0** | Audit + console: uso real de Django admin/audit ya en repo; catalog de páginas + capturas "antes" | — | Hermes |
| **B1** | Design system v2 + base.html nuevo + landing/home + auth redesign; capturas contrast 4.5:1 (UR09, UR07) | UR09, UR07 | Kimi-B + Claude-review |
| **B2** | App `custody` (FR35–FR40 + DBR05/06 + transfer codes + chain timeline) | 6 must + 1 should | Kimi-A + Claude-arch |
| **B3** | Login throttle FR57 + scan cap FR58 + FR34 rate limit + tests de abuso | FR57, FR58, FR34 | Kimi-A |
| **B4** | Verification page rediseño premium (verdict hero, pasos, historia, CTA) + FR32 chain render + perfil público FR18 | FR32, FR18 | Kimi-B |
| **B5** | Analytics dashboard empresa (FR46/47/48), alerta QR clon FR49, admin totals FR50, retención DBR09 | FR46–FR50, DBR09 | Kimi-A |
| **B6** | Revocation FR41/42 + audit filters FR44 + suspend/reactivate FR15/16 + password reset FR06 | FR41, FR42, FR43 (ya en audit), FR44, FR45, FR15, FR16, FR06 | Kimi-A |
| **B7** | Analítica avanzada: CSV export FR51 + tendencia FR52 + bulk CSV FR27 + English switch UR05 + emails FR53/54/55 (console backend) + FR56 publish head (implementación con mock externo + doc) | todas las anteriores | Kimi-A |
| **B8** | Entregable 3: 3 diagramas draw.io + brand kit + screenshots + Deliverable-3.md + actualizar wiki (Backlog, Reunions, Retrospective, Sprint-3-Review.md) | — | Hermes + Claude-doc |
| **B9** | Certificación final: suite completa ✓, `makemigrations --check`, `compilemessages`, i18n completitud, 179→N tests, wiki en `:main` | — | Hermes |

## 5. Definition of Done (cada issue)
- Test(s) que afirman el criterio exacto del requerimiento (con tiempos cuando aplica).
- Migración + `makemigrations --check` en verde.
- Strings en inglés fuente + `locale/es` compilado.
- Commit one-concern, mensaje en inglés estilo del repo.
- Issue cerrado con comentario que referencia test y página wiki afectada.

## 6. Riesgos / decisiones
- **FR56** (publicar head externo): en MVP se implementa con proveedor pluggable (mock + doc de
  despliegue real). No se inventa "hecho" donde no lo está — el test afirma la llamada, no el efecto.
- **Emails FR53-55**: se implementan con backend por configuración (console en dev, SMTP en prod docs).
- **Podría faltar cuota Claude**: fallback chairman → Kimi K3 directo. Se reporta limpio si ocurre.
- **No se toca `Pacha` rama ni Monad repo** — este es el OriginPass universitario (Django), verificado.

## 7. Entrega esperada
- Repo con MVP funcional completo (Sprints 3 y 4 Must/Should cerrados, Coulds los máximos posibles).
- 41 issues abiertas → cerradas o etiquetadas post-MVP con razón.
- Wiki con Deliverable-3.md + Sprint-3/4 artifacts + diagramas nuevos + brand kit.
- README listo para entregar. Video runbook para Emmanuel (eller demo en clase).
