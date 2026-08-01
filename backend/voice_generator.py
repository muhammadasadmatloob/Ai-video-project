import edge_tts
import re

VOICE_MAP = {
    "guy": "en-US-GuyNeural",               # Energetic / Shorts Male
    "christopher": "en-US-ChristopherNeural",# Deep / Authoritative Male
    "jenny": "en-US-JennyNeural",           # Clear / Pro Female
    "ryan": "en-GB-RyanNeural"              # British / Documentary
}

def clean_text_for_speech(text):
    # Strip ALL punctuation that causes Edge-TTS to insert robotic word-level pauses
    # This forces TTS to speak the entire text as one continuous flowing sentence
    cleaned = re.sub(r'[,;:\-\"\'\–\—\(\)\[\]\{\}]', ' ', text)
    # Remove periods, exclamation, question marks between words (they cause sentence-break pauses)
    cleaned = re.sub(r'(?<!\d)[.!?]+(?!\d)', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

async def generate_voice(text, filename, voice_key="guy"):
    voice_name = VOICE_MAP.get(voice_key.lower(), "en-US-GuyNeural")
    rate = "+0%"  # Natural speed — pauses removed via punctuation stripping, not speed increase
    
    clean_prompt = clean_text_for_speech(text)
    
    tts = edge_tts.Communicate(
        clean_prompt,
        voice=voice_name,
        rate=rate
    )
    await tts.save(filename)
    return filename


