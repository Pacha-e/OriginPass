# Diagrams

The diagrams required by Deliverable 2. Each one is a draw.io file, editable at
[app.diagrams.net](https://app.diagrams.net) or in the draw.io desktop application,
with no export step needed to read it.

| File | Deliverable 2 | What it shows |
|---|---|---|
| `deployment-model.drawio` | 1.1 | The nodes the system runs on, the software installed on each one with its version, and the protocol between them |
| `components-model.drawio` | 1.2 | One component per Django app, the functions each one provides, the dependencies between them, and the requirement each function implements |
| `data-model.drawio` | 1.3 | The six tables, their columns and types, the foreign keys with their cardinality, and the check constraints |
| `mockups.drawio` | 2 | The five views the Sprint 2 requirements are reflected in, each answering what the content groups are, where the information sits, and how the interface is used |

`export/` holds a PNG of each diagram at twice its natural size, rebuilt with

```bash
docker run --rm -v "$PWD/docs/diagrams:/data" rlespinasse/drawio-export -f png --scale 2
```

The wiki does not use them: it links the `.drawio` sources, so that what a reader opens is
the file this repository versions rather than a picture of it that can fall behind. They
exist for slides and for anywhere a link will not do.

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
green for what Sprint 2 is building, purple for what has a model but no views yet.

## Exporting for the wiki

The wiki needs PNG images, since GitHub does not render `.drawio` files:

1. Open the file in draw.io.
2. **File → Export as → PNG**, with a zoom of 200 % and a border of 10 px.
3. Save beside the source file as `<name>.png`.
4. Attach the image to the wiki page through the GitHub editor, which stores it and
   returns the URL to reference.
