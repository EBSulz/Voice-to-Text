---
name: meeting-ata
description: >-
  Writes a long meeting ATA from a voice transcription: a multi-section
  minutes note of about two to four pages. Use when the user asks for a full
  ATA, detailed meeting notes, minutes, or a broad summary of a transcription.
---

# Full meeting ATA

Turn a meeting transcription into a long ATA. Length is the requirement. Write full minutes, not a brief.

## Size

- About two to four pages. Several topic sections, enough that someone who missed the meeting can follow what was said, what was agreed, and what happens next.
- Give each distinct topic its own section and keep the points, constraints, and open questions the source actually contains.
- Do not compress the meeting into a one-screen note. Do not add topics or sentences the source does not support in order to fill the length.

## Inputs

1. Transcription. Use the path the user gives. Otherwise read `output/TranscriptionText.md`, then `src/output/TranscriptionText.md`.
2. Optional notes the user supplies (agenda, pre-recording notes, participant list). Read those too.

If no transcription file exists and the user did not paste one, stop and ask for it.

## How to read the transcription

The transcription is usually one unlabelled paragraph from speech-to-text.

- Keep only what the source supports. Do not invent decisions, owners, dates, or attendance.
- Speaker turns are not marked. Attribute a remark only when the text makes the speaker reasonably clear, and treat attributions as approximate.
- Correct a name, organisation, or term only when the intended form is clear from context. Record those corrections in the header note. Leave uncertain wording as heard and flag it.
- If the user supplied notes for a part the recording missed, put that material in its own early section and say so in the header note.
- Write the ATA in English.

Unknown date: `(to be filled in)`.

## Output

Write the new file to `ata/Meeting_ATA.md`, unless the user names another path.

Use this structure. Topic titles come from the meeting. Skip a line that the source does not support.

```markdown
# Meeting ATA — [short title]

**Date:** [date or (to be filled in)]
**Participants:** [people who took part]
**Also mentioned:** [people named who were not clearly present, or omit]

**Note:** [recording gaps, name corrections, and that speaker attributions are approximate]

## Summary

[One short paragraph: why the meeting happened and what it settled.]

## 1. [Topic]

[The substance of this part of the meeting: what was explained, asked, and agreed. Use paragraphs and bullets. **Bold** a term the reader must not miss. Mark an explicit agreement with **Decision:**.]

## 2. [Topic]

[Same depth for the next topic. Add sections until the meeting is covered.]

## Actions

| # | Action | Owner | Timing |
|---|---|---|---|
| 1 | [Action] | [Owner or Unassigned] | [Timing or Not stated] |

---

*This ATA is a cleaned summary of the transcription. Check names, dates, and action owners before circulating.*
```

When pre-recording notes were used, say in the footer that the ATA combines those notes with the transcription.

## Writing rules

- One idea per bullet. Keep the wording concrete: who, what, and any constraint or deadline the source gave.
- An action needs a verb. Owner is the person asked to do it. If the source names no owner, write `Unassigned`. If it names no timing, write `Not stated`.
- After writing, check that every name, number, and date in the ATA appears in the transcription or the user's notes.
