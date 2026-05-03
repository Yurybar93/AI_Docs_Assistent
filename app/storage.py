import re
from pathlib import Path

from app.logger import logger

DOCS_DIR = Path('docs')
DOCS_DIR.mkdir(exist_ok=True)

ACTION_KEYWORDS = {
    'get': ['abruf', 'erhalt', 'les', 'anzeigen', 'daten', 'informationen'],
    'create': ['erstell', 'anleg', 'hinzufüg', 'neu'],
    'delete': ['lösch', 'entfern', 'remove'],
    'update': ['aktualisier', 'änder', 'bearbeit', 'status', 'edit']
}

ENTITY_KEYWORDS = {
    'user': ['benutzer', 'nutzer', 'konto' 'user'],
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