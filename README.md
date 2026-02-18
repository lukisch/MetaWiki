<p align="center">
  <img src="https://img.shields.io/badge/Stubs-630+-blue?style=for-the-badge" alt="Stubs">
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

<p align="center">
  <a href="#-vision">Vision</a> •
  <a href="#-grundidee">Grundidee</a> •
  <a href="#-json-struktur">JSON-Struktur</a> •
  <a href="#-automatisierung">Automatisierung</a> •
  <a href="#-roadmap">Roadmap</a>
</p>

---

## Vision

> **Ein einziges, vollstaendiges Wissensskelett - wiederverwendbar fuer jedes Projekt.**

Das MetaWiki ist ein universelles, modular aufgebautes Wissensgeruest aus ca. **2000 kompakten Wissens-Stubs**. Jeder Stub beschreibt ein Thema in 1-3 Saetzen, neutral, praezise und projektagnostisch.

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

---

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

---

## JSON-Struktur

### Beispiel eines Stubs

```json
{
  "MetaWiki": {
    "Informatik & KI": {
      "Software Engineering": [
        {
          "title": "Domain-Driven Design",
          "definition_de": "Ein Ansatz zur Modellierung komplexer Software, der die Fachdomaene in den Mittelpunkt stellt.",
          "definition_en": "",
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
|------|--------------|
| `title` | Name des Konzepts |
| `definition_de` | Deutsche Definition (1-3 Saetze) |
| `definition_en` | Englische Uebersetzung (auto-generiert) |
| `relevance` | Warum ist das wichtig? |
| `tags` | Kategorisierung fuer Suche/Filter |

---

## Automatisierung

### Python-Pipeline

Das folgende Script zeigt den Workflow:

```python
import json
import os

def translate(text, target_lang="en"):
    """Platzhalter fuer API (DeepL, Claude, Gemini, Azure)"""
    return f"TRANSLATED({text})"

# JSON laden
with open("metawiki.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Verarbeitung
for category, subcats in data["MetaWiki"].items():
    for subcat, stubs in subcats.items():
        for stub in stubs:
            # Auto-Uebersetzung
            if not stub["definition_en"]:
                stub["definition_en"] = translate(stub["definition_de"])

            # Ordnerstruktur
            folder = f"output/{category}/{subcat}"
            os.makedirs(folder, exist_ok=True)

            # Markdown generieren
            filename = f"{folder}/{stub['title'].replace(' ', '_')}.md"
            with open(filename, "w", encoding="utf-8") as md:
                md.write(f"# {stub['title']}\n\n")
                md.write(f"**Definition (DE):** {stub['definition_de']}\n\n")
                md.write(f"**Definition (EN):** {stub['definition_en']}\n\n")
                md.write(f"**Relevanz:** {stub['relevance']}\n\n")
                md.write(f"**Tags:** {', '.join(stub['tags'])}\n")
```

---

## KI-Uebersetzung (Phase 4)

Alle Stubs koennen automatisch ins Englische uebersetzt werden:

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

## Ziel

<table>
<tr>
<td>

```
   ╔══════════════════════════════════════╗
   ║                                      ║
   ║   Ein Wissenssystem, das du einmal   ║
   ║   erzeugst und fuer immer            ║
   ║   wiederverwenden kannst.            ║
   ║                                      ║
   ╚══════════════════════════════════════╝
```

</td>
</tr>
</table>

### Das MetaWiki ist...

| Eigenschaft | Beschreibung |
|-------------|--------------|
| In JSON gespeichert | Maschinenlesbar & versionierbar |
| In Markdown exportierbar | Menschenlesbar & dokumentierbar |
| In jede Sprache uebersetzbar | Global einsetzbar |
| Modular erweiterbar | Waechst mit deinen Anforderungen |
| KI-freundlich | Optimiert fuer LLM-Integration |
| Projektagnostisch | Fuer jeden Anwendungsfall |

---

<p align="center">
  <sub>Built with brain and AI</sub>
</p>
