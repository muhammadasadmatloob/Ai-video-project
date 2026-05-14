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
You are an award-winning cinematic documentary writer and TikTok/YouTube Shorts expert.

TOPIC: {user_topic}
DURATION: {duration}s
SCENES: {scene_count}

RULES:
- Scene 1 MUST have a powerful, curiosity-inducing hook to grab attention instantly.
- The tone must be dramatic, emotional, highly engaging, and profound. 
- Use rich, descriptive, and humanized storytelling. No robotic phrasing.
- Each scene needs ~{words_per_scene} words of continuous, flowing narration.

IMPORTANT OUTPUT:
1. narration → full, engaging, expressive storytelling.
2. keywords → A JSON ARRAY of 2 to 3 precise visual search terms.
3. caption → MUST summarize narration exactly.
4. subtitle_words → MUST be EXACT words from narration (in order, stripped of punctuation for pacing).

CRITICAL:
- Your output MUST be perfectly valid JSON.

Return JSON ONLY formatted exactly like this:
{{
  "title": "{user_topic}",
  "scenes": [
    {{
      "narration": "...",
      "keywords": ["neon cityscape", "futuristic buildings", "cyberpunk"],
      "caption": "...",
      "subtitle_words": ["word1", "word2", "word3"]
    }}
  ]
}}
"""

    completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        response_format={"type": "json_object"},
        temperature=0.8
    )

    # 1. Safely load the generated JSON
    script_data = json.loads(completion.choices[0].message.content)

    # 2. Convert the keywords array into a space-separated string behind the scenes
    # This ensures your video_fetcher.py still works perfectly without any changes.
    for scene in script_data.get("scenes", []):
        if isinstance(scene.get("keywords"), list):
            scene["keywords"] = " ".join(scene["keywords"])

    return script_data