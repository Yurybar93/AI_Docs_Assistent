# AI Docs Assistant

--- 

KI-Assistent zur automatischen Generierung und semantischen Suche von API-Dokumentation unter Verwendung von RAG (Retrieval-Augmented Generation) und CrewAI.

## Beschreibung

---

AI Docs Assistant ist ein Webdienst auf Basis von FastAPI, der es ermöglicht:

* API-Dokumentation automatisch mithilfe von KI-Agenten (CrewAI) generieren  
* Vorhandene Dokumentation mithilfe semantischer Suche (RAG) durchsuchen  
* Generierte Dokumentation auf die Einhaltung eines strengen Formats validieren  

### Das Projekt verwendet:

* Qdrant — eine Vektordatenbank zur Speicherung von Dokumentations-Embeddings  
* Ollama — ein lokales LLM zur Textgenerierung und Erstellung von Embeddings  
* CrewAI — ein Framework zur Erstellung von KI-Agenten mit Rollen und Aufgaben  
* LangChain — Integration mit Vektorspeichern und Embeddings  

## Funktionen

---

* 🤖 Automatische Dokumentationsgenerierung über einen zweistufigen Prozess (Generierung + Validierung)  
* 🔍 Semantische Suche in vorhandener Dokumentation  
* ✅ Duplikatprüfung — das System warnt, wenn ein Dokument bereits existiert  
* 📝 Automatische Dateibenennung basierend auf dem Inhalt der Anfrage  
* 🐳 Docker-Unterstützung für eine einfache Bereitstellung  

## Projektstruktur

---

```
ai-docs-assistant/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI приложение и эндпоинты
│   ├── agents.py            # CrewAI агенты для генерации и валидации
│   ├── rag.py               # RAG-функциональность (Qdrant, эмбеддинги)
│   ├── storage.py           # Сохранение документов в файловую систему
│   ├── health.py            # Health-check эндпоинты
│   ├── logger.py            # Настройка логирования
│   ├── schemas.py           # Pydantic схемы для API
│   └── settings.py          # Конфигурация через переменные окружения
├── docs/                    # Хранилище сгенерированной документации
├── logs/                    # Логи приложения
├── tests/                   # Тесты
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```
## Anforderungen

---

* Python 3.11+  
* Docker und Docker Compose (für Containerisierung)  
* Ollama mit installiertem Modell für LLM und Embeddings  

## Installation

### 1. Repository klonen
```
git clone https://github.com/Stas9878/ai-docs-assistant.git
cd ai-docs-assistant
```

### 2. Abhängigkeiten installieren

```
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Umgebungsvariablen konfigurieren

Erstellen Sie eine Datei `.env` im Projektstamm:

```
# Qdrant Einstellungen
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=api_docs

# Ollama Einstellungen
API_KEY=ollama
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
OLLAMA_MODEL=ollama/my-api-docs  # feinabgestimmtes Modell

# Embeddings
EMBEDDING_MODEL_NAME=nomic-embed-text 
VECTOR_SIZE=768  
```
### 4. Start Ollama

Stellen Sie sicher, dass Ollama läuft und die erforderlichen Modelle installiert sind:
 ```

ollama pull my-api-docs

ollama pull nomic-embed-text
 ```

### 5. Start mit Docker Compose (empfohlen)

 ```
docker-compose up --build
Der Service ist erreichbar unter: http://localhost:8000
```
### 6. Lokal starten

 ```
docker run -p 6333:6333 qdrant/qdrant

uvicorn app.main:app --reload
```
# API Endpoints

 ---

```POST /search```

Semantische Suche in vorhandener Dokumentation.

#### Anfrage:
 ```
{
  "query": "Endpunkt zum Abrufen des Benutzerprofils"
}
```

#### Antwort (gefunden):

```
{
  "found": true,
  "content": "### GET /api/v1/profile\n**Beschreibung**: ..."
}
```
### #### Antwort (nicht gefunden):
```
{
  "found": false,
  "message": "Dokumentation nicht gefunden. Verwenden Sie /generate."
}
```
`POST /generate`

Generierung neuer API-Dokumentation.

#### Anfrage:
```
{
  "query": "Endpunkt zum Abrufen einer Aufgabenliste erstellen"
}
```

#### Antwort (Erfolg):

```
{
  "success": true,
  "message": "Dokument erfolgreich erstellt und gespeichert.",
  "content": "### GET /api/v1/tasks\n...",
  "file_path": "docs/get_task.md"
}
```
#### Antwort (Fehler):

```
{
  "success": false,
  "message": "Dokument existiert bereits. Verwenden Sie /search."
}
```

## Dokumentationsformat

---
### Все документы генерируются в строгом формате:

```
### METHODE /pfad
**Beschreibung**: Endpointsbeschreibung
**Parameter**: Anfrageparameter
**Antwort**:
```json
{
  "example": "response"
}
```

## Wie es funktioniert

---

* Duplikatprüfung: Prüfung auf vorhandene Dokumentation  
* Generierung: KI-Agent erstellt Dokumentation  
* Validierung: Zweiter Agent prüft Format  
* Speicherung: Datei wird automatisch gespeichert  
* RAG-Update: Vektordatenbank wird aktualisiert  

## Semantische Suche

---

* Anfrage → Embedding (Ollama)  
* Suche in Qdrant  
* Rückgabe des relevantesten Dokuments  

## Logging

---

Logs im Ordner `logs/`:

* app.log — alle Logs  
* errors.log — nur Fehler  

## Tests

---

```
pytest tests/
```

## Entwicklung

---

### Neue Entitäten hinzufügen


Zur Verbesserung der automatischen Dateibenennung bearbeiten Sie die Wörterbücher in `app/storage.py`:

```
ACTION_KEYWORDS = {
    'get': [...],
    'create': [...],
}

ENTITY_KEYWORDS = {
    'user': [...],
    'task': [...],
}

```
## Konfiguration

---

* Agenten: `app/agents.py`  
* RAG: `app/rag.py`  

## Troubleshooting

---

### Ollama nicht verfügbar

* ollama serve  
* ollama list  
* .env prüfen  

### Qdrant nicht verfügbar

* docker ps  
* .env prüfen  

### Dokumente werden nicht gefunden

* docs/ prüfen  
* Logs prüfen  
* threshold reduzieren  