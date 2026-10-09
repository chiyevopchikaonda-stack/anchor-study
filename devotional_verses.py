
import json
from pathlib import Path


BIBLE_FILE = Path(__file__).parent / "data" / "kjv.json"


def load_kjv_verses():
    with BIBLE_FILE.open("r", encoding="utf-8") as file:
        bible = json.load(file)

    verses = []

    for book in bible["books"]:
        book_name = book["englishName"]

        for chapter in book["chapters"]:
            chapter_number = chapter["chapter"]

            for verse in chapter["verses"]:
                verses.append({
                    "book": book_name,
                    "chapter": chapter_number,
                    "verse": verse["number"],
                    "reference": f"{book_name} {chapter_number}:{verse['number']}",
                    "text": verse["text"]
                })

    return verses


def search_kjv_verses(search_term):
    verses = load_kjv_verses()
    search_term = search_term.strip().lower()

    if not search_term:
        return []

    return [
        verse for verse in verses
        if search_term in verse["text"].lower()
        or search_term in verse["reference"].lower()
    ]
