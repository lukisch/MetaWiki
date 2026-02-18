#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
metawiki_cli.py - CLI-Tool fuer MetaWiki Stub-Management
=========================================================

Einfaches Kommandozeilen-Interface fuer die wichtigsten Operationen:
- list:     Stubs auflisten (mit Filtern)
- search:   Stubs nach Titel/Inhalt suchen
- add:      Neuen Stub hinzufuegen
- remove:   Stub entfernen
- stats:    Statistiken anzeigen
- export:   JSON nach Markdown exportieren
- import:   Markdown nach JSON importieren
- check:    Konsistenzpruefung

Nutzung:
    python metawiki_cli.py list
    python metawiki_cli.py search "Matrix"
    python metawiki_cli.py add --title "Neues Thema" --def "Kurze Beschreibung" --cat 07_Informatik_KI --sub Software_Engineering
    python metawiki_cli.py stats
"""

import json
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BASE_PATH = Path(__file__).parent.resolve()
JSON_PATH = BASE_PATH / "metawiki.json"
BACKUP_PATH = BASE_PATH / "backups"

CATEGORY_FOLDERS = [
    "01_Mathematik",
    "02_Physik_Astronomie",
    "03_Chemie",
    "04_Biologie_Lebenswissenschaften",
    "05_Medizin_Gesundheit",
    "06_Psychologie_Kognition",
    "07_Informatik_KI",
    "08_Technik_Ingenieurwesen",
    "09_Gesellschaft_Politik",
    "10_Wirtschaft_Recht",
    "11_Geschichte_Archaeologie",
    "12_Kultur_Kunst_Sprache"
]


# ==================== HILFSFUNKTIONEN ====================

def load_json():
    """Laedt metawiki.json."""
    if not JSON_PATH.exists():
        return {"MetaWiki": {cat: {} for cat in CATEGORY_FOLDERS}}
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data):
    """Speichert metawiki.json mit Backup."""
    if JSON_PATH.exists():
        BACKUP_PATH.mkdir(exist_ok=True)
        backup_name = f"metawiki_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        import shutil
        shutil.copy(JSON_PATH, BACKUP_PATH / backup_name)

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_all_stubs(data):
    """Gibt alle Stubs als flache Liste zurueck."""
    stubs = []
    for cat, subcats in data.get("MetaWiki", {}).items():
        if not isinstance(subcats, dict):
            continue
        for subcat, items in subcats.items():
            if not isinstance(items, list):
                continue
            for item in items:
                item["_category"] = cat
                item["_subcategory"] = subcat
                stubs.append(item)
    return stubs


# ==================== BEFEHLE ====================

def cmd_list(args):
    """Listet Stubs auf."""
    data = load_json()
    stubs = get_all_stubs(data)

    # Filter
    if args.category:
        stubs = [s for s in stubs if args.category.lower() in s["_category"].lower()]
    if args.subcategory:
        stubs = [s for s in stubs if args.subcategory.lower() in s["_subcategory"].lower()]

    # Sortieren
    stubs.sort(key=lambda s: (s["_category"], s["_subcategory"], s["title"]))

    # Limit
    total = len(stubs)
    if args.limit:
        stubs = stubs[:args.limit]

    print(f"\n  {total} Stubs gefunden" + (f" (zeige {len(stubs)})" if args.limit else "") + "\n")

    current_cat = ""
    current_sub = ""
    for stub in stubs:
        if stub["_category"] != current_cat:
            current_cat = stub["_category"]
            cat_display = current_cat.lstrip("0123456789_").replace("_", " ")
            print(f"\n  [{cat_display}]")

        if stub["_subcategory"] != current_sub:
            current_sub = stub["_subcategory"]
            sub_display = current_sub.replace("_", " ")
            print(f"    {sub_display}:")

        print(f"      - {stub['title']}")


def cmd_search(args):
    """Sucht in Stubs."""
    data = load_json()
    stubs = get_all_stubs(data)

    query = args.query.lower()
    results = []

    for stub in stubs:
        score = 0
        # Titel-Match (hoechste Prioritaet)
        if query in stub.get("title", "").lower():
            score = 3
        # Definition-Match
        elif query in stub.get("definition_de", "").lower():
            score = 2
        # Relevanz-Match
        elif query in stub.get("relevance", "").lower():
            score = 1
        # Tag-Match
        elif any(query in tag.lower() for tag in stub.get("tags", [])):
            score = 1

        if score > 0:
            results.append((stub, score))

    results.sort(key=lambda x: (-x[1], x[0]["title"]))

    print(f"\n  Suche: '{args.query}' -> {len(results)} Treffer\n")

    for stub, score in results:
        match_type = {3: "Titel", 2: "Definition", 1: "Relevanz/Tags"}[score]
        cat_display = stub["_category"].lstrip("0123456789_").replace("_", " ")
        sub_display = stub["_subcategory"].replace("_", " ")

        print(f"  [{match_type}] {stub['title']}")
        print(f"          {cat_display} > {sub_display}")
        if stub.get("definition_de"):
            defn = stub["definition_de"][:100]
            if len(stub["definition_de"]) > 100:
                defn += "..."
            print(f"          {defn}")
        print()


def cmd_add(args):
    """Fuegt einen neuen Stub hinzu."""
    data = load_json()

    cat = args.category
    subcat = args.subcategory

    # Validierung
    if cat not in data.get("MetaWiki", {}):
        if cat not in CATEGORY_FOLDERS:
            print(f"\n  FEHLER: Kategorie '{cat}' unbekannt.")
            print(f"  Verfuegbar: {', '.join(CATEGORY_FOLDERS)}")
            return

    root = data["MetaWiki"]
    if cat not in root:
        root[cat] = {}
    if subcat not in root[cat]:
        root[cat][subcat] = []

    # Duplikat pruefen
    for item in root[cat][subcat]:
        if item.get("title", "").lower() == args.title.lower():
            print(f"\n  WARNUNG: '{args.title}' existiert bereits in {cat}/{subcat}.")
            return

    # Tags generieren
    tags = []
    tag_name = cat.lstrip("0123456789_").replace("_", " ")
    tags.append(tag_name)
    tags.append(subcat.replace("_", " "))

    stub = {
        "title": args.title,
        "definition_de": args.definition,
        "definition_en": "",
        "relevance": args.relevance or "",
        "tags": tags
    }

    root[cat][subcat].append(stub)
    save_json(data)
    print(f"\n  Hinzugefuegt: '{args.title}' -> {cat}/{subcat}")


def cmd_remove(args):
    """Entfernt einen Stub."""
    data = load_json()
    query = args.title.lower()

    found = []
    for cat, subcats in data.get("MetaWiki", {}).items():
        if not isinstance(subcats, dict):
            continue
        for subcat, items in subcats.items():
            if not isinstance(items, list):
                continue
            for i, item in enumerate(items):
                if item.get("title", "").lower() == query:
                    found.append((cat, subcat, i, item["title"]))

    if not found:
        print(f"\n  Kein Stub mit Titel '{args.title}' gefunden.")
        return

    if len(found) > 1:
        print(f"\n  Mehrere Treffer fuer '{args.title}':")
        for idx, (cat, subcat, _, title) in enumerate(found):
            print(f"    {idx+1}. {title} in {cat}/{subcat}")
        print("\n  Bitte genauer spezifizieren.")
        return

    cat, subcat, idx, title = found[0]
    del data["MetaWiki"][cat][subcat][idx]
    save_json(data)
    print(f"\n  Entfernt: '{title}' aus {cat}/{subcat}")


def cmd_stats(args):
    """Zeigt Statistiken."""
    data = load_json()
    stubs = get_all_stubs(data)

    cat_counts = defaultdict(int)
    sub_counts = defaultdict(lambda: defaultdict(int))
    tag_counts = defaultdict(int)
    empty_def = 0
    empty_rel = 0

    for stub in stubs:
        cat_counts[stub["_category"]] += 1
        sub_counts[stub["_category"]][stub["_subcategory"]] += 1
        for tag in stub.get("tags", []):
            tag_counts[tag] += 1
        if not stub.get("definition_de", "").strip():
            empty_def += 1
        if not stub.get("relevance", "").strip():
            empty_rel += 1

    print(f"\n  {'='*50}")
    print(f"  MetaWiki Statistiken")
    print(f"  {'='*50}")
    print(f"\n  Gesamt: {len(stubs)} Stubs")
    print(f"  Kategorien: {len(cat_counts)}")
    print(f"  Subkategorien: {sum(len(s) for s in sub_counts.values())}")
    print(f"  Ohne Definition: {empty_def}")
    print(f"  Ohne Relevanz: {empty_rel}")

    print(f"\n  Verteilung:")
    for cat in sorted(cat_counts.keys()):
        cat_display = cat.lstrip("0123456789_").replace("_", " ")
        bar = "#" * (cat_counts[cat] // 2)
        print(f"    {cat_display:35s} {cat_counts[cat]:4d} {bar}")

        if args.verbose:
            for subcat in sorted(sub_counts[cat].keys()):
                sub_display = subcat.replace("_", " ")
                print(f"      {sub_display:33s} {sub_counts[cat][subcat]:4d}")

    print(f"\n  Top 10 Tags:")
    for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"    {tag:30s} {count:4d}")


def cmd_export(args):
    """Exportiert JSON nach Markdown."""
    data = load_json()
    stubs = get_all_stubs(data)
    output_dir = BASE_PATH / "output"
    exported = 0

    for stub in stubs:
        cat = stub["_category"]
        subcat = stub["_subcategory"]
        folder = output_dir / cat / subcat
        folder.mkdir(parents=True, exist_ok=True)

        safe_title = stub["title"].replace(" ", "_").replace("/", "_")
        filepath = folder / f"{safe_title}.md"

        cat_display = cat.lstrip("0123456789_").replace("_", " ")
        sub_display = subcat.replace("_", " ")

        content = f"# {stub['title']}\n\n"
        content += f"**Kurzdefinition:**\n{stub.get('definition_de', '')}\n\n"
        content += f"**Kategorie:**\n{cat_display} > {sub_display}\n\n"
        content += f"**Relevanz:**\n{stub.get('relevance', '')}\n\n"
        if stub.get("definition_en"):
            content += f"**Definition (EN):**\n{stub['definition_en']}\n\n"
        if stub.get("tags"):
            content += f"**Tags:**\n{', '.join(stub['tags'])}\n"

        filepath.write_text(content, encoding="utf-8")
        exported += 1

    print(f"\n  {exported} Stubs exportiert nach {output_dir}")


def cmd_import_md(args):
    """Importiert Markdown-Dateien."""
    # Delegiere an md_to_json.py
    import subprocess
    cmd = [sys.executable, str(BASE_PATH / "md_to_json.py")]
    if args.dry_run:
        cmd.append("--dry-run")
    subprocess.run(cmd)


def cmd_check(args):
    """Konsistenzpruefung."""
    # Delegiere an check_duplicates.py
    import subprocess
    cmd = [sys.executable, str(BASE_PATH / "check_duplicates.py")]
    if args.similar:
        cmd.append("--similar")
    subprocess.run(cmd)


# ==================== MAIN ====================

def main():
    parser = argparse.ArgumentParser(
        description="MetaWiki CLI - Stub-Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  metawiki_cli.py list                                    # Alle Stubs auflisten
  metawiki_cli.py list --category 07 --limit 20           # Informatik, max 20
  metawiki_cli.py search "Matrix"                         # Suche nach "Matrix"
  metawiki_cli.py add -t "Neues Thema" -d "Definition"    # Stub hinzufuegen
                  -c 07_Informatik_KI -s Software_Engineering
  metawiki_cli.py remove -t "Altes Thema"                 # Stub entfernen
  metawiki_cli.py stats                                   # Statistiken
  metawiki_cli.py stats -v                                # Detaillierte Statistiken
  metawiki_cli.py export                                  # JSON -> Markdown
  metawiki_cli.py import                                  # Markdown -> JSON
  metawiki_cli.py check --similar                         # Konsistenzpruefung
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Verfuegbare Befehle")

    # list
    p_list = subparsers.add_parser("list", help="Stubs auflisten")
    p_list.add_argument("--category", "-c", help="Nach Kategorie filtern")
    p_list.add_argument("--subcategory", "-s", help="Nach Subkategorie filtern")
    p_list.add_argument("--limit", "-l", type=int, help="Maximale Anzahl")
    p_list.set_defaults(func=cmd_list)

    # search
    p_search = subparsers.add_parser("search", help="Stubs suchen")
    p_search.add_argument("query", help="Suchbegriff")
    p_search.set_defaults(func=cmd_search)

    # add
    p_add = subparsers.add_parser("add", help="Stub hinzufuegen")
    p_add.add_argument("--title", "-t", required=True, help="Titel des Stubs")
    p_add.add_argument("--definition", "-d", required=True, help="Definition (DE)")
    p_add.add_argument("--relevance", "-r", help="Relevanz")
    p_add.add_argument("--category", "-c", required=True, help="Kategorie (z.B. 07_Informatik_KI)")
    p_add.add_argument("--subcategory", "-s", required=True, help="Subkategorie (z.B. Software_Engineering)")
    p_add.set_defaults(func=cmd_add)

    # remove
    p_remove = subparsers.add_parser("remove", help="Stub entfernen")
    p_remove.add_argument("--title", "-t", required=True, help="Titel des Stubs")
    p_remove.set_defaults(func=cmd_remove)

    # stats
    p_stats = subparsers.add_parser("stats", help="Statistiken anzeigen")
    p_stats.add_argument("--verbose", "-v", action="store_true", help="Detaillierte Ausgabe")
    p_stats.set_defaults(func=cmd_stats)

    # export
    p_export = subparsers.add_parser("export", help="JSON nach Markdown exportieren")
    p_export.set_defaults(func=cmd_export)

    # import
    p_import = subparsers.add_parser("import", help="Markdown nach JSON importieren")
    p_import.add_argument("--dry-run", action="store_true", help="Nur anzeigen")
    p_import.set_defaults(func=cmd_import_md)

    # check
    p_check = subparsers.add_parser("check", help="Konsistenzpruefung")
    p_check.add_argument("--similar", action="store_true", help="Aehnliche Titel finden")
    p_check.set_defaults(func=cmd_check)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
