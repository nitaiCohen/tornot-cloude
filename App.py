import streamlit as st
import pandas as pd
from datetime import timedelta, date
from supabase import create_client, Client

# ─────────────────────────────────────────────
# PAGE CONFIG & CSS
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="מערכת ניהול תורנויות",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;800;900&family=Rubik:wght@400;500;700;900&display=swap');

:root {
    --bg-primary:    #071018;
    --bg-secondary:  #0d1b2e;
    --bg-card:       rgba(255,255,255,.04);
    --accent:        #2d7dd2;
    --accent-light:  #5ba3f5;
    --accent-glow:   rgba(45,125,210,.25);
    --gold:          #f5c842;
    --gold-dim:      rgba(245,200,66,.15);
    --text-primary:  #e8f0fe;
    --text-secondary:#8baacf;
    --text-muted:    rgba(139,170,207,.5);
    --border:        rgba(45,125,210,.2);
    --border-hover:  rgba(45,125,210,.5);
    --success:       #22c55e;
    --danger:        #ef4444;
    --warning:       #fb923c;
}

html, body, [class*="css"] {
    font-family: 'Heebo', sans-serif;
    direction: rtl;
}

.stApp {
    background: var(--bg-primary);
    min-height: 100vh;
    position: relative;
}
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 50% at 20% 10%, rgba(45,125,210,.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(245,200,66,.06) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
}

.main-header {
    background: linear-gradient(135deg, #0d2040 0%, #1a3a6e 40%, #0d2040 100%);
    border-radius: 20px;
    padding: 36px 44px;
    margin-bottom: 32px;
    border: 1px solid var(--border);
    box-shadow: 0 0 60px var(--accent-glow), inset 0 1px 0 rgba(255,255,255,.08);
    text-align: center;
    position: relative;
    overflow: hidden;
}
.main-header::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: conic-gradient(transparent 0deg, rgba(45,125,210,.06) 90deg, transparent 180deg);
    animation: rotate 20s linear infinite;
}
@keyframes rotate { to { transform: rotate(360deg); } }
.main-header h1 {
    color: var(--text-primary);
    font-size: 2.5rem;
    font-weight: 900;
    margin: 0;
    font-family: 'Rubik', sans-serif;
    letter-spacing: -0.5px;
    position: relative;
}
.main-header p {
    color: var(--text-secondary);
    margin: 8px 0 0;
    font-size: 1rem;
    letter-spacing: 1px;
    position: relative;
}

.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 22px;
    backdrop-filter: blur(12px);
    transition: border-color .25s, box-shadow .25s;
}
.card:hover {
    border-color: var(--border-hover);
    box-shadow: 0 4px 24px var(--accent-glow);
}
.card-title {
    color: var(--accent-light);
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
    text-align: right;
    letter-spacing: .5px;
}

.week-nav {
    background: linear-gradient(135deg, rgba(45,125,210,.1), rgba(45,125,210,.05));
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 16px 22px;
    margin-bottom: 20px;
    text-align: center;
}
.week-label { color: var(--text-muted); font-size: .8rem; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 4px; }
.week-dates { color: var(--text-primary); font-size: 1.25rem; font-weight: 800; font-family: 'Rubik', sans-serif; }

.roster-table { width: 100%; border-collapse: collapse; direction: rtl; }
.roster-table th {
    background: rgba(45,125,210,.3);
    color: var(--accent-light);
    font-weight: 700;
    padding: 13px 18px;
    font-size: .82rem;
    text-align: right;
    border-bottom: 2px solid rgba(45,125,210,.5);
    text-transform: uppercase;
    letter-spacing: 1px;
}
.roster-table td {
    padding: 11px 18px;
    border-bottom: 1px solid rgba(255,255,255,.045);
    color: var(--text-primary);
    font-size: .88rem;
    text-align: right;
    vertical-align: middle;
    transition: background .15s;
}
.roster-table tr:hover td { background: rgba(45,125,210,.08); }
.roster-table .pos-cell { color: var(--accent-light); font-weight: 700; font-size: .9rem; }
.roster-table .shift-cell { color: var(--text-secondary); font-size: .8rem; }
.roster-table tr:last-child td { border-bottom: none; }

.badge { display:inline-block; padding:4px 14px; border-radius:20px; font-size:.76rem; font-weight:700; letter-spacing:.5px; }
.badge-done { background:rgba(34,197,94,.12);  color:#4ade80; border:1px solid rgba(34,197,94,.4); }
.badge-now  { background:rgba(45,125,210,.15); color:#60a5fa; border:1px solid rgba(45,125,210,.4); }
.badge-plan { background:rgba(251,146,60,.12); color:#fb923c; border:1px solid rgba(251,146,60,.4); }
.admin-badge {
    background: linear-gradient(90deg, #7c3aed, #4f46e5);
    color: white;
    padding: 5px 16px;
    border-radius: 20px;
    font-size: .78rem;
    font-weight: 700;
    box-shadow: 0 2px 12px rgba(124,58,237,.4);
}

.info-box    { background:rgba(45,125,210,.1);   border:1px solid rgba(45,125,210,.35);  border-radius:12px; padding:14px 20px; color:var(--text-secondary); font-size:.88rem; margin:12px 0; text-align:right; }
.success-box { background:rgba(34,197,94,.08);  border:1px solid rgba(34,197,94,.35);   border-radius:12px; padding:14px 20px; color:#4ade80; font-size:.88rem; margin:12px 0; text-align:right; }
.error-box   { background:rgba(239,68,68,.08);  border:1px solid rgba(239,68,68,.35);   border-radius:12px; padding:14px 20px; color:#f87171; font-size:.88rem; margin:12px 0; text-align:right; }
.warning-box { background:rgba(251,146,60,.08); border:1px solid rgba(251,146,60,.35);  border-radius:12px; padding:14px 20px; color:#fb923c; font-size:.88rem; margin:12px 0; text-align:right; }

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#071018 0%,#0d1b2e 100%) !important;
    border-left: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * { direction: rtl; }
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 { color: var(--text-primary) !important; }

.stButton > button {
    border-radius: 12px !important;
    font-family: 'Heebo', sans-serif !important;
    font-weight: 700 !important;
    transition: all .2s !important;
    border: 1px solid var(--border) !important;
}
.stButton > button:hover {
    border-color: var(--accent) !important;
    box-shadow: 0 0 20px var(--accent-glow) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1d5fa8, #2d7dd2) !important;
    border-color: var(--accent) !important;
    box-shadow: 0 4px 20px var(--accent-glow) !important;
}

input, select, textarea { direction: rtl !important; text-align: right !important; }
hr { border-color: rgba(255,255,255,.06) !important; }

.footer {
    margin-top: 48px;
    padding: 28px 36px;
    text-align: center;
    background: linear-gradient(135deg, rgba(45,125,210,.06), rgba(245,200,66,.04));
    border: 1px solid var(--border);
    border-radius: 20px;
    position: relative;
    overflow: hidden;
}
.footer::before {
    content: '🛡️';
    position: absolute;
    font-size: 8rem;
    opacity: .03;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
}
.footer-name {
    color: var(--gold);
    font-size: 1.1rem;
    font-weight: 800;
    font-family: 'Rubik', sans-serif;
    letter-spacing: .5px;
    margin-bottom: 6px;
}
.footer-phone {
    color: var(--text-secondary);
    font-size: .95rem;
    direction: ltr;
    letter-spacing: 2px;
    font-weight: 600;
    margin-bottom: 8px;
}
.footer-line {
    color: var(--text-muted);
    font-size: .75rem;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# קבועים
# ─────────────────────────────────────────────
ADMIN_PASSWORD = "1234"
DAYS_HE = ["שני","שלישי","רביעי","חמישי","שישי","שבת","ראשון"]

DEFAULT_ROSTER_ROWS = [
    ("ש\"ג מפקד חיפה",             "02:00-06:00 & 14:00-18:00"),
    ("ש\"ג מפקד חיפה",             "06:00-10:00 & 18:00-22:00"),
    ("ש\"ג מפקד חיפה",             "10:00-14:00 & 22:00-02:00"),
    ("סגן מפקד חיפה",              "02:00-06:00 & 14:00-18:00"),
    ("סגן מפקד חיפה",              "06:00-10:00 & 18:00-22:00"),
    ("סגן מפקד חיפה",              "10:00-14:00 & 22:00-02:00"),
    ("עמדה אחורית חיפה",           "02:00-06:00 & 14:00-18:00"),
    ("עמדה אחורית חיפה",           "06:00-10:00 & 18:00-22:00"),
    ("עמדה אחורית חיפה",           "10:00-14:00 & 22:00-02:00"),
    ("ש\"ג מפקדת רכבת",            "06:00-10:00 & 14:00-18:00"),
    ("ש\"ג מפקדת רכבת",            "10:00-14:00 & 18:00-22:00"),
    ("סגן רכבת",                   "06:00-10:00 & 14:00-18:00"),
    ("סגן רכבת",                   "10:00-14:00 & 18:00-22:00"),
    ("מחפה קדמי חיפה (ללא סופ\"ש)","18:00-22:00"),
    ("מחפה קדמי חיפה (ללא סופ\"ש)","22:00-02:00"),
    ("מחפה קדמי חיפה (ללא סופ\"ש)","02:00-06:00"),
    ("מחפה אחורי חיפה (סופ\"ש)",   "02:00-06:00 & 14:00-18:00"),
    ("מחפה אחורי חיפה (סופ\"ש)",   "06:00-10:00 & 18:00-22:00"),
    ("מחפה אחורי חיפה (סופ\"ש)",   "10:00-14:00 & 22:00-02:00"),
    ("חשבשבת 1",                   "06:00-18:00"),
    ("חשבשבת 2",                   "18:00-06:00"),
    ("מאייש חול",                  "א-ה (תורן 1)"),
    ("מאייש חול",                  "א-ה (תורן 2)"),
    ("מאייש סופ\"ש",               "ה-א (תורן 1)"),
    ("מאייש סופ\"ש",               "ה-א (תורן 2)"),
    ("כונן סמל",                   "24/7"),
    ("כונן רב\"ט",                 "24/7"),
]

# ─────────────────────────────────────────────
# Supabase
# ─────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

sb = get_supabase()

# ─────────────────────────────────────────────
# עזר: תאריכים
# ─────────────────────────────────────────────
def get_week_monday(d: date) -> date:
    return d - timedelta(days=d.weekday())

def get_week_dates(monday: date):
    return [monday + timedelta(days=i) for i in range(7)]

def fmt(d: date) -> str:
    return d.strftime("%d/%m/%Y")

def is_future(monday: date) -> bool:
    return monday > get_week_monday(date.today())

def is_current(monday: date) -> bool:
    return monday == get_week_monday(date.today())

def week_status(monday: date) -> str:
    if is_future(monday):   return "מתוכנן"
    if is_current(monday):  return "נוכחי"
    return "בוצע"

def row_key(position: str, shift: str) -> str:
    return f"{position}||{shift}"

# ─────────────────────────────────────────────
# Supabase — שיבוצים
# ─────────────────────────────────────────────
import json

@st.cache_data(ttl=30)
def load_week(monday_iso: str) -> dict:
    res = sb.table("roster").select("*").eq("week_monday", monday_iso).execute()
    result = {}
    for r in (res.data or []):
        key = row_key(r["position"], r["shift"])
        try:
            result[key] = json.loads(r["assignments"])
        except Exception:
            result[key] = []
    return result

@st.cache_data(ttl=60)
def load_all() -> list:
    res = sb.table("roster").select("*").execute()
    return res.data or []

def save_row(monday: date, position: str, shift: str, assignments: list):
    data = {
        "week_monday": monday.isoformat(),
        "position":    position,
        "shift":       shift,
        "assignments": json.dumps(assignments, ensure_ascii=False),
    }
    sb.table("roster").upsert(data, on_conflict="week_monday,position,shift").execute()
    st.cache_data.clear()

def delete_row(monday: date, position: str, shift: str):
    sb.table("roster")\
      .delete()\
      .eq("week_monday", monday.isoformat())\
      .eq("position", position)\
      .eq("shift", shift)\
      .execute()
    st.cache_data.clear()

# ─────────────────────────────────────────────
# עזר: עיבוד assignments לתצוגה
# ─────────────────────────────────────────────
def assignments_display(assignments: list) -> str:
    if not assignments:
        return "—"
    parts = []
    for a in assignments:
        name = a.get("name", "")
        frm  = a.get("from", "")
        to   = a.get("to", "")
        if frm and to:
            parts.append(f"{name} ({frm}–{to})")
        else:
            parts.append(name)
    return " / ".join(parts)

# ─────────────────────────────────────────────
# Session State
# ─────────────────────────────────────────────
for key, val in [
    ("week_offset", 0),
    ("is_admin", False),
    ("edit_key", None),
    ("edit_pos", None),
    ("edit_shift", None),
    ("roster_rows", list(DEFAULT_ROSTER_ROWS)),
]:
    if key not in st.session_state:
        st.session_state[key] = val

current_monday = get_week_monday(date.today()) + timedelta(weeks=st.session_state.week_offset)
week_dates     = get_week_dates(current_monday)
ROSTER_ROWS    = st.session_state.roster_rows

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛡️ מערכת תורנויות")
    st.markdown("---")
    st.markdown("### 📅 ניווט שבוע")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("◀ קודם", use_container_width=True):
            st.session_state.week_offset -= 1; st.rerun()
    with c2:
        if st.button("היום",   use_container_width=True):
            st.session_state.week_offset = 0;  st.rerun()
    with c3:
        if st.button("הבא ▶",  use_container_width=True):
            st.session_state.week_offset += 1; st.rerun()

    st.markdown(f"""
    <div class="week-nav">
        <div class="week-label">שבוע מוצג</div>
        <div class="week-dates">{fmt(week_dates[0])} – {fmt(week_dates[6])}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🔐 כניסת מנהל")
    if not st.session_state.is_admin:
        pwd = st.text_input("סיסמה", type="password")
        if st.button("כניסה", use_container_width=True):
            if pwd == ADMIN_PASSWORD:
                st.session_state.is_admin = True; st.rerun()
            else:
                st.error("סיסמה שגויה")
    else:
        st.markdown('<span class="admin-badge">✓ מנהל מחובר</span>', unsafe_allow_html=True)
        if st.button("התנתק", use_container_width=True):
            st.session_state.is_admin = False; st.rerun()

    st.markdown("---")
    sl = week_status(current_monday)
    cm = {"בוצע":"#4ade80","נוכחי":"#60a5fa","מתוכנן":"#fb923c"}.get(sl,"#93b4d8")
    st.markdown(f"**סטטוס:** <span style='color:{cm};font-weight:700'>{sl}</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; padding: 8px 0;">
        <div style="color:#f5c842; font-weight:800; font-size:.9rem; font-family:'Rubik',sans-serif; margin-bottom:4px;">🛡️ ניתאי כהן</div>
        <div style="color:#8baacf; font-size:.8rem; direction:ltr; letter-spacing:1px;">053-444-4494</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🛡️ מערכת ניהול תורנויות</h1>
    <p>גזרה אזרחית &nbsp;•&nbsp; ניהול ורישום משמרות</p>
</div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab_labels = ["📋 לוח תורנויות", "🔍 חיפוש אישי"]
if st.session_state.is_admin:
    tab_labels += ["✏️ שיבוץ", "⚙️ ניהול עמדות"]

tabs = st.tabs(tab_labels)

# ══════════════════════════════════════════════
# TAB 1 — לוח תורנויות
# ══════════════════════════════════════════════
with tabs[0]:
    week_data = load_week(current_monday.isoformat())

    st.markdown(f"""
    <div class="card">
        <div class="card-title">📋 לוח תורנויות — {fmt(week_dates[0])} עד {fmt(week_dates[6])}</div>
        <table class="roster-table">
            <thead><tr><th>עמדה</th><th>סבב / שעות</th><th>חייל משובץ</th></tr></thead>
            <tbody>""", unsafe_allow_html=True)

    prev_pos = None
    rows_html = ""
    for position, shift in ROSTER_ROWS:
        key   = row_key(position, shift)
        asgns = week_data.get(key, [])
        disp  = assignments_display(asgns)
        pos_display = position if position != prev_pos else ""
        prev_pos = position
        soldier_html = (
            f"<span style='color:#4ade80;font-weight:600'>{disp}</span>"
            if disp != "—"
            else "<span style='color:rgba(255,255,255,.2)'>—</span>"
        )
        rows_html += f"""
            <tr>
                <td class="pos-cell">{pos_display}</td>
                <td class="shift-cell">{shift}</td>
                <td>{soldier_html}</td>
            </tr>"""

    st.markdown(rows_html + "</tbody></table></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 2 — חיפוש אישי
# ══════════════════════════════════════════════
with tabs[1]:
    st.markdown('<div class="card"><div class="card-title">🔍 חיפוש תורנויות לפי שם</div>', unsafe_allow_html=True)
    search_name = st.text_input("הזן שם מלא או חלקי", placeholder="לדוגמה: כהן")
    st.markdown("</div>", unsafe_allow_html=True)

    if search_name.strip():
        all_rows = load_all()
        found = []
        for r in all_rows:
            try:
                asgns = json.loads(r["assignments"])
            except Exception:
                continue
            monday = date.fromisoformat(r["week_monday"])
            for a in asgns:
                if search_name.strip().lower() in a.get("name","").lower():
                    frm = a.get("from","")
                    to  = a.get("to","")
                    period = f"{frm}–{to}" if frm and to else "כל השבוע"
                    found.append({
                        "שבוע":   f"{fmt(monday)} – {fmt(monday+timedelta(days=6))}",
                        "עמדה":   r["position"],
                        "סבב":    r["shift"],
                        "תקופה":  period,
                        "סטטוס":  week_status(monday),
                        "_monday": monday,
                    })

        if not found:
            st.markdown(f'<div class="error-box">❌ לא נמצאו תורנויות עבור "{search_name}".</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="success-box">✅ נמצאו {len(found)} תורנויות עבור "{search_name}"</div>', unsafe_allow_html=True)
            table_html = '<div class="card"><table class="roster-table"><thead><tr><th>שבוע</th><th>עמדה</th><th>סבב</th><th>תקופה</th><th>סטטוס</th></tr></thead><tbody>'
            for f in sorted(found, key=lambda x: x["_monday"], reverse=True):
                bc = {"בוצע":"badge-done","נוכחי":"badge-now","מתוכנן":"badge-plan"}.get(f["סטטוס"],"badge-now")
                table_html += f"<tr><td>{f['שבוע']}</td><td>{f['עמדה']}</td><td>{f['סבב']}</td><td>{f['תקופה']}</td><td><span class='badge {bc}'>{f['סטטוס']}</span></td></tr>"
            table_html += "</tbody></table></div>"
            st.markdown(table_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 3 — שיבוץ (מנהל)
# ══════════════════════════════════════════════
if st.session_state.is_admin:
    with tabs[2]:
        week_data = load_week(current_monday.isoformat())
        future    = is_future(current_monday)

        st.markdown(f"""
        <div class="card">
            <div class="card-title">✏️ שיבוץ שבועי — {fmt(week_dates[0])} עד {fmt(week_dates[6])}</div>
        </div>""", unsafe_allow_html=True)

        if future:
            st.markdown('<div class="info-box">📅 שבוע עתידי — שיבוץ לתכנון</div>', unsafe_allow_html=True)

        st.markdown("#### בחר עמדה וסבב לשיבוץ")
        row_options = [f"{pos} | {shft}" for pos, shft in ROSTER_ROWS]
        selected_row_str = st.selectbox("עמדה | סבב", row_options, key="row_select")
        sel_idx   = row_options.index(selected_row_str)
        sel_pos, sel_shift = ROSTER_ROWS[sel_idx]
        sel_key   = row_key(sel_pos, sel_shift)
        current_assignments = week_data.get(sel_key, [])

        if current_assignments:
            st.markdown(f'<div class="info-box">שיבוץ נוכחי: <strong>{assignments_display(current_assignments)}</strong></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-box">אין שיבוץ לסבב זה עדיין</div>', unsafe_allow_html=True)

        st.markdown("---")

        use_split = st.toggle("פיצול שמירה (יותר מחייל אחד בסבב זה)", value=False)

        new_assignments = []

        if not use_split:
            st.markdown("#### שיבוץ לכל השבוע")
            soldier = st.text_input("שם החייל", key="single_soldier")
            if soldier.strip():
                new_assignments = [{"name": soldier.strip()}]
        else:
            st.markdown("#### שיבוץ עם פיצול")
            num_splits = st.number_input("כמה חיילים בפיצול?", min_value=2, max_value=7, value=2, step=1)

            split_valid = True
            for i in range(int(num_splits)):
                st.markdown(f"**חייל {i+1}:**")
                sc1, sc2, sc3 = st.columns(3)
                with sc1:
                    sname = st.text_input(f"שם", key=f"split_name_{i}")
                with sc2:
                    day_options = [f"{DAYS_HE[j]} {fmt(week_dates[j])}" for j in range(7)]
                    from_day = st.selectbox(f"מתאריך", day_options, key=f"split_from_{i}", index=i if i < 7 else 0)
                with sc3:
                    to_day = st.selectbox(f"עד תאריך", day_options, key=f"split_to_{i}", index=min(i+1, 6))

                from_idx = day_options.index(from_day)
                to_idx   = day_options.index(to_day)

                if to_idx < from_idx:
                    st.markdown('<div class="error-box">⚠️ תאריך הסיום חייב להיות אחרי תאריך ההתחלה</div>', unsafe_allow_html=True)
                    split_valid = False

                if sname.strip():
                    new_assignments.append({
                        "name": sname.strip(),
                        "from": fmt(week_dates[from_idx]),
                        "to":   fmt(week_dates[to_idx]),
                    })
                else:
                    split_valid = False

            if not split_valid and any(a.get("name") for a in new_assignments):
                st.markdown('<div class="error-box">מלא את כל השדות לפני השמירה</div>', unsafe_allow_html=True)

        st.markdown("---")

        btn1, btn2 = st.columns(2)
        with btn1:
            if st.button("💾 שמור שיבוץ", use_container_width=True, type="primary"):
                if not new_assignments:
                    st.error("יש למלא לפחות חייל אחד")
                else:
                    save_row(current_monday, sel_pos, sel_shift, new_assignments)
                    st.markdown(f'<div class="success-box">✅ נשמר: {assignments_display(new_assignments)}</div>', unsafe_allow_html=True)
                    st.rerun()
        with btn2:
            if st.button("🗑️ נקה שיבוץ", use_container_width=True):
                delete_row(current_monday, sel_pos, sel_shift)
                st.success("השיבוץ נמחק")
                st.rerun()

        st.markdown("---")
        st.markdown("#### סיכום שיבוצים לשבוע זה")
        week_data = load_week(current_monday.isoformat())

        table_html = '<div class="card"><table class="roster-table"><thead><tr><th>עמדה</th><th>סבב</th><th>חייל</th></tr></thead><tbody>'
        prev_p = None
        for position, shift in ROSTER_ROWS:
            key   = row_key(position, shift)
            asgns = week_data.get(key, [])
            disp  = assignments_display(asgns)
            if disp == "—":
                continue
            pos_d = position if position != prev_p else ""
            prev_p = position
            table_html += f"<tr><td class='pos-cell'>{pos_d}</td><td class='shift-cell'>{shift}</td><td>{disp}</td></tr>"
        table_html += "</tbody></table></div>"
        st.markdown(table_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 4 — ניהול עמדות (מנהל)
# ══════════════════════════════════════════════
if st.session_state.is_admin:
    with tabs[3]:
        st.markdown("""
        <div class="card">
            <div class="card-title">⚙️ עריכת רשימת עמדות וסבבים</div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="info-box">ℹ️ כאן ניתן להוסיף ולהסיר עמדות/סבבים. השינויים בתוקף לכל השבועות (אך לא משפיעים על שיבוצים שנשמרו כבר).</div>', unsafe_allow_html=True)

        # ── תצוגת הרשימה הנוכחית עם מחיקה ──
        st.markdown("### רשימת עמדות נוכחית")

        rows_to_delete = []
        for i, (pos, shft) in enumerate(st.session_state.roster_rows):
            col_num, col_pos, col_shft, col_del = st.columns([0.5, 3, 3, 0.8])
            with col_num:
                st.markdown(f"<div style='padding:10px 0; color:var(--text-muted); font-size:.8rem'>{i+1}</div>", unsafe_allow_html=True)
            with col_pos:
                st.markdown(f"<div style='padding:10px 0; color:var(--accent-light); font-weight:600'>{pos}</div>", unsafe_allow_html=True)
            with col_shft:
                st.markdown(f"<div style='padding:10px 0; color:var(--text-secondary)'>{shft}</div>", unsafe_allow_html=True)
            with col_del:
                if st.button("✕", key=f"del_row_{i}", help="מחק שורה זו"):
                    rows_to_delete.append(i)

        if rows_to_delete:
            for idx in sorted(rows_to_delete, reverse=True):
                st.session_state.roster_rows.pop(idx)
            st.rerun()

        st.markdown("---")

        # ── הוספת שורה חדשה ──
        st.markdown("### ➕ הוספת עמדה/סבב חדש")
        new_col1, new_col2 = st.columns(2)
        with new_col1:
            new_pos   = st.text_input("שם העמדה", placeholder='לדוגמה: ש"ג מחנה')
        with new_col2:
            new_shift = st.text_input("סבב / שעות", placeholder="לדוגמה: 06:00-14:00")

        if st.button("➕ הוסף שורה", use_container_width=True, type="primary"):
            if new_pos.strip() and new_shift.strip():
                st.session_state.roster_rows.append((new_pos.strip(), new_shift.strip()))
                st.success(f"✅ נוסף: {new_pos.strip()} | {new_shift.strip()}")
                st.rerun()
            else:
                st.error("יש למלא גם שם עמדה וגם סבב")

        st.markdown("---")

        # ── איפוס לברירת מחדל ──
        st.markdown("### 🔄 איפוס לרשימה המקורית")
        st.markdown('<div class="warning-box">⚠️ פעולה זו תמחק את כל השינויים שביצעת ותחזיר את רשימת העמדות למצב המקורי.</div>', unsafe_allow_html=True)

        col_reset, col_count = st.columns([2, 1])
        with col_count:
            current_count = len(st.session_state.roster_rows)
            default_count = len(DEFAULT_ROSTER_ROWS)
            st.markdown(
                f"<div style='padding:14px; text-align:center; background:rgba(255,255,255,.03); border:1px solid var(--border); border-radius:12px;'>"
                f"<div style='color:var(--text-muted); font-size:.78rem; margin-bottom:6px'>כמות שורות</div>"
                f"<div style='color:var(--accent-light); font-size:1.4rem; font-weight:800'>{current_count}</div>"
                f"<div style='color:var(--text-muted); font-size:.75rem'>ברירת מחדל: {default_count}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
        with col_reset:
            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
            if st.button("🔄 אפס לרשימה המקורית", use_container_width=True):
                st.session_state.roster_rows = list(DEFAULT_ROSTER_ROWS)
                st.success("✅ הרשימה אופסה לברירת המחדל!")
                st.rerun()

# ─────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <div class="footer-name">🛡️ נוצר על ידי ניתאי כהן</div>
    <div class="footer-phone">053-444-4494</div>
    <div class="footer-line">מערכת ניהול תורנויות • גזרה אזרחית</div>
</div>
""", unsafe_allow_html=True)
