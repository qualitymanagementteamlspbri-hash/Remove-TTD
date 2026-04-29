"""
================================================================================
  SIGNATURE BG REMOVER — Streamlit v4.0
  Fix: session_state stabil, PIL disimpan sebagai bytes, step machine benar
================================================================================
  pip install streamlit opencv-python-headless pillow numpy
  streamlit run app.py
================================================================================
"""

import io, cv2, zipfile, time
import numpy as np
import streamlit as st
from PIL import Image
from pathlib import Path

# ══════════════════════════════════════════════════════════════════════════════
#  1. PAGE CONFIG  (harus paling atas)
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Signature BG Remover",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
#  2. SESSION STATE INIT
#     Semua key didefinisikan DI SINI agar tidak hilang saat rerun.
#     PENTING: PIL Image TIDAK disimpan — hanya bytes.
# ══════════════════════════════════════════════════════════════════════════════
_DEFAULTS: dict = {
    "batch_step":    1,    # 1=upload 2=proses 3=review 4=download
    "batch_raw":     {},   # {fname: bytes}
    "batch_results": {},   # {fname: {"status","mode","png_bytes","message"}}
    "review_status": {},   # {fname: "keep"/"exclude"/"auto_skip"}
    "single_result": None,
    "single_fname":  "",
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ══════════════════════════════════════════════════════════════════════════════
#  3. CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif}
.stApp{background:#0d0d1a}

.hdr{background:linear-gradient(135deg,#13132a,#1c1c3a);
     border:1px solid rgba(139,92,246,.25);border-radius:16px;
     padding:26px 34px;margin-bottom:22px}
.hdr-title{font-size:1.75rem;font-weight:700;color:#fff;margin:0 0 4px;letter-spacing:-.5px}
.hdr-sub{font-size:.88rem;color:#a78bfa;margin:0 0 14px}
.badges{display:flex;gap:7px;flex-wrap:wrap}
.badge{background:rgba(139,92,246,.1);border:1px solid rgba(139,92,246,.22);
       color:#c4b5fd;padding:3px 11px;border-radius:100px;font-size:.7rem;font-weight:600}

.card{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);
      border-radius:13px;padding:18px;margin-bottom:13px}
.card-lbl{font-size:.7rem;font-weight:700;color:#a78bfa;text-transform:uppercase;
          letter-spacing:1.2px;margin-bottom:12px}

.srow{display:flex;gap:9px;margin:10px 0}
.sbox{flex:1;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07);
      border-radius:9px;padding:11px;text-align:center}
.snum{font-size:1.6rem;font-weight:700;font-family:'JetBrains Mono',monospace;line-height:1}
.slbl{font-size:.65rem;color:#6b7280;text-transform:uppercase;letter-spacing:.5px;
      margin-top:3px;font-weight:600}
.cg{color:#34d399}.ca{color:#fbbf24}.cgr{color:#9ca3af}.cr{color:#f87171}.cp{color:#a78bfa}

.mp{display:inline-block;padding:2px 9px;border-radius:100px;font-size:.67rem;
    font-weight:700;text-transform:uppercase;letter-spacing:.4px}
.mw{background:rgba(241,245,249,.1);color:#e2e8f0;border:1px solid rgba(226,232,240,.18)}
.md{background:rgba(168,85,247,.1);color:#c084fc;border:1px solid rgba(192,132,252,.18)}
.mc{background:rgba(251,191,36,.1);color:#fbbf24;border:1px solid rgba(251,191,36,.18)}
.mx{background:rgba(52,211,153,.1);color:#34d399;border:1px solid rgba(52,211,153,.18)}
.ms{background:rgba(107,114,128,.1);color:#9ca3af;border:1px solid rgba(107,114,128,.18)}

.info{border-radius:0 7px 7px 0;padding:9px 13px;font-size:.81rem;margin:9px 0;line-height:1.5}
.ib{background:rgba(96,165,250,.07);border-left:3px solid #60a5fa;color:#93c5fd}
.ig{background:rgba(52,211,153,.07);border-left:3px solid #34d399;color:#6ee7b7}
.iy{background:rgba(251,191,36,.07);border-left:3px solid #fbbf24;color:#fde68a}
.ie{background:rgba(248,113,113,.07);border-left:3px solid #f87171;color:#fca5a5}

.ilbl{text-align:center;font-size:.66rem;font-weight:700;text-transform:uppercase;
      letter-spacing:.8px;color:#6b7280;margin-top:5px}

.step-bar{display:flex;gap:0;margin-bottom:20px}
.step-i{flex:1;text-align:center;position:relative}
.step-i::after{content:'';position:absolute;top:17px;left:55%;width:90%;
               height:1px;background:rgba(255,255,255,.07)}
.step-i:last-child::after{display:none}
.step-c{width:34px;height:34px;border-radius:50%;
        background:rgba(139,92,246,.08);border:1.5px solid rgba(139,92,246,.2);
        margin:0 auto 5px;display:flex;align-items:center;justify-content:center;
        font-size:.88rem;position:relative;z-index:1}
.step-c.on{background:rgba(139,92,246,.22);border-color:#8b5cf6;
            box-shadow:0 0 14px rgba(139,92,246,.28)}
.step-c.done{background:rgba(52,211,153,.15);border-color:#34d399}
.step-l{font-size:.62rem;color:#6b7280;font-weight:600;text-transform:uppercase;letter-spacing:.4px}
.step-l.on{color:#c4b5fd}

[data-testid="stSidebar"]{background:rgba(9,9,20,.97);
                           border-right:1px solid rgba(255,255,255,.05)}
.stTabs [data-baseweb="tab-list"]{gap:3px;background:rgba(255,255,255,.02);
  padding:4px;border-radius:9px;border:1px solid rgba(255,255,255,.05)}
.stTabs [data-baseweb="tab"]{border-radius:6px;font-weight:600;font-size:.83rem}
.stDownloadButton>button{background:linear-gradient(135deg,#7c3aed,#5b21b6)!important;
  border:none!important;color:#fff!important;border-radius:9px!important;font-weight:700!important}
hr.s{border:none;border-top:1px solid rgba(255,255,255,.06);margin:18px 0}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  4. IMAGE PROCESSING ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def _sample_bg(img_bgr, px=10):
    h, w = img_bgr.shape[:2]
    b = min(px, h//4, w//4)
    segs = [img_bgr[:b,:], img_bgr[h-b:,:], img_bgr[:,:b], img_bgr[:,w-b:]]
    return np.median(np.vstack([s.reshape(-1,3) for s in segs]), axis=0)

def _gblur(img, k):
    if k <= 1: return img
    k = k if k%2==1 else k+1
    return cv2.GaussianBlur(img, (k,k), 0)

def _morph(mask, tight=False):
    k1 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2,2))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  k1)
    k2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2,2) if tight else (3,3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k2)
    if not tight:
        k3 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2,2))
        mask = cv2.dilate(mask, k3, iterations=1)
    return mask

def _trim_alpha(arr, min_a):
    r = arr.copy(); r[r[:,:,3] < min_a, 3] = 0; return r

def _has_lines(img_bgr):
    gray  = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    w     = gray.shape[1]
    edges = cv2.Canny(gray, 30, 100)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 80,
                             minLineLength=int(w*.4), maxLineGap=15)
    if lines is None: return False
    cnt = sum(1 for l in lines
              if abs(np.degrees(np.arctan2(
                  l[0][3]-l[0][1], l[0][2]-l[0][0])))%180 < 5)
    return cnt >= 3

def _del_lines(img_bgr, mask):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY); w = gray.shape[1]
    comb = np.zeros_like(mask)
    for t in range(1, 5):
        kk = cv2.getStructuringElement(cv2.MORPH_RECT,(max(int(w*.5),50),t))
        lm = cv2.morphologyEx(cv2.bitwise_not(gray), cv2.MORPH_OPEN, kk)
        _, lb = cv2.threshold(lm, 30, 255, cv2.THRESH_BINARY)
        comb = cv2.bitwise_or(comb, lb)
    dk = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    comb = cv2.dilate(comb, dk, iterations=1)
    out = mask.copy(); out[comb>0] = 0; return out

def _color_mask(img_bgr, bg, tol, blur_k):
    lab  = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    bgp  = bg.astype(np.uint8).reshape(1,1,3)
    bgl  = cv2.cvtColor(bgp, cv2.COLOR_BGR2LAB).astype(np.float32).reshape(3)
    dist = np.sqrt(np.sum((lab - bgl)**2, axis=2))
    dist = _gblur(dist, blur_k)
    return np.where(dist < tol, 0, 255).astype(np.uint8)

# ── 4 mode mask ──────────────────────────────────────────────────────────────

def mk_white(img_bgr, thr, blur_k):
    g = _gblur(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY), blur_k)
    _, m = cv2.threshold(g, thr, 255, cv2.THRESH_BINARY_INV)
    return m

def mk_dark(img_bgr, thr, blur_k):
    """Logika TERBALIK: piksel gelap dihapus, tanda tangan terang dipertahankan."""
    g = _gblur(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY), blur_k)
    _, m = cv2.threshold(g, thr, 255, cv2.THRESH_BINARY)
    return m

def mk_color(img_bgr, tol, blur_k):
    bg = _sample_bg(img_bgr)
    return _color_mask(img_bgr, bg, tol, blur_k)

def mk_complex(img_bgr, tol, thr, blur_k):
    gray  = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    blur  = _gblur(gray, max(blur_k, 3))
    adapt = cv2.adaptiveThreshold(blur, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 8)
    _, gm = cv2.threshold(blur, thr, 255, cv2.THRESH_BINARY_INV)
    bg    = _sample_bg(img_bgr)
    cm    = _color_mask(img_bgr, bg, tol, blur_k)
    comb  = cv2.bitwise_and(adapt, cm)
    extra = cv2.bitwise_and(gm, cv2.bitwise_not(
                np.where(cm==0,255,0).astype(np.uint8)))
    comb  = cv2.bitwise_or(comb, extra)
    comb  = _del_lines(img_bgr, comb)
    ko    = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    return cv2.morphologyEx(comb, cv2.MORPH_OPEN, ko)

def auto_detect(img_bgr) -> str:
    bg  = _sample_bg(img_bgr)
    avg = float(np.mean(bg))
    if avg < 55:            return "dark"
    if np.all(bg > 205):    return "white"
    if _has_lines(img_bgr): return "complex"
    return "color"

def is_transparent(raw: bytes) -> bool:
    arr = np.frombuffer(raw, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
    if img is None or img.ndim < 3 or img.shape[2] != 4: return False
    return float(np.sum(img[:,:,3] < 128)) / img[:,:,3].size > 0.08

# ── Helper PIL ────────────────────────────────────────────────────────────────

def pil_to_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO(); img.save(buf, "PNG"); return buf.getvalue()

def bytes_to_pil(b: bytes) -> Image.Image:
    return Image.open(io.BytesIO(b)).convert("RGBA")

def composite(rgba: Image.Image, bg=(255,255,255)) -> Image.Image:
    base = Image.new("RGBA", rgba.size, (*bg, 255))
    return Image.alpha_composite(base, rgba).convert("RGB")

def checker_preview(rgba: Image.Image) -> Image.Image:
    w, h = rgba.size; tile = 18
    arr  = np.ones((h,w,3), np.uint8) * 215
    for y in range(0,h,tile):
        for x in range(0,w,tile):
            if (x//tile + y//tile) % 2 == 0:
                arr[y:y+tile, x:x+tile] = 240
    bg = Image.fromarray(arr,"RGB").convert("RGBA")
    return Image.alpha_composite(bg, rgba).convert("RGB")

# ── Fungsi proses utama ───────────────────────────────────────────────────────

def process_one(raw: bytes, mode: str, w_thr: int, d_thr: int,
                tol: float, blur_k: int, min_a: int,
                skip_transp: bool) -> dict:
    """
    Returns dict:
      status    : "ok" | "skipped" | "error"
      mode      : mode yang dipakai
      png_bytes : bytes PNG RGBA  (hanya jika status=="ok")
      message   : pesan error/skip
    """
    if skip_transp and is_transparent(raw):
        return {"status":"skipped","mode":"skip",
                "message":"PNG sudah transparan, dilewati"}

    arr = np.frombuffer(raw, np.uint8)
    bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if bgr is None:
        return {"status":"error","mode":"?","message":"Tidak dapat membaca file"}

    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

    try:
        det = auto_detect(bgr) if mode == "auto" else mode

        if   det == "white":   mask = mk_white(bgr, w_thr, blur_k);  tight = False
        elif det == "dark":    mask = mk_dark(bgr, d_thr, blur_k);   tight = True
        elif det == "color":   mask = mk_color(bgr, tol, blur_k);    tight = False
        elif det == "complex": mask = mk_complex(bgr, tol, w_thr, blur_k); tight = False
        else:
            return {"status":"error","mode":mode,
                    "message":f"Mode tidak dikenal: {mode}"}

        mask = _morph(mask, tight)
        rgba = np.dstack([rgb, mask])
        if min_a > 0:
            rgba = _trim_alpha(rgba, min_a)

        png_b = pil_to_bytes(Image.fromarray(rgba, "RGBA"))
        return {"status":"ok","mode":det,"png_bytes":png_b}

    except Exception as e:
        return {"status":"error","mode":mode,"message":str(e)}


# ══════════════════════════════════════════════════════════════════════════════
#  5. SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:16px 0 4px'>
      <div style='font-size:2rem'>✍️</div>
      <div style='font-weight:700;font-size:.9rem;color:#e2e8f0;margin-top:3px'>BG Remover</div>
      <div style='font-size:.62rem;color:#4b5563;text-transform:uppercase;
           letter-spacing:1px;font-weight:600'>v4.0</div>
    </div>
    <hr style='border-color:rgba(255,255,255,.05);margin:10px 0'>
    """, unsafe_allow_html=True)

    st.markdown("### 🤖 Mode")
    _MODES = {
        "🤖 Auto-Detect":         "auto",
        "📄 Kertas Putih / HVS":  "white",
        "🖤 Background Hitam":    "dark",
        "🎨 Kertas Berwarna":     "color",
        "📋 Background Kompleks": "complex",
    }
    MODE = _MODES[st.selectbox("Mode", list(_MODES.keys()),
                               label_visibility="collapsed")]

    st.markdown("""<div style='font-size:.71rem;color:#6b7280;padding:7px 10px;
    background:rgba(255,255,255,.03);border-radius:7px;line-height:1.6;margin-bottom:8px'>
    <b style='color:#9ca3af'>Kompleks</b> = kertas bekas · bergaris · watermark · bayangan logo
    </div>""", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(255,255,255,.05)'>", unsafe_allow_html=True)
    st.markdown("### ⚙️ Parameter")

    ca, cb = st.columns(2)
    W_THR = ca.number_input("Threshold Putih", 100, 250, 200, 5,
        help="Naik → hapus lebih agresif (bg putih). Turun → lebih aman.")
    D_THR = cb.number_input("Threshold Gelap", 20, 150, 55, 5,
        help="Untuk bg hitam. Turun → TTD tipis/biru aman. Naik → lebih bersih.")

    TOLERANCE = st.slider("Toleransi Warna", 10, 80, 38, 2,
        help="Untuk bg berwarna & kompleks.")

    cc, cd = st.columns(2)
    BLUR_K    = cc.select_slider("Blur", [1,3,5,7], 3)
    MIN_ALPHA = cd.number_input("Min Alpha", 0, 40, 10, 1)

    SKIP_TRANSP = st.toggle("⚡ Skip PNG Transparan", True,
        help="PNG yang sudah transparan dilewati, tidak diproses ulang.")

    st.markdown("<hr style='border-color:rgba(255,255,255,.05)'>", unsafe_allow_html=True)
    st.markdown("""### 💡 Tips
<div style='font-size:.72rem;color:#6b7280;line-height:1.85'>
<b style='color:#a78bfa'>TTD hilang?</b><br>Turunkan threshold / toleransi<br><br>
<b style='color:#fbbf24'>BG tersisa?</b><br>Naikkan threshold / toleransi<br><br>
<b style='color:#34d399'>Tinta biru di kertas berwarna?</b><br>Toleransi ↓ 22–30 + Min Alpha = 0<br><br>
<b style='color:#c084fc'>PNG bg hitam + tinta biru?</b><br>Mode Bg Hitam, Dark Threshold 45–55
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  6. HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hdr">
  <div class="hdr-title">✍️ Signature Background Remover</div>
  <div class="hdr-sub">Hapus background tanda tangan — putih · hitam · berwarna · bergaris · watermark</div>
  <div class="badges">
    <span class="badge">📄 Kertas Putih</span><span class="badge">🖤 BG Hitam</span>
    <span class="badge">🎨 Berwarna</span><span class="badge">📋 Kompleks</span>
    <span class="badge">⚡ Skip Transparan</span><span class="badge">🔍 Review + Download</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  7. TABS
# ══════════════════════════════════════════════════════════════════════════════
TAB_SINGLE, TAB_BATCH, TAB_GUIDE = st.tabs([
    "🔍  Uji Satu File",
    "⚡  Batch + Review + Download",
    "📖  Panduan",
])

# ─── Lookup tables (digunakan di beberapa tempat) ────────────────────────────
_MCSS = {"white":"mw","dark":"md","color":"mc","complex":"mx","skip":"ms","?":"ms"}
_MLBL = {"white":"Putih","dark":"Bg Hitam","color":"Berwarna",
         "complex":"Kompleks","skip":"Skip","?":"Error"}


# ─────────────────────────────────────────────────────────────────────────────
#  TAB 1 — UJI SATU FILE
# ─────────────────────────────────────────────────────────────────────────────
with TAB_SINGLE:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""<div class='info ib'>
    💡 Upload satu file untuk uji parameter sebelum proses batch ratusan file.
    </div>""", unsafe_allow_html=True)

    up = st.file_uploader("Upload file tanda tangan",
                          type=["jpg","jpeg","png"], key="up_single")

    if up:
        raw = up.read()
        arr = np.frombuffer(raw, np.uint8)
        bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        h_px, w_px = bgr.shape[:2]

        bg_col  = _sample_bg(bgr)
        bg_rgb  = bg_col[::-1].astype(int)
        det     = auto_detect(bgr)
        transp  = is_transparent(raw)
        has_ln  = _has_lines(bgr)

        st.markdown(f"""<div class='card'>
        <div class='card-lbl'>📊 Analisis Otomatis</div>
        <div style='display:grid;grid-template-columns:repeat(5,1fr);gap:9px'>
          <div class='sbox'><div class='snum cp' style='font-size:.9rem'>{w_px}×{h_px}</div>
            <div class='slbl'>Resolusi</div></div>
          <div class='sbox'>
            <div style='width:22px;height:22px;border-radius:5px;margin:0 auto 3px;
                 background:rgb({bg_rgb[0]},{bg_rgb[1]},{bg_rgb[2]});
                 border:1px solid rgba(255,255,255,.15)'></div>
            <div class='slbl'>Warna BG</div></div>
          <div class='sbox'><div class='snum' style='font-size:.88rem;
               color:{"#34d399" if has_ln else "#6b7280"}'>
               {"Ada ✓" if has_ln else "Tidak"}</div>
            <div class='slbl'>Garis</div></div>
          <div class='sbox'><div class='snum' style='font-size:.88rem;
               color:{"#34d399" if transp else "#6b7280"}'>
               {"Ya ✓" if transp else "Tidak"}</div>
            <div class='slbl'>Transparan</div></div>
          <div class='sbox'>
            <span class='mp {_MCSS.get(det,"mw")}' style='font-size:.72rem'>
              {_MLBL.get(det,det)}</span>
            <div class='slbl' style='margin-top:5px'>Auto-Detect</div></div>
        </div></div>""", unsafe_allow_html=True)

        if transp and SKIP_TRANSP:
            st.markdown("""<div class='info iy'>
            ⚡ File ini sudah transparan → akan di-skip di batch.
            Matikan "Skip PNG Transparan" di sidebar untuk tetap diproses.
            </div>""", unsafe_allow_html=True)

        if st.button("🚀 Proses Sekarang", type="primary", use_container_width=True):
            with st.spinner("Memproses..."):
                res = process_one(raw, MODE, W_THR, D_THR,
                                  TOLERANCE, BLUR_K, MIN_ALPHA, SKIP_TRANSP)
            st.session_state["single_result"] = res
            st.session_state["single_fname"]  = Path(up.name).stem
            # TIDAK rerun — langsung tampilkan di bawah

        # Render hasil dari session_state
        res   = st.session_state.get("single_result")
        fname = st.session_state.get("single_fname","hasil")

        if res:
            if res["status"] == "skipped":
                st.markdown(f"<div class='info iy'>⚡ {res['message']}</div>",
                            unsafe_allow_html=True)
            elif res["status"] == "error":
                st.markdown(f"<div class='info ie'>❌ {res['message']}</div>",
                            unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class='info ig'>
                ✅ Berhasil — Mode: <span class='mp {_MCSS.get(res["mode"],"mw")}'>
                {_MLBL.get(res["mode"],res["mode"])}</span></div>""",
                unsafe_allow_html=True)

                rgba = bytes_to_pil(res["png_bytes"])

                st.markdown("#### Perbandingan Hasil")
                c1,c2,c3,c4 = st.columns(4)
                c1.image(Image.fromarray(rgb), use_container_width=True)
                c1.markdown('<div class="ilbl">Original</div>',unsafe_allow_html=True)
                c2.image(checker_preview(rgba), use_container_width=True)
                c2.markdown('<div class="ilbl">Transparan</div>',unsafe_allow_html=True)
                c3.image(composite(rgba,(255,255,255)), use_container_width=True)
                c3.markdown('<div class="ilbl">BG Putih</div>',unsafe_allow_html=True)
                c4.image(composite(rgba,(28,28,28)), use_container_width=True)
                c4.markdown('<div class="ilbl">BG Gelap</div>',unsafe_allow_html=True)

                with st.expander("🎭 Alpha Mask"):
                    am = np.array(rgba)[:,:,3]
                    st.image(Image.fromarray(am,"L"), use_container_width=True,
                             caption="Putih=TTD · Hitam=transparan")

                st.download_button(
                    f"⬇️ Download {fname}.png",
                    data=res["png_bytes"],
                    file_name=f"{fname}.png",
                    mime="image/png",
                    use_container_width=True,
                )

                st.markdown("<hr class='s'>", unsafe_allow_html=True)
                m = res["mode"]
                if m == "dark":
                    a,b_ = st.columns(2)
                    a.info(f"BG hitam masih tersisa → Threshold Gelap ↑ (coba {D_THR+10})")
                    b_.info(f"TTD hilang → Threshold Gelap ↓ (coba {max(20,D_THR-10)})")
                elif m in ("color","complex"):
                    a,b_ = st.columns(2)
                    a.info(f"BG masih ada → Toleransi ↑ (coba {min(80,int(TOLERANCE)+8)})")
                    b_.info(f"TTD terkena → Toleransi ↓ (coba {max(10,int(TOLERANCE)-8)})")
                else:
                    a,b_ = st.columns(2)
                    a.info(f"BG masih ada → Threshold Putih ↑ (coba {min(250,W_THR+10)})")
                    b_.info(f"TTD hilang → Threshold Putih ↓ (coba {max(100,W_THR-10)})")
    else:
        # reset result lama jika upload baru kosong
        st.session_state["single_result"] = None
        st.markdown("""<div style='text-align:center;padding:55px 0;color:#374151'>
        <div style='font-size:3rem;margin-bottom:10px'>📁</div>
        <div style='font-size:.9rem;font-weight:600;color:#6b7280'>Upload file di atas</div>
        <div style='font-size:.78rem;margin-top:5px;color:#4b5563'>JPG · JPEG · PNG</div>
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  TAB 2 — BATCH + REVIEW + DOWNLOAD
# ─────────────────────────────────────────────────────────────────────────────
with TAB_BATCH:
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Step indicator ───────────────────────────────────────────────────────
    cur  = st.session_state["batch_step"]
    _STP = [(1,"📤","Upload"),(2,"⚡","Proses"),(3,"🔍","Review"),(4,"⬇️","Download")]
    bar  = '<div class="step-bar">'
    for n,ico,lbl in _STP:
        cc_ = "on" if n==cur else ("done" if n<cur else "")
        cl_ = "on" if n==cur else ""
        bar += (f'<div class="step-i"><div class="step-c {cc_}">{ico}</div>'
                f'<div class="step-l {cl_}">{lbl}</div></div>')
    bar += '</div>'
    st.markdown(bar, unsafe_allow_html=True)

    # ════════════════════════════════════
    #  STEP 1 — UPLOAD
    # ════════════════════════════════════
    if cur == 1:
        utype = st.radio("Metode upload:",
                         ["📂 Pilih Banyak File","🗜️ Upload File ZIP"],
                         horizontal=True)

        if utype == "📂 Pilih Banyak File":
            ups = st.file_uploader(
                "Upload semua file tanda tangan (bisa pilih banyak sekaligus)",
                type=["jpg","jpeg","png"], accept_multiple_files=True,
                key="up_batch")
            if ups:
                fd = {f.name: f.read() for f in ups}
                st.markdown(f"<div class='info ig'>✅ {len(fd)} file siap</div>",
                            unsafe_allow_html=True)
                if st.button("Lanjut ke Proses ▶", type="primary",
                             use_container_width=True):
                    st.session_state["batch_raw"]  = fd
                    st.session_state["batch_step"] = 2
                    st.rerun()
        else:
            zup = st.file_uploader("Upload file ZIP", type=["zip"], key="up_zip")
            if zup:
                fd = {}
                with zipfile.ZipFile(io.BytesIO(zup.read()),"r") as zf:
                    for name in zf.namelist():
                        if (Path(name).suffix.lower() in {".jpg",".jpeg",".png"}
                                and not name.startswith("__MACOSX")):
                            fd[Path(name).name] = zf.read(name)
                if fd:
                    st.markdown(f"<div class='info ig'>✅ {len(fd)} file ditemukan</div>",
                                unsafe_allow_html=True)
                    if st.button("Lanjut ke Proses ▶", type="primary",
                                 use_container_width=True):
                        st.session_state["batch_raw"]  = fd
                        st.session_state["batch_step"] = 2
                        st.rerun()
                else:
                    st.markdown("<div class='info ie'>❌ Tidak ada JPG/PNG di ZIP</div>",
                                unsafe_allow_html=True)

    # ════════════════════════════════════
    #  STEP 2 — PROSES
    # ════════════════════════════════════
    elif cur == 2:
        fd    = st.session_state["batch_raw"]
        total = len(fd)

        if not fd:
            st.warning("Tidak ada file. Kembali ke Upload.")
            if st.button("← Upload Ulang", key="back_to1"):
                st.session_state["batch_step"] = 1
                st.rerun()
        else:
            _ML2 = {"white":"Putih","dark":"Bg Hitam","color":"Berwarna",
                    "complex":"Kompleks","auto":"Auto"}
            st.markdown(f"""<div class='card'>
            <div class='card-lbl'>📦 Siap Diproses</div>
            <div class='srow'>
              <div class='sbox'><div class='snum cp'>{total}</div>
                <div class='slbl'>Total File</div></div>
              <div class='sbox'><div class='snum' style='font-size:.85rem;color:#a78bfa'>
                {_ML2.get(MODE,MODE)}</div><div class='slbl'>Mode</div></div>
              <div class='sbox'><div class='snum' style='font-size:.85rem;color:#9ca3af'>
                {"Ya" if SKIP_TRANSP else "Tidak"}</div>
                <div class='slbl'>Skip Transparan</div></div>
            </div></div>""", unsafe_allow_html=True)

            bk_col, go_col = st.columns([1,3])
            with bk_col:
                if st.button("← Upload", use_container_width=True, key="back2_1"):
                    st.session_state["batch_step"] = 1
                    st.rerun()
            with go_col:
                run = st.button(f"⚡ Mulai Proses {total} File",
                                type="primary", use_container_width=True,
                                key="btn_run")

            if run:
                results: dict = {}
                pb = st.progress(0, text="Memulai...")
                t0 = time.time()

                for i, (fn, raw_b) in enumerate(fd.items()):
                    elapsed = time.time() - t0
                    eta     = (elapsed/max(i,1))*(total-i) if i > 0 else 0
                    pb.progress(int(i/total*100),
                                text=f"⏳ {i+1}/{total} — {fn} — ETA {int(eta)}s")
                    results[fn] = process_one(raw_b, MODE, W_THR, D_THR,
                                              TOLERANCE, BLUR_K, MIN_ALPHA, SKIP_TRANSP)

                pb.progress(100, text="✅ Selesai!")
                elapsed_total = time.time() - t0

                ok_n   = sum(1 for r in results.values() if r["status"]=="ok")
                skip_n = sum(1 for r in results.values() if r["status"]=="skipped")
                err_n  = sum(1 for r in results.values() if r["status"]=="error")

                st.markdown(f"""<div class='card'>
                <div class='card-lbl'>✅ Selesai — {elapsed_total:.1f} detik</div>
                <div class='srow'>
                  <div class='sbox'><div class='snum cg'>{ok_n}</div>
                    <div class='slbl'>Berhasil</div></div>
                  <div class='sbox'><div class='snum cgr'>{skip_n}</div>
                    <div class='slbl'>Di-Skip</div></div>
                  <div class='sbox'><div class='snum cr'>{err_n}</div>
                    <div class='slbl'>Error</div></div>
                  <div class='sbox'><div class='snum cp'>
                    {elapsed_total/max(total,1):.1f}s</div>
                    <div class='slbl'>Per File</div></div>
                </div></div>""", unsafe_allow_html=True)

                if MODE == "auto":
                    mc: dict = {}
                    for r in results.values():
                        if r["status"]=="ok":
                            mc[r["mode"]] = mc.get(r["mode"],0)+1
                    if mc:
                        _N = {"white":"Putih","dark":"Bg Hitam",
                              "color":"Berwarna","complex":"Kompleks"}
                        cols_m = st.columns(len(mc))
                        for ci,(m,cnt) in enumerate(mc.items()):
                            cols_m[ci].metric(_N.get(m,m), f"{cnt} file")

                # ── Simpan ke session_state ──────────────────────────────────
                # KUNCI: simpan png_bytes (bukan PIL), dan langsung set step=3
                rev: dict = {}
                for fn_, r_ in results.items():
                    rev[fn_] = "keep" if r_["status"]=="ok" else "auto_skip"

                st.session_state["batch_results"] = results
                st.session_state["review_status"] = rev
                st.session_state["batch_step"]    = 3   # <── langsung ke Review
                st.rerun()

    # ════════════════════════════════════
    #  STEP 3 — REVIEW
    # ════════════════════════════════════
    elif cur == 3:
        results       = st.session_state.get("batch_results", {})
        fd            = st.session_state.get("batch_raw", {})
        review_status = st.session_state.get("review_status", {})

        if not results:
            st.markdown("<div class='info iy'>Tidak ada hasil. Proses dulu.</div>",
                        unsafe_allow_html=True)
            if st.button("← Proses", key="back3_2"):
                st.session_state["batch_step"] = 2
                st.rerun()
        else:
            ok_list    = [fn for fn,r in results.items() if r["status"]=="ok"]
            skip_list  = [fn for fn,r in results.items() if r["status"]=="skipped"]
            err_list   = [fn for fn,r in results.items() if r["status"]=="error"]
            kept_n_now = sum(1 for fn in ok_list if review_status.get(fn)=="keep")
            excl_n_now = sum(1 for fn in ok_list if review_status.get(fn)=="exclude")

            # ── Summary ──
            st.markdown(f"""<div class='card'>
            <div class='card-lbl'>🔍 Review — Pilih File yang Akan Didownload</div>
            <div class='srow'>
              <div class='sbox'><div class='snum cg'>{kept_n_now}</div>
                <div class='slbl'>Akan Download</div></div>
              <div class='sbox'><div class='snum ca'>{len(ok_list)}</div>
                <div class='slbl'>Total Berhasil</div></div>
              <div class='sbox'><div class='snum cr'>{excl_n_now}</div>
                <div class='slbl'>Dikecualikan</div></div>
              <div class='sbox'><div class='snum cgr'>{len(skip_list)}</div>
                <div class='slbl'>Di-Skip</div></div>
            </div></div>""", unsafe_allow_html=True)

            # ── Bulk actions ──
            rb1,rb2,rb3,rb4 = st.columns(4)
            if rb1.button("✅ Pilih Semua", use_container_width=True, key="r_all"):
                for fn in ok_list: review_status[fn] = "keep"
                st.session_state["review_status"] = review_status
                st.rerun()
            if rb2.button("🚫 Batalkan Semua", use_container_width=True, key="r_none"):
                for fn in ok_list: review_status[fn] = "exclude"
                st.session_state["review_status"] = review_status
                st.rerun()
            if rb3.button("← Proses Ulang Semua", use_container_width=True, key="r_back"):
                st.session_state["batch_step"] = 2
                st.rerun()
            if rb4.button("Lanjut ke Download ▶", type="primary",
                          use_container_width=True, key="r_next"):
                st.session_state["batch_step"] = 4
                st.rerun()

            st.markdown("<hr class='s'>", unsafe_allow_html=True)

            # ── Filter ──
            flt = st.radio("Tampilkan:",
                           ["✅ Semua Berhasil","🚫 Hanya Dikecualikan"],
                           horizontal=True, key="r_filter")

            # ── Gallery ──
            for fname in sorted(ok_list):
                rs   = review_status.get(fname,"keep")
                kept = rs == "keep"

                if flt == "✅ Semua Berhasil" and not kept: continue
                if flt == "🚫 Hanya Dikecualikan" and kept: continue

                r        = results[fname]
                mode_str = r["mode"]
                png_b    = r.get("png_bytes", b"")
                bc       = "rgba(52,211,153,.4)" if kept else "rgba(107,114,128,.25)"
                op       = "1" if kept else ".55"
                ic_      = "✅" if kept else "🚫"

                # Wrapper div
                st.markdown(
                    f"<div style='border:1px solid {bc};border-radius:12px;"
                    f"padding:4px 10px 0;margin-bottom:10px;"
                    f"background:rgba(255,255,255,.02);opacity:{op}'>",
                    unsafe_allow_html=True)

                # File header
                _mcls = _MCSS.get(mode_str, "mw")
                _mlb  = _MLBL.get(mode_str, mode_str)
                st.markdown(
                    f"<div style='padding:5px 0 3px;font-size:.7rem;color:#9ca3af;"
                    f"font-weight:600'>{ic_} <b style='color:#e2e8f0'>{fname}</b>"
                    f"&nbsp;<span class='mp {_mcls}'>{_mlb}</span></div>",
                    unsafe_allow_html=True)

                # Images + actions
                cp_, cd_, ca_ = st.columns([2,2,2])

                rgba_img = bytes_to_pil(png_b) if png_b else None

                with cp_:
                    if rgba_img:
                        st.image(checker_preview(rgba_img),
                                 use_container_width=True, caption="Transparan")
                with cd_:
                    if rgba_img:
                        st.image(composite(rgba_img,(28,28,28)),
                                 use_container_width=True, caption="BG Gelap")
                with ca_:
                    # Toggle include/exclude
                    if kept:
                        if st.button("🚫 Keluarkan", key=f"ex_{fname}",
                                     use_container_width=True):
                            review_status[fname] = "exclude"
                            st.session_state["review_status"] = review_status
                            st.rerun()
                    else:
                        if st.button("✅ Masukkan", key=f"kp_{fname}",
                                     use_container_width=True):
                            review_status[fname] = "keep"
                            st.session_state["review_status"] = review_status
                            st.rerun()

                    # Download satu file
                    if png_b:
                        st.download_button(
                            "⬇️ Download",
                            data=png_b,
                            file_name=Path(fname).stem+".png",
                            mime="image/png",
                            key=f"dl1_{fname}",
                            use_container_width=True,
                        )

                    # Proses ulang
                    with st.expander("🔄 Proses Ulang"):
                        rp_mode = st.selectbox(
                            "Mode", ["auto","white","dark","color","complex"],
                            key=f"rpm_{fname}")
                        rp_wt = st.slider("Threshold Putih",100,250,W_THR,5,
                                          key=f"rpt_{fname}")
                        rp_dt = st.slider("Threshold Gelap",20,150,D_THR,5,
                                          key=f"rpd_{fname}")
                        rp_tl = st.slider("Toleransi",10,80,int(TOLERANCE),2,
                                          key=f"rpc_{fname}")
                        rp_bl = st.select_slider("Blur",[1,3,5,7],BLUR_K,
                                                  key=f"rpb_{fname}")
                        rp_al = st.slider("Min Alpha",0,40,MIN_ALPHA,1,
                                          key=f"rpa_{fname}")
                        if st.button("🚀 Terapkan", key=f"rpr_{fname}",
                                     use_container_width=True):
                            raw_b = fd.get(fname, b"")
                            if raw_b:
                                nr = process_one(raw_b, rp_mode, rp_wt, rp_dt,
                                                 float(rp_tl), rp_bl, rp_al, False)
                                results[fname] = nr
                                review_status[fname] = "keep" if nr["status"]=="ok" else "exclude"
                                st.session_state["batch_results"] = results
                                st.session_state["review_status"] = review_status
                                st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

            # Expander error/skip
            if err_list:
                with st.expander(f"❌ {len(err_list)} File Gagal"):
                    for fn in err_list:
                        st.markdown(f"- `{fn}` → {results[fn].get('message','?')}")
            if skip_list:
                with st.expander(f"⚡ {len(skip_list)} Di-Skip (sudah transparan)"):
                    for fn in skip_list:
                        st.markdown(f"- `{fn}`")

            st.markdown("<hr class='s'>", unsafe_allow_html=True)
            if st.button("Lanjut ke Download ▶", type="primary",
                         use_container_width=True, key="r_next_bot"):
                st.session_state["batch_step"] = 4
                st.rerun()

    # ════════════════════════════════════
    #  STEP 4 — DOWNLOAD
    # ════════════════════════════════════
    elif cur == 4:
        results       = st.session_state.get("batch_results",{})
        review_status = st.session_state.get("review_status",{})

        kept = {fn:r for fn,r in results.items()
                if review_status.get(fn)=="keep" and r["status"]=="ok"}
        excl = len(results) - len(kept)

        st.markdown(f"""<div class='card'>
        <div class='card-lbl'>⬇️ Download Hasil Final</div>
        <div class='srow'>
          <div class='sbox'><div class='snum cg'>{len(kept)}</div>
            <div class='slbl'>File Disertakan</div></div>
          <div class='sbox'><div class='snum cgr'>{excl}</div>
            <div class='slbl'>Dikecualikan</div></div>
        </div></div>""", unsafe_allow_html=True)

        if kept:
            with st.spinner("📦 Membuat ZIP..."):
                zb = io.BytesIO()
                with zipfile.ZipFile(zb,"w",zipfile.ZIP_DEFLATED) as zf:
                    for fn,r in kept.items():
                        zf.writestr(Path(fn).stem+".png", r["png_bytes"])
                zb.seek(0)
                zmb = len(zb.getvalue())/1024/1024

            st.markdown(f"<div class='info ig'>✅ {len(kept)} file PNG — {zmb:.1f} MB</div>",
                        unsafe_allow_html=True)

            st.download_button(
                label=f"⬇️  Download Semua ({len(kept)} file · {zmb:.1f} MB)",
                data=zb.getvalue(),
                file_name="hasil_tanda_tangan.zip",
                mime="application/zip",
                use_container_width=True,
            )

            # Mini preview
            with st.expander(f"🖼️ Preview {min(len(kept),12)} hasil"):
                sample = list(kept.items())[:12]
                cols_p = st.columns(4)
                for i,(fn,r) in enumerate(sample):
                    rgba = bytes_to_pil(r["png_bytes"])
                    cols_p[i%4].image(
                        composite(rgba,(255,255,255)),
                        caption=Path(fn).stem[:16],
                        use_container_width=True)
        else:
            st.markdown("""<div class='info iy'>
            ⚠️ Tidak ada file dipilih. Kembali ke Review dan klik ✅ Masukkan.
            </div>""", unsafe_allow_html=True)

        st.markdown("<hr class='s'>", unsafe_allow_html=True)
        d1, d2 = st.columns(2)
        if d1.button("← Kembali ke Review", use_container_width=True, key="d_back"):
            st.session_state["batch_step"] = 3
            st.rerun()
        if d2.button("🔁 Batch Baru", use_container_width=True, key="d_new"):
            for k_,v_ in _DEFAULTS.items():
                st.session_state[k_] = v_
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  TAB 3 — PANDUAN
# ─────────────────────────────────────────────────────────────────────────────
with TAB_GUIDE:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
## 📖 Panduan Penggunaan

### 🏷️ 4 Kondisi Tanda Tangan

| Kondisi | Mode | Cara Kerja |
|---|---|---|
| **Background Hitam** (tinta biru/putih/warna) | `dark` | Logika TERBALIK — piksel gelap dihapus |
| **Kertas Putih / HVS** | `white` | Threshold kecerahan |
| **Kertas Berwarna / Bergaris / Watermark** | `complex` | Adaptive + LAB color + hapus garis |
| **PNG sudah transparan** | `skip` | Dilewati otomatis |

---

### 🚀 Alur Batch (4 Step)
1. **Upload** → multiple files atau ZIP
2. **Proses** → berjalan otomatis + progress bar, lalu **langsung lanjut ke Review**
3. **Review** → preview tiap file, pilih Masukkan/Keluarkan, bisa proses ulang per file
4. **Download** → ZIP hanya file yang diapprove + preview mini gallery

---

### ⚙️ Parameter Tuning

| Kondisi | Parameter | Solusi |
|---|---|---|
| BG hitam masih tersisa | Threshold Gelap | Naikkan (60–80) |
| TTD hilang (mode dark) | Threshold Gelap | Turunkan (35–50) |
| BG putih tersisa | Threshold Putih | Naikkan (210–230) |
| TTD hilang (mode white) | Threshold Putih | Turunkan (170–190) |
| BG berwarna tersisa | Toleransi Warna | Naikkan (45–65) |
| Tinta biru ikut hilang | Toleransi Warna | Turunkan (22–32) + Min Alpha = 0 |
| Noise scan | Blur | Naikkan ke 5–7 |

---

### ⚡ Skip PNG Transparan
PNG dengan ≥8% piksel sudah transparan → dilewati otomatis.  
Ini mencegah TTD yang sudah bersih malah rusak saat parameter dinaikkan.

---

### 🔍 Fitur Review
- Preview **Transparan** (checkerboard) + **BG Gelap** per file
- **✅ Masukkan / 🚫 Keluarkan** per file
- **⬇️ Download** langsung satu file dari halaman review
- **🔄 Proses Ulang** per file dengan parameter custom berbeda
- **Pilih Semua / Batalkan Semua** untuk aksi bulk
""")
