"""
================================================================================
  SIGNATURE BACKGROUND REMOVER — Streamlit Dashboard v1.0
  Jalankan: streamlit run app.py
================================================================================
"""

import os
import io
import cv2
import time
import zipfile
import tempfile
import numpy as np
import streamlit as st
from PIL import Image
from pathlib import Path


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title  = "Signature BG Remover",
    page_icon   = "✍️",
    layout      = "wide",
    initial_sidebar_state = "expanded",
)


# ══════════════════════════════════════════════════════════════════════════════
#  CUSTOM CSS
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* ── Background ── */
.stApp {
    background: linear-gradient(135deg, #0f0f1a 0%, #12121f 50%, #0d1117 100%);
    min-height: 100vh;
}

/* ── Header Banner ── */
.header-banner {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border: 1px solid rgba(99, 179, 237, 0.2);
    border-radius: 20px;
    padding: 32px 40px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.header-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(99,179,237,0.08) 0%, transparent 70%);
    border-radius: 50%;
}
.header-title {
    font-size: 2rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
}
.header-subtitle {
    font-size: 1rem;
    color: #90cdf4;
    margin: 0;
    font-weight: 500;
}
.badge-row {
    display: flex;
    gap: 10px;
    margin-top: 18px;
    flex-wrap: wrap;
}
.badge {
    background: rgba(99,179,237,0.12);
    border: 1px solid rgba(99,179,237,0.25);
    color: #90cdf4;
    padding: 5px 14px;
    border-radius: 100px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.3px;
}

/* ── Cards ── */
.card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    backdrop-filter: blur(10px);
}
.card-title {
    font-size: 0.85rem;
    font-weight: 700;
    color: #63b3ed;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ── Step indicators ── */
.step-row {
    display: flex;
    gap: 0;
    margin-bottom: 28px;
}
.step-item {
    flex: 1;
    text-align: center;
    position: relative;
}
.step-item::after {
    content: '';
    position: absolute;
    top: 20px;
    right: -50%;
    width: 100%;
    height: 2px;
    background: rgba(255,255,255,0.1);
    z-index: 0;
}
.step-item:last-child::after { display: none; }
.step-circle {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: rgba(99,179,237,0.1);
    border: 2px solid rgba(99,179,237,0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 8px;
    font-size: 1.1rem;
    position: relative;
    z-index: 1;
}
.step-circle.active {
    background: rgba(99,179,237,0.25);
    border-color: #63b3ed;
    box-shadow: 0 0 20px rgba(99,179,237,0.3);
}
.step-label {
    font-size: 0.72rem;
    color: #718096;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.step-label.active { color: #90cdf4; }

/* ── Stat boxes ── */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin: 16px 0;
}
.stat-box {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 16px;
    text-align: center;
}
.stat-number {
    font-size: 1.8rem;
    font-weight: 800;
    color: #63b3ed;
    line-height: 1;
    font-family: 'JetBrains Mono', monospace;
}
.stat-label {
    font-size: 0.72rem;
    color: #718096;
    margin-top: 4px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.stat-box.success .stat-number { color: #68d391; }
.stat-box.warning .stat-number { color: #f6ad55; }
.stat-box.error   .stat-number { color: #fc8181; }

/* ── Mode tag ── */
.mode-tag {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 100px;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-left: 8px;
}
.mode-white  { background: rgba(255,255,255,0.1); color: #e2e8f0; }
.mode-color  { background: rgba(246,173,85,0.15);  color: #f6ad55; }
.mode-lined  { background: rgba(104,211,145,0.15); color: #68d391; }
.mode-auto   { background: rgba(99,179,237,0.15);  color: #63b3ed; }

/* ── Divider ── */
.section-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.07);
    margin: 24px 0;
}

/* ── Alert boxes ── */
.alert-info {
    background: rgba(99,179,237,0.08);
    border-left: 3px solid #63b3ed;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    font-size: 0.85rem;
    color: #90cdf4;
    margin: 12px 0;
}
.alert-success {
    background: rgba(104,211,145,0.08);
    border-left: 3px solid #68d391;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    font-size: 0.85rem;
    color: #9ae6b4;
    margin: 12px 0;
}
.alert-warning {
    background: rgba(246,173,85,0.08);
    border-left: 3px solid #f6ad55;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    font-size: 0.85rem;
    color: #fbd38d;
    margin: 12px 0;
}

/* ── Image comparison label ── */
.img-label {
    text-align: center;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #718096;
    margin-top: 8px;
}

/* ── Sidebar override ── */
[data-testid="stSidebar"] {
    background: rgba(15, 15, 30, 0.95);
    border-right: 1px solid rgba(255,255,255,0.07);
}
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #63b3ed;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 700;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    letter-spacing: 0.3px !important;
    transition: all 0.2s ease !important;
}
.stDownloadButton > button {
    border-radius: 10px !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #2b6cb0, #1a4a8a) !important;
    border: none !important;
    color: white !important;
    padding: 12px 24px !important;
}

/* ── Tab styling ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: rgba(255,255,255,0.03);
    padding: 6px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.07);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-weight: 600;
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    border-radius: 12px;
    overflow: hidden;
}

/* ── Metric ── */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 16px;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  CORE FUNCTIONS (same as remove_bg_advanced.py)
# ══════════════════════════════════════════════════════════════════════════════

def sample_background_color(img_bgr, border_px=8):
    h, w = img_bgr.shape[:2]
    b = min(border_px, h // 4, w // 4)
    regions = [img_bgr[:b,:w], img_bgr[h-b:,:w], img_bgr[:h,:b], img_bgr[:h,w-b:]]
    samples = np.vstack([r.reshape(-1, 3) for r in regions])
    return np.median(samples, axis=0)

def is_background_white(bg_color_bgr, white_thresh=210):
    return bool(np.all(bg_color_bgr > white_thresh))

def detect_horizontal_lines(img_bgr, min_length_ratio=0.4):
    gray  = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    h, w  = gray.shape
    edges = cv2.Canny(gray, 30, 100, apertureSize=3)
    min_len = int(w * min_length_ratio)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 80, minLineLength=min_len, maxLineGap=15)
    if lines is None:
        return False
    h_count = sum(
        1 for l in lines
        if abs(np.degrees(np.arctan2(l[0][3]-l[0][1], l[0][2]-l[0][0]))) < 5
        or abs(np.degrees(np.arctan2(l[0][3]-l[0][1], l[0][2]-l[0][0]))) > 175
    )
    return h_count >= 3

def auto_detect_mode(img_bgr, border_px=8):
    bg_color  = sample_background_color(img_bgr, border_px)
    has_lines = detect_horizontal_lines(img_bgr)
    is_white  = is_background_white(bg_color)
    if has_lines:   return "lined"
    elif is_white:  return "white"
    else:           return "color"

def create_mask_white(img_bgr, threshold, blur_kernel):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    if blur_kernel > 1:
        k = blur_kernel if blur_kernel % 2 == 1 else blur_kernel + 1
        gray = cv2.GaussianBlur(gray, (k, k), 0)
    _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
    return mask

def create_mask_color(img_bgr, bg_color_bgr, tolerance, blur_kernel):
    img_lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    bg_pixel = bg_color_bgr.astype(np.uint8).reshape(1, 1, 3)
    bg_lab   = cv2.cvtColor(bg_pixel, cv2.COLOR_BGR2LAB).astype(np.float32).reshape(3)
    diff = img_lab - bg_lab
    dist = np.sqrt(np.sum(diff**2, axis=2))
    if blur_kernel > 1:
        k = blur_kernel if blur_kernel % 2 == 1 else blur_kernel + 1
        dist = cv2.GaussianBlur(dist, (k, k), 0)
    return np.where(dist < tolerance, 0, 255).astype(np.uint8)

def remove_horizontal_lines(img_bgr, mask):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    w    = gray.shape[1]
    line_kw = max(int(w * 0.5), 50)
    combined = np.zeros_like(mask)
    for t in range(1, 5):
        kernel   = cv2.getStructuringElement(cv2.MORPH_RECT, (line_kw, t))
        line_map = cv2.morphologyEx(cv2.bitwise_not(gray), cv2.MORPH_OPEN, kernel)
        _, lb    = cv2.threshold(line_map, 30, 255, cv2.THRESH_BINARY)
        combined = cv2.bitwise_or(combined, lb)
    dk = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    combined = cv2.dilate(combined, dk, iterations=1)
    cleaned  = mask.copy()
    cleaned[combined > 0] = 0
    return cleaned

def apply_morphology_cleanup(mask):
    k1   = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k1)
    k2   = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k2)
    k3   = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    mask = cv2.dilate(mask, k3, iterations=1)
    return mask

def cleanup_weak_alpha(arr, min_alpha):
    result = arr.copy()
    result[result[:, :, 3] < min_alpha, 3] = 0
    return result

def remove_background_advanced(img_bytes, mode="auto", color_tolerance=38,
                                white_threshold=200, blur_kernel=3,
                                min_alpha=10, border_sample_px=8):
    """Proses satu gambar dari bytes. Returns (PIL RGBA, mode_str)."""
    arr     = np.frombuffer(img_bytes, np.uint8)
    img_bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img_bgr is None:
        raise ValueError("Tidak dapat membaca gambar")

    img_rgb  = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    bg_color = sample_background_color(img_bgr, border_sample_px)
    detected = auto_detect_mode(img_bgr, border_sample_px) if mode == "auto" else mode

    if detected == "white":
        mask = create_mask_white(img_bgr, white_threshold, blur_kernel)
    elif detected == "color":
        mask = create_mask_color(img_bgr, bg_color, color_tolerance, blur_kernel)
    elif detected == "lined":
        if is_background_white(bg_color):
            mask = create_mask_white(img_bgr, white_threshold, blur_kernel)
        else:
            mask = create_mask_color(img_bgr, bg_color, color_tolerance, blur_kernel)
        mask = remove_horizontal_lines(img_bgr, mask)
    else:
        raise ValueError(f"Mode tidak dikenal: {detected}")

    mask     = apply_morphology_cleanup(mask)
    img_rgba = np.dstack([img_rgb, mask])
    if min_alpha > 0:
        img_rgba = cleanup_weak_alpha(img_rgba, min_alpha)
    return Image.fromarray(img_rgba, mode="RGBA"), detected


def pil_to_png_bytes(pil_img):
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    return buf.getvalue()

def composite_preview(rgba_img, bg=(255, 255, 255)):
    bg_img = Image.new("RGBA", rgba_img.size, (*bg, 255))
    return Image.alpha_composite(bg_img, rgba_img).convert("RGB")

def make_checkerboard(w, h, tile=20):
    bg = np.ones((h, w, 3), np.uint8) * 220
    for y in range(0, h, tile):
        for x in range(0, w, tile):
            if (x//tile + y//tile) % 2 == 0:
                bg[y:y+tile, x:x+tile] = 245
    return Image.fromarray(bg, "RGB")


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR — SETTINGS
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 20px 0 8px;'>
        <div style='font-size:2.5rem;'>✍️</div>
        <div style='font-weight:800; font-size:1rem; color:#e2e8f0; margin-top:4px;'>BG Remover</div>
        <div style='font-size:0.72rem; color:#4a5568; margin-top:2px; font-weight:600; text-transform:uppercase; letter-spacing:1px;'>Tanda Tangan v2.0</div>
    </div>
    <hr style='border-color:rgba(255,255,255,0.07); margin: 16px 0;'>
    """, unsafe_allow_html=True)

    st.markdown("### 🎛️ Mode Pemrosesan")
    mode_options = {
        "🤖 Auto-Detect (Rekomendasi)": "auto",
        "📄 Kertas Putih / HVS":         "white",
        "🎨 Kertas Berwarna":             "color",
        "📓 Kertas Bergaris":             "lined",
    }
    selected_mode_label = st.selectbox(
        "Pilih Mode",
        list(mode_options.keys()),
        index=0,
        help="Auto-detect akan mengenali jenis background secara otomatis untuk setiap file"
    )
    MODE = mode_options[selected_mode_label]

    st.markdown("<hr style='border-color:rgba(255,255,255,0.07);'>", unsafe_allow_html=True)
    st.markdown("### 🔧 Parameter")

    color_tolerance = st.slider(
        "Toleransi Warna (Background Berwarna)",
        min_value=10, max_value=80, value=38, step=2,
        help="Naikkan jika background berwarna masih tersisa. Turunkan jika tanda tangan ikut terhapus."
    )
    white_threshold = st.slider(
        "Threshold Kecerahan (Background Putih)",
        min_value=100, max_value=250, value=200, step=5,
        help="Naikkan jika background putih masih tersisa. Turunkan jika tanda tangan ikut terhapus."
    )
    blur_kernel = st.select_slider(
        "Blur / Noise Reduction",
        options=[1, 3, 5, 7], value=3,
        help="Nilai lebih besar = lebih banyak noise berkurang. Gunakan 5 atau 7 untuk scan berkualitas rendah."
    )
    min_alpha = st.slider(
        "Bersihkan Bayangan Sisa",
        min_value=0, max_value=40, value=10, step=1,
        help="Hapus piksel semi-transparan lemah. Naikkan jika ada sisa bayangan background."
    )

    st.markdown("<hr style='border-color:rgba(255,255,255,0.07);'>", unsafe_allow_html=True)
    st.markdown("### ℹ️ Panduan Cepat")
    st.markdown("""
    <div style='font-size:0.8rem; color:#718096; line-height:1.7;'>
    <b style='color:#90cdf4;'>Kertas Putih</b><br>
    Threshold ↑ jika masih ada background<br><br>
    <b style='color:#f6ad55;'>Kertas Berwarna</b><br>
    Toleransi ↑ jika background masih ada<br>
    Toleransi ↓ jika tanda tangan terkena<br><br>
    <b style='color:#68d391;'>Kertas Bergaris</b><br>
    Gunakan mode Auto atau Bergaris<br>
    Blur 5 bantu hapus noise garis
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="header-banner">
    <div class="header-title">✍️ Signature Background Remover</div>
    <div class="header-subtitle">Hapus background tanda tangan secara otomatis — putih, berwarna, maupun bergaris</div>
    <div class="badge-row">
        <span class="badge">📄 Kertas Putih</span>
        <span class="badge">🎨 Kertas Berwarna</span>
        <span class="badge">📓 Kertas Bergaris</span>
        <span class="badge">🤖 Auto-Detect</span>
        <span class="badge">⚡ Batch 500+ File</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════════════════════════

tab1, tab2, tab3 = st.tabs([
    "🔍  Uji Satu File",
    "⚡  Batch Processing",
    "📖  Panduan Penggunaan",
])


# ──────────────────────────────────────────────────────────────────────────────
#  TAB 1 — UJI SATU FILE
# ──────────────────────────────────────────────────────────────────────────────

with tab1:
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="alert-info">
    💡 <b>Disarankan:</b> Uji satu file terlebih dahulu untuk memastikan parameter sudah tepat
    sebelum memproses ratusan file sekaligus.
    </div>
    """, unsafe_allow_html=True)

    uploaded_single = st.file_uploader(
        "Upload satu file tanda tangan untuk diuji",
        type=["jpg", "jpeg", "png"],
        key="single_upload",
        label_visibility="visible"
    )

    if uploaded_single:
        img_bytes    = uploaded_single.read()
        arr          = np.frombuffer(img_bytes, np.uint8)
        img_bgr_orig = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        img_rgb_orig = cv2.cvtColor(img_bgr_orig, cv2.COLOR_BGR2RGB)
        orig_pil     = Image.fromarray(img_rgb_orig)
        h_px, w_px   = img_bgr_orig.shape[:2]

        # ── Analisis background ──
        bg_color  = sample_background_color(img_bgr_orig)
        bg_rgb    = bg_color[::-1].astype(int)
        is_white  = is_background_white(bg_color)
        has_lines = detect_horizontal_lines(img_bgr_orig)
        detected  = auto_detect_mode(img_bgr_orig)

        mode_label_map = {"white": "Putih/Terang", "color": "Berwarna", "lined": "Bergaris"}
        mode_color_map = {"white": "#e2e8f0", "color": "#f6ad55", "lined": "#68d391"}

        st.markdown(f"""
        <div class="card">
            <div class="card-title">📊 Hasil Analisis Gambar</div>
            <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:12px;">
                <div class="stat-box">
                    <div class="stat-number" style="font-size:1rem;">{w_px}×{h_px}</div>
                    <div class="stat-label">Resolusi (px)</div>
                </div>
                <div class="stat-box">
                    <div style="width:24px;height:24px;border-radius:6px;background:rgb({bg_rgb[0]},{bg_rgb[1]},{bg_rgb[2]});margin:0 auto 4px;border:1px solid rgba(255,255,255,0.2);"></div>
                    <div class="stat-label">Warna BG</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number" style="font-size:1rem; color:{'#68d391' if has_lines else '#fc8181'}">{'Ada ✓' if has_lines else 'Tidak'}</div>
                    <div class="stat-label">Garis Terdeteksi</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number" style="font-size:1rem; color:{mode_color_map[detected]}">{mode_label_map[detected]}</div>
                    <div class="stat-label">Mode Auto-Detect</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Proses ──
        col_btn, col_info = st.columns([2, 3])
        with col_btn:
            process_btn = st.button("🚀 Proses Sekarang", type="primary", use_container_width=True)

        if process_btn or "single_result" in st.session_state:
            if process_btn:
                with st.spinner("⏳ Memproses..."):
                    try:
                        result_img, used_mode = remove_background_advanced(
                            img_bytes,
                            mode            = MODE,
                            color_tolerance = color_tolerance,
                            white_threshold = white_threshold,
                            blur_kernel     = blur_kernel,
                            min_alpha       = min_alpha,
                        )
                        st.session_state["single_result"]    = result_img
                        st.session_state["single_used_mode"] = used_mode
                        st.session_state["single_filename"]  = Path(uploaded_single.name).stem
                    except Exception as e:
                        st.error(f"❌ Gagal memproses: {e}")
                        if "single_result" in st.session_state:
                            del st.session_state["single_result"]

            if "single_result" in st.session_state:
                result_img = st.session_state["single_result"]
                used_mode  = st.session_state["single_used_mode"]
                fname      = st.session_state["single_filename"]

                mode_labels = {"white":"Putih", "color":"Berwarna", "lined":"Bergaris", "auto":"Auto"}
                mode_colors = {"white":"mode-white", "color":"mode-color", "lined":"mode-lined", "auto":"mode-auto"}

                st.markdown(f"""
                <div class="alert-success">
                ✅ Berhasil diproses — Mode yang digunakan:
                <span class="mode-tag {mode_colors.get(used_mode,'mode-auto')}">{mode_labels.get(used_mode, used_mode)}</span>
                </div>
                """, unsafe_allow_html=True)

                # ── Tampilkan perbandingan ──
                st.markdown("#### Perbandingan Hasil")

                checker_bg = make_checkerboard(result_img.width, result_img.height)
                checker_bg_rgba = checker_bg.convert("RGBA")
                preview_checker = Image.alpha_composite(checker_bg_rgba, result_img).convert("RGB")
                preview_white   = composite_preview(result_img, (255, 255, 255))
                preview_dark    = composite_preview(result_img, (40, 40, 40))
                mask_arr        = np.array(result_img)[:,:,3]
                mask_pil        = Image.fromarray(mask_arr, "L").convert("RGB")

                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.image(orig_pil, use_container_width=True)
                    st.markdown('<div class="img-label">📷 Original</div>', unsafe_allow_html=True)
                with c2:
                    st.image(preview_checker, use_container_width=True)
                    st.markdown('<div class="img-label">🔲 Transparan</div>', unsafe_allow_html=True)
                with c3:
                    st.image(preview_white, use_container_width=True)
                    st.markdown('<div class="img-label">⬜ Bg Putih</div>', unsafe_allow_html=True)
                with c4:
                    st.image(preview_dark, use_container_width=True)
                    st.markdown('<div class="img-label">⬛ Bg Gelap</div>', unsafe_allow_html=True)

                # ── Download ──
                result_bytes = pil_to_png_bytes(result_img)
                st.download_button(
                    label     = f"⬇️  Download {fname}.png",
                    data      = result_bytes,
                    file_name = f"{fname}.png",
                    mime      = "image/png",
                    use_container_width=True,
                )

                # ── Tips ──
                st.markdown("<hr style='border-color:rgba(255,255,255,0.07);'>", unsafe_allow_html=True)
                st.markdown("**💡 Kurang puas dengan hasilnya? Coba ini:**")

                if used_mode in ("color", "lined"):
                    cc1, cc2 = st.columns(2)
                    with cc1:
                        st.info(f"Background masih tersisa? → Naikkan **Toleransi Warna** di sidebar (coba {min(color_tolerance+10, 80)})")
                    with cc2:
                        st.info(f"Tanda tangan ikut hilang? → Turunkan **Toleransi Warna** (coba {max(color_tolerance-10, 10)})")
                else:
                    cc1, cc2 = st.columns(2)
                    with cc1:
                        st.info(f"Background masih tersisa? → Naikkan **Threshold Kecerahan** (coba {min(white_threshold+10, 250)})")
                    with cc2:
                        st.info(f"Tanda tangan ikut hilang? → Turunkan **Threshold Kecerahan** (coba {max(white_threshold-10, 100)})")

    else:
        st.markdown("""
        <div style="text-align:center; padding: 60px 20px; color:#4a5568;">
            <div style="font-size:4rem; margin-bottom:16px;">📁</div>
            <div style="font-size:1rem; font-weight:600; color:#718096;">Upload file tanda tangan di atas</div>
            <div style="font-size:0.85rem; margin-top:8px;">Format yang didukung: JPG, JPEG, PNG</div>
        </div>
        """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
#  TAB 2 — BATCH PROCESSING
# ──────────────────────────────────────────────────────────────────────────────

with tab2:
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="alert-info">
    💡 Upload semua file sekaligus (pilih banyak file) atau satu file ZIP berisi semua tanda tangan.
    Parameter diambil dari sidebar kiri.
    </div>
    """, unsafe_allow_html=True)

    # ── Upload method ──
    upload_method = st.radio(
        "Metode upload:",
        ["📂 Multiple Files (JPG/PNG)", "🗜️ File ZIP"],
        horizontal=True,
    )

    if upload_method == "📂 Multiple Files (JPG/PNG)":
        batch_files = st.file_uploader(
            "Upload semua file tanda tangan",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key="batch_upload",
        )
        files_info = batch_files if batch_files else []

    else:  # ZIP
        zip_file = st.file_uploader(
            "Upload file ZIP berisi semua tanda tangan",
            type=["zip"],
            key="zip_upload",
        )
        files_info = []
        if zip_file:
            with tempfile.TemporaryDirectory() as tmpdir:
                zip_path = os.path.join(tmpdir, "upload.zip")
                with open(zip_path, "wb") as f:
                    f.write(zip_file.read())
                with zipfile.ZipFile(zip_path, "r") as zf:
                    names = [n for n in zf.namelist()
                             if Path(n).suffix.lower() in {".jpg",".jpeg",".png"}
                             and not n.startswith("__MACOSX")]
                    st.session_state["zip_names"]   = names
                    st.session_state["zip_bytes_raw"] = zip_file.getvalue()
                st.success(f"✅ ZIP diekstrak — {len(names)} file gambar ditemukan")
                files_info = names  # placeholder untuk count

    # ── File summary ──
    if files_info:
        total = len(files_info)
        st.markdown(f"""
        <div class="card">
            <div class="card-title">📦 Ringkasan Upload</div>
            <div class="stat-grid">
                <div class="stat-box success">
                    <div class="stat-number">{total}</div>
                    <div class="stat-label">File Ditemukan</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number" style="font-size:1rem; color:#a0aec0;">{MODE.upper()}</div>
                    <div class="stat-label">Mode Aktif</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number" style="font-size:1rem; color:#a0aec0;">{color_tolerance}</div>
                    <div class="stat-label">Toleransi</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        start_batch = st.button(
            f"⚡ Mulai Batch Processing ({total} file)",
            type="primary",
            use_container_width=True
        )

        if start_batch:
            st.markdown("<hr style='border-color:rgba(255,255,255,0.07);'>", unsafe_allow_html=True)
            st.markdown("#### ⏳ Sedang Memproses...")

            progress_bar  = st.progress(0)
            status_text   = st.empty()
            stats_placeholder = st.empty()

            results       = {}   # filename → bytes
            failed_list   = []
            mode_counter  = {"white": 0, "color": 0, "lined": 0}
            start_time    = time.time()

            # ── Kumpulkan file untuk diproses ──
            if upload_method == "📂 Multiple Files (JPG/PNG)":
                file_iter = [(f.name, f.read()) for f in files_info]
            else:
                # Ekstrak dari ZIP kembali
                zip_bytes_raw = st.session_state.get("zip_bytes_raw", b"")
                file_iter = []
                with zipfile.ZipFile(io.BytesIO(zip_bytes_raw), "r") as zf:
                    for name in st.session_state.get("zip_names", []):
                        file_iter.append((Path(name).name, zf.read(name)))

            total_files = len(file_iter)

            for idx, (fname, fbytes) in enumerate(file_iter):
                pct = int((idx / total_files) * 100)
                elapsed = time.time() - start_time
                eta = (elapsed / max(idx, 1)) * (total_files - idx)

                progress_bar.progress(pct)
                status_text.markdown(
                    f"**Memproses:** `{fname}` &nbsp;|&nbsp; "
                    f"**{idx+1}/{total_files}** &nbsp;|&nbsp; "
                    f"ETA: **{int(eta)}s**"
                )

                try:
                    result_img, used_mode = remove_background_advanced(
                        fbytes,
                        mode            = MODE,
                        color_tolerance = color_tolerance,
                        white_threshold = white_threshold,
                        blur_kernel     = blur_kernel,
                        min_alpha       = min_alpha,
                    )
                    out_name = Path(fname).stem + ".png"
                    results[out_name] = pil_to_png_bytes(result_img)
                    mode_counter[used_mode] = mode_counter.get(used_mode, 0) + 1
                except Exception as e:
                    failed_list.append((fname, str(e)))

            progress_bar.progress(100)
            elapsed_total = time.time() - start_time
            status_text.empty()

            # ── Ringkasan ──
            success_count = len(results)
            fail_count    = len(failed_list)

            st.markdown(f"""
            <div class="card">
                <div class="card-title">✅ Batch Selesai — {elapsed_total:.1f} detik</div>
                <div class="stat-grid">
                    <div class="stat-box success">
                        <div class="stat-number">{success_count}</div>
                        <div class="stat-label">Berhasil</div>
                    </div>
                    <div class="stat-box {'error' if fail_count > 0 else ''}">
                        <div class="stat-number">{fail_count}</div>
                        <div class="stat-label">Gagal</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" style="font-size:1rem;">
                            {elapsed_total/max(total_files,1):.1f}s
                        </div>
                        <div class="stat-label">Per File</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if MODE == "auto" and any(mode_counter.values()):
                st.markdown("**Distribusi Mode Auto-Detect:**")
                mc1, mc2, mc3 = st.columns(3)
                with mc1:
                    st.metric("📄 Putih/Terang", f"{mode_counter.get('white',0)} file")
                with mc2:
                    st.metric("🎨 Berwarna",     f"{mode_counter.get('color',0)} file")
                with mc3:
                    st.metric("📓 Bergaris",      f"{mode_counter.get('lined',0)} file")

            if fail_count > 0:
                with st.expander(f"⚠️ {fail_count} File Gagal — Klik untuk lihat detail"):
                    for fp, err in failed_list:
                        st.markdown(f"- `{fp}` → {err}")

            # ── Buat ZIP dan tombol download ──
            if results:
                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                    for out_name, out_bytes in results.items():
                        zf.writestr(out_name, out_bytes)
                zip_buf.seek(0)

                zip_size_mb = len(zip_buf.getvalue()) / (1024 * 1024)
                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button(
                    label     = f"⬇️  Download Semua Hasil ({success_count} file PNG, {zip_size_mb:.1f} MB)",
                    data      = zip_buf.getvalue(),
                    file_name = "hasil_tanda_tangan.zip",
                    mime      = "application/zip",
                    use_container_width=True,
                )

    else:
        st.markdown("""
        <div style="text-align:center; padding: 60px 20px; color:#4a5568;">
            <div style="font-size:4rem; margin-bottom:16px;">📦</div>
            <div style="font-size:1rem; font-weight:600; color:#718096;">Upload file tanda tangan di atas</div>
            <div style="font-size:0.85rem; margin-top:8px;">Pilih banyak file sekaligus atau upload satu file ZIP</div>
        </div>
        """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
#  TAB 3 — PANDUAN
# ──────────────────────────────────────────────────────────────────────────────

with tab3:
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    ## 📖 Panduan Penggunaan

    ### 🚀 Langkah-langkah

    #### 1. Atur Parameter (Sidebar Kiri)
    Sebelum memproses, pilih mode dan sesuaikan parameter di sidebar:
    - **Mode Auto-Detect** → biarkan sistem mengenali jenis background otomatis (paling mudah)
    - **Toleransi Warna** → untuk kertas berwarna, naikkan jika background masih tersisa
    - **Threshold Kecerahan** → untuk kertas putih, naikkan jika background masih terlihat

    #### 2. Uji Satu File Dulu (Tab "Uji Satu File")
    Sangat disarankan sebelum batch! Upload 1 file contoh, lihat hasilnya, dan sesuaikan
    parameter sampai hasil memuaskan.

    #### 3. Proses Semua File (Tab "Batch Processing")
    Upload semua file sekaligus atau dalam format ZIP, lalu klik tombol batch.
    Setelah selesai, download hasilnya sebagai ZIP.

    ---

    ### 🎛️ Penjelasan Mode

    | Mode | Cocok Untuk | Tips |
    |------|-------------|------|
    | 🤖 **Auto-Detect** | Campuran semua jenis | Rekomendasi untuk 500+ file campuran |
    | 📄 **Kertas Putih** | HVS, scan standard | Naikkan Threshold jika background kotor |
    | 🎨 **Kertas Berwarna** | Kuning, merah muda, hijau | Sesuaikan Toleransi dengan hati-hati |
    | 📓 **Kertas Bergaris** | Buku tulis, folio bergaris | Auto sudah otomatis mendeteksi garis |

    ---

    ### 🛠️ Troubleshooting

    **Background masih tersisa setelah diproses:**
    - Mode putih → Naikkan *Threshold Kecerahan* (coba 210–230)
    - Mode berwarna → Naikkan *Toleransi Warna* (coba 45–60)

    **Tanda tangan ikut terhapus:**
    - Mode putih → Turunkan *Threshold Kecerahan* (coba 170–190)
    - Mode berwarna → Turunkan *Toleransi Warna* (coba 20–30)

    **Tanda tangan biru sebagian hilang:**
    - Turunkan Toleransi ke 20–25
    - Atau ubah Bersihkan Bayangan Sisa ke 0

    **Garis kertas masih muncul:**
    - Pastikan mode **Kertas Bergaris** atau **Auto** aktif
    - Naikkan Blur ke 5

    **File gagal diproses:**
    - Coba buka file secara manual untuk cek apakah file rusak
    - Pastikan format JPG, JPEG, atau PNG

    ---

    ### 💡 Tips untuk Hasil Terbaik

    1. **Scan dengan resolusi minimal 300 DPI** untuk hasil paling bersih
    2. **Pastikan tanda tangan berada di tengah**, bukan mepet ke tepi gambar
    3. **Uji 3-5 sampel** dari tiap jenis kertas sebelum batch
    4. Untuk **tanda tangan biru tipis** di kertas berwarna, gunakan Toleransi 25–35
    5. **File dengan background sangat gelap** (navy, hitam, coklat tua) mungkin sulit —
       coba turunkan Toleransi ke 15–20

    ---

    ### 📋 Format yang Didukung

    | Input | Output |
    |-------|--------|
    | JPG / JPEG | PNG (dengan transparansi) |
    | PNG | PNG (dengan transparansi) |
    | ZIP berisi JPG/PNG | ZIP berisi PNG |

    """)

    st.markdown("""
    <div class="alert-info" style="margin-top:24px;">
    <b>📌 Catatan:</b> Semua file diproses di browser/server lokal Anda.
    Tidak ada data yang dikirim ke server eksternal.
    </div>
    """, unsafe_allow_html=True)
