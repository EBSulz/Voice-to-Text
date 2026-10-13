.PHONY: help record finish transcribe all

.DEFAULT_GOAL := help

PYTHON := .venv/bin/python

help:
	@printf '%s\n' \
		'record      Open OBS if it is closed, then start recording' \
		'finish      Stop the recording and close OBS' \
		'transcribe  Run src/transcribe.py and answer its file prompt with the newest file in data/' \
		'all         Run finish, then transcribe'

record:
	@python3 src/obs_control.py record

finish:
	@python3 src/obs_control.py finish

transcribe:
	@file=$$(python3 -c "from pathlib import Path; exts={'.mp4','.mp3','.wav','.m4a','.mov'}; files=[p for p in Path('data').iterdir() if p.is_file() and p.suffix.lower() in exts]; print(max(files, key=lambda p: p.stat().st_mtime).name if files else '', end='')"); \
	if [ -z "$$file" ]; then echo "No recording found in data/"; exit 1; fi; \
	printf '%s\n' "Using $$file"; \
	printf '%s\n' "$$file" | $(PYTHON) src/transcribe.py

all:
	$(MAKE) finish
	$(MAKE) transcribe
