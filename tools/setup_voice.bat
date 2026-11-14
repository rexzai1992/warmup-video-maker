@echo off
rem Natural voice (Kokoro TTS, Apache-2.0) in its own Python 3.12 env: .tts-venv  (about 1 GB download)
cd /d "%~dp0\.."
python -m pip install -q uv
python -m uv venv --python 3.12 .tts-venv
python -m uv pip install --python .tts-venv\Scripts\python.exe kokoro soundfile "misaki[ja]" pip unidic-lite "en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl"
rem the big "unidic" dictionary needs a separate 700 MB download; the small unidic-lite is enough
python -m uv pip uninstall --python .tts-venv\Scripts\python.exe unidic
echo Voice setup finished.
