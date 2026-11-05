# Professor grading feedback (verbatim, Spanish source)

Provided by the student on 2026-11-01. Format per row: criterion (max points) — observation — score.

## Entregable 1 Parte 1 (repo https://github.com/Pacha-e/KeyRing, GCP http://34.58.221.78) — final 2.65

- Fecha - commits: Septiembre 2 - 32 commits
- Tipo de Dashboard: Propiedades
- Diagrama clases (5) — "ojo que nada que ver con los acuerdos" — 1
- Diagrama arquitectura (5) — "ojo que nada que ver con los acuerdos y no me mapea la realidad del código" — 0
- Documento guia estilo (3) — "muy bien, pero separar cada herramienta en su respectiva sección" — 3
- Documento reglas (3) — "se ve bien, verificar que si siga las reglas del curso" — 3
- Store (localstorage) y seeders (4) — "seeders no están separados, lo metieron en servicios. Tiene un storage que junta todo, y muy desorganizado, con funciones raras que no entienden" — 0
- DTOs (3) — "muy bien, pero ojo comentarios en español que quizás no sirvan" — 3
- Interfaces (3) — "ojo tienen ownerId, debería ser userId, tienen properties en user que no va. En general bien." — 2
- Services (5) — "desorden horrible de archivos. Ojo que los services no siguen el formato clases métodos, y ojo que utiliza métodos genericos un solo findall para todo, etc." — 0
- Utils — "Ojo los labels quizás en otro lado como enums"
- Rutas (10) — "bien, ojo usaron importaciones dinamicas" — 10
- Views (10) — "no hay comentarios que separen los elementos principales en la sección de script, no hay orden alfabetico en importaciones. Super desorganizado, llamados de métodos de la nada" — 3
- Components (10) — "demasiado texto en español, ojo quitar tabla reutilizable, algunos problemas similares a las views" — 5
- 7-14 páginas distintas (8) — "bien" — 8
- 2 cruds (8) — "bien" — 8
- 2 selectores en 2 páginas (5) — "bien" — 5
- 2 componentes reutilizables (5) — "bien" — 5
- 2 librerías JavaScript (5) — "chartjs, mapa" — 5
- Despliegue (8) — "muy bien" — 8
- Puntos restantes — "mezcla inglés español, unos funciones con un formato que no entienden <T>. Ojo con ese desorden de archivos tienen enums en interfaces, tienen seeders en services, tienen storage en service, pero tmb tiene store. Ojo utilizar piniaConfig que fácilita el uso de localstorage tal cual lo definimos en el curso. Revoltura de cosas, constantes, interfaces y funciones (a veces todo eso en un solo archivo), delegar bien la responsabilidad de cada capa. Que me quede claro que puedo y que no puedo hacer o meter en cada carpeta." — 0.8

## Entregable 1 Parte 2 (repo https://github.com/Salcedo0/keyring/, GCP http://34.121.178.26/) — final 2.4

- Fecha - commits: 10 commits, the rest outside the deadline
- Diagrama clases (5) — "se ve bien" — 5
- Diagramas de arquitectura (5) — "se ve bien" — 5
- Correcciones entregable 1 (20) — "siguen múltiples errores de la entrega 1, no aplicaron separar alfabeticamente, importaciones externas, luego internas, utilizar comentarios separadores, siguen con clases con la T" — 13
- Documento guia estilo backend (5) — "debe ser separado por herramientas que se usan, qué cómo, cuándo, dónde" — 5
- Documento reglas backend (5) — "muy muy regular, reglas que no se cumplen, reglas que faltan, no se habla de dtos en controllers" — 2
- Código Frontend (rutas, vistas, servicios, etc) (25) — "separar alfabateicamente, importaciones externas, luego internas, utilizar comentarios separadores, utils deben ser clases con métodos, http debe ir en util, o organizarlo como una super clase service. Nada que ver el orden y uso de los services con lo que vimos en clase (desde el view) y al acuerdo que llegamos. Uso de composbales no definido." — 14
- Código Backend (módulos, controladores, servicios, entidades) (25) — "no está lo de migraciones. Funciones por fuera de las clases, pasar a utils o a otros lados como métodos. Función aRespuesta ese nombre no dice absolutamente nada. En general muy bien el backend." — 20
- Despliegue (10) — "despliegue basado en repo actualizado, que incluye commits por fuera del tiempo de entrega" — 4
- Reducciones de nota — "Tiene un montón de commits nuevos que no aplicaban y que hacen que toque revisar el código manual desde versiones anteriores" — -1
- Comentarios globales — "El repositorio presenta entrega de código solo de Juan andres (nota Juan Andres 2.4), Emmanuel solo tiene dos commits de despliegue (dockerfiles) pero presenta un repo con otro código (nota Emmanuel 1.6), Paula no presenta commits (Nota Paula 1.2)."

## Student-supplied general best-practice list (Spanish, to be researched in depth)

1. Legibilidad y claridad: prioriza legibilidad; KISS; convenciones de nomenclatura descriptivas; formato e indentación consistentes (Prettier/Black).
2. Principios de diseño: DRY; SRP; composición sobre herencia; encapsulamiento.
3. Documentación y comentarios: comentar el "por qué", no el "qué"; evitar comentarios obvios; documentación actualizada.
4. Control de calidad y pruebas: tests unitarios e integración; manejo de errores sin excepciones silenciosas; refactorización constante; linters (ESLint).
5. Control de versiones y equipo: Git; ramas y Pull Requests con code review, nunca directo a main; estructura limpia de archivos y carpetas.
6. Seguridad y rendimiento: validar y sanitizar entradas (SQLi, XSS); no optimizar prematuramente, perfilar con datos reales.
