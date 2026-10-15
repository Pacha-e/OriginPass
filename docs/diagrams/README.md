# Diagrams

The diagrams required by Deliverables 2 and 3. What Sprint 3 changed is drawn in orange in
each one, with its own legend entry, as Deliverable 3 asks the changes to be marked. Each one is a draw.io file, editable at
[app.diagrams.net](https://app.diagrams.net) or in the draw.io desktop application,
with no export step needed to read it.

| File | Deliverable 2 | What it shows |
|---|---|---|
| `deployment-model.drawio` | 1.1 | The nodes the system runs on, the software installed on each one with its version, and the protocol between them |
| `components-model.drawio` | 1.2 | One component per Django app, the functions each one provides, the dependencies between them, and the requirement each function implements |
| `data-model.drawio` | 1.3 | The eight domain tables, their columns and types, the foreign keys with cardinality, and the check constraints |
| `mockups.drawio` | 2 | The five views the Sprint 2 requirements are reflected in, each answering what the content groups are, where the information sits, and how the interface is used |

`export/` holds each architecture model as a vector PDF, an SVG and a PNG at 2.5x.
The PDF is the reliable option for reading small labels at high zoom. Rebuild all
three architecture models through the official diagrams.net viewer:

```bash
python tools/presentation/render_diagrams.py
```

The mockup PNG can still be rebuilt with the draw.io desktop application or

```bash
docker run --rm -v "$PWD/docs/diagrams:/data" rlespinasse/drawio-export -f png --scale 2
```

The wiki links the editable `.drawio` sources and, for the Sprint 3 data model, the matching PNG export so the added company fields are visible without draw.io. Reexport a PNG whenever its source changes.

Every version and every column name in these diagrams was read from what is installed
and running rather than from the plan: `pip list` and the image tags in
`docker-compose.yml` for the deployment model, `views.py` and `urls.py` for the
component model, the running database through `manage.py describe_schema` for the data
model, and the templates themselves for the mockups. When the code changes, these
change with it.

Deliberately not `requirements.txt`: it states the lowest version the project accepts,
not the one in use, and reading it as though it were the second is how this file once
named four versions the project does not install.

The mockups are wireframes rather than a copy of the rendered pages, which is what
the deliverable asks for: they show the structure and the interaction, not the
styling. The last frame draws the verification verdict at 360 pixels, because UR01
is a requirement about that width specifically and a desktop frame cannot show it.

Colour carries the same meaning in all three: blue for what Sprint 1 delivered,
green for Sprint 2, orange for additions in Sprint 3, and purple for models created
in Sprint 1 whose views were delivered in Sprint 3.

## Exporting for the wiki

The wiki needs PNG images, since GitHub does not render `.drawio` files:

1. Open the file in draw.io.
2. **File → Export as → PNG**, with a zoom of 200 % and a border of 10 px.
3. Save beside the source file as `<name>.png`.
4. Attach the image to the wiki page through the GitHub editor, which stores it and
   returns the URL to reference.
