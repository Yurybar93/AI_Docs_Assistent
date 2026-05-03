### POST /api/v1/tasks
**Beschreibung**: Erstellt eine neue Aufgabe für den Benutzer
**Parameter**: `title` (str), `description` (str)
**Antwort**:
```json
{"id": 42, "title": "string", "status": "pending"}