# OriginPass — corporate image

## Idea

A passport is a security document, and OriginPass protects crafts that are copied
because they are valuable. The identity joins the two: the language of security
printing (intaglio ink, guilloche, the machine-readable strip of a passport) drawn
with the material of the craft it protects, the cana flecha of the sombrero vueltiao.

## Logo

![OriginPass logo](../../static/brand/originpass-logo.svg)

The mark is a **P** whose bowl is a set of concentric rings. Seen from above, a
sombrero vueltiao is rings of braided cana flecha, counted in *vueltas*; read again,
the same rings are a fingerprint, the one identity that cannot be copied. The dashed
middle ring is the braid. The stem is solid: the passport that holds the piece.

| File | Use |
|---|---|
| `static/brand/originpass-logo.svg` | Logo with wordmark and slogan, for documents |
| `templates/partials/logo_mark.html` | The mark inline in every page, coloured by the page |
| `static/favicon.svg` | The mark reversed on indigo, for the browser tab |

## Slogan

**El origen no se imita.** — *Origin cannot be imitated.*

It states the promise to both people the product serves: to the workshop, that its
origin is protected; to the buyer, that a copy will be told apart.

## Palette

| Name | Hex | Role |
|---|---|---|
| Añil (indigo ink) | `#1E2B58` | Brand, headings, primary actions. The natural dye of the region's textiles and the ink of security printing. |
| Caña flecha (straw) | `#D9C28A` | The woven thread, rings, highlights. Never text. |
| Papel (security paper) | `#F3F4EE` | Page background. |
| Tinta (ink) | `#232838` | Body text. |
| Sello (seal green) | `#17694A` | The verdict Genuine, approved states. |
| Carmín | `#A3253C` | The verdict Revoked, refusals, destructive actions. |
| Ámbar | `#86560A` | The verdict Not found, pending states. |

Every text and background pair clears 4.5 to 1 (UR09): indigo on white 13.6,
seal green 6.7, carmine 7.3, amber 6.3, body ink 14.7. Straw is a fill only.

## Typography

- **Headings:** Bahnschrift, the DIN of road signs and official forms, which ships with
  Windows. Other systems fall back to their own DIN or condensed grotesque.
- **Text:** the system interface face (Segoe UI, San Francisco, Roboto).
- **Codes:** OCR-B where installed, otherwise Consolas or the system monospace: the face
  of a passport's machine-readable zone.

No web font is loaded: the verification page is opened on a phone in front of a stall,
and its budget (UR06) is better spent on the answer.

## Motifs

- **The pinta.** A strip of the zigzag woven into a sombrero vueltiao runs under the
  header of every page. It is the one decorative thread, and it is not repeated
  elsewhere for its own sake.
- **The seal.** The verdict is stamped as a guilloche rosette, the interlaced line of
  banknotes and passports, in the colour of the answer. It is the only motion that plays
  on its own, once, when the verdict loads; everything else moves only in answer to the
  reader, and nothing moves for a reader who asks for reduced motion.
- **The data page.** The public page lays the product out as the data page of a
  passport, ending in its machine-readable strip.

## Screenshots

The main interfaces with the identity applied are in [`screenshots/`](screenshots/).

## Written for the people who use it

Many of the people OriginPass serves are artisans and farmers, often on a phone and
sometimes reading slowly. The interface is held to that reader:

- **One plain word per idea.** The code says custody, transfer and revoke; the
  interface says *entregar*, *código de entrega*, *recibir* and *anular*, and calls
  every item a *producto*. A test fails if the old vocabulary comes back.
- **Every action says what it does.** With a mouse, a tooltip opens on hover and on
  keyboard focus. A phone has no hover, so there the same sentence is printed under
  the button. Each one is tied to its control with `aria-describedby`, so a screen
  reader announces it too.
- **Every term can be asked about.** A "?" beside a term (passport code, verified
  through, journey, transfer code) opens its meaning in place. It is a `<details>`
  element, so it works on any phone without script.
- **Help before the field, with an example inside it.** Every form field explains
  itself above the input and shows an example as its placeholder; the photo field
  opens the phone camera or gallery.
- **Short numbered steps** above the forms where the order matters: registering a
  product and handing it over.
- **Text starts at 17px** and every control is at least 44px tall.

## Photographs

The home page and the demonstration products show real photographs of the crafts,
from Wikimedia Commons under free licences (public domain, CC BY and CC BY-SA). Their
authors and licences are listed on the credits page of the site (`/creditos/`), linked
from the footer of every page; the list itself lives in `pages/views.py`.
