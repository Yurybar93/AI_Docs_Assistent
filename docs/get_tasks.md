### GET /api/v1/tasks
**Beschreibung**: Gibt eine Liste der Aufgaben des aktuellen Benutzers zurück
**Parameter**: `status` (optional, str: "pending", "completed")
**Antwort**:
```json
[{"id": 42, "title": "string", "status": "pending"}]