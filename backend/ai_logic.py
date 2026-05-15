import os, json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_script_json(user_topic, duration):
    scene_count = max(4, duration // 6)
    total_words = int(duration * 2.4)
    words_per_scene = max(35, total_words // scene_count)

    prompt = f"""
Return ONLY valid JSON.

Topic: {user_topic}
Duration: {duration}

Scenes: {scene_count}

Each scene must include:
- narration
- keywords (2-3)
- caption
- subtitle_words (exact words only)

Return JSON format:
{{
  "title": "{user_topic}",
  "scenes": [
    {{
      "narration": "",
      "keywords": [],
      "caption": "",
      "subtitle_words": []
    }}
  ]
}}
"""

    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.7
    )

    data = json.loads(res.choices[0].message.content)

    # convert keywords list → string for FFmpeg compatibility
    for s in data.get("scenes", []):
        if isinstance(s.get("keywords"), list):
            s["keywords"] = " ".join(s["keywords"])

    return data