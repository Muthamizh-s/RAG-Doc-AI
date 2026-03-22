# if you dont use pipenv uncomment the following:
# from dotenv import load_dotenv
# load_dotenv()

#VoiceBot UI with Gradio
import os
import tempfile
import uuid
import gradio as gr

from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_gtts, text_to_speech_with_elevenlabs

# load_dotenv()

system_prompt="""You have to act as a professional doctor, i know you are not but this is for learning purpose. 
            What's in this image?. Do you find anything wrong with it medically? 
            If you make a differential, suggest some remedies for them. Donot add any numbers or special characters in 
            your response. Your response should be in one long paragraph. Also always answer as if you are answering to a real person.
            Donot say 'In the image I see' but say 'With what I see, I think you have ....'
            Dont respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot, 
            Keep your answer concise (max 2 sentences). No preamble, start your answer right away please"""

LANGUAGE_OPTIONS = {
    "English": "en",
    "Hindi": "hi",
    "Tamil": "ta"
}


def process_inputs(audio_filepath, image_filepath, language_name):
    groq_api_key = os.environ.get("GROQ_API_KEY")
    language_code = LANGUAGE_OPTIONS.get(language_name, "en")

    try:
        speech_to_text_output = transcribe_with_groq(
            GROQ_API_KEY=groq_api_key,
            audio_filepath=audio_filepath,
            stt_model="whisper-large-v3",
            language=language_code
        )
    except Exception as e:
        return f"Speech-to-text failed: {e}", "Cannot continue without transcription.", None

    # Handle the image input
    try:
        language_instruction = f" Please reply in {language_name}."
        if image_filepath:
            doctor_response = analyze_image_with_query(query=system_prompt + language_instruction + speech_to_text_output, encoded_image=encode_image(image_filepath), model="meta-llama/llama-4-scout-17b-16e-instruct") #model="meta-llama/llama-4-maverick-17b-128e-instruct") 
        else:
            doctor_response = "No image provided for me to analyze"
    except Exception as e:
        doctor_response = f"Image analysis failed: {e}"

    output_mp3 = os.path.join(tempfile.gettempdir(), f"doctor_voice_{uuid.uuid4().hex}.mp3")
    try:
        voice_of_doctor = text_to_speech_with_elevenlabs(input_text=doctor_response, output_filepath=output_mp3)
    except Exception:
        voice_of_doctor = text_to_speech_with_gtts(input_text=doctor_response, output_filepath=output_mp3, language=language_code)

    return speech_to_text_output, doctor_response, voice_of_doctor


def build_demo():
        theme = gr.themes.Base().set(
                body_text_color="#ffffff",
            block_border_color="rgba(0, 0, 0, 0)",
                block_title_text_color="#00d4ff",
                input_background_fill="rgba(255, 255, 255, 0.04)",
            input_border_color="rgba(0, 0, 0, 0)",
            input_border_color_focus="rgba(0, 0, 0, 0)",
                button_primary_background_fill="#00d4ff",
                button_primary_background_fill_hover="#33ddff",
                button_primary_text_color="#020024",
                button_secondary_background_fill="rgba(0, 212, 255, 0.12)",
                button_secondary_background_fill_hover="rgba(0, 212, 255, 0.2)",
                button_secondary_text_color="#ffffff",
                link_text_color="#00d4ff",
        )

        css = """
        * {
            background-color: transparent !important;
        }

        body, .gradio-container {
            background: linear-gradient(135deg, #020024 0%, #0d0842 50%, #1a0d4d 100%) !important;
            color: #ffffff !important;
        }

        h1, .gr-heading {
            background: transparent !important;
        }

        .gr-box, .block, .gr-panel, .gr-input-label, .gr-output-label {
            border-radius: 14px !important;
            background: rgba(2, 0, 36, 0.72) !important;
            box-shadow: none !important;
            border: none !important;
        }

        .prose h1, .prose h2, .prose h3, label {
            color: #00d4ff !important;
        }

        .label-wrap, .label-run, .gr-label-run, span {
            background: transparent !important;
            color: #00d4ff !important;
        }

        [class*="label"], [class*="badge"], [class*="chip"],
        .input-label, .output-label {
            background: rgba(2, 0, 36, 0.9) !important;
            color: #00d4ff !important;
            border: none !important;
        }

        input, textarea, select, .scroll-hide {
            background: rgba(255, 255, 255, 0.04) !important;
            color: #ffffff !important;
            border: none !important;
            box-shadow: none !important;
        }

        input::placeholder, textarea::placeholder {
            color: rgba(200, 230, 255, 0.4) !important;
        }

        .gr-info, .info-box, p, div {
            background: transparent !important;
            color: #ffffff !important;
        }

        button:not(.gr-button) {
            background: rgba(0, 212, 255, 0.15) !important;
            color: #00d4ff !important;
        }

        [style*="white"], [style*="#fff"], [style*="#ffffff"] {
            background: rgba(2, 0, 36, 0.9) !important;
            color: #00d4ff !important;
        }
        """

        return gr.Interface(
        fn=process_inputs,
        inputs=[
            gr.Audio(sources=["microphone"], type="filepath"),
            gr.Image(type="filepath"),
            gr.Dropdown(choices=list(LANGUAGE_OPTIONS.keys()), value="English", label="Speech Language")
        ],
        outputs=[
            gr.Textbox(label="Speech to Text"),
            gr.Textbox(label="Doctor's Response"),
            gr.Audio(label="Doctor's Voice", type="filepath")
        ],
        title="AI Doctor with Vision and Voice",
        description='''
<div style="text-align:right; margin-bottom:8px;">
    <a href="http://127.0.0.1:5000/logout" style="display:inline-block; padding:8px 14px; border-radius:8px; background:#ef4444; color:white; text-decoration:none; font-weight:600;">Logout</a>
</div>
''',
        theme=theme,
        css=css,
    )


def launch_gradio(server_port=7860):
    iface = build_demo().queue(default_concurrency_limit=2)
    iface.launch(debug=True, server_name="127.0.0.1", server_port=server_port)


if __name__ == "__main__":
    launch_gradio(server_port=7860)