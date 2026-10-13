import os
import ssl
import certifi
import whisper

cert_path = certifi.where()

os.environ["SSL_CERT_FILE"] = cert_path
os.environ["REQUESTS_CA_BUNDLE"] = cert_path

ssl._create_default_https_context = lambda *args, **kwargs: ssl.create_default_context(
    cafile=cert_path
)

model = whisper.load_model("turbo")

# Set the spoken language here. English: "en". Dutch: "nl". Portuguese: "pt".
result = model.transcribe("data/MeetingAudio.mp4", fp16=False, language="en")

print(result["text"])

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_path = os.path.join(project_root, "output", "TranscriptionText.md")
with open(output_path, "w", encoding="utf-8") as f:
    f.write("# Transcription\n\n")
    f.write(result["text"].strip())
    if result["text"].strip():
        f.write("\n")

print(f"Transcription saved to: {output_path}")