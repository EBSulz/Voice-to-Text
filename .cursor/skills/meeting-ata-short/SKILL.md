---
name: meeting-ata-short
description: >-
  Writes a short meeting ATA from a voice transcription: one screen, about
  30 to 40 lines. Use when the user asks for a short ATA, a brief meeting
  summary, condensed minutes, or a smaller version of a transcription.
---

# Short meeting ATA

Turn a meeting transcription into a short ATA. Length is the requirement. The note must fit on one screen.

## Size

- About 30 to 40 lines, and no more than one screen.
- Say why the meeting happened, what was agreed, and what happens next. Drop small talk, repeated explanations, and topic-by-topic retelling.
- Do not grow extra sections to hold detail that does not fit. Cut the detail instead.

## Inputs

1. Transcription. Use the path the user gives. Otherwise read `output/TranscriptionText.md`, then `src/output/TranscriptionText.md`.
2. Optional notes the user supplies (agenda, pre-recording notes, participant list). Read those too.

If no transcription file exists and the user did not paste one, stop and ask for it.

## How to read the transcription

The transcription is usually one unlabelled paragraph from speech-to-text.

- Keep only what the source supports. Do not invent decisions, owners, dates, or attendance.
- Correct a name, organisation, or term only when the intended form is clear from context. Leave uncertain wording as heard.
- Write the ATA in English.

## Output

Write the new file to `ata/Meeting_ATA_Short.md`, unless the user names another path.

Do not use Markdown headings. Section labels are plain lines.

```markdown
Meeting ATA (short) — [short title]

Present: [people who took part, comma-separated]

Summary

[Two short paragraphs. What the meeting was for, and where it landed.]

Decisions

1. [What the group agreed, in one or two sentences.]

Actions

- [Action] — [Owner], [timing]
```

Omit `Decisions` when the group agreed nothing. Omit `Actions` when no next step was assigned.

## Writing rules

- A decision is something the group agreed. A preference that was only floated stays out.
- Each action is one line: action, owner, timing. If the source names no owner, write `Unassigned`. If it names no timing, write `not stated`.
- After writing, check that every name, number, and date in the ATA appears in the transcription or the user's notes.
