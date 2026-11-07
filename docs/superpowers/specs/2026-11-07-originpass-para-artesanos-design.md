# OriginPass para artesanos — diseño

Fecha: 7 de noviembre de 2026 · Autor de las decisiones: Emmanuel Hernández Melo · Redacción: Claude

## 1. Por qué

OriginPass lo van a usar artesanos y campesinos que manejan poco la tecnología, por ejemplo un tejedor de Tuchín con un celular básico. El recorrido que se hizo el 7 de noviembre, en local y con un celular de 390 px, mostró que hoy esa persona no puede valerse sola. Lo que encontramos:

- **Inscripción.** Nueve campos en una página, con palabras como «Razón social», «Vía de verificación» o «Código de registro oficial». El tipo de empresa viene marcado en «Empresa comercial» y la casilla de consentimiento es diminuta. Además, después de crear la cuenta la persona tiene que volver a iniciar sesión.
- **Navegación.** El menú tiene ocho enlaces y ocupa media pantalla. Al entrar no hay una pantalla de inicio: se cae en la ficha de la solicitud.
- **Listas.** Las tablas de productos y entregas se salen de la pantalla y muestran códigos largos.
- **Traspaso.** Quien recibe tiene que escribir un UUID de 36 caracteres.
- **QR.** En ningún lado se explica para qué sirve. La web solo descarga un QR suelto; las hojas imprimibles (FR61) solo se pueden sacar con un comando del servidor.
- **Registro de productos.** Cada pasaporte es una pieza física, así que 20 sombreros iguales son 20 formularios. El botón de la foto aparece en inglés.

Las capturas están en el scratchpad de la sesión. Para regenerarlas se usa la herramienta de la sección 9.

**Qué significa terminado.** Un artesano sin ayuda puede hacer en el celular estas cinco cosas:

1. Inscribir su taller.
2. Registrar un producto una vez y sacarle N pasaportes.
3. Imprimir esos QR en hojas carta.
4. Pasar una pieza, o un lote, a otra empresa o a una persona, en persona.
5. Una persona recibe la pieza y la ve en su cuenta o por correo.

Todo esto corre en local, sin que se pierda ningún dato existente, y la suite queda en verde con pruebas nuevas.

## 2. Objetivos, no-objetivos y anti-objetivos

**Objetivos**

1. Inscripción con un dato por pantalla.
2. Dos tipos de cuenta, empresa/taller y persona, cada una con su propia experiencia.
3. Barra de navegación fija abajo, con íconos propios de la marca.
4. Productos registrados una vez como «tipo» y pasaportes sacados por cantidad.
5. Traspaso en persona con un código de 6 dígitos que se renueva cada 2 minutos, para una pieza o para un lote.
6. Traspaso a una persona sin cuenta, solo con su correo.
7. PDF de hojas carta con los QR elegidos.
8. Correo real por SMTP.

**No-objetivos de esta etapa**

- Traspaso a distancia (en particular, compras grandes entre empresas sin verse). Queda nombrado como trabajo futuro.
- Interfaz en inglés (UR05) y anclar la cadena fuera del servidor (FR56).
- Cambios de infraestructura en AWS, salvo las variables de SMTP.
- **La wiki de GitHub.** Está congelada desde el 7 de noviembre; no se toca.

**Anti-objetivos.** Esto sería un fracaso aunque funcione:

- Que leer un QR baste para adueñarse de una pieza.
- Debilitar o romper las cadenas firmadas: `verify_integrity` tiene que seguir pasando sobre los datos migrados.
- Volver a introducir vocabulario técnico.
- Usar emojis o íconos genéricos.
- Perder la historia de custodia de los productos que ya existen.

## 3. Restricciones

- **Firmas.** `Product.signed_parts()` (products/models.py:232) y `CustodyTransfer.signed_parts()` firman campos concretos. Todo campo nuevo que identifique, o todo cambio de quién recibe, exige revisar qué se firma y escribir una migración que vuelva a firmar las filas existentes. El precedente es `products.0008`.
- **Cadena de custodia.** Es de solo inserción (DBR06) y lineal: un único sucesor por `previous_hash`, y una sola oferta abierta por producto (restricciones en products/models.py:298-320). Las invariantes nuevas que se puedan expresar como `CHECK` o `UNIQUE` van también a la base.
- **Datos existentes.** Antes de cada restricción nueva hay que contar las filas que la violan. Las migraciones de datos se prueban contra una copia de la base con datos de demostración, no contra una base vacía.
- **Idioma.** Todo texto pasa por `{% translate %}` o `_()`. En el catálogo `locale/es` no hay GNU gettext en Windows: se usa la herramienta de i18n del proyecto, como en las entregas anteriores.
- **Entorno.** El hook de prettier rompe las plantillas Django escritas con Edit: hay que verificar el resultado. `Path.write_text` escribe CRLF. La RAM libre ronda 0,5–1,2 GB.
- **Sin dependencias nuevas** salvo que sean imprescindibles; si hacen falta, se piden antes. Pillow y qrcode ya están.
- **Verificación.** Hay que pasar las comprobaciones del README: `manage.py test`, `makemigrations --check`, `ruff check` y `ruff format --check`, y `verify_integrity`.
- **Correo.** Se envía por SMTP de Gmail, con la cuenta personal de Emmanuel y una contraseña de aplicación por el puerto 587. Las credenciales viven solo en `.env` y en `/etc/originpass.env`, nunca en el repositorio. El remitente visible es la dirección personal de Emmanuel con el nombre «OriginPass»; él lo aceptó.
- **Git.** Primero en local; el despliegue va después. No se hace commit, push ni despliegue sin permiso explícito de Emmanuel.

## 4. Lo que decidió Emmanuel

**Usuarios.** Artesanos y campesinos con poca soltura tecnológica. Todo tiene que ser más claro, más simple y más intuitivo.

**Inscripción del taller.** Un dato por pantalla, con «Paso X de Y», botón Atrás y botón Siguiente. La primera pantalla pregunta cómo trabaja la persona («Hago productos a mano» o «Tengo empresa con NIT»), y los campos que no aplican desaparecen.

**Navegación.** Una barra fija abajo con cuatro botones. Para la empresa: Productos, Imprimir QR, Entregas y Mi taller. Los íconos los diseñamos nosotros con la identidad de la marca (añil, caña flecha, los anillos del logo). Nada de emojis.

**Dos tipos de cuenta.** Empresas/talleres y personas. La persona es la `Role.HOLDER` que ya existe. Una tienda o un distribuidor que recibe y revende sin fabricar abre una **cuenta de empresa** y se inscribe como tal: con NIT entra por la vía comercial. También puede trabajar con una cuenta de persona, con el límite de lotes de la sección 5.14.

**Registro de productos.** Cada producto que fabrica la empresa se registra una sola vez («Sombrero vueltiao 24 vueltas», «Carriel»). A ese producto se le sacan N pasaportes según la cantidad pedida, y cada uno lleva su código y su QR.

**Imprimir QR.** La empresa elige los pasaportes y obtiene un PDF de hojas carta, 12 por hoja, con el mismo formato que `hoja-qr-1.png`. Si hay más de una hoja, todo va en un solo PDF. Se puede imprimir donde sea.

**Traspaso, solo en persona.**

- El QR del producto solo identifica la pieza; no da ningún derecho sobre ella. Puede estar impreso o mostrarse en el celular del dueño si no se imprimió.
- El permiso lo da un código aparte de **6 dígitos**:
  - cada producto o lote tiene el suyo;
  - solo lo ve el dueño actual;
  - cambia **cada 2 minutos**, y en pantalla se ven una cuenta regresiva y un anillo que se va cerrando;
  - deja de valer en cuanto se hace el traspaso, aunque no se hayan cumplido los 2 minutos.
- Quien recibe lee el QR y **ve la información del producto**: foto, nombre, quién lo hizo, quién lo tiene ahora. Luego escribe el código y confirma.
- Hay tres destinos:
  - **otra empresa**, que tiene cuenta;
  - **una persona con cuenta**;
  - **una persona sin cuenta**: el dueño escribe su correo, el traspaso queda registrado a ese correo y a la persona le llega un mensaje con la posesión y un enlace para ver la pieza. Para pasarla a otra persona, necesita crear su cuenta.

**Lotes.** Un solo QR, generado a propósito, cubre varios pasaportes y se traspasa de una vez con su propio código de 6 dígitos. Cada pieza sigue siendo individual: después del traspaso se puede entregar o anular por separado, y el comprador final escanea el QR de su pieza, no el del lote.

**Datos existentes.** Cada producto actual se convierte en un tipo con un pasaporte, sin perder su historia.

**Forma de trabajo.** Claude orquesta y los workers corren en Haiku 5.5. La carpeta del proyecto se equipa con las herramientas adecuadas (sección 9).

## 5. Lo que decidí yo (Claude) — revísalo

1. **Nombres en el código.** `Product` sigue siendo la unidad con pasaporte, para no reescribir las firmas, la verificación ni las URL `/v/<code>/`. El producto que se registra una vez es un modelo nuevo, `ProductLine`, con nombre, descripción, categoría, lugar, tipo (artesanal o comercial), foto y empresa. En la interfaz, `ProductLine` se llama «producto» y `Product` se llama «pasaporte» o «unidad». El campo actual `Product.product_type` (artesanal o comercial) no se confunde con esto.
2. **Datos del pasaporte.** Al sacar un pasaporte se **copian** los datos de su línea (nombre, categoría, lugar, tipo) dentro del `Product`. Así su firma sigue cubriendo lo que el comprador ve, y editar la línea no altera pasaportes ya emitidos. Si se edita la línea, los pasaportes nuevos salen con los datos nuevos; los viejos no cambian. La foto sí se comparte desde la línea, salvo que el pasaporte tenga una propia.
3. **Código de 6 dígitos.** Se deriva por HMAC con la clave del servidor sobre: id del producto o del lote, id del dueño actual, número de traspasos de la cadena y ventana de 120 s. No se guarda en ningún lado. Cuando el traspaso ocurre, el dueño y el contador cambian, así que el código queda inválido al instante.
   - Se acepta solo la ventana actual, más 15 s de gracia para quien lo escribió justo al cambiar.
   - Si alguien falla 5 veces en 15 minutos sobre el mismo producto o lote, ese producto o lote queda bloqueado 15 minutos. Se reutiliza la idea de bloqueo de FR57.
4. **Cómo se encadena.** El traspaso en persona deja de ser «oferta y aceptación» con dos pasos de quien entrega. Ahora quien entrega abre «Entregar» y quien recibe completa el traspaso en un solo paso, que escribe directamente una fila `ACCEPTED` en la cadena. La oferta por correo de cuenta y el UUID desaparecen de la interfaz. Las filas viejas siguen siendo válidas.
5. **Persona sin cuenta.** `CustodyTransfer.to_holder` pasa a ser opcional y se añade `to_email`, con un `CHECK` que exige exactamente uno de los dos. Ambos entran en `signed_parts`, y se escribe una migración que vuelve a firmar.
   - El correo lleva un **enlace firmado**. Crear la cuenta o iniciar sesión desde ese enlace reclama la posesión.
   - Registrarse con el mismo correo pero sin el enlace **no** basta, porque no hay verificación de correo y cualquiera podría registrar el correo de otro.
   - Reclamar la posesión añade una fila de custodia nueva, del correo a la cuenta, firmada. Así la cadena muestra el paso.
6. **Lotes.** Un modelo `TransferBatch` agrupa los pasaportes elegidos; tiene su propio QR (una URL con su código) y su propio código de 6 dígitos. Al confirmar, se escribe una fila de custodia por pasaporte, todas en la misma transacción. Si alguna falla, no pasa ninguna. Un pasaporte no puede estar en dos lotes abiertos (`UNIQUE` parcial). El lote no aparece en la página pública de verificación.
7. **Tipo de cuenta.** Se elige al registrarse con una pregunta simple: «¿Tienes un taller, una tienda o una empresa, o eres una persona?». Si elige taller, tienda o empresa, sigue al asistente de inscripción. La primera pantalla del asistente distingue entre taller artesanal y empresa con NIT, y una tienda entra como empresa. Al crear la cuenta se inicia sesión automáticamente (hoy obliga a volver a entrar).
8. **Íconos.** Un sprite SVG en línea en `templates/partials/`: trazo añil de unos 2,4 px, acentos en caña flecha, los anillos o la trenza del logo como motivo. Sin librería de íconos.
9. **PDF.** Se genera en el servidor con Pillow, que ya está (`Image.save(..., "PDF", save_all=True)`), reutilizando la composición de hojas de `export_passport_qr`. No se añade ninguna dependencia. La descarga sale de una vista; el comando se mantiene.
10. **Inscripción por pasos.** La sesión guarda el avance entre pantallas. La solicitud solo se crea al final, con la misma validación del formulario actual.

11. **Pieza a nombre de un correo.** `CustodyTransfer` también recibe `from_email`, y un `CHECK` exige exactamente uno de `from_holder`/`from_email`. Así la fila de reclamo va «del correo a la cuenta». Los dos campos entran en `signed_parts`. Mientras la pieza está a nombre de un correo:
    - `current_holder` devuelve `None` y la pieza no aparece en `held_by` de nadie;
    - la empresa que la fabricó puede anularla como hoy;
    - quien la entregó puede **corregir un correo mal escrito** mientras nadie la haya reclamado. La corrección añade una fila firmada de su correo viejo al correo nuevo, a nombre de quien entregó, y el enlace viejo deja de valer.

    El enlace firmado vale 30 días y se puede volver a enviar.
12. **Traspaso a persona sin cuenta.** No lleva código de 6 dígitos: lo hace el dueño mismo, con su sesión abierta y la pieza a su nombre, así que nadie más actúa. Para evitar errores, la pantalla le muestra la pieza y le pide escribir el correo dos veces.
13. **Ofertas abiertas que ya existen** (`INITIATED`). Antes de migrar se cuentan. La migración las declina pasando por el camino de rechazo del modelo, con la nota «Cerrada al cambiar el sistema de entregas». Así ninguna pieza queda bloqueada por `custody_transfer_one_open_offer`.
14. **Lotes, en detalle.**
    - Los arma el dueño actual de las piezas, sea empresa o persona. **Decisión de Emmanuel:**
      - una cuenta de persona puede armar lotes de **5 piezas como máximo**;
      - una cuenta de empresa no tiene límite;
      - recibir lotes no tiene límite para ninguna cuenta.

      El límite se valida en el servidor, no solo en la pantalla.
    - Todas las piezas tienen que ser suyas al armarlo y otra vez al confirmar, dentro de la transacción y con `select_for_update`.
    - El código del lote es un HMAC sobre: id del lote, id del dueño, estado del lote y ventana de 120 s.
    - Un lote **se cierra al traspasarse**. Quien lo recibe, por ejemplo un distribuidor, puede armar un lote nuevo con esas piezas.
    - El `UNIQUE` parcial evita que un pasaporte esté en dos lotes abiertos.
    - Un lote abierto se puede cancelar.
15. **Quién figura como dueño en la página pública.** Si es una empresa, se muestra su nombre. Si es una persona o un correo, se muestra «Una persona», nunca el correo ni el nombre: cualquiera que lea el QR ve esa página.

## 6. Lo que queda a criterio de quien construye

- Los textos exactos de cada pantalla. El tono: tú, frases cortas, una idea por frase, sin tecnicismos.
- Los dibujos exactos de los íconos, siempre dentro de la sección 5.8.
- Cómo se adaptan a la barra inferior las pantallas que no se nombran aquí: analítica, escaneos, administración, perfil público.
- Cómo se ve la lista de pasaportes de un producto: tarjetas en vez de tablas en el celular.
- El orden interno de las tareas, siempre que se respeten las dependencias de la sección 8.

## 7. Correo

Hay que añadir a `config/settings.py` la lectura de `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` y `EMAIL_USE_TLS` desde el entorno, con valores por defecto vacíos. En desarrollo, si no se define `EMAIL_BACKEND`, se sigue usando el backend de consola. Hay que documentar en `.env.example`, sin valores, y en `deploy/aws/README-AWS.md`.

## 8. Orden de construcción

1. **Base de datos y modelos.** `ProductLine`, la migración de datos (cada producto pasa a una línea), `to_email`, `TransferBatch` y las firmas nuevas, con nuevas firmas para las filas viejas. Antes de cualquier cosa: contar filas y probar sobre una copia de la base de demostración.
2. **Código que cambia cada 2 minutos y traspaso en persona.** Para una pieza, para un lote, y a persona sin cuenta con correo y enlace.
3. **Pantallas.** Barra inferior e íconos, registro de cuenta con su tipo, asistente de inscripción, registro de producto y «sacar N pasaportes», listas en tarjetas, pantalla de «Entregar» con anillo y cuenta regresiva, pantalla de «Recibir», y PDF de QR.
4. **SMTP.**
5. **Recorrido de verificación.** Repetir el recorrido de 390 px de la sección 9 con las cinco tareas de la sección 1 y revisar cada captura.

## 9. Cómo se construye

- **Orquestación.** Claude, con el modelo principal, planifica, reparte, revisa y verifica. Los workers son subagentes en Haiku 5.5 con tareas acotadas de uno o dos archivos: plantillas, CSS, traducciones, pruebas. La lógica de firmas y migraciones la escribe o revisa línea por línea el orquestador.
- **Herramientas en el proyecto.** Se crean en `.claude/` del repo, después de aprobar el plan:
  - **Agentes worker en Haiku:** uno para plantillas y CSS de la interfaz, uno para pruebas y uno para el catálogo de traducciones. Cada uno lleva las reglas de la sección 3.
  - **Herramienta de recorrido visual:** `tools/ux/recorrido.py`, versión estable del script de capturas a 390 px de esta sesión, que recorre las cinco tareas y deja capturas comparables.
  - **Skills de diseño** ya instaladas que se usan: `impeccable`, `ui-ux-pro-max` y `frontend-design` para la interfaz, `webapp-testing` y Playwright para verificar. No se instalan skills nuevas sin preguntar.

## 10. Trabajo futuro (fuera de esta etapa)

- Traspaso a distancia, pensado para compras grandes entre empresas.
- Verificación de correo al registrarse.
- Despliegue de esta versión en AWS, después de terminar en local.
