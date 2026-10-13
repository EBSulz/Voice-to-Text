import os
import re
import ssl
import certifi
import whisper

cert_path = certifi.where()

os.environ["SSL_CERT_FILE"] = cert_path
os.environ["REQUESTS_CA_BUNDLE"] = cert_path

ssl._create_default_https_context = lambda *args, **kwargs: ssl.create_default_context(
    cafile=cert_path
)

ALLOWERD_EXTENSIONS = ["mp4", "mp3", "wav", "m4a", "mov"]
FILE_NAME_PATTERN = re.compile(
    rf"[A-Za-z0-9_-]+\.({'|'.join(map(re.escape, ALLOWERD_EXTENSIONS))})",
    re.IGNORECASE,
)

model = whisper.load_model("turbo")

# Set the spoken language here. English: "en". Dutch: "nl". Portuguese: "pt".
save_string = input("Enter the file name, including extension separated by a '.', to save the transcription: ")
if not FILE_NAME_PATTERN.fullmatch(save_string):
    raise SystemExit(
        f"Invalid file name: {save_string}. Use only letters, digits, '-' or '_', "
        f"followed by one of: {', '.join('.' + ext for ext in ALLOWERD_EXTENSIONS)}"
        )
result = model.transcribe("data/MeetingAudio.mp4", fp16=False, language="en")

print(result["text"])

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_path = os.path.join(project_root, "output", f"{save_string.split('.')[0]}.md")
with open(output_path, "w", encoding="utf-8") as f:
    f.write("# Transcription\n\n")
    f.write(result["text"].strip())
    if result["text"].strip():
        f.write("\n")

print(f"Transcription saved to: {output_path}")