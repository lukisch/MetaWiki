<p align="center">
  <img src="https://img.shields.io/badge/Stubs-630+-blue?style=for-the-badge" alt="Stubs">
  <img src="https://img.shields.io/badge/Sprachen-DE_%7C_EN-orange?style=for-the-badge" alt="Sprachen">
  <img src="https://img.shields.io/badge/Format-JSON-green?style=for-the-badge" alt="Format">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge" alt="Status">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Python-3.10+-yellow?style=for-the-badge" alt="Python">
</p>

<h1 align="center">
  <br>
  <img src="https://raw.githubusercontent.com/github/explore/main/topics/knowledge/knowledge.png" alt="MetaWiki" width="120">
  <br>
  MetaWiki Framework
  <br>
</h1>

<h4 align="center">Ein universelles, modulares Wissensgeruest fuer KI-gestuetzte Wissensarbeit</h4>

---

## Vision

> **Ein einziges, vollstaendiges Wissensskelett – wiederverwendbar fuer jedes Projekt.**

Das MetaWiki ist ein universelles, modular aufgebautes Wissensgeruest aus ca. **630+ kompakten Wissens-Stubs** in 12 Wissenschaftsbereichen. Jeder Stub beschreibt ein Thema in 1–3 Saetzen, neutral, praezise und projektagnostisch – auf **Deutsch und Englisch**.

<table>
<tr>
<td width="50%">

### Die Idee

- Ein einziges, vollstaendiges Wissensskelett
- Wiederverwendbar fuer jedes Projekt
- Erweiterbar nur dort, wo es gebraucht wird
- Automatisiert transformierbar

</td>
<td width="50%">

### Einsatzgebiete

- KI-gestuetzte Wissensarbeit
- Dokumentation & Recherche
- Ontologien & Lernsysteme
- Softwareprojekte

</td>
</tr>
</table>

## Grundidee

Alle Stubs werden in einer **einheitlichen JSON-Struktur** gespeichert.

### Warum JSON?

| Eigenschaft | Vorteil |
|-------------|---------|
| Maschinenlesbar | Einfache Verarbeitung |
| Versionierbar | Git-freundlich |
| Python-kompatibel | Automatisierung |
| Uebersetzbar | Mehrsprachigkeit |
| KI-freundlich | LLM-Integration |

### Moegliche Outputs

```
                    ┌─────────────────┐
                    │   JSON Master   │
                    │    (Source)     │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   Markdown    │   │   Obsidian    │   │   Webseiten   │
│    Files      │   │    Vault      │   │   (HTML)      │
└───────────────┘   └───────────────┘   └───────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  API-Daten    │   │  Embeddings   │   │ Uebersetzung  │
│   (REST)      │   │   (Vektor)    │   │   (EN/...)    │
└───────────────┘   └───────────────┘   └───────────────┘
```

## JSON-Struktur

### Beispiel eines Stubs

```json
{
  "MetaWiki": {
    "07_Informatik_KI": {
      "Software_Engineering": [
        {
          "title": "Domain-Driven Design",
          "definition_de": "Ein Ansatz zur Modellierung komplexer Software, der die Fachdomaene in den Mittelpunkt stellt.",
          "definition_en": "An approach to modeling complex software that places the business domain at the center of development.",
          "relevance": "Hilft, komplexe Systeme verstaendlich und wartbar zu gestalten.",
          "tags": ["Informatik", "Software Engineering"]
        }
      ]
    }
  }
}
```

### Felderklaerung

| Feld | Beschreibung |
|---|---|
| `title` | Name des Konzepts |
| `definition_de` | Deutsche Definition (1–3 Saetze) |
| `definition_en` | Englische Uebersetzung |
| `relevance` | Warum ist das wichtig? |
| `tags` | Kategorisierung fuer Suche/Filter |

## Automatisierung

### Python-Pipeline

```python
import json

# JSON laden
with open("metawiki.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Alle Stubs abrufen (bilingual)
for category, subcats in data["MetaWiki"].items():
    for subcat, stubs in subcats.items():
        for stub in stubs:
            print(stub["title"])
            print(stub["definition_de"])  # Deutsch
            print(stub["definition_en"])  # English

# Neue Stubs nach dem Hinzufuegen uebersetzen
# python metawiki_pipeline.py translate
```

## KI-Uebersetzung (Phase 4)

Alle 630 Stubs sind bereits vollstaendig **zweisprachig (DE + EN)**. Fuer neue Stubs, die spaeter hinzugefuegt werden:

```bash
# API-Key setzen und optionales Paket installieren
export ANTHROPIC_API_KEY="sk-ant-..."
pip install anthropic

# Alle Stubs uebersetzen (fehlende definition_en)
python metawiki_pipeline.py translate

# Mit Limit (z.B. nur 50 Stubs)
python metawiki_pipeline.py translate --limit 50

# Verfuegbarkeit pruefen
python translate.py --check
```

Als Python-Modul:

```python
from translate import translate_text

english = translate_text("Ein Grenzwert beschreibt den Wert, dem sich eine Funktion annaeht.")
print(english)
# → "A limit describes the value that a function approaches."
```

Ohne gesetzten `ANTHROPIC_API_KEY` oder ohne `pip install anthropic` wird die Uebersetzung lautlos uebersprungen.

## Roadmap

### Phase 1 - Strukturaufbau `[ABGESCHLOSSEN]`

- [x] Definition der 12 Oberthemen
- [x] Definition von 80-120 Hauptbereichen
- [x] 630+ Stubs erstellt und in JSON importiert
- [x] Konsistenzpruefung (check_duplicates.py)

### Phase 2 - JSON-Masterdatei `[ABGESCHLOSSEN]`

- [x] Alle Stubs in metawiki.json zusammengefuehrt (md_to_json.py)
- [x] Bidirektionale Synchronisation JSON <-> Markdown (metawiki_pipeline.py)

### Phase 3 - Automatisierung `[ABGESCHLOSSEN]`

- [x] Python-Pipeline fuer Markdown-Export (metawiki_pipeline.py)
- [x] Markdown-Generator
- [x] Ordnerstruktur-Generator
- [x] CLI-Tool fuer Stub-Management (metawiki_cli.py)

### Phase 4 - Mehrsprachigkeit `[ABGESCHLOSSEN]`

- [x] Automatische Uebersetzung in Englisch via Claude API (translate.py)
- [x] Optionale Uebersetzungen in weitere Sprachen (EN/FR/ES/IT/PT)
- [x] translate-Befehl in metawiki_pipeline.py

### Phase 5 - Erweiterungen `[GEPLANT]`

- [ ] JSON-Schema-Validierung
- [ ] Einheitliches Tag-System
- [ ] Export nach Obsidian / GitHub Pages
- [ ] Sprachspezifische Markdown-Exports (DE/EN getrennt)
- [ ] Embeddings-Generierung fuer Vektor-Suche
- [ ] Such-API (REST)
- [ ] Web-Interface (FastAPI + HTML)
- [ ] KI-gestuetzte Stub-Erweiterung

## Ziel

```
   ╔══════════════════════════════════════════════════╗
   ║                                                  ║
   ║   Ein Wissenssystem, das du einmal erzeugst      ║
   ║   und fuer immer wiederverwenden kannst.          ║
   ║                                                  ║
   ╚══════════════════════════════════════════════════╝
```

### Das MetaWiki ist...

| Eigenschaft | Beschreibung |
|---|---|
| In JSON gespeichert | Maschinenlesbar & versionierbar |
| In Markdown exportierbar | Menschenlesbar & dokumentierbar |
| Zweisprachig (DE/EN) | Vollstaendig uebersetzt |
| In jede Sprache uebersetzbar | Global einsetzbar |
| Modular erweiterbar | Waechst mit deinen Anforderungen |
| KI-freundlich | Optimiert fuer LLM-Integration |
| Projektagnostisch | Fuer jeden Anwendungsfall |

<p align="center">
  <sub>Built with brain and AI &nbsp;|&nbsp; Developed by <a href="https://github.com/lukisch">lukisch</a></sub>
</p>

---

## English

**A universal, modular knowledge framework for AI-assisted knowledge work**

### Vision

> **A single, complete knowledge skeleton – reusable for any project.**

MetaWiki is a universal, modular knowledge framework of **630+ compact knowledge stubs** across 12 scientific domains. Each stub describes a topic in 1–3 sentences, neutral, precise and project-agnostic – in **German and English**.

<table>
<tr>
<td width="50%">

#### The Idea

- A single, complete knowledge skeleton
- Reusable for any project
- Extendable only where needed
- Automatically transformable

</td>
<td width="50%">

#### Use Cases

- AI-assisted knowledge work
- Documentation & Research
- Ontologies & Learning Systems
- Software Projects

</td>
</tr>
</table>

### Concept

All stubs are stored in a **unified JSON structure**.

#### Why JSON?

| Property | Benefit |
|----------|---------|
| Machine-readable | Easy processing |
| Version-controlled | Git-friendly |
| Python-compatible | Automation |
| Translatable | Multilingual |
| AI-friendly | LLM integration |

#### Possible Outputs

```
                    ┌─────────────────┐
                    │   JSON Master   │
                    │    (Source)     │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   Markdown    │   │   Obsidian    │   │   Websites    │
│    Files      │   │    Vault      │   │   (HTML)      │
└───────────────┘   └───────────────┘   └───────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  API Data     │   │  Embeddings   │   │ Translation   │
│   (REST)      │   │   (Vector)    │   │   (EN/...)    │
└───────────────┘   └───────────────┘   └───────────────┘
```

### JSON Structure

#### Example Stub

```json
{
  "MetaWiki": {
    "07_Informatik_KI": {
      "Software_Engineering": [
        {
          "title": "Domain-Driven Design",
          "definition_de": "Ein Ansatz zur Modellierung komplexer Software, der die Fachdomaene in den Mittelpunkt stellt.",
          "definition_en": "An approach to modeling complex software that places the business domain at the center of development.",
          "relevance": "Hilft, komplexe Systeme verstaendlich und wartbar zu gestalten.",
          "tags": ["Informatik", "Software Engineering"]
        }
      ]
    }
  }
}
```

#### Field Description

| Field | Description |
|---|---|
| `title` | Concept name |
| `definition_de` | German definition (1–3 sentences) |
| `definition_en` | English translation |
| `relevance` | Why does it matter? |
| `tags` | Categorization for search/filter |

### Automation

#### Python Pipeline

```python
import json

# Load JSON
with open("metawiki.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Retrieve all stubs (bilingual)
for category, subcats in data["MetaWiki"].items():
    for subcat, stubs in subcats.items():
        for stub in stubs:
            print(stub["title"])
            print(stub["definition_de"])  # German
            print(stub["definition_en"])  # English

# Translate new stubs after adding them
# python metawiki_pipeline.py translate
```

### AI Translation (Phase 4)

All 630 stubs are already fully **bilingual (DE + EN)**. For new stubs added later:

```bash
# Set API key and install optional package
export ANTHROPIC_API_KEY="sk-ant-..."
pip install anthropic

# Translate all stubs (missing definition_en)
python metawiki_pipeline.py translate

# With limit (e.g., only 50 stubs)
python metawiki_pipeline.py translate --limit 50

# Check availability
python translate.py --check
```

As a Python module:

```python
from translate import translate_text

english = translate_text("Ein Grenzwert beschreibt den Wert, dem sich eine Funktion annaeht.")
print(english)
# → "A limit describes the value that a function approaches."
```

Without a set `ANTHROPIC_API_KEY` or without `pip install anthropic`, translation is silently skipped.

### Roadmap

#### Phase 1 - Structure Setup `[COMPLETED]`

- [x] Definition of 12 top-level topics
- [x] Definition of 80-120 main areas
- [x] 630+ stubs created and imported into JSON
- [x] Consistency check (check_duplicates.py)

#### Phase 2 - JSON Master File `[COMPLETED]`

- [x] All stubs merged into metawiki.json (md_to_json.py)
- [x] Bidirectional synchronization JSON <-> Markdown (metawiki_pipeline.py)

#### Phase 3 - Automation `[COMPLETED]`

- [x] Python pipeline for Markdown export (metawiki_pipeline.py)
- [x] Markdown generator
- [x] Folder structure generator
- [x] CLI tool for stub management (metawiki_cli.py)

#### Phase 4 - Multilingual Support `[COMPLETED]`

- [x] Automatic translation to English via Claude API (translate.py)
- [x] Optional translations into additional languages (EN/FR/ES/IT/PT)
- [x] translate command in metawiki_pipeline.py

#### Phase 5 - Extensions `[PLANNED]`

- [ ] JSON schema validation
- [ ] Unified tag system
- [ ] Export to Obsidian / GitHub Pages
- [ ] Language-specific Markdown exports (DE/EN separate)
- [ ] Embeddings generation for vector search
- [ ] Search API (REST)
- [ ] Web interface (FastAPI + HTML)
- [ ] AI-assisted stub expansion

### Goal

```
   ╔══════════════════════════════════════════════════╗
   ║                                                  ║
   ║   A knowledge system you build once              ║
   ║   and reuse forever.                             ║
   ║                                                  ║
   ╚══════════════════════════════════════════════════╝
```

#### MetaWiki is...

| Property | Description |
|---|---|
| Stored in JSON | Machine-readable & version-controlled |
| Exportable to Markdown | Human-readable & documentable |
| Bilingual (DE/EN) | Fully translated |
| Translatable to any language | Globally deployable |
| Modularly extensible | Grows with your requirements |
| AI-friendly | Optimized for LLM integration |
| Project-agnostic | For any use case |

<p align="center">
  <sub>Built with brain and AI &nbsp;|&nbsp; Developed by <a href="https://github.com/lukisch">lukisch</a></sub>
</p>
