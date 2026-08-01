import edge_tts

VOICE_MAP = {
    "guy": "en-US-GuyNeural",               # Energetic / Shorts Male
    "christopher": "en-US-ChristopherNeural",# Deep / Authoritative Male
    "jenny": "en-US-JennyNeural",           # Clear / Pro Female
    "ryan": "en-GB-RyanNeural"              # British / Documentary
}

async def generate_voice(text, filename, voice_key="guy"):
    voice_name = VOICE_MAP.get(voice_key.lower(), "en-US-GuyNeural")
    rate = "+8%" if voice_key == "guy" else "+4%"
    
    tts = edge_tts.Communicate(
        text,
        voice=voice_name,
        rate=rate
    )
    await tts.save(filename)
    return filename