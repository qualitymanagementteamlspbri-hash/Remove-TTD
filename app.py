"""
================================================================================
  SIGNATURE BG REMOVER — Streamlit Dashboard v3.0
  Menangani 4 kondisi tanda tangan + Review sebelum download
================================================================================
  Jalankan: streamlit run app.py
  Install : pip install streamlit opencv-python-headless pillow numpy tqdm
================================================================================
"""

import io, os, cv2, zipfile, base64, tempfile, time
import numpy as np
import streamlit as st
from PIL import Image
from pathlib import Path

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Signature BG Remover",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
#  CUSTOM CSS
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: #0e0e16;
    min-height: 100vh;
}

/* ── Header ── */
.app-header {
    background: linear-gradient(135deg, #141428 0%, #1a1a35 100%);
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: 18px;
    padding: 28px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.app-header::after {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(139,92,246,0.1) 0%, transparent 70%);
    pointer-events: none;
}
.app-title {
    font-size: 1.9rem;
    font-weight: 700;
    color: #fff;
    margin: 0 0 4px 0;
    letter-spacing: -0.5px;
}
.app-sub {
    font-size: 0.9rem;
    color: #a78bfa;
    margin: 0 0 16px 0;
}
.badge-wrap { display: flex; gap: 8px; flex-wrap: wrap; }
.badge {
    background: rgba(139,92,246,0.12);
    border: 1px solid rgba(139,92,246,0.25);
    color: #c4b5fd;
    padding: 4px 12px;
    border-radius: 100px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.3px;
}

/* ── Cards ── */
.card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 14px;
}
.card-title {
    font-size: 0.75rem;
    font-weight: 700;
    color: #a78bfa;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-bottom: 14px;
}

/* ── Mode pills ── */
.mode-pill {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 100px;
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}
.m-white  { background:rgba(241,245,249,.12); color:#e2e8f0; border:1px solid rgba(226,232,240,.2);}
.m-dark   { background:rgba(168,85,247,.12);  color:#c084fc; border:1px solid rgba(192,132,252,.2);}
.m-color  { background:rgba(251,191,36,.12);  color:#fbbf24; border:1px solid rgba(251,191,36,.2);}
.m-complex{ background:rgba(52,211,153,.12);  color:#34d399; border:1px solid rgba(52,211,153,.2);}
.m-skip   { background:rgba(107,114,128,.12); color:#9ca3af; border:1px solid rgba(107,114,128,.2);}

/* ── Review card ── */
.review-item {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 10px;
    transition: border-color .15s;
}
.review-item.kept   { border-color: rgba(52,211,153,0.35); }
.review-item.skip   { border-color: rgba(107,114,128,0.25); opacity: .55; }
.review-item.rework { border-color: rgba(251,191,36,0.35); }

/* ── Stat boxes ── */
.stat-row { display: flex; gap: 10px; margin: 12px 0; }
.stat-box {
    flex: 1;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 12px;
    text-align: center;
}
.stat-num { font-size: 1.7rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.stat-lbl { font-size: 0.68rem; color: #6b7280; text-transform: uppercase; letter-spacing: .5px; margin-top: 2px; font-weight: 600; }
.c-green { color: #34d399; }
.c-amber { color: #fbbf24; }
.c-gray  { color: #9ca3af; }
.c-red   { color: #f87171; }
.c-purple{ color: #a78bfa; }

/* ── Info boxes ── */
.info-box {
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    font-size: 0.82rem;
    margin: 10px 0;
    line-height: 1.55;
}
.info-blue   { background:rgba(96,165,250,.08); border-left:3px solid #60a5fa; color:#93c5fd; }
.info-green  { background:rgba(52,211,153,.08); border-left:3px solid #34d399; color:#6ee7b7; }
.info-yellow { background:rgba(251,191,36,.08); border-left:3px solid #fbbf24; color:#fde68a; }
.info-red    { background:rgba(248,113,113,.08); border-left:3px solid #f87171; color:#fca5a5; }

/* ── Image label ── */
.img-lbl {
    text-align: center;
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .8px;
    color: #6b7280;
    margin-top: 6px;
}

/* ── Step indicator ── */
.step-wrap { display: flex; gap: 0; margin-bottom: 22px; }
.step { flex:1; text-align:center; position:relative; }
.step::after {
    content:''; position:absolute;
    top: 18px; left: 55%; width: 90%;
    height: 1px; background: rgba(255,255,255,.08);
}
.step:last-child::after { display:none; }
.step-circle {
    width: 36px; height: 36px; border-radius: 50%;
    background: rgba(139,92,246,.1);
    border: 1.5px solid rgba(139,92,246,.25);
    margin: 0 auto 6px;
    display: flex; align-items: center; justify-content: center;
    font-size: .9rem; position: relative; z-index: 1;
}
.step-circle.active {
    background: rgba(139,92,246,.25);
    border-color: #8b5cf6;
    box-shadow: 0 0 16px rgba(139,92,246,.3);
}
.step-lbl { font-size: .65rem; color: #6b7280; font-weight: 600; text-transform: uppercase; letter-spacing: .4px; }
.step-lbl.active { color: #c4b5fd; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: rgba(255,255,255,0.03);
    padding: 5px;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,.06);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px;
    font-weight: 600;
    font-size: 0.85rem;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(10,10,20,0.97);
    border-right: 1px solid rgba(255,255,255,.06);
}

/* ── Download button ── */
.stDownloadButton > button {
    background: linear-gradient(135deg,#7c3aed,#5b21b6) !important;
    border: none !important;
    color: white !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    padding: 12px !important;
}

/* ── Scrollable gallery ── */
.gallery-wrap {
    max-height: 70vh;
    overflow-y: auto;
    padding-right: 4px;
}

/* ── Progress ── */
.prog-label {
    font-size: 0.78rem;
    color: #9ca3af;
    margin-bottom: 4px;
}

/* ── Separator ── */
hr.section { border: none; border-top: 1px solid rgba(255,255,255,.06); margin: 20px 0; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  CORE ENGINE — semua fungsi pemrosesan
# ══════════════════════════════════════════════════════════════════════════════

def _sample_bg(img_bgr, px=10):
    h, w = img_bgr.shape[:2]
    b = min(px, h//4, w//4)
    regions = [img_bgr[:b,:w], img_bgr[h-b:,:w], img_bgr[:h,:b], img_bgr[:h,w-b:]]
    return np.median(np.vstack([r.reshape(-1,3) for r in regions]), axis=0)

def _blur(img, k):
    if k <= 1: return img
    k = k if k%2==1 else k+1
    return cv2.GaussianBlur(img, (k,k), 0)

def _morph_clean(mask, mode="normal"):
    if mode == "dark":
        k1 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2,2))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k1)
        k2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2,2))
        return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k2)
    k1 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2,2))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k1)
    k2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k2)
    k3 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2,2))
    return cv2.dilate(mask, k3, iterations=1)

def _clean_alpha(arr, min_a):
    r = arr.copy()
    r[r[:,:,3] < min_a, 3] = 0
    return r

def _hough_lines(img_bgr, ratio=0.4):
    gray  = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    w     = gray.shape[1]
    edges = cv2.Canny(gray, 30, 100, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 80,
                             minLineLength=int(w*ratio), maxLineGap=15)
    if lines is None: return False
    cnt = sum(1 for l in lines
              if abs(np.degrees(np.arctan2(l[0][3]-l[0][1], l[0][2]-l[0][0]))) < 5
              or abs(np.degrees(np.arctan2(l[0][3]-l[0][1], l[0][2]-l[0][0]))) > 175)
    return cnt >= 3

def _remove_lines(img_bgr, mask):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    w = gray.shape[1]
    combined = np.zeros_like(mask)
    for t in range(1,5):
        k  = cv2.getStructuringElement(cv2.MORPH_RECT,(max(int(w*.5),50), t))
        lm = cv2.morphologyEx(cv2.bitwise_not(gray), cv2.MORPH_OPEN, k)
        _, lb = cv2.threshold(lm, 30, 255, cv2.THRESH_BINARY)
        combined = cv2.bitwise_or(combined, lb)
    dk = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    combined = cv2.dilate(combined, dk, iterations=1)
    out = mask.copy(); out[combined > 0] = 0
    return out


def has_transparency(file_bytes: bytes) -> bool:
    """Cek apakah PNG sudah punya transparansi yang signifikan — skip jika iya."""
    arr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
    if img is None: return False
    if img.ndim < 3 or img.shape[2] != 4: return False
    alpha = img[:,:,3]
    transparent_ratio = float(np.sum(alpha < 128)) / alpha.size
    return transparent_ratio > 0.08   # ≥8% piksel sudah transparan


def auto_detect(img_bgr, border_px=10) -> str:
    """Deteksi otomatis jenis background → white / dark / color / complex"""
    bg  = _sample_bg(img_bgr, border_px)
    avg = float(np.mean(bg))
    # Dark background
    if avg < 55: return "dark"
    # White / nearly white
    if np.all(bg > 205): return "white"
    # Has horizontal lines?
    if _hough_lines(img_bgr): return "complex"
    # Colored
    return "color"


# ── MASK ENGINES ──────────────────────────────────────────────────────────────

def mask_white(img_bgr, threshold, blur_k):
    """Kertas putih/HVS: piksel terang → transparan."""
    gray = _blur(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY), blur_k)
    _, m = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
    return m

def mask_dark(img_bgr, threshold, blur_k):
    """
    Background hitam: piksel GELAP → transparan, piksel TERANG → opaque.
    Logika TERBALIK dari mode biasa.
    Berlaku untuk tinta biru, putih, atau warna apapun di atas bg hitam.
    """
    gray = _blur(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY), blur_k)
    _, m = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)   # normal (bukan INV)
    return m

def mask_color(img_bgr, tolerance, blur_k, border_px=10):
    """Kertas berwarna: LAB color-distance dari warna tepi."""
    bg_color = _sample_bg(img_bgr, border_px)
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    bg_pix = bg_color.astype(np.uint8).reshape(1,1,3)
    bg_lab  = cv2.cvtColor(bg_pix, cv2.COLOR_BGR2LAB).astype(np.float32).reshape(3)
    dist    = np.sqrt(np.sum((lab - bg_lab)**2, axis=2))
    dist    = _blur(dist, blur_k)
    return np.where(dist < tolerance, 0, 255).astype(np.uint8)

def mask_complex(img_bgr, tolerance, white_threshold, blur_k, border_px=10):
    """
    Background kompleks: kertas bekas, bergaris, ada bayangan logo/watermark.
    Strategi berlapis:
      1. Adaptive threshold (kurangi efek bayangan/gradasi)
      2. LAB color-distance untuk warna background
      3. Gabungkan & hapus garis horizontal
      4. Morphological aggressive cleanup
    """
    gray     = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    blur_g   = _blur(gray, max(blur_k, 3))

    # — Layer 1: Adaptive threshold (tanda tangan vs background lokal)
    adapt = cv2.adaptiveThreshold(
        blur_g, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        blockSize=31,    # area lokal cukup besar untuk handle gradasi
        C=8
    )

    # — Layer 2: Global threshold untuk hapus area terang (bg kertas)
    _, global_m = cv2.threshold(blur_g, white_threshold, 255, cv2.THRESH_BINARY_INV)

    # — Layer 3: Color-distance dari background
    color_m = mask_color(img_bgr, tolerance, blur_k, border_px)

    # — Gabungkan: pakai AND antara adaptive & color distance
    #   → piksel harus "terlihat sebagai foreground" oleh KEDUA metode
    combined = cv2.bitwise_and(adapt, color_m)

    # — Tambahkan juga global mask untuk memastikan area gelap (tinta) masuk
    combined = cv2.bitwise_or(combined, cv2.bitwise_and(global_m,
                cv2.bitwise_not(np.where(color_m==0, 255, 0).astype(np.uint8))))

    # — Hapus garis horizontal jika ada
    combined = _remove_lines(img_bgr, combined)

    # — Aggressive cleanup: hapus noise kecil (titik-titik dari tekstur kertas)
    k_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
    combined = cv2.morphologyEx(combined, cv2.MORPH_OPEN, k_open)

    return combined


# ── FUNGSI UTAMA ──────────────────────────────────────────────────────────────

def process_image(
    file_bytes: bytes,
    mode: str = "auto",
    white_threshold: int = 200,
    dark_threshold: int  = 55,
    color_tolerance: float = 38.0,
    blur_k: int          = 3,
    min_alpha: int       = 10,
    border_px: int       = 10,
    skip_transparent: bool = True,
) -> dict:
    """
    Proses satu gambar. Returns dict:
      status  : "ok" | "skipped" | "error"
      mode    : mode yang dipakai
      img     : PIL Image RGBA (jika ok)
      message : keterangan (jika skipped/error)
    """
    # Cek PNG transparan (skip)
    if skip_transparent and has_transparency(file_bytes):
        return {"status": "skipped", "mode": "skip",
                "message": "PNG sudah memiliki background transparan"}

    arr = np.frombuffer(file_bytes, np.uint8)
    img_bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img_bgr is None:
        return {"status": "error", "mode": "?",
                "message": "Tidak dapat membaca file gambar"}

    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    # Auto-detect
    if mode == "auto":
        detected = auto_detect(img_bgr, border_px)
    else:
        detected = mode

    try:
        if detected == "white":
            mask      = mask_white(img_bgr, white_threshold, blur_k)
            mask      = _morph_clean(mask, "normal")

        elif detected == "dark":
            mask      = mask_dark(img_bgr, dark_threshold, blur_k)
            mask      = _morph_clean(mask, "dark")

        elif detected == "color":
            mask      = mask_color(img_bgr, color_tolerance, blur_k, border_px)
            mask      = _morph_clean(mask, "normal")

        elif detected == "complex":
            mask      = mask_complex(img_bgr, color_tolerance, white_threshold, blur_k, border_px)
            mask      = _morph_clean(mask, "normal")

        else:
            return {"status": "error", "mode": detected,
                    "message": f"Mode tidak dikenal: {detected}"}

        rgba = np.dstack([img_rgb, mask])
        if min_alpha > 0:
            rgba = _clean_alpha(rgba, min_alpha)

        return {
            "status": "ok",
            "mode": detected,
            "img": Image.fromarray(rgba, mode="RGBA"),
        }

    except Exception as e:
        return {"status": "error", "mode": detected, "message": str(e)}


# ── HELPER: Gambar ke bytes PNG ───────────────────────────────────────────────

def to_png_bytes(pil_img: Image.Image) -> bytes:
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    return buf.getvalue()

def composite(rgba: Image.Image, bg=(255,255,255)) -> Image.Image:
    bg_img = Image.new("RGBA", rgba.size, (*bg, 255))
    return Image.alpha_composite(bg_img, rgba).convert("RGB")

def checkerboard(w, h, tile=18):
    arr = np.ones((h,w,3), np.uint8)*215
    for y in range(0,h,tile):
        for x in range(0,w,tile):
            if (x//tile + y//tile)%2==0:
                arr[y:y+tile,x:x+tile] = 240
    return Image.fromarray(arr,"RGB").convert("RGBA")

def make_preview(rgba: Image.Image) -> Image.Image:
    """Gambar di atas checker board untuk preview."""
    bg = checkerboard(rgba.width, rgba.height)
    return Image.alpha_composite(bg, rgba).convert("RGB")

def img_to_b64(pil_img: Image.Image, fmt="PNG") -> str:
    buf = io.BytesIO()
    pil_img.save(buf, format=fmt)
    return base64.b64encode(buf.getvalue()).decode()


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR — SETTINGS
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:18px 0 6px'>
        <div style='font-size:2.2rem'>✍️</div>
        <div style='font-weight:700;font-size:.95rem;color:#e2e8f0;margin-top:3px'>BG Remover</div>
        <div style='font-size:.65rem;color:#4b5563;margin-top:2px;text-transform:uppercase;letter-spacing:1px;font-weight:600'>Tanda Tangan v3.0</div>
    </div>
    <hr style='border-color:rgba(255,255,255,.06);margin:12px 0'>
    """, unsafe_allow_html=True)

    st.markdown("### 🤖 Mode Deteksi")
    MODE_OPTIONS = {
        "🤖 Auto-Detect (Rekomendasi)": "auto",
        "📄 Kertas Putih / HVS":        "white",
        "🖤 Background Hitam":           "dark",
        "🎨 Kertas Berwarna":            "color",
        "📋 Background Kompleks":        "complex",
    }
    sel_mode = st.selectbox("Mode", list(MODE_OPTIONS.keys()), index=0,
                            label_visibility="collapsed")
    MODE = MODE_OPTIONS[sel_mode]

    st.markdown("""<div style='font-size:.73rem;color:#6b7280;padding:8px;background:rgba(255,255,255,.03);border-radius:8px;line-height:1.6;margin-bottom:10px'>
    <b style='color:#9ca3af'>Background Kompleks</b> = kertas bekas, bergaris, ada watermark/logo/bayangan
    </div>""", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(255,255,255,.06)'>", unsafe_allow_html=True)
    st.markdown("### ⚙️ Parameter")

    col_a, col_b = st.columns(2)
    with col_a:
        white_threshold = st.number_input("Threshold Putih", 100, 250, 200, 5,
            help="Naik → hapus lebih agresif. Turun → lebih aman untuk tanda tangan tipis.")
    with col_b:
        dark_threshold = st.number_input("Threshold Gelap", 20, 150, 55, 5,
            help="Untuk bg hitam. Turun → lebih aman, Naik → lebih bersih.")

    color_tolerance = st.slider("Toleransi Warna", 10, 80, 38, 2,
        help="Untuk bg berwarna & kompleks. Naik → hapus lebih banyak warna. Turun → lebih aman.")

    col_c, col_d = st.columns(2)
    with col_c:
        blur_k    = st.select_slider("Blur Noise", [1,3,5,7], 3,
            help="Naikkan untuk gambar scan berkualitas rendah / penuh noise.")
    with col_d:
        min_alpha = st.number_input("Min Alpha", 0, 40, 10, 1,
            help="Hapus piksel semi-transparan lemah (bayangan sisa).")

    skip_transparent = st.toggle("⚡ Skip PNG Transparan", value=True,
        help="File PNG yang sudah punya background transparan akan dilewati otomatis (tidak diproses ulang).")

    border_px = st.number_input("Border Sampling (px)", 5, 30, 10, 1,
        help="Lebar area tepi untuk mendeteksi warna background.", label_visibility="collapsed")

    st.markdown("<hr style='border-color:rgba(255,255,255,.06)'>", unsafe_allow_html=True)
    st.markdown("""### 💡 Panduan Cepat
<div style='font-size:.75rem;color:#6b7280;line-height:1.8'>
<b style='color:#a78bfa'>TTD hilang?</b><br>
Turunkan threshold / toleransi<br><br>
<b style='color:#fbbf24'>BG masih tersisa?</b><br>
Naikkan threshold / toleransi<br><br>
<b style='color:#34d399'>Tinta biru di kertas berwarna?</b><br>
Toleransi ↓ 22–30 + Min Alpha = 0<br><br>
<b style='color:#c084fc'>PNG bg hitam + tinta biru?</b><br>
Mode: Background Hitam, Dark Threshold 45–55
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="app-header">
    <div class="app-title">✍️ Signature Background Remover</div>
    <div class="app-sub">Hapus background tanda tangan — putih, hitam, berwarna, bergaris, watermark</div>
    <div class="badge-wrap">
        <span class="badge">📄 Kertas Putih</span>
        <span class="badge">🖤 Background Hitam</span>
        <span class="badge">🎨 Kertas Berwarna</span>
        <span class="badge">📋 Background Kompleks</span>
        <span class="badge">⚡ Skip PNG Transparan</span>
        <span class="badge">🔍 Review Sebelum Download</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════════════════════════

tab_single, tab_batch, tab_guide = st.tabs([
    "🔍  Uji Satu File",
    "⚡  Batch + Review",
    "📖  Panduan",
])


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — UJI SATU FILE
# ══════════════════════════════════════════════════════════════════════════════

with tab_single:
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""<div class='info-box info-blue'>
    💡 Upload satu file untuk uji parameter. Lihat hasilnya sebelum proses ratusan file.
    </div>""", unsafe_allow_html=True)

    f_single = st.file_uploader("Upload file tanda tangan",
                                 type=["jpg","jpeg","png"],
                                 key="single_up")

    if f_single:
        raw = f_single.read()
        arr = np.frombuffer(raw, np.uint8)
        img_bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        h_px, w_px = img_bgr.shape[:2]

        bg_color   = _sample_bg(img_bgr)
        bg_rgb     = bg_color[::-1].astype(int)
        has_lines  = _hough_lines(img_bgr)
        detected   = auto_detect(img_bgr)
        is_transp  = has_transparency(raw)
        avg_bright = float(np.mean(bg_color))

        # Warna badge sesuai mode
        mode_css = {"white":"m-white","dark":"m-dark","color":"m-color","complex":"m-complex","skip":"m-skip"}
        mode_lbl = {"white":"Putih","dark":"Bg Hitam","color":"Berwarna","complex":"Kompleks","skip":"Transparan"}

        st.markdown(f"""
        <div class='card'>
            <div class='card-title'>📊 Analisis Otomatis</div>
            <div style='display:grid;grid-template-columns:repeat(5,1fr);gap:10px'>
                <div class='stat-box'>
                    <div class='stat-num c-purple' style='font-size:1rem'>{w_px}×{h_px}</div>
                    <div class='stat-lbl'>Resolusi</div>
                </div>
                <div class='stat-box'>
                    <div style='width:22px;height:22px;border-radius:5px;background:rgb({bg_rgb[0]},{bg_rgb[1]},{bg_rgb[2]});margin:0 auto 3px;border:1px solid rgba(255,255,255,.15)'></div>
                    <div class='stat-lbl'>Warna BG</div>
                </div>
                <div class='stat-box'>
                    <div class='stat-num' style='font-size:1rem;color:{"#34d399" if has_lines else "#6b7280"}'>{"Ada ✓" if has_lines else "Tidak"}</div>
                    <div class='stat-lbl'>Garis</div>
                </div>
                <div class='stat-box'>
                    <div class='stat-num' style='font-size:1rem;color:{"#34d399" if is_transp else "#6b7280"}'>{"Ya ✓" if is_transp else "Tidak"}</div>
                    <div class='stat-lbl'>Transparan</div>
                </div>
                <div class='stat-box'>
                    <span class='mode-pill {mode_css.get(detected,"m-white")}' style='font-size:.75rem'>{mode_lbl.get(detected,detected)}</span>
                    <div class='stat-lbl' style='margin-top:6px'>Mode Detect</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if is_transp and skip_transparent:
            st.markdown("""<div class='info-box info-yellow'>
            ⚡ File ini sudah memiliki background transparan dan akan di-<b>skip</b> secara otomatis
            saat batch processing. Matikan toggle "Skip PNG Transparan" di sidebar jika ingin tetap diproses.
            </div>""", unsafe_allow_html=True)

        btn_col, _ = st.columns([1.5, 3])
        with btn_col:
            do_process = st.button("🚀 Proses Sekarang", type="primary",
                                   use_container_width=True)

        if do_process:
            with st.spinner("⏳ Memproses..."):
                result = process_image(
                    raw, MODE, white_threshold, dark_threshold,
                    color_tolerance, blur_k, min_alpha, border_px, skip_transparent
                )
            st.session_state["single_result"] = result
            st.session_state["single_fname"]  = Path(f_single.name).stem

        if "single_result" in st.session_state and st.session_state["single_result"]:
            res   = st.session_state["single_result"]
            fname = st.session_state.get("single_fname", "result")

            if res["status"] == "skipped":
                st.markdown(f"""<div class='info-box info-yellow'>
                ⚡ <b>Dilewati:</b> {res['message']}
                </div>""", unsafe_allow_html=True)

            elif res["status"] == "error":
                st.markdown(f"""<div class='info-box info-red'>
                ❌ <b>Error:</b> {res['message']}
                </div>""", unsafe_allow_html=True)

            else:
                used_mode = res["mode"]
                rgba_img  = res["img"]

                st.markdown(f"""<div class='info-box info-green'>
                ✅ Berhasil — Mode: <span class='mode-pill {mode_css.get(used_mode,"m-white")}'>{mode_lbl.get(used_mode,used_mode)}</span>
                </div>""", unsafe_allow_html=True)

                # Preview 4 kolom
                st.markdown("#### 🖼️ Perbandingan Hasil")
                c1,c2,c3,c4 = st.columns(4)
                with c1:
                    st.image(Image.fromarray(img_rgb), use_container_width=True)
                    st.markdown('<div class="img-lbl">Original</div>', unsafe_allow_html=True)
                with c2:
                    st.image(make_preview(rgba_img), use_container_width=True)
                    st.markdown('<div class="img-lbl">Transparan</div>', unsafe_allow_html=True)
                with c3:
                    st.image(composite(rgba_img,(255,255,255)), use_container_width=True)
                    st.markdown('<div class="img-lbl">BG Putih</div>', unsafe_allow_html=True)
                with c4:
                    st.image(composite(rgba_img,(30,30,30)), use_container_width=True)
                    st.markdown('<div class="img-lbl">BG Gelap</div>', unsafe_allow_html=True)

                st.markdown("<hr class='section'>", unsafe_allow_html=True)

                # Alpha mask
                with st.expander("🎭 Lihat Alpha Mask (opsional)"):
                    alpha_ch = np.array(rgba_img)[:,:,3]
                    st.image(Image.fromarray(alpha_ch,"L"), use_container_width=True,
                             caption="Putih = tanda tangan, Hitam = transparan")

                # Download
                st.download_button(
                    label=f"⬇️  Download {fname}.png",
                    data=to_png_bytes(rgba_img),
                    file_name=f"{fname}.png",
                    mime="image/png",
                    use_container_width=True,
                )

                # Tips tuning
                st.markdown("<hr class='section'>", unsafe_allow_html=True)
                st.markdown("**💡 Tidak puas? Coba sesuaikan parameter di sidebar:**")
                if used_mode == "dark":
                    c1,c2 = st.columns(2)
                    c1.info(f"BG hitam masih tersisa → Naikkan **Threshold Gelap** (coba {dark_threshold+10})")
                    c2.info(f"Tanda tangan hilang → Turunkan **Threshold Gelap** (coba {max(20,dark_threshold-10)})")
                elif used_mode == "color":
                    c1,c2 = st.columns(2)
                    c1.info(f"BG berwarna masih ada → Naikkan **Toleransi Warna** (coba {color_tolerance+8})")
                    c2.info(f"Tanda tangan terkena → Turunkan **Toleransi** (coba {max(10,color_tolerance-8)})")
                elif used_mode == "complex":
                    st.info("Untuk background kompleks: coba naikkan **Toleransi Warna** + **Blur Noise** ke 5")
                else:
                    c1,c2 = st.columns(2)
                    c1.info(f"BG masih tersisa → Naikkan **Threshold Putih** (coba {white_threshold+10})")
                    c2.info(f"Tanda tangan hilang → Turunkan **Threshold Putih** (coba {max(100,white_threshold-10)})")

    else:
        st.markdown("""<div style='text-align:center;padding:60px 20px;color:#374151'>
        <div style='font-size:3.5rem;margin-bottom:12px'>📁</div>
        <div style='font-size:.95rem;font-weight:600;color:#6b7280'>Upload file di atas untuk mulai</div>
        <div style='font-size:.8rem;margin-top:6px;color:#4b5563'>JPG · JPEG · PNG</div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — BATCH + REVIEW
# ══════════════════════════════════════════════════════════════════════════════

with tab_batch:
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Step indicator ──────────────────────────────────────────────────────
    batch_step = st.session_state.get("batch_step", 1)
    steps = [("📤","Upload"), ("⚡","Proses"), ("🔍","Review"), ("⬇️","Download")]
    step_html = '<div class="step-wrap">' + "".join(
        f'<div class="step"><div class="step-circle{"  active" if i+1==batch_step else ""}">{icon}</div>'
        f'<div class="step-lbl{"  active" if i+1==batch_step else ""}">{lbl}</div></div>'
        for i,(icon,lbl) in enumerate(steps)
    ) + '</div>'
    st.markdown(step_html, unsafe_allow_html=True)

    # ═══════════════════════════════════════════
    #  STEP 1 — UPLOAD
    # ═══════════════════════════════════════════
    if batch_step == 1:
        upload_type = st.radio("Metode upload:", ["📂 Multiple Files","🗜️ File ZIP"], horizontal=True)

        if upload_type == "📂 Multiple Files":
            batch_files = st.file_uploader(
                "Upload semua file tanda tangan (bisa pilih banyak sekaligus)",
                type=["jpg","jpeg","png"], accept_multiple_files=True, key="b_files")

            if batch_files:
                file_data = {f.name: f.read() for f in batch_files}
                st.session_state["batch_file_data"] = file_data
                n = len(file_data)
                st.markdown(f"""<div class='info-box info-green'>
                ✅ {n} file siap diproses
                </div>""", unsafe_allow_html=True)

                if st.button("Lanjut ke Proses →", type="primary", use_container_width=True):
                    st.session_state["batch_step"] = 2
                    st.rerun()

        else:  # ZIP
            zip_up = st.file_uploader("Upload file ZIP", type=["zip"], key="b_zip")
            if zip_up:
                with st.spinner("Membaca ZIP..."):
                    file_data = {}
                    zb = io.BytesIO(zip_up.read())
                    with zipfile.ZipFile(zb,"r") as zf:
                        for name in zf.namelist():
                            if Path(name).suffix.lower() in {".jpg",".jpeg",".png"} \
                               and not name.startswith("__MACOSX"):
                                file_data[Path(name).name] = zf.read(name)

                st.session_state["batch_file_data"] = file_data
                n = len(file_data)
                st.markdown(f"""<div class='info-box info-green'>
                ✅ {n} file ditemukan dalam ZIP
                </div>""", unsafe_allow_html=True)

                if n > 0 and st.button("Lanjut ke Proses →", type="primary", use_container_width=True):
                    st.session_state["batch_step"] = 2
                    st.rerun()

    # ═══════════════════════════════════════════
    #  STEP 2 — PROSES
    # ═══════════════════════════════════════════
    elif batch_step == 2:
        file_data = st.session_state.get("batch_file_data", {})
        total = len(file_data)

        if not file_data:
            st.warning("Tidak ada file. Kembali ke Upload.")
            if st.button("← Upload Ulang"):
                st.session_state["batch_step"] = 1
                st.rerun()
        else:
            st.markdown(f"""<div class='card'>
            <div class='card-title'>📦 Siap Diproses</div>
            <div class='stat-row'>
                <div class='stat-box'><div class='stat-num c-purple'>{total}</div><div class='stat-lbl'>Total File</div></div>
                <div class='stat-box'><div class='stat-num c-amber' style='font-size:.9rem'>{MODE}</div><div class='stat-lbl'>Mode</div></div>
                <div class='stat-box'><div class='stat-num c-gray' style='font-size:.9rem'>{"Ya" if skip_transparent else "Tidak"}</div><div class='stat-lbl'>Skip Transparan</div></div>
            </div>
            </div>""", unsafe_allow_html=True)

            col_start, col_back = st.columns([3,1])
            with col_back:
                if st.button("← Kembali", use_container_width=True):
                    st.session_state["batch_step"] = 1
                    st.rerun()
            with col_start:
                do_batch = st.button(f"⚡ Mulai Proses {total} File", type="primary", use_container_width=True)

            if do_batch:
                results  = {}  # fname → result dict
                prog_bar = st.progress(0)
                status_ph= st.empty()
                t0       = time.time()

                for i, (fname, fbytes) in enumerate(file_data.items()):
                    pct = int((i/total)*100)
                    elapsed = time.time() - t0
                    eta = (elapsed/max(i,1))*(total-i)
                    prog_bar.progress(pct)
                    status_ph.markdown(
                        f'<div class="prog-label">⏳ {fname} &nbsp;|&nbsp; {i+1}/{total} &nbsp;|&nbsp; ETA {int(eta)}s</div>',
                        unsafe_allow_html=True)

                    res = process_image(
                        fbytes, MODE, white_threshold, dark_threshold,
                        color_tolerance, blur_k, min_alpha, border_px, skip_transparent
                    )
                    results[fname] = res

                prog_bar.progress(100)
                status_ph.empty()
                elapsed_total = time.time() - t0

                # Summary
                ok_count   = sum(1 for r in results.values() if r["status"]=="ok")
                skip_count = sum(1 for r in results.values() if r["status"]=="skipped")
                err_count  = sum(1 for r in results.values() if r["status"]=="error")
                mode_count = {}
                for r in results.values():
                    if r["status"]=="ok":
                        mode_count[r["mode"]] = mode_count.get(r["mode"],0)+1

                st.markdown(f"""<div class='card'>
                <div class='card-title'>✅ Proses Selesai — {elapsed_total:.1f} detik</div>
                <div class='stat-row'>
                    <div class='stat-box'><div class='stat-num c-green'>{ok_count}</div><div class='stat-lbl'>Berhasil</div></div>
                    <div class='stat-box'><div class='stat-num c-gray'>{skip_count}</div><div class='stat-lbl'>Di-Skip</div></div>
                    <div class='stat-box'><div class='stat-num c-red'>{err_count}</div><div class='stat-lbl'>Gagal</div></div>
                    <div class='stat-box'><div class='stat-num c-purple'>{elapsed_total/max(total,1):.1f}s</div><div class='stat-lbl'>Per File</div></div>
                </div>
                </div>""", unsafe_allow_html=True)

                if MODE == "auto" and mode_count:
                    mode_lbl_map = {"white":"Putih","dark":"Bg Hitam","color":"Berwarna","complex":"Kompleks"}
                    st.markdown("**Distribusi mode auto-detect:**")
                    m_cols = st.columns(len(mode_count))
                    for ci, (m, cnt) in enumerate(mode_count.items()):
                        m_cols[ci].metric(f"{mode_lbl_map.get(m,m)}", f"{cnt} file")

                # Simpan & lanjut ke review
                st.session_state["batch_results"]     = results
                st.session_state["batch_file_data"]   = file_data   # pertahankan untuk reprocess
                # Init review status: semua "keep" kecuali skipped/error
                review_status = {}
                for fname, r in results.items():
                    if r["status"] == "ok":
                        review_status[fname] = "keep"
                    elif r["status"] == "skipped":
                        review_status[fname] = "skip_auto"
                    else:
                        review_status[fname] = "error"
                st.session_state["review_status"] = review_status

                st.success(f"✅ Selesai! {ok_count} file siap direview.")
                if st.button("Lanjut ke Review →", type="primary", use_container_width=True):
                    st.session_state["batch_step"] = 3
                    st.rerun()

    # ═══════════════════════════════════════════
    #  STEP 3 — REVIEW
    # ═══════════════════════════════════════════
    elif batch_step == 3:
        results       = st.session_state.get("batch_results", {})
        file_data     = st.session_state.get("batch_file_data", {})
        review_status = st.session_state.get("review_status", {})

        if not results:
            st.warning("Tidak ada hasil. Kembali ke proses.")
            if st.button("← Proses Ulang"):
                st.session_state["batch_step"] = 2
                st.rerun()
        else:
            # ── Toolbar Review ──
            ok_files    = [fn for fn,r in results.items() if r["status"]=="ok"]
            skip_files  = [fn for fn,r in results.items() if r["status"]=="skipped"]
            err_files   = [fn for fn,r in results.items() if r["status"]=="error"]
            kept_count  = sum(1 for fn,s in review_status.items() if s=="keep")
            excl_count  = sum(1 for fn,s in review_status.items() if s in ("exclude","error","skip_auto"))

            st.markdown(f"""<div class='card'>
            <div class='card-title'>🔍 Review Hasil — Pilih file yang ingin didownload</div>
            <div class='stat-row'>
                <div class='stat-box'><div class='stat-num c-green'>{kept_count}</div><div class='stat-lbl'>Akan Didownload</div></div>
                <div class='stat-box'><div class='stat-num c-amber'>{len(ok_files)}</div><div class='stat-lbl'>Berhasil Diproses</div></div>
                <div class='stat-box'><div class='stat-num c-gray'>{len(skip_files)}</div><div class='stat-lbl'>Di-Skip (PNG Transparan)</div></div>
                <div class='stat-box'><div class='stat-num c-red'>{len(err_files)}</div><div class='stat-lbl'>Gagal</div></div>
            </div>
            </div>""", unsafe_allow_html=True)

            # Tombol aksi bulk
            b1,b2,b3,b4 = st.columns(4)
            with b1:
                if st.button("✅ Pilih Semua", use_container_width=True):
                    for fn in ok_files:
                        review_status[fn] = "keep"
                    st.session_state["review_status"] = review_status
                    st.rerun()
            with b2:
                if st.button("❌ Batalkan Semua", use_container_width=True):
                    for fn in ok_files:
                        review_status[fn] = "exclude"
                    st.session_state["review_status"] = review_status
                    st.rerun()
            with b3:
                if st.button("← Proses Ulang Semua", use_container_width=True):
                    st.session_state["batch_step"] = 2
                    st.rerun()
            with b4:
                if st.button("Lanjut ke Download →", type="primary", use_container_width=True):
                    st.session_state["batch_step"] = 4
                    st.rerun()

            st.markdown("<hr class='section'>", unsafe_allow_html=True)

            # ── Filter ──
            filter_opt = st.radio("Tampilkan:", ["Semua Berhasil","Perlu Diperiksa","Semua"], horizontal=True)

            # ── Gallery Review ──
            mode_css = {"white":"m-white","dark":"m-dark","color":"m-color",
                        "complex":"m-complex","skip":"m-skip","?":"m-skip"}
            mode_lbl_r = {"white":"Putih","dark":"Bg Hitam","color":"Berwarna",
                          "complex":"Kompleks","skip":"Skip","?":"Error"}

            for fname in sorted(ok_files):
                r = results[fname]
                current_status = review_status.get(fname, "keep")

                # Filter
                if filter_opt == "Perlu Diperiksa" and current_status == "keep":
                    continue

                rgba_img  = r["img"]
                used_mode = r["mode"]
                preview   = make_preview(rgba_img)

                # Border warna sesuai status
                border_col = {
                    "keep":     "rgba(52,211,153,.4)",
                    "exclude":  "rgba(107,114,128,.25)",
                    "reprocess":"rgba(251,191,36,.4)",
                }.get(current_status, "rgba(107,114,128,.2)")

                status_icon = {"keep":"✅","exclude":"🚫","reprocess":"🔄"}.get(current_status,"")

                # ── Satu baris per file ──
                st.markdown(f"""
                <div style='border:1px solid {border_col};border-radius:12px;
                     padding:4px 12px 0 12px;margin-bottom:8px;
                     background:rgba(255,255,255,.02)'>
                    <div style='font-size:.7rem;font-weight:700;color:#6b7280;
                         text-transform:uppercase;letter-spacing:.5px;padding:6px 0 2px'>
                        {status_icon} {fname}
                        &nbsp;<span class='mode-pill {mode_css.get(used_mode,"m-white")}'>
                        {mode_lbl_r.get(used_mode,used_mode)}</span>
                        &nbsp;<span style='color:#4b5563;font-weight:400;text-transform:none;letter-spacing:0'>
                        {rgba_img.width}×{rgba_img.height}px</span>
                    </div>
                </div>""", unsafe_allow_html=True)

                img_col, info_col, action_col = st.columns([2, 3, 2])

                with img_col:
                    st.image(preview, use_container_width=True)

                with info_col:
                    # Preview bg gelap
                    on_dark = composite(rgba_img, (28, 28, 28))
                    st.image(on_dark, use_container_width=True,
                             caption="Preview bg gelap")

                with action_col:
                    keep_btn    = st.button("✅ Simpan",    key=f"keep_{fname}", use_container_width=True)
                    exclude_btn = st.button("🚫 Keluarkan", key=f"excl_{fname}", use_container_width=True)

                    if keep_btn:
                        review_status[fname] = "keep"
                        st.session_state["review_status"] = review_status
                        st.rerun()
                    if exclude_btn:
                        review_status[fname] = "exclude"
                        st.session_state["review_status"] = review_status
                        st.rerun()

                    # Download satu file langsung dari review
                    st.download_button(
                        "⬇️ Download",
                        data=to_png_bytes(rgba_img),
                        file_name=Path(fname).stem + ".png",
                        mime="image/png",
                        key=f"dl_{fname}",
                        use_container_width=True,
                    )

                    # Reprocess per-file
                    with st.expander("🔄 Proses Ulang"):
                        rp_mode = st.selectbox(
                            "Mode", ["auto","white","dark","color","complex"],
                            key=f"rm_{fname}")
                        rp_threshold = st.slider(
                            "Threshold Putih", 100, 250, white_threshold, 5,
                            key=f"rt_{fname}")
                        rp_dark = st.slider(
                            "Threshold Gelap", 20, 150, dark_threshold, 5,
                            key=f"rd_{fname}")
                        rp_tol = st.slider(
                            "Toleransi Warna", 10, 80, int(color_tolerance), 2,
                            key=f"rc_{fname}")
                        rp_blur = st.select_slider(
                            "Blur", [1,3,5,7], blur_k,
                            key=f"rb_{fname}")
                        rp_alpha = st.slider(
                            "Min Alpha", 0, 40, min_alpha, 1,
                            key=f"ra_{fname}")

                        if st.button("🚀 Terapkan", key=f"rp_{fname}",
                                     use_container_width=True):
                            fbytes = file_data.get(fname, b"")
                            if fbytes:
                                new_res = process_image(
                                    fbytes, rp_mode,
                                    rp_threshold, rp_dark, float(rp_tol),
                                    rp_blur, rp_alpha, border_px, False)
                                results[fname] = new_res
                                review_status[fname] = "keep" if new_res["status"]=="ok" else "error"
                                st.session_state["batch_results"]  = results
                                st.session_state["review_status"]  = review_status
                                st.rerun()

                st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)

            # File error / skip info
            if err_files:
                with st.expander(f"❌ {len(err_files)} File Gagal"):
                    for fn in err_files:
                        st.markdown(f"- `{fn}` → {results[fn].get('message','?')}")
            if skip_files:
                with st.expander(f"⚡ {len(skip_files)} File Di-Skip (sudah transparan)"):
                    for fn in skip_files:
                        st.markdown(f"- `{fn}`")

            st.markdown("<hr class='section'>", unsafe_allow_html=True)
            if st.button("Lanjut ke Download →", type="primary", use_container_width=True):
                st.session_state["batch_step"] = 4
                st.rerun()

    # ═══════════════════════════════════════════
    #  STEP 4 — DOWNLOAD
    # ═══════════════════════════════════════════
    elif batch_step == 4:
        results       = st.session_state.get("batch_results", {})
        review_status = st.session_state.get("review_status", {})

        kept = {fn: r for fn,r in results.items()
                if review_status.get(fn) == "keep" and r["status"]=="ok"}

        excluded = sum(1 for s in review_status.values() if s in ("exclude","skip_auto","error"))

        st.markdown(f"""<div class='card'>
        <div class='card-title'>⬇️ Download Hasil Final</div>
        <div class='stat-row'>
            <div class='stat-box'><div class='stat-num c-green'>{len(kept)}</div><div class='stat-lbl'>File Disertakan</div></div>
            <div class='stat-box'><div class='stat-num c-gray'>{excluded}</div><div class='stat-lbl'>Dikecualikan</div></div>
        </div>
        </div>""", unsafe_allow_html=True)

        if kept:
            with st.spinner("📦 Membuat ZIP..."):
                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf,"w", zipfile.ZIP_DEFLATED) as zf:
                    for fn, r in kept.items():
                        out_name = Path(fn).stem + ".png"
                        zf.writestr(out_name, to_png_bytes(r["img"]))
                zip_buf.seek(0)
                zip_mb = len(zip_buf.getvalue()) / 1024 / 1024

            st.markdown(f"""<div class='info-box info-green'>
            ✅ ZIP siap — {len(kept)} file PNG transparan, ukuran {zip_mb:.1f} MB
            </div>""", unsafe_allow_html=True)

            st.download_button(
                label=f"⬇️  Download Hasil ({len(kept)} file — {zip_mb:.1f} MB)",
                data=zip_buf.getvalue(),
                file_name="hasil_tanda_tangan.zip",
                mime="application/zip",
                use_container_width=True,
            )
        else:
            st.markdown("""<div class='info-box info-yellow'>
            ⚠️ Tidak ada file yang disertakan. Kembali ke Review dan tandai file yang ingin didownload.
            </div>""", unsafe_allow_html=True)

        st.markdown("<hr class='section'>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Kembali ke Review", use_container_width=True):
                st.session_state["batch_step"] = 3
                st.rerun()
        with col2:
            if st.button("🔁 Mulai Batch Baru", use_container_width=True):
                for key in ["batch_step","batch_results","batch_file_data","review_status"]:
                    st.session_state.pop(key, None)
                st.session_state["batch_step"] = 1
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3 — PANDUAN
# ══════════════════════════════════════════════════════════════════════════════

with tab_guide:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
## 📖 Panduan Lengkap

### 🏷️ 4 Kondisi Tanda Tangan yang Ditangani

| # | Kondisi | Mode | Cara Kerja |
|---|---------|------|-----------|
| 1 | **Background Hitam** (PNG/foto, tinta biru/putih/warna lain) | `dark` | Logika **TERBALIK** — piksel gelap dihapus, piksel terang (tinta) dipertahankan |
| 2 | **Kertas Putih / HVS** | `white` | Threshold kecerahan — piksel terang → transparan |
| 3 | **Background Kompleks** (berwarna, bergaris, ada logo/watermark/bayangan) | `complex` | Adaptive threshold + LAB color-distance + hapus garis horizontal |
| 4 | **PNG sudah Transparan** | `skip` | Dilewati otomatis — tidak diproses agar tanda tangan tidak rusak |

---

### 🚀 Alur Batch Processing (4 Langkah)

1. **Upload** → multiple files atau ZIP
2. **Proses** → semua file diproses otomatis dengan parameter dari sidebar
3. **Review** → lihat hasil satu per satu, tandai mana yang OK / dikeluarkan / diproses ulang
4. **Download** → hanya file yang sudah diapprove yang masuk ZIP

---

### ⚙️ Panduan Parameter

#### Untuk Background Hitam
- **Threshold Gelap** = parameter utama
- Turunkan (40–50) jika tanda tangan tipis/hilang
- Naikkan (60–80) jika background hitam masih tersisa
- Untuk tinta BIRU di background hitam: Threshold Gelap 50–60 biasanya optimal

#### Untuk Kertas Putih
- **Threshold Putih** = parameter utama
- Naikkan (210–230) jika background masih tersisa
- Turunkan (170–190) jika tanda tangan ikut terhapus

#### Untuk Kertas Berwarna / Kompleks
- **Toleransi Warna** = parameter utama
- Naikkan (45–65) jika background berwarna masih ada
- Turunkan (22–32) jika tanda tangan (terutama tinta biru) ikut terhapus
- Untuk tinta biru tipis di kertas berwarna: Toleransi 25–30 + Min Alpha = 0

#### Untuk Background Kompleks (watermark, logo, bayangan)
- Gunakan mode `complex`
- Naikkan Blur ke 5–7 untuk kurangi texture kertas
- Toleransi 40–55 biasanya cocok
- Jika masih kurang bersih, pertimbangkan rembg AI

---

### 🛑 Fitur Skip PNG Transparan

Aktifkan toggle **"Skip PNG Transparan"** (sidebar) agar:
- File PNG yang sudah punya background transparan → **tidak diproses**
- Ini mencegah tanda tangan yang sudah bersih malah rusak ketika parameter dinaikkan
- File yang di-skip tetap muncul di review dengan label "Skip"

---

### 💡 Tips Tanda Tangan Biru di Background Hitam

Ini kasus yang paling tricky. Rekomendasi:
```
Mode         : dark (Background Hitam)
Threshold Gelap : 45–55
Blur         : 3
Min Alpha    : 5
```
Jika tinta biru sangat terang: Threshold Gelap 40–50
Jika tinta biru agak gelap/tua: Threshold Gelap 55–65

---

### 📋 Format yang Didukung

- Input: **JPG, JPEG, PNG** (single atau dalam ZIP)
- Output: **PNG transparan** (semua file, apapun format inputnya)
- Upload ZIP: otomatis diekstrak, file dalam subfolder ZIP juga terbaca
""")


# ══════════════════════════════════════════════════════════════════════════════
#  Fix: pastikan batch_step selalu ada
# ══════════════════════════════════════════════════════════════════════════════

if "batch_step" not in st.session_state:
    st.session_state["batch_step"] = 1
