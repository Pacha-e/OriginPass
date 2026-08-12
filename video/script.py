"""The narration and the slides of the Deliverable 1 video, in one place.

Everything downstream reads from here: the narration is spoken from `text`,
the slides are built from `slide`, and the length of each section is decided by
how long its narration turns out to be rather than by a number written here.

The narration is in Spanish because the video is presented in Spanish. The
code, the comments and the project documentation stay in English, as the
pedagogical agreement requires.
"""

VOICE = "es-CO-GonzaloNeural"

#: Spoken a little under the default, which lands around 200 words a minute and
#: is faster than a person presenting.
RATE = "-8%"

#: Seconds of silence held after each section, so one does not run into the next.
GAP = 0.45


SECTIONS = [
    {
        "id": "01-title",
        "kind": "slide",
        "slide": {
            "layout": "title",
            "title": "OriginPass",
            "subtitle": "Un pasaporte verificable para cada producto",
            "footer": "Equipo 1 · Proyecto Integrador 1 · 2026-2",
        },
        "text": (
            "Este es OriginPass, equipo uno, para Proyecto Integrador uno. "
            "OriginPass le da a cada producto físico un pasaporte que el comprador "
            "puede verificar por sí mismo, y registra cada mano por la que pasa "
            "antes de llegar a él."
        ),
    },
    {
        "id": "02-problem",
        "kind": "slide",
        "slide": {
            "layout": "statement",
            "eyebrow": "El problema",
            "title": "Comprar algo auténtico hoy significa confiar en quien lo vende",
            "body": (
                "Frente al producto, el comprador no tiene forma de distinguir "
                "un original de una copia."
            ),
        },
        "text": (
            "Comprar algo auténtico significa confiar en quien lo vende. "
            "Parado frente a un producto, el comprador no tiene manera de "
            "distinguir un original de una copia."
        ),
    },
    {
        "id": "03-problem-cost",
        "kind": "slide",
        "slide": {
            "layout": "bullets",
            "eyebrow": "A quién le duele",
            "title": "Las artesanías con denominación de origen son el caso más grave",
            "bullets": [
                "Una imitación industrial de un sombrero vueltiao se vende al lado de uno tejido en Tuchín",
                "El productor pierde la venta y, cuando la copia es mala, la reputación del oficio",
                "El comprador paga precio de original por algo que puede no serlo",
                "La denominación de origen deja de decirle algo útil a quien compra",
            ],
        },
        "text": (
            "Esto golpea más fuerte a las artesanías con denominación de origen. "
            "Una imitación hecha a máquina de un sombrero vueltiao se vende al lado "
            "de uno tejido en Tuchín, cuesta una fracción de producir, y a un metro "
            "de distancia se ve bastante parecida. "
            "De ahí salen tres consecuencias. El productor pierde la venta y, cuando "
            "la copia es mala, la reputación que carga el oficio. "
            "El comprador paga precio de artículo genuino por algo que puede no serlo. "
            "Y la denominación de origen, que existe para proteger el trabajo de una "
            "región, deja de cargar información sobre la que el comprador pueda actuar."
        ),
    },
    {
        "id": "04-alternatives",
        "kind": "slide",
        "slide": {
            "layout": "table",
            "eyebrow": "Lo que existe hoy",
            "title": "Cuatro opciones, la misma brecha",
            "columns": ["Opción", "Dónde se queda corta"],
            "rows": [
                [
                    "Certificados impresos y holdogramas",
                    "Se reproducen en lote; nada ata un certificado a una unidad",
                ],
                [
                    "Apps de verificación de marca",
                    "Cuestan más de lo que un productor pequeño puede pagar",
                ],
                [
                    "Garantías de marketplace",
                    "No llegan al punto de venta informal, que es donde duele",
                ],
                ["Sellos de origen", "Prueban que el productor califica, no que la pieza es suya"],
            ],
        },
        "text": (
            "Las opciones que existen hoy no cierran esto. "
            "Los certificados impresos y los holdogramas se reproducen en lote, y nada "
            "ata un certificado a una unidad. "
            "Las aplicaciones de verificación de marca cuestan más de lo que un productor "
            "pequeño puede pagar, y harían falta una por cada marca. "
            "Las garantías de marketplace no llegan al punto de venta informal, que es "
            "justamente donde el problema es peor. "
            "Y los sellos de origen prueban que un productor califica, no que la pieza "
            "que usted tiene en la mano salió de sus manos. "
            "La brecha es la misma en las cuatro: dicen algo del productor, y nada de la unidad."
        ),
    },
    {
        "id": "04b-evidence",
        "kind": "slide",
        "slide": {
            "layout": "evidence",
            "eyebrow": "Superintendencia de Industria y Comercio · consultado el 11 de agosto de 2026",
            "title": "La protección legal existe. Casi nadie la usa.",
            "stat": "1",
            "statLabel": "autorización de uso registrada para la Tejeduría Zenú en quince años",
            "rows": [
                ["Tejeduría Wayuú", "40"],
                ["Sombreros de Sandoná", "13"],
                ["Tejeduría San Jacinto", "6"],
                ["Tejeduría Zenú — el sombrero vueltiao", "1"],
            ],
            "note": "12 artesanías colombianas tienen denominación de origen. La mediana es 3 autorizaciones.",
        },
        "text": (
            "Y hay un dato que lo dice mejor que cualquier argumento. "
            "Colombia protege doce tradiciones artesanales con denominación de origen. "
            "Pero una denominación solo surte efecto a través de una autorización de uso, "
            "que es lo que realmente habilita a un productor a poner el nombre protegido "
            "en lo que hace. "
            "El sombrero vueltiao está protegido desde diciembre de dos mil once, bajo el "
            "nombre de Tejeduría Zenú. En quince años se ha registrado exactamente una "
            "autorización de uso. Una. "
            "La mediana de las nueve denominaciones que publican la cifra es tres. "
            "Y no es que el mecanismo no funcione: la Tejeduría Wayuú, protegida el mismo "
            "día por la resolución siguiente, tiene cuarenta. "
            "El problema no es que a las artesanías colombianas les falte protección legal. "
            "Es que esa protección se queda en el productor y nunca llega al objeto."
        ),
    },
    {
        "id": "05-team",
        "kind": "slide",
        "slide": {
            "layout": "team",
            "eyebrow": "Equipo",
            "title": "Equipo 1 — OriginPass",
            "members": [
                {
                    "name": "Emmanuel Hernández Melo",
                    "email": "ehernandem@eafit.edu.co",
                    "roles": "Scrum Master · Product Owner · Desarrollador",
                }
            ],
            "note": "Proyecto individual, acordado con el profesor antes de la Entrega 1",
        },
        "text": (
            "El proyecto lo desarrollo individualmente. Emmanuel Hernández Melo, "
            "con los roles de Scrum Master, Product Owner y desarrollador. "
            "Trabajar solo en los tres roles se consultó con el profesor y quedó "
            "aprobado antes de esta entrega, y el acuerdo de trabajo que evita que "
            "esos roles se confundan está registrado en la wiki."
        ),
    },
    {
        "id": "06-solution",
        "kind": "slide",
        "slide": {
            "layout": "statement",
            "eyebrow": "La solución",
            "title": "Un pasaporte por unidad, no por línea de producto",
            "body": (
                "Un código que cubriera un lote entero legitimaría cada copia de ese lote. "
                "La unidad es lo que se identifica."
            ),
        },
        "text": (
            "OriginPass emite un pasaporte por unidad física, no por línea de producto. "
            "Un código que cubriera un lote entero legitimaría cada copia de ese lote, "
            "así que la unidad es lo que se identifica."
        ),
    },
    {
        "id": "07-demo",
        "kind": "demo",
        "text": (
            "Esto es la aplicación corriendo. "
            "Un taller crea su cuenta y presenta su solicitud de empresa. "
            "Aquí elige la vía comercial, que es la que se verifica contra un registro "
            "oficial, y llena el nombre legal, la descripción, la ubicación y el sitio de contacto. "
            "Envía sin poner el código de registro. "
            "El sistema lo rechaza, y no con un mensaje genérico arriba de la página: "
            "pone la causa justo al lado del campo que la produjo, y marca ese campo. "
            "Ese comportamiento es un requisito del proyecto, no un detalle de estilo. "
            "Con el código puesto, la solicitud se guarda y queda en estado pendiente. "
            "Ahora entra el administrador. Ve todas las solicitudes y puede filtrarlas "
            "por cada uno de los cuatro estados: pendiente, aprobada, rechazada y suspendida. "
            "Abre la solicitud nueva. "
            "Intenta rechazarla sin escribir un motivo, y el sistema no lo deja. "
            "Esa regla no vive solo en el formulario: hay una restricción en la base de datos "
            "que también la rechaza, así que ninguna vista futura puede saltársela. "
            "Con el motivo escrito, el rechazo se guarda junto a la decisión. "
            "Y aquí está la razón de que eso importe. El dueño del taller vuelve a entrar, "
            "y ve el rechazo con el motivo textual, no un estado vacío. "
            "Puede corregir, volver a enviar, y la solicitud regresa a pendiente. "
            "El administrador aprueba. "
            "Y desde ese momento el dueño ya no puede editarla: el sistema se lo niega, "
            "y le dice exactamente por qué."
        ),
    },
    {
        "id": "08-value",
        "kind": "slide",
        "slide": {
            "layout": "bullets",
            "eyebrow": "Propuesta de valor",
            "title": "Lo que lo hace distinto de un certificado",
            "bullets": [
                "Verifica el comprador, no el vendedor",
                "Un escaneo, sin cuenta y sin instalar nada",
                "Muestra la cadena de custodia, del taller al estante",
                "Registra cada escaneo: un mismo código en dos lugares distantes es visible",
            ],
        },
        "text": (
            "Lo que separa esto de un certificado es que quien verifica es el comprador, "
            "no el vendedor. La verificación toma un escaneo, sin cuenta y sin instalar "
            "una aplicación, y muestra la cadena de custodia desde el taller hasta el estante. "
            "Y como un código QR se puede fotografiar y reimprimir, OriginPass registra "
            "cada escaneo, de modo que un mismo pasaporte apareciendo en dos lugares "
            "distantes en poco tiempo es algo que el sistema puede ver."
        ),
    },
    {
        "id": "09-requirements-1",
        "kind": "slide",
        "slide": {
            "layout": "requirements",
            "eyebrow": "Priorización MoSCoW · 77 requisitos",
            "title": "Los cinco requisitos de mayor prioridad",
            "rows": [
                ["1", "FR07", "Enviar una solicitud de empresa", "Entregado"],
                ["2", "FR08", "Exigir código de registro a empresas comerciales", "Entregado"],
                ["3", "FR09", "Aceptar artesanos sin código, marcados para revisión", "Entregado"],
                ["4", "FR13", "El administrador aprueba una solicitud pendiente", "Entregado"],
                ["5", "FR14", "El administrador rechaza guardando un motivo escrito", "Entregado"],
            ],
        },
        "text": (
            "Estos diez requisitos salieron de una priorización MoSCoW sobre setenta y "
            "siete, contrastada contra las horas realmente disponibles y no contra una "
            "lista ideal de funcionalidades. "
            "Los cinco primeros son el registro y la aprobación de empresas: enviar la "
            "solicitud, exigir el código de registro al comercial, aceptar al artesano "
            "sin él, aprobar, y rechazar guardando el motivo. "
            "Los cinco están construidos y cubiertos por pruebas automáticas."
        ),
    },
    {
        "id": "10-requirements-2",
        "kind": "slide",
        "slide": {
            "layout": "requirements",
            "eyebrow": "Priorización MoSCoW · 77 requisitos",
            "title": "Los otros cinco, y el objetivo del Sprint 2",
            "rows": [
                ["6", "FR19", "Una empresa aprobada registra un producto", "Sprint 2"],
                ["7", "FR20", "Rechazar el registro de empresas no aprobadas", "Sprint 2"],
                ["8", "FR21", "Generar un código no derivable de otro", "Sprint 2"],
                ["9", "FR22", "Generar un QR descargable de la verificación", "Sprint 2"],
                ["10", "FR23", "Que el tipo de producto coincida con el de la empresa", "Sprint 2"],
            ],
        },
        "text": (
            "Los cinco siguientes son el objetivo del Sprint dos: que una empresa "
            "aprobada registre un producto, que se rechace a quien no está aprobado, "
            "que el código de pasaporte no se pueda derivar de otro, que se genere el "
            "QR descargable, y que el tipo de producto coincida con el tipo de empresa. "
            "El sprint dos es el que hace que OriginPass haga, por primera vez, aquello "
            "para lo que existe."
        ),
    },
    {
        "id": "11-close",
        "kind": "slide",
        "slide": {
            "layout": "close",
            "title": "Porque comprar algo auténtico\nno debería depender solo de la confianza",
            "links": [
                "github.com/Pacha-e/OriginPass",
                "Wiki · Backlog · 84 pruebas automáticas sobre PostgreSQL",
            ],
        },
        "text": (
            "El código, el backlog y la documentación están en GitHub. Todo lo que se "
            "mostró corre contra PostgreSQL con ochenta y cuatro pruebas automáticas detrás. "
            "Porque comprar algo auténtico no debería depender solo de la confianza."
        ),
    },
]


def total_words():
    return sum(len(section["text"].split()) for section in SECTIONS)


if __name__ == "__main__":
    print(f"{len(SECTIONS)} sections, {total_words()} words")
    for section in SECTIONS:
        print(f"  {section['id']:22} {section['kind']:6} {len(section['text'].split()):4} words")
