# Calidad de código: ley del worker

Gobierna todo el código de OriginPass (Python 3.12, Django 5.2). Las excepciones de Django están en `reglas\global-rules.md`, sección "Aplicación a OriginPass (Django)"; esa sección prevalece sobre las reglas genéricas.

## Lectura obligatoria
- Habilidades: `habilidades\source-ordering\SKILL.md` y `habilidades\meaningful-names\SKILL.md`, más las que liste la tarea. Lee un `references\` solo si tocas esa tecnología.
- Reglas: consulta `reglas\global-rules.md` por identificador (G-...). No leas el archivo completo.

## Barra de calidad
- Cada archivo Python: comentarios separadores de sección (`# --- Section ---`); imports de biblioteca estándar, después de terceros, después propios; nombres en orden alfabético dentro de cada sección. El cuerpo de cada función conserva su orden lógico.
- Solo inglés en identificadores, comentarios, docstrings y nombres de archivo. El texto de interfaz va en español mediante `gettext`.
- Sin código muerto ni código comentado. Sin `Any` en anotaciones. Sin helpers genéricos. Sin funciones sueltas en servicios ni utilidades: van como métodos de clase. Las vistas, las señales y los hooks de Django son excepciones documentadas.
- Conserva el comportamiento salvo que la tarea pida cambiarlo. Lista en el reporte cada cambio de comportamiento.
- Toca solo las rutas PROPIAS de la tarea.

Hecho = los comandos de verificación de la tarea pasan. Incluye sus resúmenes en el reporte.