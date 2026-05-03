### PATCH /api/v1/tasks/{id}
**Beschreibung**: Aktualisiert den Status der Aufgabe
**Parameter**: `id` (path), `status` (str: "pending", "completed")
**Antwort**:
```json
{"id": 42, "status": "completed"}