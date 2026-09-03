# Diagrams

The three architecture diagrams required by Deliverable 2, section 1. Each one is a
draw.io file, editable at [app.diagrams.net](https://app.diagrams.net) or in the
draw.io desktop application, with no export step needed to read it.

| File | Deliverable 2 | What it shows |
|---|---|---|
| `deployment-model.drawio` | 1.1 | The nodes the system runs on, the software installed on each one with its version, and the protocol between them |
| `components-model.drawio` | 1.2 | One component per Django app, the functions each one provides, the dependencies between them, and the requirement each function implements |
| `data-model.drawio` | 1.3 | The six tables, their columns and types, the foreign keys with their cardinality, and the check constraints |

Every version and every column name in these diagrams was read from the code rather
than from the plan: `requirements.txt` and `docker-compose.yml` for the deployment
model, `views.py` and `urls.py` for the component model, and `models.py` for the
data model. When the code changes, these change with it.

Colour carries the same meaning in all three: blue for what Sprint 1 delivered,
green for what Sprint 2 is building, purple for what has a model but no views yet.

## Exporting for the wiki

The wiki needs PNG images, since GitHub does not render `.drawio` files:

1. Open the file in draw.io.
2. **File → Export as → PNG**, with a zoom of 200 % and a border of 10 px.
3. Save beside the source file as `<name>.png`.
4. Attach the image to the wiki page through the GitHub editor, which stores it and
   returns the URL to reference.
