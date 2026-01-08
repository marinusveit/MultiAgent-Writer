"""
Text-Processor für Diff-Generierung und -Anzeige
"""

import difflib
from typing import List, Tuple


class TextProcessor:
    """Verarbeitet Texte und generiert HTML-Diffs"""

    # Farben für Diff-Darstellung
    COLOR_ADDITION = "#c8e6c9"  # Grün
    COLOR_DELETION = "#ffcdd2"  # Rot
    COLOR_MODIFICATION = "#fff9c4"  # Gelb

    @staticmethod
    def generate_diff_html(original: str, modified: str) -> str:
        """
        Generiert HTML mit farblich markierten Unterschieden.

        Args:
            original: Original-Text
            modified: Verbesserter Text

        Returns:
            HTML-String mit farblichen Markierungen
        """
        if not modified or not modified.strip():
            return original

        # Word-level Diff für bessere Granularität
        original_words = original.split()
        modified_words = modified.split()

        matcher = difflib.SequenceMatcher(None, original_words, modified_words)

        html_parts = []
        html_parts.append('<div style="font-family: Arial, sans-serif; line-height: 1.6; padding: 10px;">')

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # Unveränderte Wörter
                text = ' '.join(modified_words[j1:j2])
                html_parts.append(text)

            elif tag == 'delete':
                # Gelöschte Wörter (rot, durchgestrichen)
                deleted = ' '.join(original_words[i1:i2])
                html_parts.append(
                    f'<span style="background-color: {TextProcessor.COLOR_DELETION}; '
                    f'text-decoration: line-through;">{deleted}</span>'
                )

            elif tag == 'insert':
                # Hinzugefügte Wörter (grün)
                inserted = ' '.join(modified_words[j1:j2])
                html_parts.append(
                    f'<span style="background-color: {TextProcessor.COLOR_ADDITION}; '
                    f'font-weight: normal;">{inserted}</span>'
                )

            elif tag == 'replace':
                # Ersetzte Wörter (gelb für alt, grün für neu)
                deleted = ' '.join(original_words[i1:i2])
                inserted = ' '.join(modified_words[j1:j2])

                html_parts.append(
                    f'<span style="background-color: {TextProcessor.COLOR_DELETION}; '
                    f'text-decoration: line-through;">{deleted}</span> '
                    f'<span style="background-color: {TextProcessor.COLOR_ADDITION}; '
                    f'font-weight: normal;">{inserted}</span>'
                )

            # Leerzeichen nach jedem Block (außer am Ende)
            if tag != 'equal' or (j2 < len(modified_words)):
                html_parts.append(' ')

        html_parts.append('</div>')

        return ''.join(html_parts)

    @staticmethod
    def get_statistics(original: str, modified: str) -> dict:
        """
        Berechnet Statistiken über die Änderungen.

        Args:
            original: Original-Text
            modified: Verbesserter Text

        Returns:
            Dictionary mit Statistiken
        """
        original_words = original.split()
        modified_words = modified.split()

        original_sentences = original.count('.') + original.count('!') + original.count('?')
        modified_sentences = modified.count('.') + modified.count('!') + modified.count('?')

        # Berechne Änderungen
        matcher = difflib.SequenceMatcher(None, original_words, modified_words)
        changes = 0
        additions = 0
        deletions = 0

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'delete':
                deletions += (i2 - i1)
                changes += 1
            elif tag == 'insert':
                additions += (j2 - j1)
                changes += 1
            elif tag == 'replace':
                deletions += (i2 - i1)
                additions += (j2 - j1)
                changes += 1

        return {
            'original_words': len(original_words),
            'modified_words': len(modified_words),
            'word_diff': len(modified_words) - len(original_words),
            'original_sentences': original_sentences,
            'modified_sentences': modified_sentences,
            'total_changes': changes,
            'additions': additions,
            'deletions': deletions
        }

    @staticmethod
    def extract_plain_text(html: str) -> str:
        """
        Extrahiert reinen Text aus HTML (entfernt alle Tags).

        Args:
            html: HTML-String

        Returns:
            Reiner Text ohne HTML-Tags
        """
        import re
        # Einfache Regex zum Entfernen von HTML-Tags
        clean = re.sub('<.*?>', '', html)
        # Mehrfache Leerzeichen reduzieren
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()


def test_text_processor():
    """Test der Text-Processor-Funktionalität"""
    processor = TextProcessor()

    original = "KI ist wichtig für Zukunft."
    modified = "Künstliche Intelligenz ist von fundamentaler Bedeutung für die zukünftige Entwicklung."

    print("Original:", original)
    print("\nModifiziert:", modified)

    # HTML-Diff generieren
    html_diff = processor.generate_diff_html(original, modified)
    print("\n=== HTML Diff ===")
    print(html_diff)

    # Statistiken
    stats = processor.get_statistics(original, modified)
    print("\n=== Statistiken ===")
    print(f"Original: {stats['original_words']} Wörter, {stats['original_sentences']} Sätze")
    print(f"Modifiziert: {stats['modified_words']} Wörter, {stats['modified_sentences']} Sätze")
    print(f"Unterschied: {stats['word_diff']:+d} Wörter")
    print(f"Änderungen: {stats['total_changes']} (+ {stats['additions']}, - {stats['deletions']})")


if __name__ == "__main__":
    test_text_processor()
