import json
import re
from pathlib import Path

from app.logger import logger

DOCS_DIR = Path('docs')
DOCS_DIR.mkdir(exist_ok=True)

QUERIES_INDEX = DOCS_DIR / '.query_index.json'

ACTION_KEYWORDS = {
    'get': ['abruf', 'erhalt', 'les', 'anzeigen', 'daten', 'informationen'],
    'create': ['erstell', 'anleg', 'hinzufüg', 'neu'],
    'delete': ['lösch', 'entfern', 'remove', 'delete'],
    'update': ['aktualisier', 'änder', 'bearbeit', 'status', 'edit']
}

ENTITY_KEYWORDS = {
    'user': ['benutzer', 'nutzer', 'konto', 'user'],
    'task': ['aufgabe', 'aufgaben', 'todo', 'task'],
    'profile': ['profil', 'persönlich']
}


def _slugify(text: str) -> str:
    """
    Wandelt die Anfrage in einen Dateinamen im Format action_entity um
    """
    text = text.lower()

    action = 'api'
    for act, keywords in ACTION_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            action = act
            break 

    entity = None
    for ent, keywords in ENTITY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            entity = ent
            break

    if entity:
        return f"{action}_{entity}"
    return action


def save_document(content: str, query: str) -> str:
    base_name = _slugify(query)
    base_name = re.sub(r'[^a-z0-9_]', '', base_name)
    if not base_name:
        base_name = 'api_doc'

    file_path = DOCS_DIR / f'{base_name}.md'
    counter = 1
    while file_path.exists():
        file_path = DOCS_DIR / f'{base_name}_{counter}.md'
        counter += 1

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content.strip())

    logger.info(f'Dokument gespeichert: {file_path}')
    return str(file_path)


def _normalize_query(query: str) -> str:
    return ' '.join(query.lower().strip().split())


def find_document_by_query(query: str) -> str | None:
    """Findet den Pfad eines Dokuments, das mit einer identischen Anfrage erzeugt wurde."""
    if not QUERIES_INDEX.exists():
        return None
    try:
        index = json.loads(QUERIES_INDEX.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return None
    return index.get(_normalize_query(query))


def remember_query(query: str, file_path: str) -> None:
    """Speichert die Anfrage->Datei-Zuordnung für exakte Dubletten-Pruefung."""
    DOCS_DIR.mkdir(exist_ok=True)
    index: dict[str, str] = {}
    if QUERIES_INDEX.exists():
        try:
            index = json.loads(QUERIES_INDEX.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            index = {}
    index[_normalize_query(query)] = file_path
    QUERIES_INDEX.write_text(
        json.dumps(index, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )