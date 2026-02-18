#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_duplicates.py - Konsistenzpruefung fuer MetaWiki
======================================================

Prueft metawiki.json auf:
- Duplikate: Gleiche Titel in verschiedenen Kategorien/Subkategorien
- Aehnliche Titel: Levenshtein-Distanz-basierte Erkennung
- Leere Eintraege: Stubs ohne Definition oder Relevanz

Nutzung:
    python check_duplicates.py                # Standard-Pruefung
    python check_duplicates.py --similar      # Auch aehnliche Titel finden
    python check_duplicates.py --fix          # Interaktiv bereinigen
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

BASE_PATH = Path(__file__).parent.resolve()
JSON_PATH = BASE_PATH / "metawiki.json"


def load_json():
    """Laedt metawiki.json."""
    if not JSON_PATH.exists():
        print(f"FEHLER: {JSON_PATH} nicht gefunden.")
        sys.exit(1)

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_all_stubs(data):
    """Extrahiert alle Stubs mit Kategorie-Info."""
    stubs = []
    for cat, subcats in data.get("MetaWiki", {}).items():
        if not isinstance(subcats, dict):
            continue
        for subcat, items in subcats.items():
            if not isinstance(items, list):
                continue
            for item in items:
                stubs.append({
                    "title": item.get("title", ""),
                    "definition_de": item.get("definition_de", ""),
                    "relevance": item.get("relevance", ""),
                    "tags": item.get("tags", []),
                    "category": cat,
                    "subcategory": subcat
                })
    return stubs


def find_exact_duplicates(stubs):
    """Findet exakte Titel-Duplikate (case-insensitive)."""
    title_map = defaultdict(list)
    for stub in stubs:
        key = stub["title"].lower().strip()
        title_map[key].append(stub)

    duplicates = {k: v for k, v in title_map.items() if len(v) > 1}
    return duplicates


def find_similar_titles(stubs, threshold=0.85):
    """Findet aehnliche Titel mittels einfacher Aehnlichkeitsmessung."""
    similar = []
    titles = [(s["title"], s) for s in stubs]

    for i in range(len(titles)):
        for j in range(i + 1, len(titles)):
            t1, s1 = titles[i]
            t2, s2 = titles[j]

            # Gleiche Kategorie + Subkategorie -> kein interessanter Fund
            if s1["category"] == s2["category"] and s1["subcategory"] == s2["subcategory"]:
                continue

            ratio = _similarity(t1.lower(), t2.lower())
            if ratio >= threshold and t1.lower() != t2.lower():
                similar.append((s1, s2, ratio))

    return sorted(similar, key=lambda x: -x[2])


def _similarity(a, b):
    """Einfache Zeichenkettenaehnlichkeit (SequenceMatcher-Algorithmus)."""
    from difflib import SequenceMatcher
    return SequenceMatcher(None, a, b).ratio()


def find_empty_entries(stubs):
    """Findet Stubs mit fehlenden Pflichtfeldern."""
    empty = []
    for stub in stubs:
        issues = []
        if not stub["definition_de"].strip():
            issues.append("definition_de leer")
        if not stub["relevance"].strip():
            issues.append("relevanz leer")
        if not stub["tags"]:
            issues.append("keine tags")
        if issues:
            empty.append((stub, issues))
    return empty


def main():
    import argparse
    parser = argparse.ArgumentParser(description="MetaWiki: Konsistenzpruefung")
    parser.add_argument("--similar", action="store_true", help="Auch aehnliche Titel finden")
    parser.add_argument("--threshold", type=float, default=0.85, help="Aehnlichkeits-Schwellwert (0-1)")
    args = parser.parse_args()

    print("=" * 60)
    print("  MetaWiki: Konsistenzpruefung")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    data = load_json()
    stubs = get_all_stubs(data)
    print(f"\nGeprueft: {len(stubs)} Stubs")

    # 1. Exakte Duplikate
    print(f"\n{'='*60}")
    print("  1. EXAKTE DUPLIKATE (gleicher Titel)")
    print(f"{'='*60}")

    duplicates = find_exact_duplicates(stubs)
    if duplicates:
        print(f"\n  {len(duplicates)} Duplikate gefunden:\n")
        for title, entries in sorted(duplicates.items()):
            print(f"  [{title}]")
            for e in entries:
                print(f"    -> {e['category']}/{e['subcategory']}")
            print()
    else:
        print("\n  Keine exakten Duplikate gefunden.")

    # 2. Aehnliche Titel
    if args.similar:
        print(f"\n{'='*60}")
        print(f"  2. AEHNLICHE TITEL (Schwellwert: {args.threshold})")
        print(f"{'='*60}")

        similar = find_similar_titles(stubs, args.threshold)
        if similar:
            print(f"\n  {len(similar)} aehnliche Paare gefunden:\n")
            for s1, s2, ratio in similar[:30]:  # Max 30 anzeigen
                print(f"  [{ratio:.0%}] '{s1['title']}' <-> '{s2['title']}'")
                print(f"         {s1['category']}/{s1['subcategory']}")
                print(f"         {s2['category']}/{s2['subcategory']}")
                print()
        else:
            print("\n  Keine aehnlichen Titel gefunden.")

    # 3. Leere Eintraege
    print(f"\n{'='*60}")
    print("  3. UNVOLLSTAENDIGE EINTRAEGE")
    print(f"{'='*60}")

    empty = find_empty_entries(stubs)
    if empty:
        print(f"\n  {len(empty)} unvollstaendige Eintraege:\n")
        for stub, issues in empty[:50]:  # Max 50 anzeigen
            print(f"  [{stub['category']}/{stub['subcategory']}] {stub['title']}")
            for issue in issues:
                print(f"    - {issue}")
    else:
        print("\n  Alle Eintraege vollstaendig.")

    # Zusammenfassung
    print(f"\n{'='*60}")
    print("  ZUSAMMENFASSUNG")
    print(f"{'='*60}")
    print(f"    Gesamt Stubs:         {len(stubs)}")
    print(f"    Exakte Duplikate:     {len(duplicates)}")
    if args.similar:
        print(f"    Aehnliche Titel:      {len(similar)}")
    print(f"    Unvollstaendige:      {len(empty)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
