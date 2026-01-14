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

    def _generate_css(self) -> str:
        """Generate CSS stylesheet for interactive diff"""
        from ..config.constants import DiffColors, DiffStyle

        return f"""
        <style>
            /* Base change styling */
            .change {{
                cursor: pointer;
                padding: {DiffStyle.PADDING};
                margin: {DiffStyle.MARGIN};
                border-radius: {DiffStyle.BORDER_RADIUS};
                border: {DiffStyle.BORDER_WIDTH} solid transparent;
                text-decoration: none;
                display: inline-block;
                transition: {DiffStyle.TRANSITION};
            }}

            /* Pending state base */
            .change-pending {{
                border-color: {DiffColors.BORDER_PENDING};
            }}

            /* Delete operation (pending) */
            .change-delete.change-pending {{
                background-color: {DiffColors.DELETION};
                text-decoration: line-through;
            }}

            /* Insert operation (pending) */
            .change-insert.change-pending {{
                background-color: {DiffColors.ADDITION};
            }}

            /* Accepted state */
            .change-accepted {{
                color: {DiffColors.ACCEPTED_COLOR};
                background-color: transparent;
                border-color: {DiffColors.BORDER_ACCEPTED};
            }}

            /* Rejected state */
            .change-rejected {{
                color: {DiffColors.REJECTED_COLOR};
                background-color: transparent;
                border-color: {DiffColors.BORDER_REJECTED};
            }}

            /* Hover effects - pending */
            .change-pending:hover {{
                border-width: {DiffStyle.BORDER_WIDTH_HOVER};
                border-color: {DiffColors.BORDER_HOVER_PENDING};
                box-shadow: {DiffStyle.BOX_SHADOW_HOVER};
            }}

            .change-delete.change-pending:hover {{
                background-color: {DiffColors.DELETION_HOVER};
            }}

            .change-insert.change-pending:hover {{
                background-color: {DiffColors.ADDITION_HOVER};
            }}

            /* Hover effects - accepted */
            .change-accepted:hover {{
                border-width: {DiffStyle.BORDER_WIDTH_HOVER};
                border-color: {DiffColors.BORDER_HOVER_ACCEPTED};
                color: {DiffColors.ACCEPTED_HOVER};
                box-shadow: {DiffStyle.BOX_SHADOW_HOVER};
            }}

            /* Hover effects - rejected */
            .change-rejected:hover {{
                border-width: {DiffStyle.BORDER_WIDTH_HOVER};
                border-color: {DiffColors.BORDER_HOVER_REJECTED};
                color: {DiffColors.REJECTED_HOVER};
                box-shadow: {DiffStyle.BOX_SHADOW_HOVER};
            }}

            /* Strikethrough for deletions/rejections */
            .change-delete.change-pending,
            .change-delete.change-accepted {{
                text-decoration: line-through;
            }}

            .change-insert.change-rejected {{
                text-decoration: line-through;
            }}
        </style>
        """

    def _get_state_icon(self, change: DiffChange) -> str:
        """Get visual icon for change state"""
        if change.state == ChangeState.PENDING:
            return "◯"
        elif change.state == ChangeState.ACCEPTED:
            return "✓"
        elif change.state == ChangeState.REJECTED:
            return "✗"
        return ""

    def _get_tooltip(self, change: DiffChange) -> str:
        """Get state-specific tooltip text"""
        if change.state == ChangeState.PENDING:
            return "🖱️ Klicken um zu akzeptieren/ablehnen"
        elif change.state == ChangeState.ACCEPTED:
            return "✓ Akzeptiert - Klicken um Status zu ändern"
        elif change.state == ChangeState.REJECTED:
            return "✗ Abgelehnt - Klicken um Status zu ändern"
        return "Klicken um zu ändern"

    def generate_interactive_html(self) -> str:
        """Generate HTML with clickable changes"""
        html_parts = []

        # Add CSS stylesheet
        html_parts.append(self._generate_css())

        # Add content wrapper
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
        """Render a single change as clickable HTML with CSS classes"""
        state_name = change.state.name.lower()
        tooltip = self._get_tooltip(change)
        icon = self._get_state_icon(change)

        # Build CSS class list
        css_classes = f"change change-{change.operation} change-{state_name}"

        if change.operation == 'delete':
            # Deletions show original text
            text = change.original_text
        elif change.operation == 'insert':
            # Insertions show modified text
            text = change.modified_text
        elif change.operation == 'replace':
            # Replacements: show original or modified based on state
            if change.state == ChangeState.REJECTED:
                # Rejected: keep original
                text = change.original_text
            else:
                # Accepted or pending: show modified
                text = change.modified_text
        else:
            text = change.modified_text

        # Special handling for replace operation in PENDING state
        # Show both old (strikethrough) and new text
        if change.operation == 'replace' and change.state == ChangeState.PENDING:
            old_part = (f'<a href="#{change.change_id}" '
                       f'class="change change-delete change-pending" '
                       f'data-state="{state_name}" '
                       f'data-operation="{change.operation}" '
                       f'title="{tooltip}">'
                       f'{icon} {change.original_text}</a>')
            new_part = (f'<a href="#{change.change_id}" '
                       f'class="change change-insert change-pending" '
                       f'data-state="{state_name}" '
                       f'data-operation="{change.operation}" '
                       f'title="{tooltip}">'
                       f'{icon} {change.modified_text}</a>')
            return f'{old_part} {new_part}'

        # Standard rendering for all other cases
        return (f'<a href="#{change.change_id}" '
               f'class="{css_classes}" '
               f'data-state="{state_name}" '
               f'data-operation="{change.operation}" '
               f'title="{tooltip}">'
               f'{icon} {text}</a>')


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
