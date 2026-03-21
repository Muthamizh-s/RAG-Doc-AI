# AI Doctor

AI Doctor is a multimodal assistant that combines:

1. Speech-to-text (Groq Whisper)
2. Medical-style image analysis (Llama vision model)
3. Text-to-speech (ElevenLabs with gTTS fallback)
4. Flask authentication + Gradio app UI

## Features

1. Login/register flow with MongoDB-backed users
2. Voice input from microphone
3. Optional medical image upload
4. Doctor response in text and generated voice
5. Multilingual speech mode in UI:
   - English
   - Hindi
   - Tamil

## Project Structure

1. `main.py` starts both Flask (`:5000`) and Gradio (`:7860`)
2. `flask_app.py` handles auth and routing
3. `gradio_app.py` handles voice + image doctor interaction
4. `voice_of_the_patient.py` handles speech-to-text
5. `voice_of_the_doctor.py` handles text-to-speech
6. `brain_of_the_doctor.py` handles image-aware LLM response

## Prerequisites

1. Python 3.10+
2. FFmpeg installed and available on PATH
3. PortAudio (required by `pyaudio` / microphone stack)
4. MongoDB running locally or remotely

## Install System Dependencies

### Windows

1. Install FFmpeg and add `ffmpeg\bin` to PATH
2. Install PortAudio (or install audio tooling that satisfies `pyaudio` requirements)

### macOS

```bash
brew install ffmpeg portaudio
```

### Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install ffmpeg portaudio19-dev
```

## Python Environment Setup

Choose one method.

### Option A: pip + venv

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Option B: Pipenv

```bash
pip install pipenv
pipenv install
pipenv shell
```

## Environment Variables

Set these before running:

```bash
GROQ_API_KEY=your_groq_key
ELEVEN_API_KEY=your_elevenlabs_key_optional
MONGO_URI=mongodb://127.0.0.1:27017/
MONGO_DB_NAME=ai_doctor
FLASK_SECRET_KEY=replace_with_secure_secret
GRADIO_URL=http://127.0.0.1:7860
```

Notes:

1. `ELEVEN_API_KEY` is optional. If missing, app falls back to gTTS.
2. `GRADIO_URL` usually does not need to change for local run.

## Run the App

Recommended (starts both Flask and Gradio):

```bash
python main.py
```

Then open:

1. `http://127.0.0.1:5000` for login/home
2. Gradio runs at `http://127.0.0.1:7860`

## Optional: Run Services Separately

```bash
python flask_app.py
python gradio_app.py
```

## How to Use

1. Register or login from Flask app
2. Open AI app page
3. Select speech language (English/Hindi/Tamil)
4. Record microphone input
5. Upload an image (optional)
6. Submit and review:
   - Transcribed speech
   - Doctor text response
   - Doctor audio response

## Troubleshooting

1. Microphone not working:
   - Confirm browser mic permissions
   - Confirm FFmpeg and PortAudio are installed
2. Mongo errors:
   - Check `MONGO_URI` and MongoDB service status
3. No ElevenLabs audio:
   - Set valid `ELEVEN_API_KEY` or rely on gTTS fallback
4. API errors:
   - Verify `GROQ_API_KEY` is present and valid

