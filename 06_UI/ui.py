from __future__ import annotations
import json, threading, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HTML = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>JARVIS</title><style>
*{box-sizing:border-box}body{margin:0;background:#05070b;color:#d9f4ff;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;height:100vh;overflow:hidden}
.wrap{height:100%;display:flex;align-items:center;justify-content:center;position:relative}
.core{width:280px;height:280px;border-radius:50%;border:2px solid #61d9ff;box-shadow:0 0 30px #61d9ff55, inset 0 0 45px #61d9ff22;display:flex;align-items:center;justify-content:center;animation:pulse 3s infinite}
.core:after{content:'';width:90px;height:90px;border-radius:50%;border:1px solid #b9f2ff;box-shadow:0 0 40px #61d9ff;animation:spin 8s linear infinite}
.panel{position:absolute;left:32px;top:32px;width:300px;background:#09111bd9;border:1px solid #21475c;border-radius:18px;padding:18px;backdrop-filter:blur(12px)}
h1{margin:0 0 12px;font-size:20px;letter-spacing:5px}.label{font-size:11px;color:#6d9bad;text-transform:uppercase;letter-spacing:2px;margin-top:14px}.value{margin-top:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bottom{position:absolute;bottom:30px;width:min(720px,90%);text-align:center;color:#7ea8b7}.state{font-size:14px;letter-spacing:3px;text-transform:uppercase}
@keyframes pulse{50%{transform:scale(1.035);box-shadow:0 0 65px #61d9ff77,inset 0 0 65px #61d9ff33}}@keyframes spin{to{transform:rotate(360deg)}}
</style></head><body><div class="wrap"><div class="panel"><h1>J.A.R.V.I.S.</h1>
<div class="label">Status</div><div class="value" id="state">OFFLINE</div>
<div class="label">Heard</div><div class="value" id="heard">—</div>
<div class="label">Response</div><div class="value" id="response">—</div>
<div class="label">Task</div><div class="value" id="task">—</div></div>
<div class="core"></div><div class="bottom"><div class="state" id="bottom">INITIALIZING</div></div></div>
<script>async function tick(){try{let d=await fetch('/api/status').then(r=>r.json());for(let k of ['state','heard','response','task']){document.getElementById(k).textContent=d[k]||'—'}document.getElementById('bottom').textContent=d.state||'ONLINE'}catch(e){}}setInterval(tick,400);tick();</script></body></html>"""

class UI:
    def __init__(self,status,host="127.0.0.1",port=8765):
        self.status=status; self.host=host; self.port=port
    def start(self):
        status=self.status
        class H(BaseHTTPRequestHandler):
            def log_message(self,*a): pass
            def do_GET(self):
                if self.path=="/":
                    body=HTML.encode()
                    self.send_response(200); self.send_header("Content-Type","text/html"); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)
                elif self.path=="/api/status":
                    body=json.dumps(status.get()).encode()
                    self.send_response(200); self.send_header("Content-Type","application/json"); self.send_header("Cache-Control","no-store"); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)
                else: self.send_response(404); self.end_headers()
        server=ThreadingHTTPServer((self.host,self.port),H)
        threading.Thread(target=server.serve_forever,daemon=True).start()
        webbrowser.open(f"http://{self.host}:{self.port}")
        return server
