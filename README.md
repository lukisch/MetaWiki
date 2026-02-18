<p align="center">
  <img src="https://img.shields.io/badge/Stubs-630+-blue?style=for-the-badge" alt="Stubs">
  <img src="https://img.shields.io/badge/Sprachen-DE_%7C_EN-orange?style=for-the-badge" alt="Sprachen">
  <img src="https://img.shields.io/badge/Format-JSON-green?style=for-the-badge" alt="Format">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge" alt="Status">
  <img src="https://img.shields.io/badge/License-GPL--3.0-red?style=for-the-badge" alt="License">
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
<h4 align="center">A universal, modular knowledge framework for AI-assisted knowledge work</h4>

<p align="center">
  <a href="#vision--vision">Vision</a> •
  <a href="#grundidee--concept">Grundidee / Concept</a> •
  <a href="#json-struktur--json-structure">JSON-Struktur</a> •
  <a href="#automatisierung--automation">Automatisierung</a> •
  <a href="#roadmap">Roadmap</a>
</p>

---

## Vision / Vision

> **DE: Ein einziges, vollstaendiges Wissensskelett – wiederverwendbar fuer jedes Projekt.**
>
> **EN: A single, complete knowledge skeleton – reusable for any project.**

Das MetaWiki ist ein universelles, modular aufgebautes Wissensgeruest aus ca. **630+ kompakten Wissens-Stubs** in 12 Wissenschaftsbereichen. Jeder Stub beschreibt ein Thema in 1–3 Saetzen, neutral, praezise und projektagnostisch – auf **Deutsch und Englisch**.

MetaWiki is a universal, modular knowledge framework of **630+ compact knowledge stubs** across 12 scientific domains. Each stub describes a topic in 1–3 sentences, neutral, precise and project-agnostic – in **German and English**.

<table>
<tr>
<td width="50%">

### Die Idee / The Idea

- Ein einziges, vollstaendiges Wissensskelett
- A single, complete knowledge skeleton
- Wiederverwendbar fuer jedes Projekt
- Reusable for any project
- Erweiterbar nur dort, wo es gebraucht wird
- Extendable only where needed
- Automatisiert transformierbar
- Automatically transformable

</td>
<td width="50%">

### Einsatzgebiete / Use Cases

- KI-gestuetzte Wissensarbeit / AI-assisted knowledge work
- Dokumentation & Recherche / Documentation & Research
- Ontologien & Lernsysteme / Ontologies & Learning Systems
- Softwareprojekte / Software Projects

</td>
</tr>
</table>

---

## Grundidee / Concept

Alle Stubs werden in einer **einheitlichen JSON-Struktur** gespeichert. / All stubs are stored in a **unified JSON structure**.

### Warum JSON? / Why JSON?

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

---

## JSON-Struktur / JSON Structure

### Beispiel eines Stubs / Example Stub

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

### Felderklaerung / Field Description

| Feld / Field | DE | EN |
|---|---|---|
| `title` | Name des Konzepts | Concept name |
| `definition_de` | Deutsche Definition (1–3 Saetze) | German definition (1–3 sentences) |
| `definition_en` | Englische Uebersetzung | English translation |
| `relevance` | Warum ist das wichtig? | Why does it matter? |
| `tags` | Kategorisierung fuer Suche/Filter | Categorization for search/filter |

---

## Automatisierung / Automation

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

---

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

---

## Roadmap

### Phase 1 - Strukturaufbau `[ABGESCHLOSSEN]`

- [x] Definition der 12 Oberthemen
- [x] Definition von 80-120 Hauptbereichen
- [x] 630+ Stubs erstellt und in JSON importiert
- [x] Konsistenzpruefung (check_duplicates.py)

### Phase 2 - JSON-Masterdatei `[ABGESCHLOSSEN]`

- [x] Alle Stubs in metawiki.json zusammengefuehrt (md_to_json.py)
- [x] Bidirektionale Synchronisation JSON <-> Markdown (metawiki_pipeline.py)
- [ ] JSON-Schema-Validierung (geplant)
- [ ] Einheitliches Tag-System (geplant)

### Phase 3 - Automatisierung `[ABGESCHLOSSEN]`

- [x] Python-Pipeline fuer Markdown-Export (metawiki_pipeline.py)
- [x] Markdown-Generator
- [x] Ordnerstruktur-Generator
- [x] CLI-Tool fuer Stub-Management (metawiki_cli.py)
- [ ] Export nach Obsidian / GitHub Pages (geplant)

### Phase 4 - Mehrsprachigkeit `[ABGESCHLOSSEN]`

- [x] Automatische Uebersetzung in Englisch via Claude API (translate.py)
- [x] Optionale Uebersetzungen in weitere Sprachen (EN/FR/ES/IT/PT)
- [x] translate-Befehl in metawiki_pipeline.py
- [ ] Sprachspezifische Markdown-Exports (geplant)

### Phase 5 - Erweiterungen `[GEPLANT]`

- [ ] Embeddings-Generierung fuer Vektor-Suche
- [ ] Such-API (REST)
- [ ] Web-Interface (FastAPI + HTML)
- [ ] KI-gestuetzte Stub-Erweiterung

---

## Ziel / Goal

<table>
<tr>
<td>

```
   ╔══════════════════════════════════════════════════╗
   ║                                                  ║
   ║   DE: Ein Wissenssystem, das du einmal           ║
   ║       erzeugst und fuer immer wiederverwenden    ║
   ║       kannst.                                    ║
   ║                                                  ║
   ║   EN: A knowledge system you build once          ║
   ║       and reuse forever.                         ║
   ║                                                  ║
   ╚══════════════════════════════════════════════════╝
```

</td>
</tr>
</table>

### Das MetaWiki ist... / MetaWiki is...

| Eigenschaft / Property | DE | EN |
|---|---|---|
| In JSON gespeichert | Maschinenlesbar & versionierbar | Machine-readable & version-controlled |
| In Markdown exportierbar | Menschenlesbar & dokumentierbar | Human-readable & documentable |
| Zweisprachig (DE/EN) | Vollstaendig uebersetzt | Fully translated |
| In jede Sprache uebersetzbar | Global einsetzbar | Globally deployable |
| Modular erweiterbar | Waechst mit deinen Anforderungen | Grows with your requirements |
| KI-freundlich | Optimiert fuer LLM-Integration | Optimized for LLM integration |
| Projektagnostisch | Fuer jeden Anwendungsfall | For any use case |

---

<p align="center">
  <sub>Built with brain and AI &nbsp;|&nbsp; Developed by <a href="https://github.com/lukisch">lukisch</a></sub>
</p>
