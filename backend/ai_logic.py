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


def generate_local_fallback_script(topic, scene_count, style="viral_shorts", target_duration=30):
    title = topic.strip().title()
    total_target_words = int(target_duration * 2.5)
    words_per_scene = max(15, total_target_words // scene_count)
    
    if style == "viral_shorts":
        narrations = [
            f"What if I told you that {topic} holds a secret that almost everyone gets wrong? Today we reveal the truth.",
            f"When you examine {topic} up close, the reality is completely mind-blowing and defies common logic.",
            f"Top researchers discovered that {topic} actually operates under rules nobody expected, changing how we view it.",
            f"Every single day, new breakthroughs in {topic} continue to shock experts around the globe.",
            f"Understanding the core mechanics of {topic} gives you a huge advantage in predicting what comes next.",
            f"Subscribe now if {topic} blew your mind today, and hit the notification bell for more insane facts!"
        ]
    elif style == "documentary":
        narrations = [
            f"Deep within the fascinating realm of {topic} lies an extraordinary mystery that has baffled historians for generations.",
            f"For decades, top scientists have analyzed {topic}, uncovering unbelievable hidden facts beneath the surface.",
            f"Every single discovery about {topic} pushes the boundaries of human knowledge and technology further into the future.",
            f"As we examine {topic} more closely, the true scope of its impact becomes strikingly clear to everyone.",
            f"The ongoing story of {topic} is far from over, and what comes next will redefine our understanding forever."
        ]
    elif style == "educational":
        narrations = [
            f"Here is how {topic} actually works in sixty seconds or less, explained in the simplest possible way!",
            f"First, the foundational core of {topic} relies on natural principles that interact in powerful, unique ways.",
            f"Next, when these core elements combine under pressure, {topic} produces remarkable and unexpected results.",
            f"Finally, mastering {topic} unlocks new possibilities across technology, science, and everyday life for everyone."
        ]
    else: # storytelling
        narrations = [
            f"Imagine a world where {topic} suddenly changed the entire course of human history forever.",
            f"Against all impossible odds, the journey through {topic} took an unexpected turn that nobody saw coming.",
            f"What happened next with {topic} left the entire world absolutely speechless and searching for answers.",
            f"This epic story of {topic} serves as an incredible reminder of what human ingenuity can accomplish."
        ]
    
    # Adjust narrations to match scene_count
    while len(narrations) < scene_count:
        narrations.insert(len(narrations) - 1, f"Furthermore, examining {topic} deeper reveals even more surprising layers that defy conventional wisdom.")
        
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
    scene_count = max(4, min(12, duration // 6))
    total_words = int(duration * 2.5)
    words_per_scene = max(15, total_words // scene_count)

    if not client:
        print("GROQ_API_KEY is not configured. Using high-retention local script generator...")
        return generate_local_fallback_script(user_topic, scene_count, style, target_duration=duration)

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
Target Duration: {duration} seconds
Scenes Count: {scene_count}
Total Script Word Target: Exactly {total_words} words (approx {words_per_scene} words per scene).
Script Style: {selected_instruction}

IMPORTANT RULES FOR YOUTUBE RETENTION & LENGTH ACCURACY:
1. Scene 1 narration MUST be an attention-grabbing, curiosity-driven viral hook. NO 'Welcome to' or 'In this video'!
2. Total words across ALL scenes MUST equal roughly {total_words} words so that spoken voice narration fills the full {duration} seconds duration. DO NOT make short 5-word scenes!
3. Sentences must be clear, high-impact, and energetic without awkward silent pauses.
4. Keywords for each scene must be 2-3 visual search terms for HD stock videos (e.g. ['cinematic space', 'galaxy', 'abstract']).

Return JSON format:
{{
  "title": "{user_topic}",
  "scenes": [
    {{
      "narration": "First scene full narration containing roughly {words_per_scene} words...",
      "keywords": "cinematic space, galaxy, abstract",
      "caption": "Short badge caption",
      "subtitle_words": ["First", "scene", "full", "narration"]
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
        data = generate_local_fallback_script(user_topic, scene_count, style, target_duration=duration)

    for s in data.get("scenes", []):
        if isinstance(s.get("keywords"), list):
            s["keywords"] = ", ".join(s["keywords"])
        if "subtitle_words" not in s or not s["subtitle_words"]:
            s["subtitle_words"] = s.get("narration", "").split()

    return data