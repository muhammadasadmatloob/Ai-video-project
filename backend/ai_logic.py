import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Safely initialize Groq client (avoid crash on missing env variable)
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

def generate_local_fallback_script(topic, scene_count):
    title = topic.strip().title()
    
    # Generic templates to build a professional script outline
    narrations = [
        f"Welcome. Today we explore the fascinating topic of {topic}. It represents one of the most intriguing subjects of study in modern times.",
        f"As we look closer at the mechanics of {topic}, we begin to discover the underlying principles that make it so unique and complex.",
        f"Through advanced research and careful observation, scientists and experts are uncovering new aspects of {topic} every single day.",
        f"In conclusion, understanding {topic} opens up new horizons for technology and human knowledge. Thank you for joining us on this journey."
    ]
    
    # If scene_count is greater than 4, pad it with generic narration
    while len(narrations) < scene_count:
        narrations.insert(len(narrations) - 1, f"Furthermore, we must examine how {topic} interacts with its environment and shapes the world around it.")
        
    scenes = []
    # Extract keywords from topic
    topic_keywords = [w.strip(",.?!").lower() for w in topic.split() if len(w) > 3]
    if not topic_keywords:
        topic_keywords = ["education", "science"]
        
    for i, narration in enumerate(narrations[:scene_count]):
        # Alternate keywords to keep scenes visual
        keywords_pool = topic_keywords + ["technology", "space", "future", "universe", "knowledge", "discovery", "abstract"]
        scene_keywords = [keywords_pool[i % len(keywords_pool)], keywords_pool[(i+1) % len(keywords_pool)]]
        
        words = narration.split()
        scenes.append({
            "narration": narration,
            "keywords": scene_keywords,
            "caption": f"Exploring {title} - Part {i+1}",
            "subtitle_words": words
        })
        
    return {
        "title": title,
        "scenes": scenes
    }

def generate_script_json(user_topic, duration):
    scene_count = max(4, duration // 6)
    total_words = int(duration * 2.4)
    words_per_scene = max(35, total_words // scene_count)

    # If no client is available, skip Groq and use the local generator
    if not client:
        print("GROQ_API_KEY is not configured. Using local fallback script generator...")
        return generate_local_fallback_script(user_topic, scene_count)

    prompt = f"""
Return ONLY valid JSON.
Topic: {user_topic}
Duration: {duration} seconds
Scenes: {scene_count}

Each scene must include:
- narration (string)
- keywords (list of 2-3 search terms for stock video)
- caption (string)
- subtitle_words (list of exact words from the narration)

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
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        data = json.loads(res.choices[0].message.content)
    except Exception as e:
        print(f"Groq API failed ({e}). Falling back to local script generator...")
        data = generate_local_fallback_script(user_topic, scene_count)

    # Ensure keywords are formatted as a comma-separated string for fetch_stock_video
    for s in data.get("scenes", []):
        if isinstance(s.get("keywords"), list):
            s["keywords"] = ", ".join(s["keywords"])

    return data