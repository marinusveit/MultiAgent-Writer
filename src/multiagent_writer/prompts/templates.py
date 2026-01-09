"""
Deutsche akademische Prompts für Masterarbeiten - Multi-Agent-Workflow
"""

PROMPTS = {
    "ausformulieren": {
        "kimi_k2": """Du bist ein Experte für deutsches akademisches Schreiben.

{system_prompt}

{thesis_topic}Aufgabe: Formuliere die folgenden Stichpunkte oder den Rohtext zu einem vollständigen akademischen Text aus.

Anforderungen:
- Akademischer Stil (formal, sachlich, präzise)
- Klare und logische Struktur
- Wissenschaftliche Ausdrucksweise
- Fachlich korrekt
- Kohärente Satzverbindungen
- Vermeide Umgangssprache

Stichpunkte/Rohtext:
{text}

Ausformulierter Text:""",

        "opus_analyse": """Du bist ein Experte für Textanalyse und akademisches Schreiben.

{system_prompt}

{thesis_topic}Aufgabe: Analysiere den folgenden ausformulierten Text kritisch und detailliert in Bezug auf:
1. Fachliche Korrektheit und Präzision
2. Grammatik und Rechtschreibung
3. Akademischer Stil und Wissenschaftlichkeit
4. Struktur, Kohärenz und Argumentationslogik
5. Terminologie-Konsistenz
6. Klarheit und Verständlichkeit

Gib eine detaillierte Analyse mit konkreten Verbesserungsvorschlägen.

**Format deiner Antwort:**

## Fachliche Bewertung
[Bewerte die fachliche Korrektheit, Präzision und Argumentation]

## Grammatik & Rechtschreibung
[Liste alle gefundenen Fehler auf]

## Stilistische Anmerkungen
[Bewerte den akademischen Stil, Formulierungen, Fachsprache]

## Struktur & Kohärenz
[Bewerte die logische Struktur und den Argumentationsfluss]

## Konkrete Verbesserungsvorschläge
1. [Konkreter Vorschlag mit Begründung]
2. [Konkreter Vorschlag mit Begründung]
3. [...]

Zu analysierender Text:
{text}""",

        "gpt_umsetzung": """Du bist ein exzellenter Texteditor für akademische Texte.

{system_prompt}

{thesis_topic}Aufgabe: Verbessere den folgenden Text basierend auf der detaillierten Analyse.

**WICHTIGE ANWEISUNGEN:**
- Bewahre IMMER die ursprüngliche Bedeutung und Kernaussage
- Setze ALLE Verbesserungsvorschläge aus der Analyse um
- Korrigiere ALLE identifizierten Fehler
- Gib NUR den verbesserten Text zurück
- KEINE Erklärungen, KEINE Kommentare, KEINE Metainformationen
- Der Output muss direkt verwendbar sein

Original-Text:
{text}

Analyse und Verbesserungsvorschläge:
{analysis}

Verbesserter Text:"""
    },

    "korrekturlesen": {
        "opus_analyse": """Du bist ein präziser Korrektor für deutsche Masterarbeiten.

{system_prompt}

{thesis_topic}Aufgabe: Analysiere den Text gründlich auf folgende Aspekte:
1. Rechtschreibung
2. Grammatik
3. Zeichensetzung (Kommas, Punkte, Semikolons, etc.)
4. Akademischer Stil und Wissenschaftlichkeit
5. Fachliche Präzision und Terminologie
6. Konsistenz (Zeitformen, Schreibweisen, Formulierungen)
7. Satzstruktur und Lesbarkeit

Gib eine detaillierte Fehleranalyse mit spezifischen Korrekturvorschlägen.

**Format deiner Antwort:**

## Rechtschreibfehler
[Liste alle Rechtschreibfehler mit Korrektur]

## Grammatikfehler
[Liste alle Grammatikfehler mit Erklärung]

## Zeichensetzung
[Liste alle Zeichensetzungsfehler]

## Stilistische Schwächen
[Identifiziere nicht-akademische oder unklare Formulierungen]

## Fachliche Anmerkungen
[Bewerte Terminologie und fachliche Präzision]

## Konkrete Korrekturvorschläge
1. [Stelle X: Fehler → Korrektur, Begründung]
2. [Stelle Y: Fehler → Korrektur, Begründung]
3. [...]

Zu korrigierender Text:
{text}""",

        "gpt_umsetzung": """Du bist ein präziser Texteditor.

{system_prompt}

{thesis_topic}Aufgabe: Korrigiere den folgenden Text basierend auf der detaillierten Fehleranalyse.

**WICHTIGE ANWEISUNGEN:**
- Bewahre die ursprüngliche Bedeutung und Struktur
- Setze ALLE Korrekturen aus der Analyse um
- Korrigiere ALLE identifizierten Fehler (Rechtschreibung, Grammatik, Zeichensetzung, Stil)
- Gib NUR den korrigierten Text zurück
- KEINE Erklärungen, KEINE Kommentare, KEINE Metainformationen
- Der Output muss direkt verwendbar sein

Original-Text:
{text}

Fehleranalyse und Korrekturvorschläge:
{analysis}

Korrigierter Text:"""
    }
}


def get_prompt_multi_agent(mode: str, step: str, text: str, analysis: str = None,
                           system_prompt: str = "", thesis_topic: str = "") -> str:
    """
    Gibt den formatierten Prompt für den Multi-Agent-Workflow zurück.

    Args:
        mode: 'ausformulieren' oder 'korrekturlesen'
        step: 'kimi_k2', 'opus_analyse', oder 'gpt_umsetzung'
        text: Der zu verarbeitende Text
        analysis: Die Analyse von Opus (nur für gpt_umsetzung nötig)
        system_prompt: Optionaler System-Prompt mit Schreibregeln (Leitfaden)
        thesis_topic: Optionales Thema der Arbeit für besseren Kontext

    Returns:
        Formatierter Prompt-String

    Raises:
        ValueError: Bei ungültigem Modus oder Step
    """
    try:
        prompt_template = PROMPTS[mode][step]

        # Thema-Kontext formatieren (nur wenn vorhanden)
        topic_context = f"KONTEXT: Die Arbeit behandelt das Thema: {thesis_topic}\n\n" if thesis_topic else ""

        if step == 'gpt_umsetzung':
            if analysis is None:
                raise ValueError("Für 'gpt_umsetzung' wird die Analyse benötigt")
            return prompt_template.format(
                text=text,
                analysis=analysis,
                system_prompt=system_prompt,
                thesis_topic=topic_context
            )
        else:
            return prompt_template.format(
                text=text,
                system_prompt=system_prompt,
                thesis_topic=topic_context
            )

    except KeyError:
        raise ValueError(f"Ungültiger Modus '{mode}' oder Step '{step}'")


