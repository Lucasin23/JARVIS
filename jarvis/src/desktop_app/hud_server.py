"""
JARVIS HUD — cinematic arc-reactor heads-up display.

A self-contained Flask server that serves a canvas-rendered HUD and exposes the
current assistant state plus live system metrics. It mirrors the architecture of
``desktop_app.memory_viewer``: in dev it runs as a subprocess, in bundled mode it
runs in a daemon thread. The HUD page is inlined as a single HTML document so it
works in both packaged and development builds with no extra static-asset wiring.

State is read from the shared ``jarvis_state`` file written by
``desktop_app.face_widget.JarvisStateManager`` — the same source the on-screen
face widget uses — so the HUD always reflects what the assistant is doing
(idle / listening / thinking / speaking / dictating), even across processes.

Run directly:  python -m desktop_app.hud_server [port]
Default port: 5060
"""

from __future__ import annotations

import os
import tempfile
import time
from datetime import datetime
from typing import Any

from flask import Flask, jsonify, Response

try:
    from jarvis.debug import debug_log
except Exception:  # HUD must start even if debug logging isn't wired up
    def debug_log(*_args, **_kwargs) -> None:
        return None


app = Flask(__name__)

HUD_PORT = 5060


# ─────────────────────────────────────────────────────────────────────────────
# State source (shared with the face widget)
# ─────────────────────────────────────────────────────────────────────────────

def _state_file() -> str:
    """Path to the shared jarvis_state file written by the face widget."""
    return os.path.join(tempfile.gettempdir(), "jarvis_state")


# Human-readable labels + accent colours per assistant state. These drive the
# whole HUD palette, so adding a new state here is enough to theme it.
_STATE_META: dict[str, dict[str, str]] = {
    "asleep":                {"label": "STANDBY",          "color": "#3b82f6"},
    "idle":                  {"label": "ONLINE",           "color": "#22d3ee"},
    "listening":             {"label": "LISTENING",       "color": "#34d399"},
    "thinking":              {"label": "PROCESSING",     "color": "#fbbf24"},
    "speaking":              {"label": "SPEAKING",        "color": "#e2e8f0"},
    "dictating":             {"label": "RECORDING",       "color": "#f472b6"},
    "dictation_processing":  {"label": "TRANSCRIBING",   "color": "#f472b6"},
}


def read_state() -> dict[str, Any]:
    """Read the current assistant state + system metrics for the HUD."""
    raw = "asleep"
    try:
        with open(_state_file(), "r") as f:
            raw = f.read().strip() or "asleep"
    except OSError:
        pass

    meta = _STATE_META.get(raw, _STATE_META["asleep"])

    metrics = _read_metrics()
    now = datetime.now()
    return {
        "state": raw,
        "label": meta["label"],
        "color": meta["color"],
        "timestamp": now.isoformat(timespec="seconds"),
        "uptime": _uptime_seconds(),
        "metrics": metrics,
    }


def _read_metrics() -> dict[str, Any]:
    """Best-effort system metrics via psutil (already a project dependency)."""
    try:
        import psutil  # local import; psutil is imported by desktop_app.app
        vm = psutil.virtual_memory()
        return {
            "cpu_percent": round(psutil.cpu_percent(interval=None), 1),
            "cpu_count": psutil.cpu_count(logical=True) or 0,
            "mem_percent": round(vm.percent, 1),
            "mem_used_gb": round(vm.used / (1024 ** 3), 2),
            "mem_total_gb": round(vm.total / (1024 ** 3), 2),
            "disk_percent": round(psutil.disk_usage("/").percent, 1),
            "boot_time": int(psutil.boot_time()),
        }
    except Exception as e:  # noqa: BLE001 - HUD must never crash on metrics
        debug_log(f"hud metrics unavailable: {e}", "desktop")
        return {}


def _uptime_seconds() -> int:
    try:
        import psutil
        return int(time.time() - psutil.boot_time())
    except Exception:
        return 0


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/state")
def api_state() -> Response:
    return jsonify(read_state())


@app.route("/api/health")
def api_health() -> Response:
    return jsonify({"ok": True, "service": "jarvis-hud"})


@app.route("/")
def index() -> Response:
    return Response(_INDEX_HTML, mimetype="text/html")


# ─────────────────────────────────────────────────────────────────────────────
# The HUD page (inlined HTML + CSS + JS so packaging needs no static assets)
# ─────────────────────────────────────────────────────────────────────────────

_INDEX_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>J.A.R.V.I.S. — HUD</title>
<style>
  :root{
    --accent:#22d3ee;
    --accent-dim:rgba(34,211,238,.35);
    --bg:#04070d;
    --grid:rgba(56,189,248,.06);
    --text:#9fd8e8;
    --text-dim:#5b7d8c;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  html,body{width:100%;height:100%;overflow:hidden;background:var(--bg);
    font-family:"Segoe UI",Roboto,"Helvetica Neue",system-ui,sans-serif;
    color:var(--text);cursor:crosshair}
  #stage{position:fixed;inset:0;display:block}
  /* faint engineering grid */
  .grid{position:fixed;inset:0;pointer-events:none;
    background-image:
      linear-gradient(var(--grid) 1px,transparent 1px),
      linear-gradient(90deg,var(--grid) 1px,transparent 1px);
    background-size:46px 46px;opacity:.7;
    -webkit-mask-image:radial-gradient(circle at 50% 50%,#000 0%,transparent 78%);
            mask-image:radial-gradient(circle at 50% 50%,#000 0%,transparent 78%);}
  /* scanlines + vignette */
  .scan{position:fixed;inset:0;pointer-events:none;
    background:repeating-linear-gradient(0deg,rgba(0,0,0,.16) 0 1px,transparent 1px 3px);
    mix-blend-mode:multiply;opacity:.5}
  .vignette{position:fixed;inset:0;pointer-events:none;
    background:radial-gradient(circle at 50% 50%,transparent 52%,rgba(0,0,0,.65) 100%)}
  /* HUD readout panels */
  .panel{position:fixed;min-width:188px;padding:10px 14px;
    border:1px solid var(--accent-dim);border-radius:4px;
    background:linear-gradient(180deg,rgba(8,16,26,.72),rgba(4,7,13,.55));
    -webkit-backdrop-filter:blur(2px);backdrop-filter:blur(2px);
    font-size:11px;letter-spacing:.12em;text-transform:uppercase;
    box-shadow:0 0 22px rgba(34,211,238,.07),inset 0 0 18px rgba(34,211,238,.04)}
  .panel::before{content:"";position:absolute;left:0;top:0;width:10px;height:10px;
    border-top:1px solid var(--accent);border-left:1px solid var(--accent)}
  .panel::after{content:"";position:absolute;right:0;bottom:0;width:10px;height:10px;
    border-bottom:1px solid var(--accent);border-right:1px solid var(--accent)}
  .panel h2{font-size:10px;color:var(--accent);font-weight:600;margin-bottom:8px;
    text-shadow:0 0 8px var(--accent-dim)}
  .row{display:flex;justify-content:space-between;gap:18px;line-height:1.85;
    color:var(--text-dim)}
  .row b{color:var(--text);font-weight:600;font-variant-numeric:tabular-nums}
  .bar{height:5px;background:rgba(120,180,200,.12);border-radius:3px;overflow:hidden;margin-top:3px}
  .bar i{display:block;height:100%;background:linear-gradient(90deg,var(--accent),#fff);
    box-shadow:0 0 10px var(--accent-dim);transition:width .4s ease}
  .tl{top:22px;left:22px}
  .tr{top:22px;right:22px;text-align:right}
  .bl{bottom:22px;left:22px;min-width:320px}
  .br{bottom:22px;right:22px;text-align:right}
  .center-label{position:fixed;left:50%;top:62%;transform:translate(-50%,0);
    text-align:center;pointer-events:none}
  .center-label .kicker{font-size:11px;letter-spacing:.5em;color:var(--text-dim)}
  .center-label .state{font-size:30px;letter-spacing:.42em;font-weight:700;
    color:var(--accent);text-shadow:0 0 18px var(--accent);margin-top:6px;
    transition:color .35s ease,text-shadow .35s ease}
  .ticker{position:fixed;left:0;right:0;bottom:0;height:22px;
    background:rgba(0,0,0,.4);border-top:1px solid var(--accent-dim);
    overflow:hidden;white-space:nowrap;font-size:10px;letter-spacing:.22em;
    color:var(--text-dim);line-height:22px}
  .ticker span{display:inline-block;padding-left:100%;
    animation:tick 38s linear infinite}
  @keyframes tick{to{transform:translateX(-100%)}}
  .boot{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;
    flex-direction:column;gap:14px;background:var(--bg);z-index:10;
    transition:opacity .8s ease}
  .boot.gone{opacity:0;pointer-events:none}
  .boot .ring{width:64px;height:64px;border-radius:50%;border:2px solid var(--accent-dim);
    border-top-color:var(--accent);animation:spin 1s linear infinite}
  @keyframes spin{to{transform:rotate(360deg)}}
  .boot p{font-size:12px;letter-spacing:.4em;color:var(--accent);
    text-shadow:0 0 10px var(--accent-dim)}
  .glitch{animation:glitch .14s steps(2) infinite}
  @keyframes glitch{50%{opacity:.4}}
</style>
</head>
<body>
  <canvas id="stage"></canvas>
  <div class="grid"></div>
  <div class="scan"></div>
  <div class="vignette"></div>

  <section class="panel tl">
    <h2>System Diagnostics</h2>
    <div class="row"><span>CPU</span><b id="m-cpu">--</b></div>
    <div class="bar"><i id="b-cpu" style="width:0%"></i></div>
    <div class="row" style="margin-top:6px"><span>Memory</span><b id="m-mem">--</b></div>
    <div class="bar"><i id="b-mem" style="width:0%"></i></div>
    <div class="row" style="margin-top:6px"><span>Disk</span><b id="m-disk">--</b></div>
    <div class="bar"><i id="b-disk" style="width:0%"></i></div>
    <div class="row" style="margin-top:6px"><span>Cores</span><b id="m-cores">--</b></div>
  </section>

  <section class="panel tr">
    <h2>Chronometer</h2>
    <div class="row"><span>Time</span><b id="t-time">--:--:--</b></div>
    <div class="row"><span>Date</span><b id="t-date">----</b></div>
    <div class="row"><span>Uptime</span><b id="t-up">--</b></div>
    <div class="row"><span>Lat</span><b>--</b></div>
    <div class="row"><span>Lon</span><b>--</b></div>
  </section>

  <section class="panel bl">
    <h2>Command Console</h2>
    <div class="row"><span>Mode</span><b id="c-mode">VOICE / TEXT</b></div>
    <div class="row"><span>Backend</span><b id="c-backend">OpenAI-Compatible</b></div>
    <div class="row"><span>Signal</span><b id="c-signal">●●●●●</b></div>
    <div class="row"><span>Link</span><b id="c-link" style="color:var(--accent)">SECURE</b></div>
  </section>

  <section class="panel br">
    <h2>Reactor</h2>
    <div class="row"><span>Output</span><b id="r-out">3.14 GJ/s</b></div>
    <div class="row"><span>Coherence</span><b id="r-coh">98.7%</b></div>
    <div class="row"><span>Temp</span><b id="r-temp">412 K</b></div>
    <div class="row"><span>Status</span><b id="r-status" style="color:var(--accent)">NOMINAL</b></div>
  </section>

  <div class="center-label">
    <div class="kicker">J · A · R · V · I · S</div>
    <div class="state" id="state-label">INITIALIZING</div>
  </div>

  <div class="ticker"><span id="ticker-text">J.A.R.V.I.S. ONLINE · ALL SYSTEMS NOMINAL · NEURAL LINK STABILIZED · DEFENSE PROTOCOLS ACTIVE · AWAITING COMMAND · LOCAL SECURE NETWORK · TELEMETRY STREAMING · </span></div>

  <div class="boot" id="boot"><div class="ring"></div><p>INITIALIZING HUD</p></div>

<script>
"use strict";
const canvas = document.getElementById("stage");
const ctx = canvas.getContext("2d");
let W=0, H=0, CX=0, CY=0, DPR=1;

function resize(){
  DPR = Math.min(window.devicePixelRatio||1, 2);
  W = window.innerWidth; H = window.innerHeight;
  canvas.width = Math.floor(W*DPR); canvas.height = Math.floor(H*DPR);
  canvas.style.width = W+"px"; canvas.style.height = H+"px";
  ctx.setTransform(DPR,0,0,DPR,0,0);
  CX = W/2; CY = H/2;
}
window.addEventListener("resize", resize); resize();

// ── live state (polled from /api/state) ────────────────────────────────────
const STATE = {
  state:"asleep", label:"STANDBY", color:"#3b82f6",
  cpu:0, mem:0, disk:0, cores:0, memUsed:0, memTotal:0, uptime:0
};
const $ = id => document.getElementById(id);

async function poll(){
  try{
    const r = await fetch("/api/state", {cache:"no-store"});
    const d = await r.json();
    STATE.state = d.state; STATE.label = d.label; STATE.color = d.color;
    const m = d.metrics||{};
    STATE.cpu = m.cpu_percent||0; STATE.mem = m.mem_percent||0;
    STATE.disk = m.disk_percent||0; STATE.cores = m.cpu_count||0;
    STATE.memUsed = m.mem_used_gb||0; STATE.memTotal = m.mem_total_gb||0;
    STATE.uptime = d.uptime||0;
    paintState(d);
  }catch(e){ $("c-link").textContent="RECONNECTING"; $("c-link").style.color="#f472b6"; }
}
setInterval(poll, 600); poll();

function paintState(d){
  const root = document.documentElement.style;
  root.setProperty("--accent", STATE.color);
  root.setProperty("--accent-dim", STATE.color+"59");
  $("state-label").textContent = STATE.label;
  // metrics
  $("m-cpu").textContent = STATE.cpu.toFixed(1)+"%";
  $("b-cpu").style.width = STATE.cpu+"%";
  $("m-mem").textContent = STATE.mem.toFixed(1)+"% · "+STATE.memUsed.toFixed(1)+"/"+STATE.memTotal.toFixed(1)+"GB";
  $("b-mem").style.width = STATE.mem+"%";
  $("m-disk").textContent = STATE.disk.toFixed(1)+"%";
  $("b-disk").style.width = STATE.disk+"%";
  $("m-cores").textContent = STATE.cores;
  // clock
  const now = new Date();
  $("t-time").textContent = now.toLocaleTimeString("en-GB",{hour12:false});
  $("t-date").textContent = now.toLocaleDateString("en-GB");
  $("t-up").textContent = fmtUptime(STATE.uptime);
  // reactor readouts flicker with state
  const intensity = stateIntensity();
  $("r-out").textContent = (3.14*intensity).toFixed(2)+" GJ/s";
  $("r-coh").textContent = (92+6*intensity).toFixed(1)+"%";
  $("r-temp").textContent = (380+40*intensity).toFixed(0)+" K";
  const statuses = {asleep:"LOW POWER",idle:"NOMINAL",listening:"ACTIVE",
    thinking:"PROCESSING",speaking:"TRANSMITTING",dictating:"RECORDING",
    dictation_processing:"TRANSCRIBING"};
  $("r-status").textContent = statuses[STATE.state]||"NOMINAL";
  $("c-signal").textContent = STATE.state==="asleep" ? "●○○○○" : "●●●●●";
  $("c-link").textContent = STATE.state==="asleep" ? "STANDBY" : "SECURE";
  $("c-link").style.color = STATE.color;
}

function stateIntensity(){
  return {asleep:0.25,idle:0.6,listening:0.85,thinking:0.95,
    speaking:1,dictating:0.9,dictation_processing:0.9}[STATE.state]||0.6;
}
function fmtUptime(s){
  s=Math.max(0,Math.floor(s));
  const d=Math.floor(s/86400); s%=86400;
  const h=Math.floor(s/3600); s%=3600; const mn=Math.floor(s/60);
  return (d?d+"d ":"")+String(h).padStart(2,"0")+"h "+String(mn).padStart(2,"0")+"m";
}

// ── HUD drawing ────────────────────────────────────────────────────────────
let t=0, bootDone=false;
const TAU = Math.PI*2;

function rgba(hex, a){
  // hex #rrggbb -> rgba()
  const r=parseInt(hex.slice(1,3),16), g=parseInt(hex.slice(3,5),16), b=parseInt(hex.slice(5,7),16);
  return `rgba(${r},${g},${b},${a})`;
}

function draw(){
  t += 0.016;
  ctx.clearRect(0,0,W,H);
  const R = Math.min(W,H)*0.30;       // base radius of the HUD
  const accent = STATE.color;

  drawOuterRing(R*2.55, accent);
  drawRadarSweep(R*1.7, accent);
  drawTickRing(R*1.55, accent);
  drawArcSegments(R*1.9, accent);
  drawArcSegments(R*2.2, accent, -1);
  drawWaveformRing(R*1.25, accent);
  drawCenterReactor(R*0.5, accent);
  drawCrosshair(R, accent);
  drawCornerBrackets(accent);

  if(!bootDone && t>1.4){
    bootDone=true; const b=$("boot"); b.classList.add("gone");
  }
  requestAnimationFrame(draw);
}

// Big dashed ring, slowly rotating, with degree tick marks.
function drawOuterRing(r, accent){
  ctx.save(); ctx.translate(CX,CY); ctx.rotate(t*0.06);
  ctx.strokeStyle=rgba(accent,.28); ctx.lineWidth=1.2;
  ctx.beginPath(); ctx.arc(0,0,r,0,TAU); ctx.stroke();
  ctx.setLineDash([4,10]); ctx.strokeStyle=rgba(accent,.5);
  ctx.beginPath(); ctx.arc(0,0,r-8,0,TAU); ctx.stroke(); ctx.setLineDash([]);
  // tick marks every 6°
  for(let i=0;i<60;i++){
    const a=i*6*Math.PI/180;
    const big = i%5===0;
    ctx.strokeStyle=rgba(accent, big?.7:.3);
    ctx.lineWidth=big?1.6:1;
    ctx.beginPath();
    ctx.moveTo(Math.cos(a)*(r-16), Math.sin(a)*(r-16));
    ctx.lineTo(Math.cos(a)*(r-(big?30:22)), Math.sin(a)*(r-(big?30:22)));
    ctx.stroke();
  }
  ctx.restore();
}

// Rotating radar sweep with a fading trail.
function drawRadarSweep(r, accent){
  ctx.save(); ctx.translate(CX,CY);
  const a0 = t*0.9;
  for(let i=0;i<26;i++){
    const a = a0 - i*0.05;
    ctx.strokeStyle=rgba(accent, 0.18*(1-i/26));
    ctx.lineWidth=2;
    ctx.beginPath(); ctx.moveTo(0,0);
    ctx.lineTo(Math.cos(a)*r, Math.sin(a)*r); ctx.stroke();
  }
  ctx.restore();
}

// Thin ring with fast-moving ticks + a moving "scanner" notch.
function drawTickRing(r, accent){
  ctx.save(); ctx.translate(CX,CY);
  ctx.strokeStyle=rgba(accent,.2); ctx.lineWidth=1;
  ctx.beginPath(); ctx.arc(0,0,r,0,TAU); ctx.stroke();
  const sweep = (t*1.4)%TAU;
  ctx.strokeStyle=rgba(accent,.9); ctx.lineWidth=2.4;
  ctx.beginPath(); ctx.arc(0,0,r, sweep, sweep+0.32); ctx.stroke();
  ctx.restore();
}

// Partial arc segments orbiting at different speeds.
function drawArcSegments(r, accent, dir=1){
  ctx.save(); ctx.translate(CX,CY); ctx.rotate(t*0.22*dir);
  const segs=8, gap=0.12;
  const step=TAU/segs;
  for(let i=0;i<segs;i++){
    const a=i*step;
    ctx.strokeStyle=rgba(accent, i%2? .6:.25);
    ctx.lineWidth=3;
    ctx.beginPath(); ctx.arc(0,0,r, a+gap, a+step-gap); ctx.stroke();
  }
  ctx.restore();
}

// Circular voice waveform around the reactor — amplitude reacts to state.
function drawWaveformRing(r, accent){
  ctx.save(); ctx.translate(CX,CY);
  const N=140, base=r, amp=r*0.10*stateIntensity();
  const speed = {speaking:3.2,thinking:1.8,listening:2.4,idle:0.9,asleep:0.3}[STATE.state]||1.2;
  ctx.beginPath();
  for(let i=0;i<=N;i++){
    const p=i/N*TAU;
    const noise =
      Math.sin(p*8 + t*speed*3)*0.5 +
      Math.sin(p*17 + t*speed*5)*0.3 +
      Math.sin(p*3 + t*speed*1.2)*0.4;
    const rad = base + noise*amp;
    const x=Math.cos(p)*rad, y=Math.sin(p)*rad;
    i?ctx.lineTo(x,y):ctx.moveTo(x,y);
  }
  ctx.closePath();
  ctx.strokeStyle=rgba(accent,.55); ctx.lineWidth=1.4; ctx.shadowColor=accent; ctx.shadowBlur=14;
  ctx.stroke(); ctx.shadowBlur=0;
  // inner echo ring
  ctx.strokeStyle=rgba(accent,.18); ctx.lineWidth=1;
  ctx.beginPath(); ctx.arc(0,0,base-amp-6,0,TAU); ctx.stroke();
  ctx.restore();
}

// The arc reactor core: layered radial glow + rotating triangle + hex.
function drawCenterReactor(r, accent){
  ctx.save(); ctx.translate(CX,CY);
  const pulse = 0.5 + 0.5*Math.sin(t*2.2);
  const intensity = stateIntensity();

  // outer glow halo
  const g = ctx.createRadialGradient(0,0,0,0,0,r*2.4);
  g.addColorStop(0, rgba(accent, 0.30*intensity+0.12));
  g.addColorStop(0.4, rgba(accent, 0.10));
  g.addColorStop(1, rgba(accent, 0));
  ctx.fillStyle=g; ctx.beginPath(); ctx.arc(0,0,r*2.4,0,TAU); ctx.fill();

  // concentric rings
  for(let i=4;i>=1;i--){
    ctx.strokeStyle=rgba(accent, 0.12+i*0.08);
    ctx.lineWidth=i*0.6;
    ctx.beginPath(); ctx.arc(0,0,r*(0.3+i*0.18),0,TAU); ctx.stroke();
  }

  // rotating triangular coil
  ctx.save(); ctx.rotate(t*0.5);
  ctx.strokeStyle=rgba(accent,.9); ctx.lineWidth=2;
  ctx.beginPath();
  for(let k=0;k<3;k++){
    const a=k*TAU/3;
    ctx.moveTo(Math.cos(a)*r*0.5, Math.sin(a)*r*0.5);
    ctx.lineTo(Math.cos(a+TAU/3)*r*0.5, Math.sin(a+TAU/3)*r*0.5);
  }
  ctx.stroke();
  ctx.restore();

  // counter-rotating hexagon
  ctx.save(); ctx.rotate(-t*0.8);
  ctx.strokeStyle=rgba(accent,.5); ctx.lineWidth=1.4;
  ctx.beginPath();
  for(let k=0;k<=6;k++){const a=k*TAU/6;const x=Math.cos(a)*r*0.78,y=Math.sin(a)*r*0.78;k?ctx.lineTo(x,y):ctx.moveTo(x,y);}
  ctx.closePath(); ctx.stroke();
  ctx.restore();

  // bright core
  const cg = ctx.createRadialGradient(0,0,0,0,0,r*0.45);
  cg.addColorStop(0,"rgba(255,255,255,"+(0.5+0.4*pulse)+")");
  cg.addColorStop(0.4, rgba(accent,0.9));
  cg.addColorStop(1, rgba(accent,0));
  ctx.fillStyle=cg; ctx.beginPath(); ctx.arc(0,0,r*0.45,0,TAU); ctx.fill();
  ctx.restore();
}

// Thin crosshair lines through the reactor.
function drawCrosshair(r, accent){
  ctx.save(); ctx.translate(CX,CY);
  ctx.strokeStyle=rgba(accent,.12); ctx.lineWidth=1;
  ctx.beginPath(); ctx.moveTo(-r*2.6,0); ctx.lineTo(-r*1.0,0);
  ctx.moveTo(r*1.0,0); ctx.lineTo(r*2.6,0);
  ctx.moveTo(0,-r*2.6); ctx.lineTo(0,-r*1.0);
  ctx.moveTo(0,r*1.0); ctx.lineTo(0,r*2.6); ctx.stroke();
  ctx.restore();
}

// Corner brackets framing the viewport.
function drawCornerBrackets(accent){
  const m=26, s=46; ctx.strokeStyle=rgba(accent,.6); ctx.lineWidth=2;
  const corners=[[m,m,1,1],[W-m,m,-1,1],[m,H-m,1,-1],[W-m,H-m,-1,-1]];
  ctx.beginPath();
  for(const [x,y,dx,dy] of corners){
    ctx.moveTo(x, y+dy*s); ctx.lineTo(x,y); ctx.lineTo(x+dx*s,y);
  }
  ctx.stroke();
}

// randomise ticker telemetry occasionally
setInterval(()=>{
  const pool=["J.A.R.V.I.S. ONLINE","ALL SYSTEMS NOMINAL","NEURAL LINK STABILIZED",
    "DEFENSE PROTOCOLS ACTIVE","AWAITING COMMAND","LOCAL SECURE NETWORK",
    "TELEMETRY STREAMING","REACTOR STABLE","GEOFENCE CLEAR"];
  const pick = Array.from({length:6},()=>pool[Math.floor(Math.random()*pool.length)]);
  $("ticker-text").textContent = pick.join(" · ") + " · ";
}, 9000);

draw();
</script>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """Run the HUD server."""
    import sys

    port = HUD_PORT
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass

    print("\n" + "=" * 60)
    print("◎ JARVIS HUD — heads-up display")
    print("=" * 60)
    print(f"\n  🌐 URL: http://localhost:{port}")
    print("  Press Ctrl+C to stop\n")
    print("=" * 60 + "\n")

    app.run(host="127.0.0.1", port=port, debug=False)


if __name__ == "__main__":
    main()
