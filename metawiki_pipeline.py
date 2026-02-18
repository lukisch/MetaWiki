#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MetaWiki Pipeline - Vollständiges Wissensdatenbank-Management
=============================================================

Features:
- Markdown → JSON Konvertierung
- JSON → Markdown Export
- Bidirektionale Synchronisation
- Validierung und Konsistenzprüfung
- Statistiken und Reporting
- Tag-Management
"""

import json
import os
import re
import sys
import hashlib
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
import argparse

# ==================== KONFIGURATION ====================

BASE_PATH = Path(__file__).parent.resolve()
JSON_PATH = BASE_PATH / "metawiki.json"
OUTPUT_PATH = BASE_PATH / "output"
BACKUP_PATH = BASE_PATH / "backups"

# Kategorien-Ordner (mit Nummern-Prefix)
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

# Validierungsregeln
MAX_DEFINITION_LENGTH = 500
MIN_DEFINITION_LENGTH = 20
MAX_RELEVANCE_LENGTH = 300


# ==================== DATENKLASSEN ====================

@dataclass
class WikiStub:
    """Ein einzelner Wissenseintrag."""
    title: str
    definition_de: str
    definition_en: str = ""
    relevance: str = ""
    tags: List[str] = field(default_factory=list)
    category: str = ""
    subcategory: str = ""
    source_file: str = ""
    content_hash: str = ""

    def compute_hash(self) -> str:
        """Berechnet einen Hash über den Inhalt."""
        content = f"{self.title}|{self.definition_de}|{self.relevance}"
        return hashlib.md5(content.encode()).hexdigest()[:8]

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "definition_de": self.definition_de,
            "definition_en": self.definition_en,
            "relevance": self.relevance,
            "tags": self.tags
        }

    @classmethod
    def from_dict(cls, data: dict, category: str = "", subcategory: str = "") -> 'WikiStub':
        return cls(
            title=data.get("title", ""),
            definition_de=data.get("definition_de", ""),
            definition_en=data.get("definition_en", ""),
            relevance=data.get("relevance", ""),
            tags=data.get("tags", []),
            category=category,
            subcategory=subcategory
        )


@dataclass
class ValidationResult:
    """Ergebnis einer Validierung."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# ==================== MARKDOWN PARSER ====================

class MarkdownParser:
    """Parst MetaWiki Markdown-Dateien."""

    @staticmethod
    def parse_file(filepath: Path) -> Optional[WikiStub]:
        """Parst eine Markdown-Datei in einen WikiStub."""
        try:
            content = filepath.read_text(encoding="utf-8")
            return MarkdownParser.parse_content(content, str(filepath))
        except Exception as e:
            print(f"  ⚠ Fehler beim Lesen von {filepath}: {e}")
            return None

    @staticmethod
    def parse_content(content: str, source_file: str = "") -> Optional[WikiStub]:
        """Parst Markdown-Content in einen WikiStub."""
        lines = content.strip().split('\n')

        title = ""
        definition = ""
        category = ""
        relevance = ""
        tags = []

        current_section = None
        section_content = []

        for line in lines:
            line = line.strip()

            # Titel (# ...)
            if line.startswith("# ") and not title:
                title = line[2:].strip()
                continue

            # Sektions-Header
            if line.startswith("**") and line.endswith(":**"):
                # Speichere vorherige Sektion
                if current_section and section_content:
                    text = ' '.join(section_content).strip()
                    if current_section == "kurzdefinition":
                        definition = text
                    elif current_section == "kategorie":
                        category = text
                    elif current_section == "relevanz":
                        relevance = text

                # Neue Sektion
                header = line[2:-3].lower()
                current_section = header
                section_content = []
                continue

            # Inhalt sammeln
            if current_section and line:
                section_content.append(line)

        # Letzte Sektion speichern
        if current_section and section_content:
            text = ' '.join(section_content).strip()
            if current_section == "kurzdefinition":
                definition = text
            elif current_section == "kategorie":
                category = text
            elif current_section == "relevanz":
                relevance = text

        if not title:
            return None

        # Bereinige unerwünschte Zeichen (z.B. 同期)
        definition = MarkdownParser._clean_text(definition)
        relevance = MarkdownParser._clean_text(relevance)

        # Extrahiere Kategorie/Subkategorie aus Pfad
        cat, subcat = MarkdownParser._extract_category_from_path(source_file)

        # Tags aus Kategorie generieren
        if cat:
            tags = [cat.replace("_", " ").lstrip("0123456789_")]
            if subcat:
                tags.append(subcat.replace("_", " "))

        stub = WikiStub(
            title=title,
            definition_de=definition,
            relevance=relevance,
            tags=tags,
            category=cat,
            subcategory=subcat,
            source_file=source_file
        )
        stub.content_hash = stub.compute_hash()

        return stub

    @staticmethod
    def _clean_text(text: str) -> str:
        """Entfernt unerwünschte Zeichen."""
        # Entferne nicht-lateinische Zeichen am Ende
        text = re.sub(r'[^\x00-\x7F]+$', '', text)
        # Entferne doppelte Leerzeichen
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def _extract_category_from_path(filepath: str) -> Tuple[str, str]:
        """Extrahiert Kategorie und Subkategorie aus dem Dateipfad."""
        parts = Path(filepath).parts

        category = ""
        subcategory = ""

        for i, part in enumerate(parts):
            # Suche nach Kategorie-Ordner
            for cat_folder in CATEGORY_FOLDERS:
                if part == cat_folder or part.endswith(cat_folder):
                    category = cat_folder
                    # Nächster Teil ist Subkategorie
                    if i + 1 < len(parts) - 1:  # -1 weil letztes Element die Datei ist
                        subcategory = parts[i + 1]
                    break

        return category, subcategory


# ==================== JSON HANDLER ====================

class JsonHandler:
    """Verwaltet die MetaWiki JSON-Datei."""

    def __init__(self, json_path: Path = JSON_PATH):
        self.json_path = json_path
        self.data: Dict = {"MetaWiki": {}}

    def load(self) -> bool:
        """Lädt die JSON-Datei."""
        if not self.json_path.exists():
            print(f"  ℹ JSON-Datei nicht gefunden, erstelle neue.")
            return True

        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            return True
        except Exception as e:
            print(f"  ✗ Fehler beim Laden: {e}")
            return False

    def save(self) -> bool:
        """Speichert die JSON-Datei."""
        try:
            # Backup erstellen
            if self.json_path.exists():
                BACKUP_PATH.mkdir(exist_ok=True)
                backup_name = f"metawiki_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                backup_file = BACKUP_PATH / backup_name

                import shutil
                shutil.copy(self.json_path, backup_file)

            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"  ✗ Fehler beim Speichern: {e}")
            return False

    def add_stub(self, stub: WikiStub) -> bool:
        """Fügt einen Stub hinzu."""
        if "MetaWiki" not in self.data:
            self.data["MetaWiki"] = {}

        root = self.data["MetaWiki"]

        # Kategorie
        if stub.category not in root:
            root[stub.category] = {}

        # Subkategorie
        if stub.subcategory not in root[stub.category]:
            root[stub.category][stub.subcategory] = []

        # Prüfe auf Duplikate
        existing = root[stub.category][stub.subcategory]
        for i, item in enumerate(existing):
            if item.get("title") == stub.title:
                # Update
                existing[i] = stub.to_dict()
                return True

        # Neu hinzufügen
        existing.append(stub.to_dict())
        return True

    def get_all_stubs(self) -> List[WikiStub]:
        """Gibt alle Stubs zurück."""
        stubs = []

        if "MetaWiki" not in self.data:
            return stubs

        for category, subcats in self.data["MetaWiki"].items():
            if not isinstance(subcats, dict):
                continue
            for subcategory, items in subcats.items():
                if not isinstance(items, list):
                    continue
                for item in items:
                    stub = WikiStub.from_dict(item, category, subcategory)
                    stubs.append(stub)

        return stubs

    def get_statistics(self) -> Dict:
        """Gibt Statistiken zurück."""
        stubs = self.get_all_stubs()

        categories = {}
        tags = {}

        for stub in stubs:
            # Kategorien zählen
            if stub.category not in categories:
                categories[stub.category] = {"total": 0, "subcategories": {}}
            categories[stub.category]["total"] += 1

            if stub.subcategory not in categories[stub.category]["subcategories"]:
                categories[stub.category]["subcategories"][stub.subcategory] = 0
            categories[stub.category]["subcategories"][stub.subcategory] += 1

            # Tags zählen
            for tag in stub.tags:
                tags[tag] = tags.get(tag, 0) + 1

        return {
            "total_stubs": len(stubs),
            "categories": len(categories),
            "category_details": categories,
            "unique_tags": len(tags),
            "tag_frequency": dict(sorted(tags.items(), key=lambda x: -x[1])[:20])
        }


# ==================== MARKDOWN GENERATOR ====================

class MarkdownGenerator:
    """Generiert Markdown-Dateien aus Stubs."""

    @staticmethod
    def generate(stub: WikiStub, include_english: bool = False) -> str:
        """Generiert Markdown-Content."""
        cat_display = stub.category.lstrip("0123456789_").replace("_", " ")
        subcat_display = stub.subcategory.replace("_", " ")

        lines = [
            f"# {stub.title}",
            "",
            "**Kurzdefinition:**",
            stub.definition_de,
            "",
            "**Kategorie:**",
            f"{cat_display} → {subcat_display}",
            "",
            "**Relevanz:**",
            stub.relevance,
            ""
        ]

        if include_english and stub.definition_en:
            lines.extend([
                "**Definition (EN):**",
                stub.definition_en,
                ""
            ])

        if stub.tags:
            lines.extend([
                "**Tags:**",
                ", ".join(stub.tags),
                ""
            ])

        return "\n".join(lines)

    @staticmethod
    def write_file(stub: WikiStub, output_dir: Path, include_english: bool = False) -> bool:
        """Schreibt eine Markdown-Datei."""
        try:
            # Ordnerstruktur
            folder = output_dir / stub.category / stub.subcategory
            folder.mkdir(parents=True, exist_ok=True)

            # Dateiname
            safe_title = stub.title.replace(' ', '_').replace('/', '_')
            filepath = folder / f"{safe_title}.md"

            # Inhalt generieren
            content = MarkdownGenerator.generate(stub, include_english)

            # Schreiben
            filepath.write_text(content, encoding="utf-8")
            return True

        except Exception as e:
            print(f"  ✗ Fehler beim Schreiben von {stub.title}: {e}")
            return False


# ==================== VALIDATOR ====================

class Validator:
    """Validiert MetaWiki-Einträge."""

    @staticmethod
    def validate_stub(stub: WikiStub) -> ValidationResult:
        """Validiert einen einzelnen Stub."""
        errors = []
        warnings = []

        # Titel
        if not stub.title:
            errors.append("Titel fehlt")
        elif len(stub.title) > 100:
            warnings.append(f"Titel zu lang ({len(stub.title)} Zeichen)")

        # Definition
        if not stub.definition_de:
            errors.append("Definition fehlt")
        elif len(stub.definition_de) < MIN_DEFINITION_LENGTH:
            warnings.append(f"Definition zu kurz ({len(stub.definition_de)} < {MIN_DEFINITION_LENGTH})")
        elif len(stub.definition_de) > MAX_DEFINITION_LENGTH:
            warnings.append(f"Definition zu lang ({len(stub.definition_de)} > {MAX_DEFINITION_LENGTH})")

        # Relevanz
        if not stub.relevance:
            warnings.append("Relevanz fehlt")
        elif len(stub.relevance) > MAX_RELEVANCE_LENGTH:
            warnings.append(f"Relevanz zu lang ({len(stub.relevance)} > {MAX_RELEVANCE_LENGTH})")

        # Kategorie
        if not stub.category:
            warnings.append("Kategorie fehlt")

        # Tags
        if not stub.tags:
            warnings.append("Keine Tags")

        # Sonderzeichen prüfen
        if re.search(r'[^\x00-\x7F]', stub.definition_de[-10:] if len(stub.definition_de) > 10 else stub.definition_de):
            # Erlaube Umlaute, aber warnt bei anderen Zeichen
            non_latin = re.findall(r'[^\x00-\xFF]', stub.definition_de)
            if non_latin:
                warnings.append(f"Unerwartete Zeichen: {non_latin}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    @staticmethod
    def find_duplicates(stubs: List[WikiStub]) -> List[Tuple[WikiStub, WikiStub]]:
        """Findet Duplikate basierend auf Titel."""
        duplicates = []
        seen = {}

        for stub in stubs:
            title_lower = stub.title.lower()
            if title_lower in seen:
                duplicates.append((seen[title_lower], stub))
            else:
                seen[title_lower] = stub

        return duplicates


# ==================== PIPELINE COMMANDS ====================

def cmd_import(args):
    """Importiert Markdown-Dateien in JSON."""
    print("\n📥 IMPORT: Markdown → JSON")
    print("=" * 50)

    json_handler = JsonHandler()
    json_handler.load()

    imported = 0
    errors = 0

    # Scanne alle Kategorien
    for category in CATEGORY_FOLDERS:
        cat_path = BASE_PATH / category
        if not cat_path.exists():
            continue

        print(f"\n📁 {category}")

        # Scanne Unterkategorien
        for subcat in cat_path.iterdir():
            if not subcat.is_dir():
                continue

            # Scanne MD-Dateien
            for md_file in subcat.glob("*.md"):
                stub = MarkdownParser.parse_file(md_file)
                if stub:
                    json_handler.add_stub(stub)
                    imported += 1
                    print(f"  ✓ {stub.title}")
                else:
                    errors += 1
                    print(f"  ✗ {md_file.name}")

    # Speichern
    if imported > 0:
        json_handler.save()

    print(f"\n{'=' * 50}")
    print(f"✓ {imported} Stubs importiert, {errors} Fehler")


def cmd_export(args):
    """Exportiert JSON nach Markdown."""
    print("\n📤 EXPORT: JSON → Markdown")
    print("=" * 50)

    output_dir = OUTPUT_PATH if args.output else BASE_PATH

    json_handler = JsonHandler()
    if not json_handler.load():
        return

    stubs = json_handler.get_all_stubs()
    print(f"  Gefunden: {len(stubs)} Stubs")

    exported = 0
    for stub in stubs:
        if MarkdownGenerator.write_file(stub, output_dir, args.english):
            exported += 1

    print(f"\n✓ {exported} Dateien exportiert nach {output_dir}")


def cmd_validate(args):
    """Validiert alle Einträge."""
    print("\n🔍 VALIDIERUNG")
    print("=" * 50)

    json_handler = JsonHandler()
    json_handler.load()
    stubs = json_handler.get_all_stubs()

    valid = 0
    with_warnings = 0
    invalid = 0

    for stub in stubs:
        result = Validator.validate_stub(stub)

        if not result.is_valid:
            invalid += 1
            print(f"\n✗ {stub.title}")
            for err in result.errors:
                print(f"    ERROR: {err}")
            for warn in result.warnings:
                print(f"    WARN: {warn}")
        elif result.warnings:
            with_warnings += 1
            if args.verbose:
                print(f"\n⚠ {stub.title}")
                for warn in result.warnings:
                    print(f"    WARN: {warn}")
        else:
            valid += 1

    # Duplikate
    duplicates = Validator.find_duplicates(stubs)
    if duplicates:
        print(f"\n⚠ {len(duplicates)} Duplikate gefunden:")
        for stub1, stub2 in duplicates:
            print(f"  - {stub1.title}: {stub1.category}/{stub1.subcategory} vs {stub2.category}/{stub2.subcategory}")

    print(f"\n{'=' * 50}")
    print(f"✓ Gültig: {valid} | ⚠ Mit Warnungen: {with_warnings} | ✗ Ungültig: {invalid}")
    print(f"🔄 Duplikate: {len(duplicates)}")


def cmd_stats(args):
    """Zeigt Statistiken an."""
    print("\n📊 STATISTIKEN")
    print("=" * 50)

    json_handler = JsonHandler()
    json_handler.load()
    stats = json_handler.get_statistics()

    print(f"\n📈 Übersicht:")
    print(f"   Gesamt-Stubs: {stats['total_stubs']}")
    print(f"   Kategorien: {stats['categories']}")
    print(f"   Eindeutige Tags: {stats['unique_tags']}")

    print(f"\n📁 Kategorien:")
    for cat, details in sorted(stats['category_details'].items()):
        print(f"   {cat}: {details['total']} Stubs")
        if args.verbose:
            for subcat, count in details['subcategories'].items():
                print(f"      └─ {subcat}: {count}")

    print(f"\n🏷 Top Tags:")
    for tag, count in list(stats['tag_frequency'].items())[:10]:
        print(f"   {tag}: {count}")


def cmd_sync(args):
    """Bidirektionale Synchronisation."""
    print("\n🔄 SYNCHRONISATION")
    print("=" * 50)

    # Erst Import
    print("\n1️⃣ Importiere neue Markdown-Dateien...")

    json_handler = JsonHandler()
    json_handler.load()
    existing_titles = {s.title.lower() for s in json_handler.get_all_stubs()}

    new_stubs = 0

    for category in CATEGORY_FOLDERS:
        cat_path = BASE_PATH / category
        if not cat_path.exists():
            continue

        for subcat in cat_path.iterdir():
            if not subcat.is_dir():
                continue

            for md_file in subcat.glob("*.md"):
                stub = MarkdownParser.parse_file(md_file)
                if stub and stub.title.lower() not in existing_titles:
                    json_handler.add_stub(stub)
                    new_stubs += 1
                    print(f"  + {stub.title}")

    if new_stubs > 0:
        json_handler.save()

    print(f"\n   ✓ {new_stubs} neue Stubs importiert")

    # Dann Export (wenn gewünscht)
    if args.export:
        print("\n2️⃣ Exportiere nach Markdown...")
        stubs = json_handler.get_all_stubs()
        for stub in stubs:
            MarkdownGenerator.write_file(stub, OUTPUT_PATH)
        print(f"   ✓ {len(stubs)} Dateien exportiert")


def cmd_translate(args):
    """Uebersetzt alle Stubs mit fehlender definition_en via Claude API."""
    print("\n🌐 UEBERSETZUNG")
    print("=" * 50)

    try:
        from translate import translate_text, is_available
    except ImportError:
        print("  ✗ translate.py nicht gefunden.")
        return

    if not is_available():
        print("  ✗ Uebersetzung nicht verfuegbar.")
        print("  Bitte setze ANTHROPIC_API_KEY und installiere: pip install anthropic")
        return

    import time

    json_handler = JsonHandler()
    json_handler.load()
    stubs = json_handler.get_all_stubs()

    to_translate = [s for s in stubs if not s.definition_en]
    total = len(to_translate)

    if args.limit and args.limit < total:
        to_translate = to_translate[:args.limit]

    print(f"  Gesamt ohne Uebersetzung: {total}")
    print(f"  Zu uebersetzen: {len(to_translate)}")

    translated = 0
    errors = 0

    for stub in to_translate:
        result = translate_text(stub.definition_de)
        if result:
            stub.definition_en = result
            json_handler.add_stub(stub)
            translated += 1
            print(f"  ✓ {stub.title}")
        else:
            errors += 1
            print(f"  ✗ {stub.title}")

        if translated < len(to_translate):
            time.sleep(0.3)

    if translated > 0:
        json_handler.save()

    print(f"\n{'=' * 50}")
    print(f"✓ {translated} uebersetzt, {errors} Fehler")


def cmd_clean(args):
    """Bereinigt Daten (Encoding-Fehler, etc.)."""
    print("\n🧹 BEREINIGUNG")
    print("=" * 50)

    json_handler = JsonHandler()
    json_handler.load()
    stubs = json_handler.get_all_stubs()

    cleaned = 0

    for stub in stubs:
        original_def = stub.definition_de
        original_rel = stub.relevance

        # Bereinige
        stub.definition_de = MarkdownParser._clean_text(stub.definition_de)
        stub.relevance = MarkdownParser._clean_text(stub.relevance)

        if stub.definition_de != original_def or stub.relevance != original_rel:
            cleaned += 1
            print(f"  🧹 {stub.title}")
            json_handler.add_stub(stub)

    if cleaned > 0:
        json_handler.save()

    print(f"\n✓ {cleaned} Einträge bereinigt")


# ==================== MAIN ====================

def main():
    parser = argparse.ArgumentParser(
        description="MetaWiki Pipeline - Wissensdatenbank-Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python metawiki_pipeline.py import          # Markdown → JSON
  python metawiki_pipeline.py export          # JSON → Markdown
  python metawiki_pipeline.py validate -v     # Validierung (verbose)
  python metawiki_pipeline.py stats -v        # Statistiken (detailliert)
  python metawiki_pipeline.py sync            # Bidirektionale Sync
  python metawiki_pipeline.py clean           # Daten bereinigen
  python metawiki_pipeline.py translate       # Englische Uebersetzungen ergaenzen
  python metawiki_pipeline.py translate -l 50 # Maximal 50 Stubs uebersetzen
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Verfügbare Befehle")

    # Import
    p_import = subparsers.add_parser("import", help="Importiere Markdown → JSON")
    p_import.set_defaults(func=cmd_import)

    # Export
    p_export = subparsers.add_parser("export", help="Exportiere JSON → Markdown")
    p_export.add_argument("--output", "-o", action="store_true", help="In output/ exportieren")
    p_export.add_argument("--english", "-e", action="store_true", help="Englische Übersetzung inkludieren")
    p_export.set_defaults(func=cmd_export)

    # Validate
    p_validate = subparsers.add_parser("validate", help="Validiere Einträge")
    p_validate.add_argument("--verbose", "-v", action="store_true", help="Zeige auch Warnungen")
    p_validate.set_defaults(func=cmd_validate)

    # Stats
    p_stats = subparsers.add_parser("stats", help="Zeige Statistiken")
    p_stats.add_argument("--verbose", "-v", action="store_true", help="Detaillierte Ausgabe")
    p_stats.set_defaults(func=cmd_stats)

    # Sync
    p_sync = subparsers.add_parser("sync", help="Bidirektionale Synchronisation")
    p_sync.add_argument("--export", "-e", action="store_true", help="Auch nach Markdown exportieren")
    p_sync.set_defaults(func=cmd_sync)

    # Clean
    p_clean = subparsers.add_parser("clean", help="Bereinige Daten")
    p_clean.set_defaults(func=cmd_clean)

    # Translate
    p_translate = subparsers.add_parser("translate", help="Uebersetze Stubs via Claude API")
    p_translate.add_argument("--limit", "-l", type=int, help="Maximale Anzahl zu uebersetzender Stubs")
    p_translate.set_defaults(func=cmd_translate)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    print(f"\n{'='*60}")
    print(f"  MetaWiki Pipeline v2.0")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    args.func(args)

    print(f"\n{'='*60}")
    print("  Fertig!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
