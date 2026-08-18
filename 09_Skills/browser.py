from __future__ import annotations
import subprocess, urllib.parse
SITES={"youtube":"https://youtube.com","google":"https://google.com","spotify":"https://open.spotify.com","github":"https://github.com"}
def open_browser(target=None):
    url=SITES.get(target.lower(),target) if target else None
    if url and not url.startswith(("http://","https://")): url="https://"+url
    cmd=["open","-a","Safari"] + ([url] if url else [])
    try: subprocess.run(cmd,check=True); return True
    except Exception:return False
def search_web(q):
    return open_browser("https://www.google.com/search?q="+urllib.parse.quote_plus(q))
