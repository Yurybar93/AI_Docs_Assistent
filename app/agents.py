from crewai import Agent, Task, Crew, LLM

from app.logger import logger
from app.settings import settings

llm = LLM(
    model=settings.OLLAMA_MODEL,
    base_url=settings.ollama_url,
    temperature=0.0,
    timeout=60.0,
    max_tokens=300,
    api_key=settings.API_KEY
)


def _create_generator_agent():
    return Agent(
        role='API-Dokumentator',
        goal='Dokumentation in einem strikten Format generieren.',
        backstory=(
            'Du bist ein API-Spezialist. Generiere die Dokumentation NUR im folgenden Format.\n'
            'Wichtig: <METHODE> ist ein Platzhalter — ersetze ihn IMMER durch eine konkrete '
            'HTTP-Methode (GET, POST, PUT, DELETE oder PATCH). Schreibe NICHT das Wort '
            '"METHODE" wörtlich.\n'
            'Format:\n'
            '### <METHODE> /pfad\n'
            '**Beschreibung**: ... \n'
            '**Parameter**: ... \n'
            '**Antwort**:\n'
            '```json\n{...}\n```\n'
            'Beispiel:\n'
            '### GET /api/v1/example\n'
            '**Beschreibung**: Beispielbeschreibung\n'
            '**Parameter**: keine\n'
            '**Antwort**:\n'
            '```json\n{"example": "value"}\n```'
        ),
        llm=llm,
        verbose=False
    )

def _create_validator_agent():
    return Agent(
        role='Dokumentations-Validator',
        goal='Überprüft, ob das Dokument dem strikten Format entspricht.',
        backstory=(
            'Du bist ein strenger QA-Ingenieur. Du musst prüfen, ob das Dokument Folgendes enthält:\n'
            '1. Eine Überschrift, die mit "###" beginnt, gefolgt von einer konkreten '
            'HTTP-Methode (GET, POST, PUT, DELETE oder PATCH) und einem URL-Pfad. '
            'Das Wort "METHODE" als Platzhalter ist ungültig,\n'
            '2. Einen Block "**Beschreibung**:",\n'
            '3. Einen Block "**Parameter**" oder "**Pfadparameter**:",\n'
            '4. Einen Block "**Antwort**:" mit einem JSON-Beispiel in dreifachen Backticks.\n'
            'Wenn alles vorhanden ist — antworte "valid". Andernfalls — "invalid".'
        ),
        llm=llm,
        verbose=False
    )


def generate_and_validate_documentation(query: str) -> str | None:
    """
    Generiert Dokumentation und prüft sie mit einem Validator.
    Gibt den Inhalt nur zurück, wenn er valide ist.
    """
    logger.info(f'Start der Generierung für Anfrage: {query}')

    generator = _create_generator_agent()
    gen_task = Task(
        description=f'Erstelle Dokumentation für: {query}',
        expected_output='Dokument im strikten Format. Nichts anderes.',
        agent=generator
    )
    gen_crew = Crew(agents=[generator], tasks=[gen_task])
    raw_content = str(gen_crew.kickoff()).strip()

    if not raw_content:
        logger.error(f'Die Generierung lieferte ein leeres Ergebnis für die Anfrage: {query}')
        return None

    validator = _create_validator_agent()
    val_task = Task(
        description=f'Prüfe das Dokument:\n\n{raw_content}',
        expected_output='Nur "valid" oder "invalid", ohne Erklärungen.',
        agent=validator
    )
    val_crew = Crew(agents=[validator], tasks=[val_task])
    validation_result = str(val_crew.kickoff()).strip().lower()

    if validation_result.strip(' .,!?"\'') == 'valid':
        logger.info(f'Das Dokument hat die Validierung für die Anfrage bestanden: {query}')
        return raw_content
    else:
        logger.warning(f'Das Dokument hat die Validierung nicht bestanden: {validation_result} für die Anfrage: {query}')
        return None