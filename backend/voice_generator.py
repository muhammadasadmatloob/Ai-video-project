import edge_tts

async def generate_voice(text, filename):
    communicate = edge_tts.Communicate(
        text,
        voice="en-US-ChristopherNeural",  # 🔥 Very dramatic, expressive human-like voice
        rate="+5%",                       # 🔥 Slight speed increase to keep it engaging
        pitch="+0Hz"
    )
    await communicate.save(filename)
    return filename