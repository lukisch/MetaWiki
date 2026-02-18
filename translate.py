#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
translate.py - Optionale KI-Uebersetzung fuer MetaWiki
=======================================================

Uebersetzt deutsche Wissens-Stubs ins Englische via Claude API.

Voraussetzungen:
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."

Nutzung als Modul:
    from translate import translate_text
    english = translate_text("Kurzdefinition auf Deutsch")

Ohne API-Key oder ohne installiertes Paket wird "" zurueckgegeben (kein Fehler).
"""

import os
import time


def translate_text(text: str, target_lang: str = "en") -> str:
    """
    Uebersetzt Text via Claude API.

    Args:
        text:        Zu uebersetzender Text (Deutsch)
        target_lang: Zielsprache als ISO-Code (default: "en")

    Returns:
        Uebersetzter Text oder "" falls API nicht verfuegbar.
    """
    if not text or not text.strip():
        return ""

    try:
        import anthropic
    except ImportError:
        return ""

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return ""

    lang_names = {
        "en": "English",
        "fr": "French",
        "es": "Spanish",
        "it": "Italian",
        "pt": "Portuguese",
    }
    target_name = lang_names.get(target_lang, target_lang)

    prompt = (
        f"Translate the following German academic definition to {target_name}. "
        f"Return only the translation, no explanations or additional text.\n\n"
        f"German text: {text}"
    )

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text.strip()
    except Exception:
        return ""


def is_available() -> bool:
    """Prueft ob die Translation-API verfuegbar ist."""
    try:
        import anthropic  # noqa: F401
    except ImportError:
        return False
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def translate_batch(texts: list, target_lang: str = "en", delay: float = 0.3) -> list:
    """
    Uebersetzt eine Liste von Texten mit optionalem Delay zwischen Anfragen.

    Args:
        texts:       Liste von Texten
        target_lang: Zielsprache als ISO-Code
        delay:       Wartezeit in Sekunden zwischen API-Anfragen (Rate-Limit)

    Returns:
        Liste von uebersetzten Texten (gleiche Laenge wie Input)
    """
    results = []
    for i, text in enumerate(texts):
        result = translate_text(text, target_lang)
        results.append(result)
        if delay > 0 and i < len(texts) - 1:
            time.sleep(delay)
    return results


if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="MetaWiki: Text-Uebersetzung")
    parser.add_argument("text", nargs="?", help="Zu uebersetzender Text")
    parser.add_argument("--lang", default="en", help="Zielsprache (default: en)")
    parser.add_argument("--check", action="store_true", help="API-Verfuegbarkeit pruefen")
    args = parser.parse_args()

    if args.check:
        if is_available():
            print("  Uebersetzung verfuegbar (ANTHROPIC_API_KEY gesetzt)")
        else:
            print("  Uebersetzung nicht verfuegbar.")
            print("  Bitte setze ANTHROPIC_API_KEY und installiere: pip install anthropic")
        sys.exit(0)

    if not args.text:
        parser.print_help()
        sys.exit(1)

    if not is_available():
        print("FEHLER: ANTHROPIC_API_KEY nicht gesetzt oder 'anthropic' nicht installiert.")
        sys.exit(1)

    result = translate_text(args.text, args.lang)
    if result:
        print(result)
    else:
        print("FEHLER: Uebersetzung fehlgeschlagen.")
        sys.exit(1)
