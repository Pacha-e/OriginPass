# OriginPass — presentar la Entrega 3 desde el portátil

Esta guía deja el portátil listo para la revisión del Sprint 3: la aplicación corriendo con
los datos de demostración, todas las vistas abiertas, los diagramas, la presentación y los
videos. La preparación se hace **antes de clase y con internet**; el día de la presentación
solo se arranca y se abre lo de la lista.

**Empieza por `ABRIR-KIT.html`**, en la raíz del ZIP extraído: reúne todos los archivos
de exposición, incluidos los cinco videos de lanzamiento. Funcionan sin internet.
`Verificar-Kit.ps1` comprueba que ningún archivo del kit falte o haya cambiado.
`Setup-Portatil.ps1` genera `ABRIR-DEMO.html` con los pasaportes reales de ese equipo.
El ZIP usa PostgreSQL aislado en `127.0.0.1:55432`, proyecto Docker `originpass-kit` y
volumen propio. El clon conserva su PostgreSQL de desarrollo en el puerto 5432.
Guarda la carpeta preparada completa: su `.env` contiene la clave que firma esa base.

## Lo que tiene que estar listo, corriendo y abierto

Marca cada punto antes de empezar.

**1. La aplicación, corriendo.**

- [ ] Docker Desktop abierto, en estado *Running*.
- [ ] Una ventana de PowerShell con `Start-OriginPass.ps1` en marcha. No se cierra durante
  la presentación.
- [ ] `http://127.0.0.1:8000/` responde en el navegador.

**2. Las vistas de la aplicación, abiertas en pestañas.** Cada cuenta va en su propia
ventana, porque el navegador guarda una sola sesión por ventana: una ventana normal, una de
incógnito y otro navegador. La contraseña de todas las cuentas de demostración la imprime
`seed_demo` al final de la preparación.

| Ventana | Cuenta | Pestañas, en este orden |
|---|---|---|
| Chrome, normal | sin sesión | Inicio `/` · Veredicto Auténtico `/v/<código del Sombrero vueltiao 21 vueltas>/` · Veredicto Anulado `/v/<código de la Hamaca de San Jacinto>/` · No encontrado `/v/NO-EXISTE/` |
| Chrome, incógnito | `taller@tuchin.co` | Mis productos `/products/` · Escaneos `/products/analytics/` (con la alerta de posible copia) · Entregas `/products/custody/` |
| Edge | `contacto@labonga.co` | Entregas `/products/custody/`, con la oferta abierta del Sombrero vueltiao 15 vueltas |
| Edge, InPrivate | `admin@originpass.co` | Panel `/products/admin/overview/` · Solicitudes `/companies/review/` (Mochilas Wayuu pendiente) · Auditoría `/audit/` |

Los códigos de pasaporte cambian en cada equipo. Para verlos, desde la carpeta de la
aplicación:

```powershell
.\.venv\Scripts\python.exe manage.py shell -c "from products.models import Product; [print(p.status, p.passport_code, p.name) for p in Product.objects.all()]"
```

**3. La presentación.**

- [ ] `presentacion\OriginPass-Entrega-3-presentacion.pdf`, abierta y lista para pantalla
  completa. El texto y los diagramas son vectoriales: se pueden ampliar sin pixelarse.
- [ ] `presentacion\OriginPass-Entrega-3-presentacion.html`, alternativa en el navegador,
  con enlaces para abrir cada diagrama por separado. Conserva la carpeta `diagramas` a su lado.
- [ ] `presentacion\capturas\index.html`, las capturas de la aplicación a su tamaño
  original, para leer los detalles pequeños que aparecen en las diapositivas.

Los enlaces para abrir archivos funcionan en la versión HTML. El PDF muestra la ruta
del archivo junto a cada diagrama o captura, para abrirlo desde la carpeta del kit.

- [ ] `presentacion\OriginPass-Entrega-3-guion.md`, lo que se dice en cada diapositiva, en el
  teléfono o impreso.

**4. El video del recorrido.**

- [ ] `presentacion\OriginPass-Entrega-3-recorrido.mp4`, abierto en pausa: muestra todas las
  funciones nuevas con un rótulo por paso, sin narración. Es el respaldo si algo falla en la
  demostración en vivo.

**5. Los diagramas** (abre `presentacion\diagramas\index.html` para elegir uno).

- [ ] `deployment-model-Deployment-model.pdf` — despliegue
- [ ] `components-model-Component-model.pdf` — componentes
- [ ] `data-model-Data-model.pdf` — datos

En `presentacion\diagramas\` cada modelo tiene PDF vectorial para ampliar, SVG para
el navegador, PNG de alta resolución de respaldo y fuente `.drawio` editable. Para
leer las tablas completas durante la exposición, abre el PDF individual y amplía.

Los cambios del Sprint 3 van en naranja en los tres. Los `.drawio` editables están en
`app\docs\diagrams\`.

**6. Los videos de lanzamiento**, con la voz de Emmanuel, incluidos en `videos\` y
enlazados desde `ABRIR-KIT.html` (también disponibles en la
[release de videos](https://github.com/Pacha-e/OriginPass/releases/tag/originpass-videos-lanzamiento)):

- [ ] `OriginPass-lanzamiento-16x9.mp4` — lanzamiento, horizontal
- [ ] `OriginPass-lanzamiento-9x16.mp4` — lanzamiento, vertical
- [ ] `OriginPass-reel-cual-es-el-original-9x16.mp4` — reel «¿Cuál es el original?»
- [ ] `OriginPass-reel-como-funciona-9x16.mp4` — reel «Cómo funciona»
- [ ] `OriginPass-reel-manifiesto-9x16.mp4` — reel «Manifiesto»

**7. La documentación**, en pestañas del navegador normal:

- [ ] Wiki [Deliverable 3](https://github.com/Pacha-e/OriginPass/wiki/Deliverable-3)
- [ ] Wiki [Videos](https://github.com/Pacha-e/OriginPass/wiki/Videos)
- [ ] Wiki [Daily Log](https://github.com/Pacha-e/OriginPass/wiki/Daily-Log)
- [ ] El [pull request #82](https://github.com/Pacha-e/OriginPass/pull/82), con el CI en verde
- [ ] El [backlog](https://github.com/users/Pacha-e/projects/1)

## Preparación, una sola vez y con internet

1. Instala **Python 3.12 para Windows** (marca *Add to PATH*) y **Docker Desktop** con
   contenedores Linux. Docker puede pedir WSL2 y un reinicio: hazlo con tiempo.
2. Consigue la aplicación de una de dos formas:
   - **ZIP:** descarga `OriginPass-Portatil.zip` y `SHA256SUMS.txt` de la
     [release del kit](https://github.com/Pacha-e/OriginPass/releases/tag/originpass-kit-portatil-2026-10-15),
     comprueba el hash con `Get-FileHash .\OriginPass-Portatil.zip` y extrae **todo** el ZIP,
     por ejemplo en `C:\OriginPass-Portatil`.
   - **Clon:** `git clone https://github.com/Pacha-e/OriginPass.git C:\OriginPass`. La
     aplicación se prepara con los scripts de `delivery\`. Para el índice, el manifiesto
     y todos los materiales, descarga y extrae también el ZIP completo. `ABRIR-KIT.html`
     y `Verificar-Kit.ps1` se usan desde esa extracción, no desde la carpeta fuente `delivery\`.
3. Abre PowerShell en esa carpeta y ejecuta la preparación. Con el ZIP, el script está en la
   raíz; con el clon, en `delivery\`:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\Setup-Portatil.ps1
   ```

   Con un clon, entra primero en `delivery\` (`cd C:\OriginPass\delivery`).

   Levanta PostgreSQL, crea el entorno de Python, instala las dependencias, crea una clave
   local nueva sin mostrarla, migra la base, carga los datos de demostración y verifica las
   cadenas firmadas. Termina con `Preparacion local terminada`.
4. Desde la raíz del ZIP extraído, ejecuta
   `powershell -NoProfile -ExecutionPolicy Bypass -File .\Verificar-Kit.ps1`.
   Debe terminar con `Kit OK`. No modifica datos ni instala dependencias.
5. Abre `ABRIR-KIT.html` y haz un ensayo completo: arranca la aplicación, abre
   `ABRIR-DEMO.html` y recorre la demostración con cuentas en ventanas separadas.

## El día de la presentación

1. Abre Docker Desktop y espera a *Running*.
2. En PowerShell, en la misma carpeta que `Setup-Portatil.ps1`:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\Start-OriginPass.ps1
   ```

3. Abre `ABRIR-KIT.html` y luego todo lo de la lista, en su orden.

## La demostración en vivo

El orden es el de la diapositiva 4 de la presentación y el del video del recorrido:

1. El taller registra un producto con su foto y recibe el pasaporte y el QR.
2. El veredicto Auténtico, el recorrido y el perfil público del taller.
3. El taller entrega el producto a La Bonga; La Bonga lo recibe en Entregas.
4. La Bonga lo entrega al comprador, que lo recibe con los dos códigos.
5. El recorrido creció.
6. Escaneos: la alerta de posible copia y la exportación en CSV.
7. El taller anula el pasaporte; el QR responde Anulado.
8. El administrador: panel, solicitudes y auditoría con la cadena íntegra.

## Si algo falla

- **Docker no responde:** ciérralo, ábrelo de nuevo y espera a *Running*; luego
  `Start-OriginPass.ps1`.
- **El puerto 5432 o el 8000 está ocupado:** otro PostgreSQL o servidor está corriendo. Para
  el 8000, arranca en otro puerto:
  `.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8001 --noreload`.
- **Los datos se ven raros:** `.\.venv\Scripts\python.exe manage.py seed_demo` vuelve a crear
  lo que falte.
- **Integridad:** `.\.venv\Scripts\python.exe manage.py verify_integrity`.
- **Sin aplicación:** presenta con el video del recorrido y las capturas de la presentación.

No borres `.env` ni el volumen de Docker entre intentos: la clave local firma las cadenas de
integridad. El servidor solo escucha en `127.0.0.1`, no en la red del salón.

## Qué contiene el ZIP

- `app\`: el código de `main`, las migraciones, las fotos de demostración y los diagramas. Sin
  `.env`, sin base de datos y sin entorno virtual.
- `presentacion\`: la presentación en PDF y HTML, su guion, los diagramas individuales
  en `diagramas\`, las capturas originales en `capturas\` y el video del recorrido.
- `wiki\`: las páginas de la wiki.
  Es una copia local de su texto Markdown; algunos enlaces e imágenes de la wiki
  siguen apuntando a GitHub. Los diagramas y capturas para exponer están incluidos aparte.
- `videos\`: los cinco videos de lanzamiento; atribuciones en `CREDITOS-VIDEOS.md`.
- `ABRIR-KIT.html`: índice local de todo el material.
- `KIT-MANIFEST.json`, `verify_kit.py` y `Verificar-Kit.ps1`: identificación del commit
  fuente y comprobación de cada archivo del kit por tamaño y SHA-256.
- `ABRIR-DEMO.html`: página regenerada por la preparación y el arranque, con los
  pasaportes de la base de datos local. Por eso no se incluye en el hash del manifiesto.
- `Setup-Portatil.ps1` y `Start-OriginPass.ps1`: preparar y arrancar. Funcionan igual desde
  el ZIP y desde `delivery\` en un clon.

## Reconstruir el kit, desde el PC de desarrollo

Desde un clon actualizado de `main`. Instala las herramientas de autoría una vez
(el portátil que presenta no las necesita):

```powershell
python -m pip install -r tools/presentation/requirements.txt
python -m playwright install chromium
```

GitHub CLI (`gh`) permite recuperar los videos publicados. El empaquetador descarga
los que falten, incluido el recorrido, y valida su SHA-256:

```powershell
python tools/presentation/render_diagrams.py
python tools/presentation/build_deck.py
python delivery/build_portable.py --fetch-videos
```

Para volver a grabar el recorrido tras cambiar funciones: prepara la demo, arranca
`python manage.py runserver 127.0.0.1:8765` en otra ventana y ejecuta
`python tools/video/record_features.py`. Al cambiar un video publicado, actualiza
también su tamaño y hash en `media-manifest.json` antes de empaquetar.

`build_portable.py` escribe `delivery\OriginPass-Portatil.zip` y `delivery\SHA256SUMS.txt`.
Ninguno se versiona: se suben a la release del kit.
Las páginas necesarias de la wiki están versionadas en `docs/wiki/`; no hace falta
otro clon para empaquetar. Los videos de lanzamiento se descargan solo si faltan y
se comprueban contra `delivery/media-manifest.json`.
