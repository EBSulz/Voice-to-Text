# Voice to Text

Transcribe a meeting recording with OpenAI Whisper and save the text as Markdown.

The script is `src/transcribe.py`. It reads `data/MeetingAudio.mp4` and writes `output/TranscriptionText.md`.

## What you need

- Python 3.13
- [ffmpeg](https://ffmpeg.org/) installed and available on your `PATH`. See below.

## ffmpeg

ffmpeg is a free command-line program that reads and converts audio and video. Whisper does not open an `.mp4` file by itself. It calls ffmpeg, which pulls the audio out of the recording and hands that audio to the model. `pip` does not install ffmpeg, so it has to be installed on the Mac before you run the script.

Install it with Homebrew:

```bash
brew install ffmpeg
```

If `brew` is not found, install Homebrew from [brew.sh](https://brew.sh/), then run the command above.

Check that the install worked:

```bash
ffmpeg -version
```

You should see a version line such as `ffmpeg version 7.x`. If the terminal says `command not found`, close the terminal, open a new one, and try again. The program must be on your `PATH`, which is the list of folders the terminal searches when you type a command.

## Setup

From the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Put the recording at `data/MeetingAudio.mp4`. The audio path in the script is relative to the folder you run the command from, so run it from the project root.

## Language

The transcription language can be changed. It is the `language` argument of `model.transcribe(...)` in `src/transcribe.py`. One value applies to the whole recording.

- English: `en`
- Dutch: `nl`
- Portuguese: `pt`

The script is currently set to English (`en`). Change that value, then run the script again.

## Run

```bash
source .venv/bin/activate
python src/transcribe.py
```

The script prints the transcription and saves it to `output/TranscriptionText.md`. The `output` folder must already exist.

The first run downloads the Whisper `turbo` model. Later runs reuse the downloaded model.

## Generate the ATA

When `output/TranscriptionText.md` exists, use a Cursor skill to turn it into the meeting notes. The skills live in `.cursor/skills/`. Each one reads that transcription and writes a new file in the `ata` folder. The `ata` folder must already exist.

### Long version

In the Cursor chat, run:

```text
/meeting-ata using output/TranscriptionText.md
```

This follows `.cursor/skills/meeting-ata/SKILL.md` and writes `ata/Meeting_ATA.md`.

The note is about two to four pages. It has a short summary, one section per topic, and an actions table, so someone who missed the meeting can follow what was said, what was agreed, and what happens next.

### Short version

In the Cursor chat, run:

```text
/meeting-ata-short using output/TranscriptionText.md
```

This follows `.cursor/skills/meeting-ata-short/SKILL.md` and writes `ata/Meeting_ATA_Short.md`.

The note fits on one screen, about 30 to 40 lines. It names who was present, then gives a two-paragraph summary, the decisions, and the actions.

To use another transcription, name that file in the same message instead of `output/TranscriptionText.md`.

## How it works

1. It points Python’s HTTPS checks at the certificate bundle from `certifi`, so the model download can verify its connection.
2. It loads the Whisper `turbo` model.
3. It transcribes `data/MeetingAudio.mp4` with `fp16=False`, which is the setting to use on a machine without a supported GPU.
4. It writes a Markdown file at `output/TranscriptionText.md`, next to the project root rather than next to the script.

To transcribe a different file, change the path in `model.transcribe(...)` in `src/transcribe.py`.
