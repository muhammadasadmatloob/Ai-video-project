import edge_tts
import re

VOICE_MAP = {
    "guy": "en-US-GuyNeural",               # Energetic / Shorts Male
    "christopher": "en-US-ChristopherNeural",# Deep / Authoritative Male
    "jenny": "en-US-JennyNeural",           # Clear / Pro Female
    "ryan": "en-GB-RyanNeural"              # British / Documentary
}

def clean_text_for_speech(text):
    # Remove internal commas, dashes, colons, semi-colons & quotes that cause Edge-TTS to insert robotic word pauses
    cleaned = re.sub(r'[\,\;\:\-\"\–\—\(\)\[\]]', ' ', text)
    cleaned = re.sub(r'\.{2,}', '.', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

async def generate_voice(text, filename, voice_key="guy"):
    voice_name = VOICE_MAP.get(voice_key.lower(), "en-US-GuyNeural")
    rate = "+12%" # Moderate, fluid human speech — faster than default to avoid word-by-word pauses
    
    clean_prompt = clean_text_for_speech(text)
    
    tts = edge_tts.Communicate(
        clean_prompt,
        voice=voice_name,
        rate=rate
    )
    await tts.save(filename)
    return filename


