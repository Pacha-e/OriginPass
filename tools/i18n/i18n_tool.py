"""Extract missing msgids (like makemessages) and compile the .po (like msgfmt),
without GNU gettext installed. Run from the repository root with the venv python.

  python tools/i18n/i18n_tool.py missing            -> writes missing.json
  python tools/i18n/i18n_tool.py add translations.json
  python tools/i18n/i18n_tool.py compile
"""

import ast
import json
import os
import re
import struct
import sys
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, os.getcwd())
import django  # noqa: E402

django.setup()
from django.utils.translation.template import templatize  # noqa: E402

ROOT = Path.cwd()
PO = ROOT / "locale/es/LC_MESSAGES/django.po"
MO = PO.with_suffix(".mo")
APPS = [
    "accounts",
    "audit",
    "companies",
    "pages",
    "products",
    "verification",
    "templates",
    "config",
]
FUNCS = {
    "_",
    "gettext",
    "gettext_lazy",
    "_trans",
    "ngettext",
    "ngettext_lazy",
    "pgettext",
    "pgettext_lazy",
}


def strings_in_python(source):
    found = []
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if name in FUNCS and node.args:
                args = [
                    a.value if isinstance(a, ast.Constant) and isinstance(a.value, str) else None
                    for a in node.args
                ]
                if name.startswith("ngettext") and len(args) >= 2 and args[0] and args[1]:
                    found.append((args[0], args[1]))
                elif name.startswith("pgettext"):
                    continue
                elif args[0]:
                    found.append((args[0], None))
    return found


def collect():
    found = {}
    for app in APPS:
        for path in sorted((ROOT / app).rglob("*")):
            if "migrations" in path.parts or "tests" in path.parts:
                continue
            if path.suffix == ".py":
                for msgid, plural in strings_in_python(path.read_text(encoding="utf-8")):
                    found.setdefault(msgid, plural)
            elif path.suffix in (".html", ".txt"):
                code = templatize(path.read_text(encoding="utf-8"), origin=str(path))
                literal = r"""u?(?:'(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*")"""
                pattern = rf"\b(n?gettext)\(({literal})(?:,\s*({literal}))?"
                for match in re.finditer(pattern, code):
                    msgid = ast.literal_eval(match.group(2))
                    plural = (
                        ast.literal_eval(match.group(3))
                        if match.group(1) == "ngettext" and match.group(3)
                        else None
                    )
                    found.setdefault(msgid, plural)
    return found


def unquote(lines):
    return "".join(ast.literal_eval(line) for line in lines)


def read_po():
    entries = []  # dicts: msgid, msgid_plural, msgstr (list or str)
    current, key = None, None
    for raw in PO.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("msgid "):
            current = {"msgid": [line[6:]], "msgid_plural": None, "msgstr": {}}
            entries.append(current)
            key = ("msgid",)
        elif line.startswith("msgid_plural "):
            current["msgid_plural"] = [line[13:]]
            key = ("msgid_plural",)
        elif line.startswith("msgstr["):
            index = int(line[7 : line.index("]")])
            current["msgstr"][index] = [line[line.index("]") + 2 :]]
            key = ("msgstr", index)
        elif line.startswith("msgstr "):
            current["msgstr"][0] = [line[7:]]
            key = ("msgstr", 0)
        elif line.startswith('"') and current is not None:
            if key[0] == "msgstr":
                current["msgstr"][key[1]].append(line)
            else:
                current[key[0]].append(line)
        elif line.startswith("#,") and "fuzzy" in line and current is not None:
            pass
    result = []
    for e in entries:
        result.append(
            {
                "msgid": unquote(e["msgid"]),
                "msgid_plural": unquote(e["msgid_plural"]) if e["msgid_plural"] else None,
                "msgstr": {k: unquote(v) for k, v in e["msgstr"].items()},
            }
        )
    return result


def quote(text):
    return json.dumps(text, ensure_ascii=False)


def missing():
    known = {e["msgid"] for e in read_po()}
    found = collect()
    out = {k: v for k, v in found.items() if k not in known}
    Path("missing.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(found)} strings in code, {len(out)} missing from the catalogue")


def add(path):
    translations = json.loads(Path(path).read_text(encoding="utf-8"))
    known = {e["msgid"] for e in read_po()}
    blocks = []
    for msgid, value in translations.items():
        if msgid in known:
            continue
        if isinstance(value, list):
            plural, singular_es, plural_es = value
            blocks.append(
                f"\nmsgid {quote(msgid)}\nmsgid_plural {quote(plural)}\n"
                f"msgstr[0] {quote(singular_es)}\nmsgstr[1] {quote(plural_es)}\n"
            )
        else:
            blocks.append(f"\nmsgid {quote(msgid)}\nmsgstr {quote(value)}\n")
    with PO.open("a", encoding="utf-8") as handle:
        handle.write("".join(blocks))
    print(f"added {len(blocks)} entries")


def compile_mo():
    catalogue = {}
    seen = set()
    for e in read_po():
        if e["msgid"] in seen and e["msgid"]:
            raise SystemExit(f"duplicate msgid: {e['msgid']!r}")
        seen.add(e["msgid"])
        if e["msgid_plural"]:
            if not all(e["msgstr"].values()):
                continue
            key = e["msgid"] + "\0" + e["msgid_plural"]
            value = "\0".join(e["msgstr"][i] for i in sorted(e["msgstr"]))
        else:
            value = e["msgstr"].get(0, "")
            if not value and e["msgid"]:
                continue
            key = e["msgid"]
        catalogue[key] = value
    keys = sorted(catalogue)
    ids = b""
    strs = b""
    offsets = []
    for k in keys:
        kb, vb = k.encode("utf-8"), catalogue[k].encode("utf-8")
        offsets.append((len(ids), len(kb), len(strs), len(vb)))
        ids += kb + b"\0"
        strs += vb + b"\0"
    keystart = 7 * 4 + 16 * len(keys)
    valuestart = keystart + len(ids)
    koffsets, voffsets = [], []
    for o1, l1, o2, l2 in offsets:
        koffsets += [l1, o1 + keystart]
        voffsets += [l2, o2 + valuestart]
    output = struct.pack("Iiiiiii", 0x950412DE, 0, len(keys), 7 * 4, 7 * 4 + len(keys) * 8, 0, 0)
    output += struct.pack(f"{len(koffsets)}i", *koffsets)
    output += struct.pack(f"{len(voffsets)}i", *voffsets)
    output += ids + strs
    MO.write_bytes(output)
    print(f"compiled {len(keys)} entries into {MO}")


def set_existing(path):
    """Replace the msgstr of msgids already in the catalogue (singular entries)."""
    wanted = json.loads(Path(path).read_text(encoding="utf-8"))
    raw = PO.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    text = raw.replace("\r\n", "\n")
    blocks = text.split("\n\n")
    done = set()
    for index, block in enumerate(blocks):
        lines = block.split("\n")
        id_start = next((i for i, ln in enumerate(lines) if ln.startswith("msgid ")), None)
        if id_start is None or any(ln.startswith("msgid_plural") for ln in lines):
            continue
        str_start = next(i for i, ln in enumerate(lines) if ln.startswith("msgstr "))
        msgid = unquote([lines[id_start][6:], *lines[id_start + 1 : str_start]])
        if msgid in wanted:
            lines = lines[:str_start] + [f"msgstr {quote(wanted[msgid])}"]
            lines = [ln for ln in lines if ln != "#, fuzzy"]
            blocks[index] = "\n".join(lines)
            done.add(msgid)
    out = "\n\n".join(blocks)
    if crlf:
        out = out.replace("\n", "\r\n")
    PO.write_bytes(out.encode("utf-8"))
    missing = set(wanted) - done
    print(f"replaced {len(done)}; not found: {sorted(missing)}")


if __name__ == "__main__":
    command = sys.argv[1]
    if command == "set":
        set_existing(sys.argv[2])
    if command == "missing":
        missing()
    elif command == "add":
        add(sys.argv[2])
    elif command == "compile":
        compile_mo()
