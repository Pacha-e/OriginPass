# Demo Ready — OriginPass Sprint 3 → Entregable 3

## Para mañana — qué hacer

### 1. Arrancar
```bash
cd "D:\Universidad\Proyecto integrador 1\OriginPass"
docker compose up -d db
.venv/Scripts/python.exe manage.py migrate
.venv/Scripts/python.exe manage.py seed_demo
.venv/Scripts/python.exe manage.py runserver
```

**ABRE el navegador en:** http://127.0.0.1:8000

### 2. Lo que vas a mostrar
| # | Acción | Franja | Score |
|---|--------|---------|-------|
| 1 | Home (landing orgánica) — cómo aparece al entrar | 00:00-00:30 | Landing |
| 2 | Login — muestra registro de intentos (bloqueo después de 5 fallos) | 00:30-01:00 | FR57 |
| 3 | Register/Apply company → approval by admin | 01:00-01:30 | FR15/16 + email |
| 4 | Create product → download QR code | 01:30-02:00 | FR19-22 |
| 5 | Public verification page (from phone/360px) | 02:00-02:30 | UR06 — cadena visible |
| 6 | Transfer product (ofertar a otro usuario) | 02:30-03:00 | FR35-40 |
| 7 | Buyer claims with passport code + transfer code | 03:00-03:30 | FR40 |
| 8 | Analytics dashboard — duplicate scan alert | 03:30-04:00 | FR49-52 |
| 9 | Admin overview — totals + revoke product | 04:00-04:45 | FR42/FR50 |
| 10 | Revocation — reason visible on public page | 04:45-05:00 | FR41 |

### 3. Correo (backend consola)
Los emails se ven en la terminal donde corre runserver — `DEFAULT_FROM_EMAIL` es
test@example.com, no hace falta SMTP para la demo.

### 4. Qué está abierto (pendiente Sprint 4)
- Perfil público empresa (FR18) — creado pero necesita más polish
- Auditoría filters (FR44) — modelo ok, vista pendiente
- Bulk CSV upload (FR27—Could)
- English switch (UR05 — Could)
- Publicar hash externo (FR56 — Sprint 4)

### 5. Video YouTube
Edita `docs/sprint-3-demo-runbook.md` antes de grabar. La demo toma ~4 minutos.

## Estado técnico
- Commit: `185a35d` en rama `sprint-3-mvp` (pushed)
- Tests: 248+ verdes (incl(9 transfer + 9 verification + 5 revoke + 6 login_throttle)
- Migraciones: 0005 alert + 0006 transfer_code OK

## FAQ rápido
Q: ¿El brand/logo?  
A: `docs/brand/originpass-mark.svg` — paleta terracota/verde, WCAG-validated.

Q: ¿Backlog con issues?  
A: https://github.com/Pacha-e/projects/> 1 — etiquetas `sprint-3` y `sprint-4`.

Q: ¿Demo rota?  
A: `docker compose down -v && up -d && migrate && seed_demo` — regenera todo.
