from __future__ import annotations
import os, subprocess, tempfile, urllib.request, urllib.error, json

def _eleven(text):
    key=os.getenv("ELEVENLABS_API_KEY","").strip()
    voice=os.getenv("ELEVENLABS_VOICE_ID","xbpwjFFJpcRThvL5EyVi")
    if not key: return False
    body=json.dumps({"text":text,"model_id":os.getenv("ELEVENLABS_MODEL","eleven_multilingual_v2"),
        "voice_settings":{"stability":0.75,"similarity_boost":0.85,"style":0.0,"use_speaker_boost":True}}).encode()
    req=urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128",
        data=body,headers={"Content-Type":"application/json","xi-api-key":key},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=30) as r: audio=r.read()
        with tempfile.NamedTemporaryFile(suffix=".mp3",delete=False) as f:
            f.write(audio); path=f.name
        subprocess.run(["afplay",path],check=False)
        os.unlink(path)
        return True
    except Exception: return False

def speak(text, speed="1.0"):
    if not text: return
    if os.getenv("JARVIS_TTS","macos").lower()=="elevenlabs" and _eleven(text): return
    subprocess.run(["say","-r",str(int(180*float(speed))),text],check=False)
