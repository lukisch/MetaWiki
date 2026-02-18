import json
import os

try:
    from translate import translate_text as _translate_api
    _API_AVAILABLE = True
except ImportError:
    _API_AVAILABLE = False


def translate(text, target_lang="en"):
    """
    Uebersetzt Text via Claude API (translate.py).
    Erfordert: pip install anthropic && ANTHROPIC_API_KEY gesetzt.
    Gibt leeren String zurueck falls API nicht verfuegbar.
    """
    if not text:
        return ""
    if _API_AVAILABLE:
        return _translate_api(text, target_lang)
    return ""

def main():
    print("Starte MetaWiki Pipeline...")
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_path, "metawiki.json")
    
    if not os.path.exists(json_path):
        print(f"FEHLER: {json_path} nicht gefunden.")
        return

    # JSON laden
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"FEHLER beim Lesen von {json_path}: {e}")
        return

    # Verarbeitung
    root_key = "MetaWiki"
    if root_key not in data:
        print(f"FEHLER: Root-Key '{root_key}' fehlt in JSON.")
        return

    count_processed = 0
    
    for category, subcats in data[root_key].items():
        print(f"Verarbeite Kategorie: {category}")
        for subcat, stubs in subcats.items():
            for stub in stubs:
                title = stub.get("title", "Unbenannt")
                print(f"  - Generiere Stub: {title}")
                
                # Auto-Uebersetzung (Simulation)
                if not stub.get("definition_en"):
                    stub["definition_en"] = translate(stub.get("definition_de", ""))

                # Tags verarbeiten
                tags_list = stub.get("tags", [])
                tags_str = ', '.join(tags_list)

                # Ordnerstruktur
                # HINWEIS: Wir nutzen hier 'output' als Basis, um nichts zu ueberschreiben.
                # Spaeter kann dies auf '.' geaendet werden.
                folder = os.path.join(base_path, "output", category, subcat)
                os.makedirs(folder, exist_ok=True)

                # Markdown generieren
                safe_title = title.replace(' ', '_')
                filename = f"{folder}/{safe_title}.md"
                
                try:
                    with open(filename, "w", encoding="utf-8") as md:
                        md.write(f"# {title}\n\n")
                        md.write(f"**Definition (DE):** {stub.get('definition_de', '')}\n\n")
                        md.write(f"**Definition (EN):** {stub.get('definition_en', '')}\n\n")
                        md.write(f"**Relevanz:** {stub.get('relevance', '')}\n\n")
                        md.write(f"**Tags:** {tags_str}\n")
                    
                    count_processed += 1
                except IOError as e:
                    print(f"    FEHLER beim Schreiben von {filename}: {e}")

    print(f"\nFertig! {count_processed} Stubs generiert.")

if __name__ == "__main__":
    main()
