import edge_tts
import re

VOICE_MAP = {
    "guy": "en-US-GuyNeural",               # Energetic / Shorts Male
    "christopher": "en-US-ChristopherNeural",# Deep / Authoritative Male
    "jenny": "en-US-JennyNeural",           # Clear / Pro Female
    "ryan": "en-GB-RyanNeural"              # British / Documentary
}

def clean_text_for_speech(text):
    # Remove excessive punctuation that causes long awkward pauses in TTS
    cleaned = re.sub(r'\.{2,}', '.', text)  # Replace ... with .
    cleaned = re.sub(r'[\,\;\:\-]{2,}', ',', cleaned) # Replace multiple commas with single
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

async def generate_voice(text, filename, voice_key="guy"):
    voice_name = VOICE_MAP.get(voice_key.lower(), "en-US-GuyNeural")
    rate = "+4%" # Moderate, clear speech pacing
    
    clean_prompt = clean_text_for_speech(text)
    
    tts = edge_tts.Communicate(
        clean_prompt,
        voice=voice_name,
        rate=rate
    )
    await tts.save(filename)
    return filename

