"""
WaveFlow - YouTube Music + AI Playlist Agent
pip install fastapi uvicorn ytmusicapi anthropic openai jinja2 python-multipart
python main.py
"""

import json
import os
import re
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from ytmusicapi import YTMusic

DATA_FILE = "userdata.json"
SETTINGS_FILE = "settings.json"

app = FastAPI(title="WaveFlow")
templates = Jinja2Templates(directory="templates")

static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

ytmusic = YTMusic()

# ============================================================
# SETTINGS (api key / provider stored in settings.json)
# ============================================================

def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"provider": "claude", "api_key": ""}


def save_settings(s: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=2)


# ============================================================
# DATA STORAGE
# ============================================================

def load_data() -> dict:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"likes": [], "history": [], "agent_history": []}


def save_data(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ============================================================
# TRACK HELPERS
# ============================================================

def format_track(raw: dict) -> dict:
    try:
        thumbs = raw.get("thumbnails", [])
        thumb = thumbs[-1]["url"] if thumbs else ""
        artists = raw.get("artists", [])
        artist_name = ", ".join(a.get("name", "") for a in artists) if artists else raw.get("artist", "")
        album = raw.get("album", {})
        album_name = album.get("name", "") if isinstance(album, dict) else str(album or "")
        return {
            "id": raw.get("videoId", ""),
            "title": raw.get("title", "Unknown"),
            "artist": artist_name,
            "album": album_name,
            "duration": raw.get("duration", ""),
            "thumb": thumb,
            "year": raw.get("year", ""),
        }
    except Exception:
        return {}


def get_recommendations(data: dict, limit: int = 20) -> list:
    liked = data.get("likes", [])
    if not liked:
        try:
            results = ytmusic.search("top hits 2024", filter="songs", limit=limit)
            return [t for t in [format_track(r) for r in results] if t.get("id")]
        except Exception:
            return []
    artists = list(set(t.get("artist", "").split(",")[0].strip() for t in liked if t.get("artist")))[:5]
    recs = []
    for artist in artists:
        try:
            results = ytmusic.search(artist, filter="songs", limit=5)
            for r in results:
                t = format_track(r)
                if t.get("id") and not any(l["id"] == t["id"] for l in liked):
                    recs.append(t)
        except Exception:
            continue
    return recs[:limit]


# ============================================================
# AI CALLER (multi-provider)
# ============================================================

def call_ai(provider: str, api_key: str, system: str, messages: list) -> str:
    if provider == "claude":
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2048,
            system=system,
            messages=messages,
        )
        return response.content[0].text.strip()

    elif provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        msgs = [{"role": "system", "content": system}] + messages
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=msgs,
            max_tokens=2048,
        )
        return response.choices[0].message.content.strip()

    elif provider == "gemini":
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system)
        history_text = "\n".join(f"{m['role']}: {m['content']}" for m in messages[:-1])
        user_msg = messages[-1]["content"] if messages else ""
        prompt = f"{history_text}\nuser: {user_msg}" if history_text else user_msg
        response = model.generate_content(prompt)
        return response.text.strip()

    elif provider == "groq":
        from groq import Groq
        client = Groq(api_key=api_key)
        msgs = [{"role": "system", "content": system}] + messages
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=msgs,
            max_tokens=2048,
        )
        return response.choices[0].message.content.strip()

    else:
        raise ValueError(f"Unknown provider: {provider}")


# ============================================================
# ROUTES
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/settings")
async def get_settings():
    s = load_settings()
    return {"provider": s.get("provider", "claude"), "has_key": bool(s.get("api_key", ""))}


class SettingsBody(BaseModel):
    provider: str
    api_key: str


@app.post("/api/settings")
async def update_settings(body: SettingsBody):
    save_settings({"provider": body.provider, "api_key": body.api_key})
    return {"ok": True}


@app.get("/api/search")
async def search(q: str, limit: int = 20):
    if not q.strip():
        raise HTTPException(400, "Empty query")
    try:
        results = ytmusic.search(q, filter="songs", limit=limit)
        tracks = [t for t in [format_track(r) for r in results] if t.get("id")]
        return {"tracks": tracks}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/likes")
async def get_likes():
    return {"likes": load_data().get("likes", [])}


class TrackBody(BaseModel):
    track: dict


@app.post("/api/likes/add")
async def add_like(body: TrackBody):
    data = load_data()
    likes = data.get("likes", [])
    if not any(l["id"] == body.track["id"] for l in likes):
        likes.append(body.track)
        data["likes"] = likes
        save_data(data)
    return {"ok": True}


@app.post("/api/likes/remove")
async def remove_like(body: TrackBody):
    data = load_data()
    data["likes"] = [l for l in data.get("likes", []) if l["id"] != body.track["id"]]
    save_data(data)
    return {"ok": True}


@app.post("/api/history/add")
async def add_history(body: TrackBody):
    data = load_data()
    hist = data.get("history", [])
    track = dict(body.track)
    track["played_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    hist.insert(0, track)
    data["history"] = hist[:100]
    save_data(data)
    return {"ok": True}


@app.get("/api/history")
async def get_history():
    return {"history": load_data().get("history", [])[:30]}


@app.get("/api/recommendations")
async def recommendations():
    return {"tracks": get_recommendations(load_data())}


# ============================================================
# AI AGENT
# ============================================================

class AgentMessage(BaseModel):
    message: str
    reset: bool = False


@app.post("/api/agent")
async def agent_chat(body: AgentMessage):
    data = load_data()

    if body.reset:
        data["agent_history"] = []
        save_data(data)
        return {"reply": "Ready. Describe what you want to hear.", "playlist": []}

    settings = load_settings()
    api_key = settings.get("api_key", "")
    provider = settings.get("provider", "claude")

    if not api_key:
        raise HTTPException(400, "No API key configured. Go to Settings and add your API key.")

    user_msg = body.message.strip()
    if not user_msg:
        raise HTTPException(400, "Empty message")

    history = data.get("agent_history", [])

    # Search YouTube Music for tracks
    search_results = []
    try:
        raw = ytmusic.search(user_msg, filter="songs", limit=30)
        search_results = [t for t in [format_track(r) for r in raw] if t.get("id")]
    except Exception:
        pass

    for kw in extract_keywords(user_msg)[:2]:
        try:
            raw2 = ytmusic.search(kw, filter="songs", limit=15)
            for r in raw2:
                t = format_track(r)
                if t.get("id") and not any(s["id"] == t["id"] for s in search_results):
                    search_results.append(t)
        except Exception:
            pass

    tracks_context = json.dumps(search_results[:40], ensure_ascii=False)

    system = """You are a music playlist AI agent. Your job: select tracks from the provided YouTube Music list that match the user's request.
Return ONLY valid JSON (no markdown):
{
  "reply": "short friendly response explaining the playlist vibe",
  "playlist": ["videoId1", "videoId2", ...]
}
Max 15 tracks. Only use videoIds from the provided list. Keep reply concise."""

    user_content = f"Request: {user_msg}\n\nAvailable tracks:\n{tracks_context}\n\nSelect matching tracks and return JSON."

    try:
        messages = list(history) + [{"role": "user", "content": user_content}]
        raw_reply = call_ai(provider, api_key, system, messages)

        try:
            parsed = json.loads(raw_reply)
        except Exception:
            m = re.search(r'\{.*\}', raw_reply, re.DOTALL)
            parsed = json.loads(m.group()) if m else {"reply": raw_reply, "playlist": []}

        playlist_ids = parsed.get("playlist", [])
        playlist_tracks = [t for t in search_results if t["id"] in playlist_ids]

        history.append({"role": "user", "content": f"Request: {user_msg}"})
        history.append({"role": "assistant", "content": raw_reply})
        data["agent_history"] = history[-20:]
        save_data(data)

        return {"reply": parsed.get("reply", ""), "playlist": playlist_tracks}

    except Exception as e:
        raise HTTPException(500, str(e))


def extract_keywords(text: str) -> list:
    mood_map = {
        "утро": "morning acoustic", "работ": "focus music", "спорт": "workout",
        "грустн": "sad songs", "вечер": "evening chill", "ночь": "night ambient",
        "лоуфай": "lofi hip hop", "инди": "indie music", "ретро": "retro 80s",
        "рок": "rock", "поп": "pop hits", "рэп": "rap hip hop", "джаз": "jazz",
        "электронн": "electronic", "расслаб": "relaxing music",
        "morning": "morning acoustic", "work": "focus music", "workout": "gym workout",
        "sad": "sad emotional", "night": "night lo-fi", "lofi": "lofi beats",
        "indie": "indie alternative", "retro": "retro 80s", "rock": "rock",
        "pop": "pop hits", "rap": "hip hop", "jazz": "jazz smooth",
        "electronic": "electronic music", "chill": "chill vibes",
        "party": "party hits", "focus": "concentration music",
    }
    text_lower = text.lower()
    return [en for ru, en in mood_map.items() if ru in text_lower]


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
