import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Safely initialize Groq client (avoid crash on missing env variable or library mismatch)
api_key = os.getenv("GROQ_API_KEY")
try:
    client = Groq(api_key=api_key) if api_key else None
except Exception as e:
    print(f"Warning initializing Groq client: {e}")
    client = None


def generate_local_fallback_script(topic, scene_count, style="viral_shorts"):
    title = topic.strip().title()
    
    if style == "viral_shorts":
        narrations = [
            f"What if I told you that {topic} holds a secret that almost everyone gets wrong?",
            f"When you look closely at {topic}, the reality is completely mind-blowing.",
            f"Experts discovered that {topic} actually operates under rules nobody expected.",
            f"Subscribe now if {topic} blew your mind today!"
        ]
    elif style == "documentary":
        narrations = [
            f"Deep within the realm of {topic} lies an extraordinary mystery waiting to be uncovered.",
            f"For decades, researchers have analyzed {topic}, revealing unbelievable hidden facts.",
            f"Every discovery about {topic} pushes the boundaries of human knowledge further.",
            f"The true story of {topic} is only just beginning to take shape."
        ]
    elif style == "educational":
        narrations = [
            f"Here is how {topic} actually works in under sixty seconds!",
            f"First, the core foundation of {topic} relies on fascinating natural mechanics.",
            f"Next, when you combine these elements, {topic} produces unexpected results.",
            f"And that is why understanding {topic} is essential for the future!"
        ]
    else: # storytelling
        narrations = [
            f"Imagine a world where {topic} changed the course of history forever.",
            f"Against all odds, the journey through {topic} took an incredible unexpected turn.",
            f"What happened next with {topic} left everyone absolutely speechless.",
            f"This epic story of {topic} reminds us of what is truly possible."
        ]
    
    # If scene_count is greater than narrations length, pad with engaging filler
    while len(narrations) < scene_count:
        narrations.insert(len(narrations) - 1, f"Even more surprising is how {topic} continues to defy expectations.")
        
    scenes = []
    topic_keywords = [w.strip(",.?!").lower() for w in topic.split() if len(w) > 3]
    if not topic_keywords:
        topic_keywords = ["technology", "future"]
        
    for i, narration in enumerate(narrations[:scene_count]):
        keywords_pool = topic_keywords + ["cinematic", "dramatic", "hyperrealistic", "discovery", "abstract", "universe"]
        scene_keywords = f"{keywords_pool[i % len(keywords_pool)]}, {keywords_pool[(i+1) % len(keywords_pool)]}, cinematic"
        
        words = narration.split()
        scenes.append({
            "narration": narration,
            "keywords": scene_keywords,
            "caption": f"Exploring {title}",
            "subtitle_words": words
        })
        
    return {
        "title": title,
        "scenes": scenes
    }

def generate_script_json(user_topic, duration, style="viral_shorts"):
    scene_count = max(4, duration // 6)
    
    if not client:
        print("GROQ_API_KEY is not configured. Using high-retention local script generator...")
        return generate_local_fallback_script(user_topic, scene_count, style)

    style_instructions = {
        "viral_shorts": "Create a high-energy, fast-paced YouTube Shorts script. Start with a 3-second shocking viral hook. Short punchy sentences (5-10 words max). High curiosity gap.",
        "documentary": "Create a cinematic, intrigue-filled documentary script with a mysterious opening hook and deep storytelling pace.",
        "educational": "Create a clear, fascinating explainer script starting with 'Did you know...?' or an engaging question, broken into clear visual steps.",
        "storytelling": "Create a dramatic narrative script with a strong emotional hook, climax, and captivating resolution."
    }

    selected_instruction = style_instructions.get(style, style_instructions["viral_shorts"])

    prompt = f"""
Return ONLY valid JSON.
Topic: {user_topic}
Duration: {duration} seconds
Scenes count: {scene_count}
Script Style: {selected_instruction}

IMPORTANT RULES FOR YOUTUBE RETENTION:
1. Scene 1 narration MUST be an attention-grabbing, curiosity-driven viral hook. NO 'Welcome to' or 'In this video'!
2. Sentences must be punchy, clear, and high-impact.
3. Keywords for each scene must be 2-3 visual search terms for HD stock videos (e.g. ['cinematic space', 'black hole', 'galaxy']).

Return JSON format:
{{
  "title": "{user_topic}",
  "scenes": [
    {{
      "narration": "First scene narration...",
      "keywords": "cinematic space, galaxy, abstract",
      "caption": "Short badge caption",
      "subtitle_words": ["First", "scene", "narration"]
    }}
  ]
}}
"""
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.85
        )
        data = json.loads(res.choices[0].message.content)
    except Exception as e:
        print(f"Groq API failed ({e}). Falling back to high-retention script generator...")
        data = generate_local_fallback_script(user_topic, scene_count, style)

    for s in data.get("scenes", []):
        if isinstance(s.get("keywords"), list):
            s["keywords"] = ", ".join(s["keywords"])
        if "subtitle_words" not in s or not s["subtitle_words"]:
            s["subtitle_words"] = s.get("narration", "").split()

    return data