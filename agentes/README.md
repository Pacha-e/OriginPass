# agentes/: método de trabajo con workers para OriginPass

Carpeta de método para coordinar workers (agentes de código) sobre el repositorio OriginPass. Se adaptó desde un proyecto previo con otro stack; las piezas de ese stack quedan solo como referencia en `habilidades\_referencia-otros-stacks\` y `referencia\`.

## Contenido

- `reglas\`: reglas globales (`global-rules.md`, con la sección Django al inicio) y ley de calidad (`calidad-de-codigo.md`).
- `habilidades\`: una carpeta por principio, con `SKILL.md`. Se cargan según la tarea.
- `flujo\`: contrato del worker (`worker-preamble.md`), formatos (`fmt\`), plantillas de issues y PR (`plantillas-issues\`, `plantillas-pr\`) y `verificar.ps1`.
- `referencia\`: documentos históricos del método original. No se editan.

## Aplicación a OriginPass

- Stack: Python 3.12, Django 5.2, PostgreSQL 17.
- Excepciones de Django (orden de `INSTALLED_APPS` y `MIDDLEWARE`, `urlpatterns`, migraciones inmutables, vistas basadas en función, orden de plantillas) en `reglas\global-rules.md`.
- Idioma: código y comentarios en inglés; texto de interfaz en español mediante `gettext` y `locale/`.
- Estilo: separadores de sección, imports ordenados (ruff, regla I) y nombres en orden alfabético dentro de cada sección.

## Cómo trabaja el orquestador con workers

1. Cada tarea declara rutas PROPIAS (escritura), rutas de LECTURA, habilidades a cargar y comandos de verificación.
2. El worker solo escribe en sus rutas propias. Los archivos compartidos (`config\settings.py`, `config\urls.py`, `pyproject.toml`, `requirements*.txt`, `docker-compose.yml`, `.env*`) se tocan solo si la tarea los lista.
3. El worker no hace git (commit, push, reset, stash, clean) ni instala dependencias. Esas acciones requieren permiso del usuario.
4. Antes de dar una tarea por hecha, el orquestador ejecuta las compuertas que la tarea pida, revisa el diff y confirma que no hubo escrituras fuera de las rutas propias.
5. El reporte del worker sigue el formato STATUS, OUT, FIND, NEED y RISK, con una línea por archivo cambiado y su motivo.
6. Si un worker necesita una acción prohibida, escribe `NEED:` en lugar de improvisarla.

## Verificación

Desde cualquier directorio:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File agentes\flujo\verificar.ps1 -DatabaseUrl "<postgresql://usuario:clave@host:puerto/base>"
```

Compuertas, en orden y desde la raíz del repositorio. Se detiene en el primer fallo:

1. `ruff check .`
2. `ruff format --check .`
3. `manage.py makemigrations --check --dry-run`
4. `manage.py test --noinput` (suite completa, unos 6 minutos; PostgreSQL 17 debe estar levantado)

- `-Python` apunta por defecto al venv `D:\OriginPass-D4-orq\venv\Scripts\python.exe`.
- `SECRET_KEY` se toma del entorno. Si no existe, el script usa un valor de prueba solo dentro del proceso.
- El valor de `DATABASE_URL` no se imprime, y el script restaura las variables de entorno al terminar.

## Procedencia

- Las citas `[fuente no incluida]` en `reglas\global-rules.md` apuntan a documentos del método original que no se copiaron aquí.
- Las habilidades que mencionaban otros lenguajes llevan la línea "Ejemplos de otros lenguajes se ignoran; aplica el principio a Python/Django.".

## Estado de la validación

- `verificar.ps1`: sintaxis validada con el parser de PowerShell (0 errores). No se ejecutó de extremo a extremo porque el PostgreSQL 17 del repositorio (`127.0.0.1:55432`) no respondía.