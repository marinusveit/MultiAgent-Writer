"""
Text-Processor für Diff-Generierung und -Anzeige
"""

import difflib
from typing import List, Tuple
from dataclasses import dataclass
from enum import Enum


class ChangeState(Enum):
    """State of a diff change"""
    PENDING = "pending"      # Not yet decided
    ACCEPTED = "accepted"    # User accepted the change
    REJECTED = "rejected"    # User rejected (keep original)


@dataclass
class DiffChange:
    """Represents a single diff change with state tracking"""
    change_id: str                          # Unique identifier (e.g., "change_0", "change_1")
    operation: str                          # Type of change: 'delete', 'insert', 'replace', 'equal'
    original_text: str                      # Original words (for delete/replace)
    modified_text: str                      # Modified words (for insert/replace)
    original_indices: Tuple[int, int]       # (i1, i2) from SequenceMatcher
    modified_indices: Tuple[int, int]       # (j1, j2) from SequenceMatcher
    state: ChangeState = ChangeState.PENDING  # Current state


class InteractiveDiff:
    """Manages interactive diff state and rendering"""

    def __init__(self, original: str, modified: str):
        self.original = original
        self.modified = modified
        self.original_words = original.split()
        self.modified_words = modified.split()
        self.changes: List[DiffChange] = []
        self._generate_changes()

    def _generate_changes(self):
        """Generate DiffChange objects from SequenceMatcher"""
        matcher = difflib.SequenceMatcher(None, self.original_words, self.modified_words)
        change_id = 0

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            original_text = ' '.join(self.original_words[i1:i2])
            modified_text = ' '.join(self.modified_words[j1:j2])

            # Only assign IDs to non-equal changes
            if tag != 'equal':
                change_id_str = f"change_{change_id}"
                change_id += 1
            else:
                change_id_str = ""  # Equal changes don't need IDs

            change = DiffChange(
                change_id=change_id_str,
                operation=tag,
                original_text=original_text,
                modified_text=modified_text,
                original_indices=(i1, i2),
                modified_indices=(j1, j2),
                state=ChangeState.PENDING if tag != 'equal' else ChangeState.ACCEPTED
            )
            self.changes.append(change)

    def toggle_change(self, change_id: str):
        """Toggle a change between accepted/rejected states"""
        for change in self.changes:
            if change.change_id == change_id:
                if change.state == ChangeState.PENDING:
                    change.state = ChangeState.ACCEPTED
                elif change.state == ChangeState.ACCEPTED:
                    change.state = ChangeState.REJECTED
                elif change.state == ChangeState.REJECTED:
                    change.state = ChangeState.ACCEPTED
                break

    def get_final_text(self) -> str:
        """Reconstruct final text based on current change states"""
        result_words = []

        for change in self.changes:
            if change.operation == 'equal':
                result_words.append(change.modified_text)
            elif change.operation == 'delete':
                if change.state == ChangeState.REJECTED:
                    # User rejected the deletion, keep original
                    result_words.append(change.original_text)
                # If accepted or pending, delete it (contribute nothing)
            elif change.operation == 'insert':
                if change.state != ChangeState.REJECTED:
                    # Pending or accepted: include the insertion
                    result_words.append(change.modified_text)
                # If rejected, don't insert (contribute nothing)
            elif change.operation == 'replace':
                if change.state == ChangeState.REJECTED:
                    # User rejected the replacement, use original
                    result_words.append(change.original_text)
                else:  # ACCEPTED or PENDING defaults to modified
                    result_words.append(change.modified_text)

        return ' '.join(result_words)

    def generate_interactive_html(self) -> str:
        """Generate HTML with clickable changes"""
        html_parts = []
        html_parts.append('<div style="font-family: Arial, sans-serif; line-height: 1.8; padding: 10px;">')

        for change in self.changes:
            if change.operation == 'equal':
                html_parts.append(change.modified_text)
            else:
                html_parts.append(self._render_change(change))

            html_parts.append(' ')

        html_parts.append('</div>')
        return ''.join(html_parts)

    def _render_change(self, change: DiffChange) -> str:
        """Render a single change as clickable HTML"""
        cursor_style = "cursor: pointer;"
        tooltip = "title='Klicken um zu akzeptieren/ablehnen'"

        if change.operation == 'delete':
            if change.state == ChangeState.ACCEPTED:
                # Accepted deletion: show with dark green text + strikethrough
                return (f'<a href="#{change.change_id}" style="{cursor_style} '
                       f'color: #2e7d32; background-color: transparent; '
                       f'text-decoration: line-through;" {tooltip}>{change.original_text}</a>')
            elif change.state == ChangeState.REJECTED:
                # Rejected deletion: show with dark red text (deletion rejected, kept original)
                return (f'<a href="#{change.change_id}" style="{cursor_style} '
                       f'color: #c62828; background-color: transparent;" '
                       f'{tooltip}>{change.original_text}</a>')
            else:  # PENDING
                # Pending deletion: red background + strikethrough
                return (f'<a href="#{change.change_id}" style="{cursor_style} '
                       f'background-color: {TextProcessor.COLOR_DELETION}; '
                       f'text-decoration: line-through; padding: 2px 4px;" '
                       f'{tooltip}>{change.original_text}</a>')

        elif change.operation == 'insert':
            if change.state == ChangeState.ACCEPTED:
                # Accepted insertion: dark green text on white
                return (f'<a href="#{change.change_id}" style="{cursor_style} '
                       f'color: #2e7d32; background-color: transparent;" '
                       f'{tooltip}>{change.modified_text}</a>')
            elif change.state == ChangeState.REJECTED:
                # Rejected insertion: dark red text with strikethrough (not included)
                return (f'<a href="#{change.change_id}" style="{cursor_style} '
                       f'color: #c62828; background-color: transparent; '
                       f'text-decoration: line-through;" {tooltip}>{change.modified_text}</a>')
            else:  # PENDING
                # Pending insertion: green background
                return (f'<a href="#{change.change_id}" style="{cursor_style} '
                       f'background-color: {TextProcessor.COLOR_ADDITION}; '
                       f'padding: 2px 4px;" '
                       f'{tooltip}>{change.modified_text}</a>')

        elif change.operation == 'replace':
            if change.state == ChangeState.ACCEPTED:
                # Accepted replacement: dark green text on white (new version)
                return (f'<a href="#{change.change_id}" style="{cursor_style} '
                       f'color: #2e7d32; background-color: transparent;" '
                       f'{tooltip}>{change.modified_text}</a>')
            elif change.state == ChangeState.REJECTED:
                # Rejected replacement: dark red text on white (original kept)
                return (f'<a href="#{change.change_id}" style="{cursor_style} '
                       f'color: #c62828; background-color: transparent;" '
                       f'{tooltip}>{change.original_text}</a>')
            else:  # PENDING
                # Pending replacement: old (red bg, strikethrough) → new (green bg)
                return (f'<a href="#{change.change_id}" style="{cursor_style} '
                       f'background-color: {TextProcessor.COLOR_DELETION}; '
                       f'text-decoration: line-through; padding: 2px 4px;" '
                       f'{tooltip}>{change.original_text}</a> '
                       f'<a href="#{change.change_id}" style="{cursor_style} '
                       f'background-color: {TextProcessor.COLOR_ADDITION}; '
                       f'padding: 2px 4px;" '
                       f'{tooltip}>{change.modified_text}</a>')

        return change.modified_text


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
