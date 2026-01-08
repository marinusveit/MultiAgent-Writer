# Selective Diff Feature - Usage Guide

## Overview

The Thesis Improver now supports **selective acceptance of individual changes**. Instead of accepting or rejecting all changes at once, you can click on each change individually to accept or reject it.

## How to Use

### 1. Process Your Text

1. Enter your text in the left panel
2. Select your mode (Ausformulieren or Korrekturlesen)
3. Click "Ausformulieren" or "Korrektur lesen"
4. Wait for the multi-agent workflow to complete

### 2. Review Changes in the Diff View

After processing, you'll see the improved text in the right panel with all changes highlighted:

- **Red background with strikethrough** = Deleted or replaced text (pending)
- **Green background** = Added or new replacement text (pending)
- **Green border** = Change is accepted ✓
- **Red border** = Change is rejected ✗

### 3. Click Individual Changes

**To accept/reject a change:**
- Simply **click on any highlighted change**
- The change will cycle through states: PENDING → ACCEPTED → REJECTED → ACCEPTED...

**Visual feedback:**
- **PENDING** (default): Shows the modified version with colored background
- **ACCEPTED**: Shows the change with a green border (explicitly accepted)
- **REJECTED**: Shows the original with a red border (explicitly rejected, keeps original)

**Hover to see tooltip:**
- All changes have a tooltip: "Klicken um zu akzeptieren/ablehnen"

### 4. Batch Operations

**Accept All Changes:**
- Click the "✓ Alle akzeptieren" button
- All changes will be marked as accepted

**Reject All Changes:**
- Click the "✗ Alle ablehnen" button
- All changes will be marked as rejected (keeps original text)

### 5. Monitor Progress

The status bar at the bottom shows live statistics:
```
Änderungen: 15 gesamt | 8 akzeptiert | 3 abgelehnt | 4 ausstehend
```

### 6. Finalize Your Choices

Once you've reviewed and accepted/rejected individual changes:

- **"← Übernehmen"**: Transfers the final text (with your choices) to the input field
- **"Kopieren"**: Copies the final text to clipboard
- **"Speichern"**: Saves the final text to a .txt file
- **"Text anzeigen"**: Toggles between diff view and plain text view

## Examples

### Example 1: Simple Replacement

**Original:** "KI ist wichtig"
**Modified:** "Künstliche Intelligenz ist wichtig"

**In diff view:**
- Click on "KI → Künstliche Intelligenz" to toggle acceptance
- PENDING: Shows both (red "KI" crossed out + green "Künstliche Intelligenz")
- ACCEPTED: Shows "Künstliche Intelligenz" with green border
- REJECTED: Shows "KI" with red border

**Final text:**
- If ACCEPTED: "Künstliche Intelligenz ist wichtig"
- If REJECTED: "KI ist wichtig"

### Example 2: Multiple Changes

**Original:** "AI ist sehr wichtig"
**Modified:** "Künstliche Intelligenz ist fundamental wichtig"

**Three changes detected:**
1. Replace "AI" → "Künstliche Intelligenz"
2. Delete "sehr"
3. Insert "fundamental"

**You can:**
- Accept change 1 (use "Künstliche Intelligenz")
- Reject change 2 (keep "sehr")
- Accept change 3 (add "fundamental")

**Result:** "Künstliche Intelligenz ist sehr fundamental wichtig"

## Keyboard Shortcuts

- **Ctrl+Enter**: Process text
- **Ctrl+K**: Copy to clipboard
- **Ctrl+S**: Save to file

## Technical Details

### Change States

Each change has one of three states:

1. **PENDING** (default after processing)
   - Shows the modified version by default
   - Appears with colored background only

2. **ACCEPTED**
   - Explicitly accepted by user
   - Shows with green border confirmation

3. **REJECTED**
   - Explicitly rejected by user
   - Keeps the original wording
   - Shows with red border

### Change Types

The system detects three types of changes:

1. **INSERT**: New words added
   - PENDING/ACCEPTED: Included in final text
   - REJECTED: Not included

2. **DELETE**: Words removed
   - PENDING/ACCEPTED: Not in final text (deleted)
   - REJECTED: Kept in final text

3. **REPLACE**: Words changed
   - PENDING/ACCEPTED: New version used
   - REJECTED: Original version kept

## Tips

1. **Start with "Alle akzeptieren"** if you trust most changes, then reject specific ones
2. **Start with "Alle ablehnen"** if you want to be selective, then accept specific ones
3. **Use "Text anzeigen"** to preview the final result without color coding
4. **The statistics** help track your progress through all changes
5. **Changes persist** until you process new text or reset

## Troubleshooting

**Changes don't highlight when hovering:**
- This is normal - changes are clickable but don't show hover effects

**Clicked a change by mistake:**
- Just click it again to cycle to the next state
- States cycle: PENDING → ACCEPTED → REJECTED → ACCEPTED...

**Want to reset all decisions:**
- Click "Zurücksetzen" to clear everything and start over

**Statistics not updating:**
- This should not happen - if it does, try clicking "Zurücksetzen" and processing again

## Implementation Notes

- Built with PyQt6 QTextBrowser for clickable HTML anchors
- Uses Python's difflib.SequenceMatcher for word-level diffs
- State management with Python dataclasses and Enums
- All changes are tracked individually with unique IDs
- Final text is dynamically reconstructed based on user selections
