"""What the Deliverable 3 presentation says: the slides and the script, in Spanish.

The presentation is given in Spanish, so its text is Spanish; the code and the
project documentation stay in English, as the pedagogical agreement requires.
Every figure here was read from the project: the test count from continuous
integration, the requirement states from the backlog, the limits from the code.
"""

SLIDES = [
    {
        "kind": "cover",
        "eyebrow": "Entrega 3 · Revisión del Sprint 3",
        "title": "OriginPass",
        "lead": "El MVP: el pasaporte de cada producto, su recorrido y lo que lo protege",
        "slogan": "El origen no se imita.",
        "who": "Emmanuel Hernández Melo · Equipo 1\n"
        "ST0251 Proyecto Integrador 1 · Universidad EAFIT · 2026-2",
        "say": (
            "Presento OriginPass, del equipo 1. Lo desarrollo de forma individual, con los "
            "roles de Product Owner, Scrum Master y desarrollador, como se acordó con el "
            "profesor. Esta es la revisión del Sprint 3: la entrega en la que el producto "
            "funciona de punta a punta."
        ),
    },
    {
        "kind": "cols",
        "eyebrow": "El pitch",
        "title": "Comprar algo original no debería depender de confiar en el vendedor",
        "cards": [
            {
                "title": "El problema",
                "text": "Una imitación hecha a máquina se vende al lado de un sombrero "
                "vueltiao tejido en Tuchín. El comprador no puede distinguirlos y el "
                "artesano pierde la venta y la reputación de su oficio.",
            },
            {
                "title": "La solución",
                "text": "Un pasaporte digital para cada unidad física, con un QR que "
                "cualquiera verifica desde el teléfono, sin cuenta ni aplicación, y el "
                "recorrido completo del producto.",
            },
            {
                "title": "Para quién",
                "text": "Talleres artesanales, aun sin NIT ni registro; empresas formales; "
                "distribuidores y tiendas; y el comprador, en la tienda o en el mercado.",
            },
        ],
        "say": (
            "El problema: un comprador no tiene cómo saber si una artesanía es original, y "
            "el productor no puede demostrar que una pieza concreta es suya. En Colombia, "
            "la Tejeduría Zenú, que protege el sombrero vueltiao, tiene una sola "
            "autorización de uso registrada en quince años. La solución es un pasaporte por "
            "unidad, verificable por cualquiera, que además cuenta por qué manos pasó."
        ),
    },
    {
        "kind": "cols",
        "eyebrow": "Dónde estábamos y dónde estamos",
        "title": "Tres sprints, cada uno sobre el anterior",
        "cards": [
            {
                "title": "Sprint 1",
                "text": "Cuentas y empresas: postular, revisar y aprobar o rechazar "
                "con un motivo escrito.",
                "num": "18 de 18 requisitos · 80 pruebas",
            },
            {
                "title": "Sprint 2",
                "text": "El pasaporte: registrar un producto, su código único, su QR y la "
                "página pública de verificación.",
                "num": "22 de 22 requisitos · 179 pruebas",
            },
            {
                "title": "Sprint 3 · hoy",
                "text": "El recorrido: entregas firmadas, analítica que detecta copias, "
                "anulación, panel del administrador y la identidad de marca.",
                "num": "22 de 22, y 14 del Sprint 4 · 314 pruebas",
                "on": True,
            },
        ],
        "say": (
            "El Sprint 1 dejó lista la verificación de empresas. El Sprint 2, el pasaporte "
            "y la página pública. El Sprint 3 cierra el ciclo: el producto ya tiene "
            "recorrido. Se entregaron los 22 requisitos del sprint, y de paso 14 de los 18 "
            "requisitos planeados para el Sprint 4."
        ),
    },
    {
        "kind": "steps",
        "eyebrow": "El ciclo completo",
        "title": "Lo que ya se puede hacer, de principio a fin",
        "steps": [
            "El taller registra el producto y recibe su pasaporte y su QR",
            "El comprador escanea: veredicto Auténtico y el recorrido",
            "El taller lo entrega a un distribuidor, que lo acepta",
            "El distribuidor lo vende y da un código de entrega",
            "El comprador lo pone a su nombre con los dos códigos",
            "La analítica avisa si el mismo QR aparece en dos regiones",
            "Si se pierde o lo copian, el pasaporte se anula",
            "El administrador audita cada decisión firmada",
        ],
        "say": (
            "Estos son los ocho pasos que voy a mostrar en la aplicación. Cada uno es un "
            "requisito del backlog con su prueba automática."
        ),
    },
    {
        "kind": "statement",
        "eyebrow": "Demostración",
        "title": "Ahora, en la aplicación",
        "lead": "El recorrido completo con los datos de demostración: un taller de Tuchín, un "
        "distribuidor en Montería, un comprador y el administrador.",
        "say": (
            "Paso a la aplicación. Si algo falla en vivo, está el video del recorrido, "
            "grabado con la misma secuencia."
        ),
    },
    {
        "kind": "split",
        "eyebrow": "Cadena de custodia",
        "title": "Cada mano por la que pasa el producto queda firmada",
        "points": [
            "Solo quien tiene el producto puede entregarlo; a cualquier otro se le dice "
            "por qué no [FR35, FR38]",
            "Quien recibe acepta o rechaza; solo lo aceptado entra al recorrido [FR36, FR37]",
            "Un producto anulado no se puede entregar [FR39]",
            "El comprador lo pone a su nombre con el código del pasaporte y el de entrega [FR40]",
            "Una sola oferta abierta por producto: la base de datos impide venderlo dos veces",
            "Cada entrega aceptada se firma y se encadena con la anterior [DBR05, DBR06]",
        ],
        "shot": "11-empresa-detalle-oferta.png",
        "say": (
            "La cadena de custodia es la pieza central del MVP. El producto sigue a nombre "
            "de quien lo entrega hasta que el otro lo acepta. Cada entrega lleva un código "
            "propio, y con ese código y el del pasaporte el comprador final lo pone a su "
            "nombre. La regla de una sola oferta abierta está en la base de datos, no solo "
            "en la vista, para que dos peticiones simultáneas no puedan venderlo dos veces."
        ),
    },
    {
        "kind": "split",
        "eyebrow": "Verificación pública",
        "title": "Lo que ve el comprador al escanear",
        "points": [
            "Tres respuestas: Auténtico, Anulado o No encontrado, en palabras y no solo en color",
            "El recorrido completo del producto, sin mostrar el correo de nadie [FR32]",
            "Cada escaneo guarda la región y el tipo de dispositivo, sin datos personales [FR33]",
            "Hasta 60 escaneos registrados por hora desde una dirección; el veredicto se "
            "responde siempre [FR58]",
            "Diseñada para un teléfono de 360 px y una conexión 3G",
        ],
        "shot": "05-veredicto-autentico.png",
        "say": (
            "La página pública es la única que ve alguien sin cuenta, así que es la más "
            "simple. Muestra el veredicto como un sello, los datos del producto como la "
            "página de un pasaporte, y el recorrido. Una auditoría encontró que mostraba "
            "los correos de los compradores; se corrigió y hay una prueba que lo impide."
        ),
    },
    {
        "kind": "split",
        "eyebrow": "Analítica",
        "title": "Un QR se puede fotografiar. Dos lugares a la vez, no.",
        "points": [
            "Escaneos por día en 7, 30, 90 o 365 días, comparados con el periodo anterior "
            "[FR46, FR52]",
            "Escaneos por región y por producto [FR47, FR48]",
            "Alerta de posible copia: el mismo pasaporte en dos regiones en menos de 24 "
            "horas [FR49]",
            "Exportación a CSV, protegida contra fórmulas inyectadas [FR51]",
        ],
        "shot": "12-empresa-analitica.png",
        "say": (
            "Un QR se puede fotografiar y reimprimir; eso ningún código lo evita. Lo que sí "
            "se puede ver es que el mismo pasaporte se escanee en Córdoba y en Bogotá el "
            "mismo día. Eso levanta una alerta en la analítica del taller, que además le "
            "muestra dónde y cuándo se verifican sus productos."
        ),
    },
    {
        "kind": "split",
        "eyebrow": "Anulación",
        "title": "Un pasaporte se puede retirar, con su motivo",
        "points": [
            "El taller anula sus productos y el administrador cualquiera, siempre con un "
            "motivo escrito [FR41, FR42]",
            "El QR pasa a responder Anulado, con la fecha y el motivo",
            "El dueño actual recibe un correo con el motivo [FR55]",
            "La decisión queda firmada en la auditoría [FR43]",
        ],
        "shot": "06-veredicto-revocado.png",
        "say": (
            "Si una pieza se pierde, se daña o la copian, su pasaporte se anula. No se "
            "borra: el comprador que la escanee ve que fue anulada, cuándo y por qué, y "
            "el recorrido sigue visible."
        ),
    },
    {
        "kind": "split",
        "eyebrow": "El administrador",
        "title": "La plataforma completa, y cada decisión firmada",
        "points": [
            "Panel con las empresas y los productos por estado [FR50]",
            "Registro de auditoría filtrable por actor, acción y fechas; arriba dice si la "
            "cadena firmada está íntegra [FR44, FR45]",
            "Suspender y reactivar empresas, con motivo [FR15, FR16]",
            "Perfil público de cada empresa aprobada [FR18]",
            "Correos de cada decisión y de cada entrega [FR53, FR54]",
        ],
        "shot": "24-admin-auditoria.png",
        "say": (
            "El registro de auditoría no es solo una lista: cada entrada firma la anterior, "
            "y la página verifica la cadena completa cada vez que se abre. Si alguien "
            "borra o edita una fila directamente en la base de datos, se nota."
        ),
    },
    {
        "kind": "table",
        "eyebrow": "Seguridad",
        "title": "Lo que se encontró atacando el sistema",
        "columns": ["Intento", "Lo que lo detiene"],
        "rows": [
            [
                "Adivinar contraseñas",
                "5 intentos fallidos en 15 minutos bloquean ese correo desde ese origen "
                "15 minutos, con el mismo mensaje de error [FR57]",
            ],
            [
                "Llenar la base con escaneos",
                "Máximo 60 registros por hora por dirección; el veredicto nunca se niega [FR58]",
            ],
            [
                "Vender un producto dos veces",
                "Una sola oferta abierta por producto, en la base de datos",
            ],
            [
                "Falsificar la región de un escaneo",
                "La región solo se lee de un CDN configurado como confiable",
            ],
            ["Fórmulas en el CSV", "Las celdas que empiezan con =, +, - o @ se neutralizan"],
            [
                "Recuperar una cuenta ajena",
                "Enlace firmado que vence y deja de servir al cambiar la contraseña [FR06]",
            ],
        ],
        "say": (
            "Estos límites no salieron de describir el sistema sino de atacarlo. El bloqueo "
            "responde con el mismo mensaje que una contraseña errada, para que quien adivina "
            "no sepa si la cuenta existe. Y el límite de escaneos nunca le niega la "
            "respuesta a un comprador: solo deja de guardar el registro."
        ),
    },
    {
        "kind": "split",
        "eyebrow": "Seguimiento del 1 de octubre",
        "title": "Pensado para el artesano y el campesino",
        "points": [
            "Una palabra simple por idea: producto, entregar, código de entrega, recibir, anular",
            "Cada botón dice qué hace: al pasar el mouse, o escrito debajo en el teléfono",
            "Un «?» junto a cada término abre su significado",
            "Cada campo explica qué pedir antes de escribir, con un ejemplo dentro",
            "La foto se toma con la cámara; texto desde 17 px y botones de 44 px",
            "Una prueba falla si vuelve el vocabulario técnico",
        ],
        "shot": "31-ayuda-que-significa.png",
        "say": (
            "En el seguimiento, el profesor señaló que uno de los usuarios es el artesano o "
            "el campesino. Ese mismo día la interfaz cambió: cada acción explica qué hace, "
            "cada término tiene su ayuda y el vocabulario técnico desapareció."
        ),
    },
    {
        "kind": "brand",
        "eyebrow": "Identidad de marca",
        "slogan": "El origen no se imita.",
        "lead": "Una P cuyo óvalo son anillos concéntricos: visto desde arriba, el sombrero "
        "vueltiao es anillos de caña flecha trenzada; leídos de nuevo, son una huella "
        "digital, la identidad que no se copia.",
        "palette": [
            ("Añil #1E2B58", "#1e2b58", "#ffffff", "Marca y acciones principales"),
            ("Caña flecha #D9C28A", "#d9c28a", "#232838", "El hilo tejido, los anillos"),
            ("Papel #F3F4EE", "#f3f4ee", "#232838", "Fondo de página"),
            ("Sello #17694A", "#17694a", "#ffffff", "Veredicto Auténtico"),
            ("Carmín #A3253C", "#a3253c", "#ffffff", "Veredicto Anulado"),
            ("Ámbar #86560A", "#86560a", "#ffffff", "No encontrado y pendientes"),
        ],
        "shot": "01-inicio.png",
        "title": "Identidad de marca",
        "say": (
            "El logo es una P cuyos anillos son a la vez el sombrero vueltiao visto desde "
            "arriba y una huella digital. El eslogan: el origen no se imita. Los encabezados "
            "van en Bahnschrift, la tipografía de los formularios oficiales, y el veredicto "
            "se presenta como la página de datos de un pasaporte."
        ),
    },
    {
        "kind": "points",
        "eyebrow": "Retroalimentación del Product Owner · 15 de octubre",
        "title": "Formales e informales, con su foto",
        "points": [
            "Un taller informal, sin NIT ni registro, describe la evidencia de su oficio; "
            "solo la lee quien revisa la solicitud",
            "Cada solicitante acepta que su perfil se publique al ser aprobado",
            "La foto de un producto se agrega o se cambia después de registrarlo",
            "Siete productos de demostración, de una empresa formal y de un taller informal",
        ],
        "note": "Cada cambio llegó con su prueba: 8 pruebas nuevas, 314 en total.",
        "say": (
            "Como Product Owner pedí tres cosas: subir la foto de un producto ya "
            "registrado, más variedad en la demostración y cubrir explícitamente a las "
            "empresas formales y a los talleres informales. Un taller sin registro ahora "
            "presenta la evidencia de su oficio, y una persona la revisa."
        ),
    },
    {
        "kind": "diagram",
        "eyebrow": "Arquitectura · Despliegue",
        "title": "Dónde corre cada parte",
        "image": "deployment-model-Deployment-model.png",
        "changes": [
            "Servicio de correo (SMTP) para avisos y recuperación de contraseña",
            "En desarrollo, los correos se imprimen en la consola",
            "La región del escaneo se lee de un CDN solo si se declara confiable",
        ],
        "say": (
            "En los tres diagramas, lo que cambió en este sprint está en naranja. En el de "
            "despliegue, lo nuevo es el servicio de correo."
        ),
    },
    {
        "kind": "diagram",
        "eyebrow": "Arquitectura · Componentes",
        "title": "Una aplicación de Django por responsabilidad",
        "image": "components-model-Component-model.png",
        "changes": [
            "accounts: bloqueo, recuperación de contraseña y correos",
            "companies: suspensión, reactivación y perfil público",
            "products: entregas, analítica, anulación y panel",
            "verification: recorrido, región, alerta y límite",
            "audit: registro filtrable con la cadena verificada",
        ],
        "say": (
            "Cada componente es una aplicación de Django con una sola responsabilidad. Las "
            "reglas de negocio viven en los modelos, la validación en los formularios y las "
            "vistas solo orquestan."
        ),
    },
    {
        "kind": "diagram",
        "eyebrow": "Arquitectura · Datos",
        "title": "PostgreSQL 17: las reglas también en la base",
        "image": "data-model-Data-model.png",
        "changes": [
            "Tabla accounts_loginattempt [FR57]",
            "Tabla products_alert [FR49]",
            "Columna transfer_code en las entregas [FR40]",
            "Restricción: una oferta abierta por producto",
            "evidence_notes y publish_consent en la empresa",
        ],
        "say": (
            "Las reglas que se pueden expresar en SQL están también en la base de datos, "
            "como el motivo obligatorio al anular o la oferta única por producto. Así se "
            "cumplen aunque alguien escriba directamente en la base."
        ),
    },
    {
        "kind": "stats",
        "eyebrow": "Cómo se verificó",
        "title": "Cada afirmación tiene su prueba",
        "stats": [
            ("314", "pruebas automáticas contra PostgreSQL 17"),
            ("22/22", "requisitos del Sprint 3 cerrados con su prueba"),
            ("14/18", "requisitos del Sprint 4 ya cumplidos"),
            ("0", "errores de lint y de formato"),
        ],
        "note": "La integración continua corre las migraciones, las pruebas, el lint y el "
        "formato en cada cambio. El Sprint 3 se fusionó en main con el CI en verde, y "
        "verify_integrity confirma que las cadenas firmadas están íntegras. De 80 pruebas "
        "en el Sprint 1 a 179 en el Sprint 2 y 314 hoy.",
        "say": (
            "Nada de lo que mostré es una afirmación suelta. Cada criterio de aceptación "
            "tiene una prueba, y los tiempos que piden los requisitos se miden en lugar de "
            "suponerse."
        ),
    },
    {
        "kind": "points",
        "eyebrow": "Lo que sigue · Sprint 4",
        "title": "Del MVP a un producto que no dependa del operador",
        "points": [
            "Publicar la cabeza de la cadena de integridad fuera del servidor; la meta es "
            "anclarla en Monad [FR56]",
            "Límite de verificaciones por minuto, con mensaje de espera [FR34]",
            "Registro masivo por CSV e interfaz en inglés [FR27, UR05]",
            "Entrevistas con artesanos y encuesta a compradores",
            "El despliegue en un servidor público",
        ],
        "say": (
            "Hoy la integridad protege contra quien tiene acceso a la base de datos, pero "
            "no contra quien opera el servidor, porque tiene la clave. Publicar la cabeza "
            "de la cadena fuera de su control cierra eso; la meta es anclarla en Monad. "
            "Y queda pendiente la investigación con usuarios reales."
        ),
    },
    {
        "kind": "close",
        "title": "El origen no se imita.",
        "lead": "Gracias. Preguntas.",
        "links": [
            "github.com/Pacha-e/OriginPass",
            "github.com/Pacha-e/OriginPass/wiki/Deliverable-3",
        ],
        "say": "Gracias. Quedo atento a las preguntas.",
    },
]
