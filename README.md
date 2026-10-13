# Voice to Text

Transcribe a meeting recording with OpenAI Whisper and save the text as Markdown.

The script is `src/transcribe.py`. It reads a recording from `data/` and writes a Markdown file in `output/`.

## What you need

- Python 3.12
- [ffmpeg](https://ffmpeg.org/) installed and available on your `PATH`. See below.
- OBS properly configured on your machine.

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
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Recordings go in the `data` folder. Run the commands below from the project root.

## OBS

In OBS, open **Settings → Output**. In the Recording section, set **Recording Path** to this project's `data` folder. If **Output Mode** is **Advanced**, that field is on the **Recording** tab.

Set **Filename Formatting** to:

```text
Meeting_%CCYY-%MM-%DD_%hh-%mm
```

OBS fills in the date and time when a recording starts. `%CCYY` is the year, `%MM` the month, `%DD` the day, `%hh` the hour, and `%mm` the minute. A recording started on 13 October 2026 at 13:56 is saved as `data/Meeting_2026-10-13_13-56.mp4`.

`make record` and `make finish` control OBS through its WebSocket server. In OBS, open **Tools → WebSocket Server Settings** and enable the server. If OBS was already open when you turned the server on, quit OBS once so the next `make record` starts it.

## Make

From the project folder:

```bash
make record
```

Opens OBS if it is closed, then starts recording into `data/`.

```bash
make finish
```

Stops the recording and closes OBS.

```bash
make transcribe
```

Runs `src/transcribe.py`. The script asks for a file name. This command answers with the newest recording in `data/`. The text is saved in `output/` using that name without the extension. For `data/Meeting_2026-10-13_13-56.mp4`, the file is `output/Meeting_2026-10-13_13-56.md`.

```bash
make all
```

Runs `finish`, then `transcribe`.

`make` on its own lists these commands.

The first transcription downloads the Whisper `turbo` model. Later runs reuse the downloaded model.

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

The script asks for a file name, including the extension. It transcribes that file from `data/` and saves the text in `output/` using the same name without the extension. The `output` folder must already exist.

The first run downloads the Whisper `turbo` model. Later runs reuse the downloaded model.

## Generate the ATA

When a transcription exists in `output/`, use a Cursor skill to turn it into the meeting notes. The skills live in `.cursor/skills/`. Each one reads that transcription and writes a new file in the `ata` folder. The `ata` folder must already exist.

### Long version

In the Cursor chat, run:

```text
/meeting-ata using output/Meeting_2026-10-13_13-56.md
```

This follows `.cursor/skills/meeting-ata/SKILL.md` and writes `ata/Meeting_ATA.md`.

The note is about two to four pages. It has a short summary, one section per topic, and an actions table, so someone who missed the meeting can follow what was said, what was agreed, and what happens next.

### Short version

In the Cursor chat, run:

```text
/meeting-ata-short using output/Meeting_2026-10-13_13-56.md
```

This follows `.cursor/skills/meeting-ata-short/SKILL.md` and writes `ata/Meeting_ATA_Short.md`.

The note fits on one screen, about 30 to 40 lines. It names who was present, then gives a two-paragraph summary, the decisions, and the actions.

To use another transcription, name that file in the same message instead of `output/Meeting_2026-10-13_13-56.md`.

## How it works

### Recording

`make record` runs `src/obs_control.py`. That script reads OBS’s WebSocket port and password from OBS’s own settings file. If OBS is closed, it opens the app and tells it to start recording. It then connects to the WebSocket server, checks whether a recording is already in progress, and starts one if it is not. OBS writes the file into the Recording Path, which should be this project’s `data` folder, using the filename pattern from OBS.

`make finish` uses the same connection. If OBS is closed, it does nothing else. If a recording is in progress, it stops that recording and waits for OBS to finish the file. It then quits OBS and waits until the app has closed.

### Transcription

`make transcribe` looks in `data/` for the newest `.mp4`, `.mp3`, `.wav`, `.m4a`, or `.mov` file and passes that name to `src/transcribe.py`. `make all` runs `finish` first, then `transcribe`, so the file just recorded is the one that gets transcribed.

The script then does this:

1. It points Python’s HTTPS checks at the certificate bundle from `certifi`, so the model download can verify its connection.
2. It loads the Whisper `turbo` model.
3. It asks for a file name, including the extension. The name may contain only letters, digits, `-`, and `_`, and it must end in `.mp4`, `.mp3`, `.wav`, `.m4a`, or `.mov`.
4. It transcribes `data/<that name>` with `fp16=False`, which is the setting to use on a machine without a supported GPU. The spoken language is the `language` argument, currently `en`.
5. It prints the text, then writes `output/<name>.md` next to the project root rather than next to the script. The Markdown file starts with a `# Transcription` heading, and `<name>` is the recording name without its extension.
