"""The narration and the slides of the Deliverable 3 (MVP) video, in one place.

Everything downstream reads from here: the narration is spoken from `text`,
the slides are built from `slide`, and the length of each section is decided by
how long its narration turns out to be rather than by a number written here.

The narration is in Spanish because the video is presented in Spanish. The
code, the comments and the project documentation stay in English, as the
pedagogical agreement requires.

Deliverable 3 covers the MVP: the custody chain, the public verdict with its
seal, the analytics that see a cloned QR, and the abuse limits that keep the
public page honest.
"""

VOICE = "es-CO-GonzaloNeural"
RATE = "-8%"
GAP = 0.45


SECTIONS = [
    {
        "id": "01-title",
        "kind": "slide",
        "slide": {
            "layout": "title",
            "title": "OriginPass",
            "subtitle": "Entrega 3 — El MVP: la cadena de custodia y el veredicto público",
            "footer": "Equipo 1 · Proyecto Integrador 1 · 2026-2",
        },
        "text": (
            "Esta es la entrega tres de OriginPass, equipo uno, Proyecto "
            "Integrador uno. El producto ya existe de punta a punta: la empresa "
            "emite el pasaporte, el comprador lo verifica con un escaneo, y el "
            "sistema registra el viaje completo del producto. Esta entrega "
            "cierra el MVP."
        ),
    },
    {
        "id": "02-where-we-are",
        "kind": "slide",
        "slide": {
            "layout": "bullets",
            "eyebrow": "Dónde estábamos",
            "title": "La entrega anterior dejó lista la verificación",
            "bullets": [
                "La empresa aprobada registra un producto y descarga su QR",
                "El comprador escanea y ve el veredicto, sin cuenta",
                "Un pasaporte por unidad física, no por lote",
                "306 pruebas automáticas contra PostgreSQL",
            ],
        },
        "text": (
            "En la entrega anterior, una empresa aprobada ya podía registrar un "
            "producto, descargar su código QR, y cualquier comprador podía "
            "escanearlo y ver el veredicto sin tener cuenta. "
            "Lo que no existía todavía era el viaje del producto: quién lo tenía, "
            "a quién se lo entregó, y qué pasa cuando algo se pierde o se copia. "
            "Eso es lo que cierra esta entrega."
        ),
    },
    {
        "id": "03-custody-model",
        "kind": "slide",
        "slide": {
            "layout": "statement",
            "eyebrow": "Cadena de custodia",
            "title": "Cada mano por la que pasa el producto queda firmada",
            "body": (
                "Una transferencia aceptada es un eslabón que no se puede editar "
                "ni borrar: la base de datos lo exige."
            ),
        },
        "text": (
            "La cadena de custodia es la pieza central del MVP. "
            "Cuando el tenedor actual ofrece el producto a otra persona, se crea "
            "una transferencia en estado iniciada. La otra cuenta la acepta o la "
            "rechaza, y solo si acepta, la transferencia se vuelve un eslabón de "
            "la cadena. "
            "Cada eslabón firma al anterior con un hash encadenado, así que "
            "editar uno rompe todos los que siguen. La base de datos, no el "
            "código de la vista, es la que se niega a tocar un eslabón ya "
            "aceptado."
        ),
    },
    {
        "id": "04-demo",
        "kind": "demo",
        "text": (
            "Vamos a verlo corriendo. "
            "El taller entra y registra un producto nuevo: un sombrero vueltiao "
            "de veintiuna. El sistema le genera el pasaporte y el QR. "
            "Descarga el QR y lo imprime para ponerlo en la pieza. "
            "Ahora, desde el teléfono del comprador: escanea el código, y la "
            "página pública responde Auténtico, con el sello de la marca, la "
            "empresa que lo registró, y la cadena de custodia completa: del "
            "taller, al distribuidor, al comprador. "
            "El taller ofrece la transferencia al distribuidor escribiendo su "
            "correo y una nota que queda en la cadena. "
            "El distribuidor la acepta, y el comprador que escanea el mismo código "
            "después ve que la cadena creció: la pieza tiene una mano más. "
            "Si alguien intenta transferir un producto que no tiene, el sistema "
            "se lo rechaza con la razón, no con un error genérico."
        ),
    },
    {
        "id": "05-clone-signal",
        "kind": "slide",
        "slide": {
            "layout": "evidence",
            "eyebrow": "El QR se puede fotografiar. El pasaporte no.",
            "title": "Un mismo código escaneado en dos regiones, en 24 horas",
            "stat": "1",
            "statLabel": "alerta por escaneo duplicado, visible en la analítica de la empresa",
            "rows": [
                ["Se registra cada escaneo con región y dispositivo", "FR33"],
                ["Dos regiones en 24 horas levantan la alerta", "FR49"],
                ["La alerta apunta al escaneo sospechoso, no al original", "FR49"],
            ],
            "note": "El QR clonado responde lo mismo que el original. La cadena de escaneos es lo que lo delata.",
        },
        "text": (
            "Hay un ataque que un QR no puede evitar: fotografiarlo y reimprimirlo. "
            "OriginPass lo ve. "
            "Cada verificación registra la región gruesa del escaneo. Si un mismo "
            "pasaporte aparece en dos regiones distintas dentro de veinticuatro "
            "horas, el sistema levanta una alerta de escaneo duplicado y la "
            "empresa la ve en su panel de analítica, apuntando al escaneo "
            "sospechoso. "
            "La copia puede responder lo mismo que el original, pero no puede "
            "estar en dos países al mismo tiempo."
        ),
    },
    {
        "id": "06-analytics",
        "kind": "slide",
        "slide": {
            "layout": "table",
            "eyebrow": "Analítica de verificaciones",
            "title": "La empresa ve quién escanea sus pasaportes",
            "columns": ["Vista", "Qué responde"],
            "rows": [
                ["Escaneos por día", "Cuánta gente está verificando, y cuándo"],
                ["Distribución por región", "Dónde se está vendiendo de verdad"],
                ["Productos por escaneos", "Qué pieza está llamando la atención"],
                ["Alertas de escaneo duplicado", "Qué pasaporte fue clonado, y cuándo"],
                ["Exportar CSV", "La misma tabla, para el que analiza en Excel"],
            ],
        },
        "text": (
            "La analítica le da a la empresa la otra mitad del valor. "
            "Escaneos por día: cuánta gente está verificando y cuándo. "
            "Distribución por región: dónde se está vendiendo de verdad. "
            "Productos por número de escaneos: qué pieza está llamando la "
            "atención. "
            "Y la alerta de escaneo duplicado, que es la que delata el clon. "
            "Todo se puede exportar en CSV, porque el que analiza no siempre "
            "trabaja en el navegador."
        ),
    },
    {
        "id": "07-hardening",
        "kind": "slide",
        "slide": {
            "layout": "bullets",
            "eyebrow": "Lo que se encuentra atacando el sistema",
            "title": "Los límites que se le pusieron al abuso",
            "bullets": [
                "Cinco contraseñas erróneas en 15 minutos bloquean la dirección (FR57)",
                "60 verificaciones por hora desde una misma IP; el veredicto nunca se niega (FR58)",
                "Una sola oferta de transferencia abierta por producto",
                "El veredicto No encontrado es idéntico para todos los códigos muertos (FR31)",
            ],
        },
        "text": (
            "Estos requisitos no salieron de describir el sistema, sino de "
            "atacarlo. "
            "Cinco contraseñas erróneas en quince minutos desde una misma "
            "dirección, y esa dirección queda bloqueada otros quince. Pero el "
            "mensaje que recibe es el mismo que si la contraseña estuviera "
            "mal, así que quien intenta adivinar no puede distinguir una cuenta "
            "bloqueada de una que no existe. "
            "En la verificación pública, sesenta escaneos por hora desde una "
            "misma IP. Pasado el límite, el veredicto se sigue respondiendo, "
            "porque un comprador con un producto real no puede recibir un "
            "rechazo; solo deja de guardarse el registro. "
            "Una sola oferta de transferencia abierta por producto, porque dos "
            "a la vez era una carrera que la vista no podía cerrar. "
            "Y el No encontrado es idéntico para todos los códigos muertos: "
            "decir cuál existe y cuál no sería regalarle el mapa al atacante."
        ),
    },
    {
        "id": "08-revocation",
        "kind": "slide",
        "slide": {
            "layout": "bullets",
            "eyebrow": "Revocación",
            "title": "Un pasaporte se puede retirar, y el motivo queda público",
            "bullets": [
                "La empresa que lo emitió lo revoca con un motivo escrito (FR41)",
                "El administrador puede revocar cualquiera (FR42)",
                "El veredicto cambia a Revocado, con la fecha, en la página pública",
                "Cada revocación queda en la cadena de auditoría firmada (FR43)",
            ],
        },
        "text": (
            "Un pasaporte no es para siempre. "
            "La empresa que lo emitió puede revocarlo, y el administrador "
            "también, siempre con un motivo escrito que queda guardado con la "
            "decisión. "
            "El comprador que escanea un pasaporte revocado ve el veredicto "
            "Revocado con la fecha en que se retiró, y la cadena de custodia "
            "sigue visible, porque saber dónde se detuvo también es parte de la "
            "respuesta. "
            "Y la revocación misma queda firmada en la cadena de auditoría, "
            "igual que cada aprobación y cada transferencia."
        ),
    },
    {
        "id": "09-admin",
        "kind": "slide",
        "slide": {
            "layout": "bullets",
            "eyebrow": "El administrador",
            "title": "La plataforma completa, en una pantalla",
            "bullets": [
                "Totales de empresas y productos por estado (FR50)",
                "El registro de auditoría, filtrable por actor, acción y fecha (FR44)",
                "El estado de la cadena de auditoría, arriba de los registros (FR45)",
                "Suspender y reactivar empresas, con motivo (FR15/16)",
            ],
        },
        "text": (
            "El administrador tiene su propia pantalla. "
            "Los totales de empresas y productos por estado, que son el pulso de "
            "la plataforma. "
            "El registro de auditoría completo, filtrable por actor, por acción y "
            "por rango de fechas. Y arriba de los registros, el estado de la "
            "cadena firmada, porque una lista filtrada no dice si le quitaron "
            "filas. "
            "Suspender una empresa, con su motivo, y reactivarla, con el suyo. "
            "Todo lo que el administrador decide queda en el registro."
        ),
    },
    {
        "id": "10-numbers",
        "kind": "slide",
        "slide": {
            "layout": "evidence",
            "eyebrow": "Pruebas",
            "title": "Cada afirmación de este video está cubierta",
            "stat": "306",
            "statLabel": "pruebas automáticas contra PostgreSQL, en integración continua",
            "rows": [
                ["De 84 en la Entrega 1", "a 306 en la Entrega 3"],
                ["Cada requisito del sprint tiene su prueba", "FR32 a FR58"],
                ["La cadena firmada se verifica en cada corrida", "FR45"],
                ["La página pública carga en menos de 3 segundos sobre 3G", "UR06"],
            ],
            "note": "Ninguna prueba de interfaz compara contra el inglés: la interfaz se sirve en español.",
        },
        "text": (
            "Nada de lo que se mostró en este video es una afirmación suelta. "
            "El proyecto pasó de ochenta y cuatro pruebas en la entrega uno a "
            "trescientas seis hoy, todas contra PostgreSQL en integración "
            "continua. "
            "Cada requisito del sprint tiene su prueba, la cadena firmada se "
            "verifica en cada corrida, y la página pública se mide cargando en "
            "menos de tres segundos sobre una conexión tres G, porque ese es el "
            "requisito y la prueba lo afirma en lugar de asumirlo."
        ),
    },
    {
        "id": "11-close",
        "kind": "slide",
        "slide": {
            "layout": "close",
            "title": "El origen no se imita.\nEl pasaporte que lo prueba.",
            "links": [
                "github.com/Pacha-e/OriginPass · rama sprint-3-mvp",
                "Wiki · Backlog · 306 pruebas automáticas",
            ],
        },
        "text": (
            "El código y la documentación están en GitHub, la wiki tiene la "
            "especificación completa y el backlog con el estado de cada "
            "requisito. "
            "Trescientas seis pruebas automáticas atrás de cada afirmación. "
            "El origen no se imita. El pasaporte que lo prueba."
        ),
    },
]


def total_words():
    return sum(len(section["text"].split()) for section in SECTIONS)


if __name__ == "__main__":
    print(f"{len(SECTIONS)} sections, {total_words()} words")
    for section in SECTIONS:
        print(f"  {section['id']:22} {section['kind']:6} {len(section['text'].split()):4} words")
