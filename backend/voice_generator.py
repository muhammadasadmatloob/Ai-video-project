import edge_tts

async def generate_voice(text, filename):
    tts = edge_tts.Communicate(
        text,
        voice="en-US-ChristopherNeural",
        rate="+5%"
    )
    await tts.save(filename)
    return filename