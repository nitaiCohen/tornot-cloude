import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from supabase import create_client, Client

# ─────────────────────────────────────────────
# הגדרות עיצוב
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="מערכת ניהול תורנויות",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Heebo', sans-serif; direction: rtl; }
.stApp { background: linear-gradient(135deg, #0f1923 0%, #1a2744 50%, #0f1923 100%); min-height: 100vh; }
.main-header { background: linear-gradient(90deg,#1e3a5f,#2563a8,#1e3a5f); border-radius: 16px; padding: 28px 36px; margin-bottom: 28px; border: 1px solid #2563a8; box-shadow: 0 8px 32px rgba(37,99,168,0.3); text-align: center; }
.main-header h1 { color: #e8f0fe; font-size: 2.2rem; font-weight: 800; margin: 0; }
.main-header p  { color: #93b4d8; margin: 6px 0 0 0; font-size: 1rem; }
.card { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 14px; padding: 22px 26px; margin-bottom: 20px; backdrop-filter: blur(10px); }
.card-title { color: #7eb3f5; font-size: 1rem; font-weight: 600; margin-bottom: 14px; padding-bottom: 10px; border-bottom: 1px solid rgba(126,179,245,0.2); text-align: right; }
.badge { display: inline-block; padding: 3px 12px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; }
.badge-done { background: #1a4731; color: #4ade80; border: 1px solid #4ade80; }
.badge-now  { background: #1e3a5f; color: #60a5fa; border: 1px solid #60a5fa; }
.badge-plan { background: #3b2a1a; color: #fb923c; border: 1px solid #fb923c; }
.week-nav { background: rgba(37,99,168,0.15); border: 1px solid rgba(37,99,168,0.3); border-radius: 12px; padding: 14px 20px; margin-bottom: 18px; text-align: center; }
.week-label { color: #93b4d8; font-size: 0.85rem; }
.week-dates { color: #e8f0fe; font-size: 1.2rem; font-weight: 700; }
.styled-table { width: 100%; border-collapse: collapse; direction: rtl; }
.styled-table th { background: rgba(37,99,168,0.4); color: #7eb3f5; font-weight: 600; padding: 10px 14px; font-size: 0.85rem; text-align: right; border-bottom: 2px solid rgba(37,99,168,0.5); }
.styled-table td { padding: 10px 14px; border-bottom: 1px solid rgba(255,255,255,0.06); color: #d1dff0; font-size: 0.88rem; text-align: right; }
.styled-table tr:hover td { background: rgba(37,99,168,0.12); }
.admin-badge { background: linear-gradient(90deg,#7c3aed,#5b21b6); color: white; padding: 4px 14px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; }
.stButton > button { border-radius: 10px !important; font-family: 'Heebo', sans-serif !important; font-weight: 600 !important; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg,#0d1b2e 0%,#1a2744 100%) !important; border-left: 1px solid rgba(37,99,168,0.3) !important; }
section[data-testid="stSidebar"] * { direction: rtl; }
.info-box    { background: rgba(37,99,168,0.15); border: 1px solid rgba(37,99,168,0.35); border-radius: 10px; padding: 12px 18px; color: #93b4d8; font-size: 0.88rem; margin: 10px 0; text-align: right; }
.success-box { background: rgba(26,71,49,0.5); border: 1px solid #4ade80; border-radius: 10px; padding: 12px 18px; color: #4ade80; font-size: 0.88rem; margin: 10px 0; text-align: right; }
.error-box   { background: rgba(127,29,29,0.4); border: 1px solid #f87171; border-radius: 10px; padding: 12px 18px; color: #f87171; font-size: 0.88rem; margin: 10px 0; text-align: right; }
hr { border-color: rgba(255,255,255,0.08) !important; }
input, select, textarea { direction: rtl !important; text-align: right !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# קבועים
# ─────────────────────────────────────────────
ADMIN_PASSWORD = "1234"
DAYS_HE = ["שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת", "ראשון"]

DEFAULT_SETTINGS = [
    {"עמדה": "ש\"ג מפקד",                "סבבים": "02-06+14-18,06-10+18-22,10-14+22-02", "תקן": 1},
    {"עמדה": "סגן מפקד",                 "סבבים": "02-06+14-18,06-10+18-22,10-14+22-02", "תקן": 1},
    {"עמדה": "עמדה אחורית חיפה",         "סבבים": "02-06+14-18,06-10+18-22,10-14+22-02", "תקן": 1},
    {"עמדה": "ש\"ג רכבת",                "סבבים": "06-10+14-18,10-14+18-22",             "תקן": 1},
    {"עמדה": "סגן רכבת",                 "סבבים": "06-10+14-18,10-14+18-22",             "תקן": 1},
    {"עמדה": "מחפה קדמי חיפה",           "סבבים": "18-22,22-02,02-06",                   "תקן": 1},
    {"עמדה": "מחפה אחורי חיפה (סופ\"ש)","סבבים": "02-06+14-18,06-10+18-22,10-14+22-02", "תקן": 1},
    {"עמדה": "חשבשבת 1",                 "סבבים": "06-18,18-06",                          "תקן": 1},
    {"עמדה": "חשבשבת 2",                 "סבבים": "06-18,18-06",                          "תקן": 1},
    {"עמדה": "מאייש חול (א-ה)",          "סבבים": "משמרת יום",                            "תקן": 2},
    {"עמדה": "מאייש סופ\"ש (ה-א)",       "סבבים": "משמרת סוף שבוע",                      "תקן": 2},
    {"עמדה": "כונן סמל",                 "סבבים": "24/7",                                 "תקן": 1},
    {"עמדה": "כונן רב\"ט",               "סבבים": "24/7",                                 "תקן": 1},
]

# ─────────────────────────────────────────────
# Supabase
# ─────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()

# ─────────────────────────────────────────────
# עזר: תאריכים
# ─────────────────────────────────────────────
def get_week_monday(d: date) -> date:
    return d - timedelta(days=d.weekday())

def get_week_dates(monday: date):
    return [monday + timedelta(days=i) for i in range(7)]

def format_date_he(d: date) -> str:
    return d.strftime("%d/%m/%Y")

def is_future_week(monday: date) -> bool:
    return monday > get_week_monday(date.today())

def is_current_week(monday: date) -> bool:
    return monday == get_week_monday(date.today())

def week_status(monday: date) -> str:
    if is_future_week(monday):    return "מתוכנן"
    elif is_current_week(monday): return "נוכחי"
    else:                         return "בוצע"

# ─────────────────────────────────────────────
# Supabase — עמדות
# ─────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_settings() -> pd.DataFrame:
    res = supabase.table("settings").select("*").execute()
    if res.data:
        df = pd.DataFrame(res.data)
        return df[["עמדה", "סבבים", "תקן"]]
    for row in DEFAULT_SETTINGS:
        supabase.table("settings").upsert(row, on_conflict="עמדה").execute()
    return pd.DataFrame(DEFAULT_SETTINGS)

def save_setting_row(row: dict):
    supabase.table("settings").upsert(row, on_conflict="עמדה").execute()
    st.cache_data.clear()

def reset_settings_to_default():
    supabase.table("settings").delete().neq("עמדה", "").execute()
    for row in DEFAULT_SETTINGS:
        supabase.table("settings").upsert(row, on_conflict="עמדה").execute()
    st.cache_data.clear()

# ─────────────────────────────────────────────
# Supabase — תורנויות
# ─────────────────────────────────────────────
@st.cache_data(ttl=30)
def load_week_shifts(monday_iso: str) -> pd.DataFrame:
    res = supabase.table("shifts").select("*").eq("week_monday", monday_iso).execute()
    if res.data:
        df = pd.DataFrame(res.data)
        cols = [c for c in ["id", "תאריך", "יום", "עמדה", "סבב", "שם_תורן"] if c in df.columns]
        return df[cols]
    return pd.DataFrame(columns=["id", "תאריך", "יום", "עמדה", "סבב", "שם_תורן"])

@st.cache_data(ttl=60)
def load_all_shifts() -> pd.DataFrame:
    res = supabase.table("shifts").select("*").execute()
    if res.data:
        return pd.DataFrame(res.data)
    return pd.DataFrame(columns=["id", "week_monday", "תאריך", "יום", "עמדה", "סבב", "שם_תורן"])

def add_shift(monday: date, row: dict):
    row["week_monday"] = monday.isoformat()
    supabase.table("shifts").insert(row).execute()
    st.cache_data.clear()

def delete_shift(shift_id: int):
    supabase.table("shifts").delete().eq("id", shift_id).execute()
    st.cache_data.clear()

# ─────────────────────────────────────────────
# Session State
# ─────────────────────────────────────────────
if "week_offset" not in st.session_state:
    st.session_state.week_offset = 0
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

current_monday = get_week_monday(date.today()) + timedelta(weeks=st.session_state.week_offset)
week_dates     = get_week_dates(current_monday)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛡️ מערכת תורנויות")
    st.markdown("---")
    st.markdown("### 📅 ניווט שבוע")

    col_p, col_c, col_n = st.columns(3)
    with col_p:
        if st.button("◀ קודם", use_container_width=True):
            st.session_state.week_offset -= 1
            st.rerun()
    with col_c:
        if st.button("היום", use_container_width=True):
            st.session_state.week_offset = 0
            st.rerun()
    with col_n:
        if st.button("הבא ▶", use_container_width=True):
            st.session_state.week_offset += 1
            st.rerun()

    st.markdown(f"""
    <div class="week-nav">
        <div class="week-label">שבוע מוצג</div>
        <div class="week-dates">{format_date_he(week_dates[0])} – {format_date_he(week_dates[6])}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🔐 כניסת מנהל")
    if not st.session_state.is_admin:
        pwd = st.text_input("סיסמה", type="password", key="pwd_input")
        if st.button("כניסה", use_container_width=True):
            if pwd == ADMIN_PASSWORD:
                st.session_state.is_admin = True
                st.rerun()
            else:
                st.error("סיסמה שגויה")
    else:
        st.markdown('<span class="admin-badge">✓ מנהל מחובר</span>', unsafe_allow_html=True)
        if st.button("התנתק", use_container_width=True):
            st.session_state.is_admin = False
            st.rerun()

    st.markdown("---")
    status_label = week_status(current_monday)
    color_map    = {"בוצע": "#4ade80", "נוכחי": "#60a5fa", "מתוכנן": "#fb923c"}
    c = color_map.get(status_label, "#93b4d8")
    st.markdown(f"**סטטוס שבוע:** <span style='color:{c};font-weight:700'>{status_label}</span>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🛡️ מערכת ניהול תורנויות</h1>
    <p>גזרה אזרחית • ניהול ורישום משמרות</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tabs_list = ["📋 לוח תורנויות", "🔍 חיפוש אישי"]
if st.session_state.is_admin:
    tabs_list += ["✏️ שיבוץ", "⚙️ ניהול עמדות"]

tabs = st.tabs(tabs_list)

# ══════════════════════════════════════════════
# TAB 1 – לוח תורנויות
# ══════════════════════════════════════════════
with tabs[0]:
    df_week    = load_week_shifts(current_monday.isoformat())
    settings_df = load_settings()

    st.markdown(f"""
    <div class="card">
        <div class="card-title">📋 לוח תורנויות — {format_date_he(week_dates[0])} עד {format_date_he(week_dates[6])}</div>
    </div>
    """, unsafe_allow_html=True)

    if df_week.empty:
        st.markdown('<div class="info-box">⚠️ אין נתונים לשבוע זה עדיין.</div>', unsafe_allow_html=True)
    else:
        for _, row_s in settings_df.iterrows():
            position = row_s["עמדה"]
            pos_data = df_week[df_week["עמדה"] == position]
            if pos_data.empty:
                continue
            table_html = f'<div class="card"><div class="card-title">🔹 {position}</div>'
            table_html += '<table class="styled-table"><thead><tr><th>יום</th><th>תאריך</th><th>סבב</th><th>תורן</th></tr></thead><tbody>'
            for _, r in pos_data.iterrows():
                table_html += f"<tr><td>{r.get('יום','')}</td><td>{r.get('תאריך','')}</td><td>{r.get('סבב','')}</td><td>{r.get('שם_תורן','')}</td></tr>"
            table_html += "</tbody></table></div>"
            st.markdown(table_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 2 – חיפוש אישי
# ══════════════════════════════════════════════
with tabs[1]:
    st.markdown('<div class="card"><div class="card-title">🔍 חיפוש תורנויות לפי שם</div>', unsafe_allow_html=True)
    search_name = st.text_input("הזן שם מלא או חלקי", placeholder="לדוגמה: כהן")
    st.markdown("</div>", unsafe_allow_html=True)

    if search_name.strip():
        all_df = load_all_shifts()
        if all_df.empty:
            st.markdown('<div class="info-box">אין נתונים בארכיון.</div>', unsafe_allow_html=True)
        else:
            results = all_df[all_df["שם_תורן"].str.contains(search_name.strip(), na=False, case=False)].copy()
            if results.empty:
                st.markdown(f'<div class="error-box">לא נמצאו תורנויות עבור "{search_name}".</div>', unsafe_allow_html=True)
            else:
                results["סטטוס"] = results["week_monday"].apply(
                    lambda m: week_status(date.fromisoformat(str(m))) if pd.notna(m) else ""
                )
                results["שבוע"] = results["week_monday"].apply(
                    lambda m: format_date_he(date.fromisoformat(str(m))) if pd.notna(m) else ""
                )
                st.markdown(f'<div class="success-box">נמצאו {len(results)} תורנויות עבור "{search_name}"</div>', unsafe_allow_html=True)
                table_html = '<div class="card"><table class="styled-table"><thead><tr><th>שבוע</th><th>יום</th><th>תאריך</th><th>עמדה</th><th>סבב</th><th>סטטוס</th></tr></thead><tbody>'
                for _, r in results.iterrows():
                    status = r.get("סטטוס", "")
                    bc = {"בוצע": "badge-done", "נוכחי": "badge-now", "מתוכנן": "badge-plan"}.get(status, "badge-now")
                    table_html += f"<tr><td>{r.get('שבוע','')}</td><td>{r.get('יום','')}</td><td>{r.get('תאריך','')}</td><td>{r.get('עמדה','')}</td><td>{r.get('סבב','')}</td><td><span class='badge {bc}'>{status}</span></td></tr>"
                table_html += "</tbody></table></div>"
                st.markdown(table_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 3 – שיבוץ (מנהל)
# ══════════════════════════════════════════════
if st.session_state.is_admin:
    with tabs[2]:
        settings_df = load_settings()
        df_week     = load_week_shifts(current_monday.isoformat())
        future      = is_future_week(current_monday)

        st.markdown(f"""
        <div class="card">
            <div class="card-title">✏️ שיבוץ תורנים — {'📅 תכנון עתידי' if future else '📝 רישום ביצוע'}</div>
        </div>
        """, unsafe_allow_html=True)

        mode_msg = "מצב תכנון: שבוע עתידי — שיבוץ כללי לעמדה" if future else "מצב רישום: שיבוץ מדויק לפי יום וסבב שעות"
        st.markdown(f'<div class="info-box">{mode_msg}</div>', unsafe_allow_html=True)

        with st.form("assignment_form"):
            col1, col2 = st.columns(2)
            with col1:
                position     = st.selectbox("עמדה", settings_df["עמדה"].tolist())
                soldier_name = st.text_input("שם התורן")
            with col2:
                selected_day = st.selectbox("יום", DAYS_HE)
                if future:
                    selected_shift = st.text_input("הערה (אופציונלי)", placeholder="לדוגמה: כוננות")
                else:
                    pos_row     = settings_df[settings_df["עמדה"] == position]
                    shifts_raw  = pos_row["סבבים"].values[0] if not pos_row.empty else ""
                    shifts_list = [s.strip() for s in shifts_raw.split(",") if s.strip()]
                    selected_shift = st.selectbox("סבב", shifts_list if shifts_list else ["—"])

            if st.form_submit_button("💾 שמור שיבוץ", use_container_width=True):
                if not soldier_name.strip():
                    st.error("יש להזין שם תורן")
                else:
                    day_idx  = DAYS_HE.index(selected_day)
                    sel_date = week_dates[day_idx]
                    add_shift(current_monday, {
                        "תאריך":   format_date_he(sel_date),
                        "יום":     selected_day,
                        "עמדה":    position,
                        "סבב":     selected_shift if not future else "כללי",
                        "שם_תורן": soldier_name.strip(),
                    })
                    st.success(f"✅ {soldier_name} שובץ לעמדה {position} — יום {selected_day}")
                    st.rerun()

        df_week = load_week_shifts(current_monday.isoformat())
        if not df_week.empty:
            st.markdown("---")
            table_html = '<div class="card"><div class="card-title">📄 שיבוצים קיימים</div><table class="styled-table"><thead><tr><th>יום</th><th>תאריך</th><th>עמדה</th><th>סבב</th><th>תורן</th><th>ID</th></tr></thead><tbody>'
            for _, r in df_week.iterrows():
                table_html += f"<tr><td>{r.get('יום','')}</td><td>{r.get('תאריך','')}</td><td>{r.get('עמדה','')}</td><td>{r.get('סבב','')}</td><td>{r.get('שם_תורן','')}</td><td>{r.get('id','')}</td></tr>"
            table_html += "</tbody></table></div>"
            st.markdown(table_html, unsafe_allow_html=True)

            st.markdown("**מחק שיבוץ לפי ID:**")
            dc1, dc2 = st.columns([2, 1])
            with dc1:
                del_id = st.number_input("ID שורה", min_value=1, step=1)
            with dc2:
                if st.button("🗑️ מחק", use_container_width=True):
                    delete_shift(int(del_id))
                    st.success("נמחק ✓")
                    st.rerun()

# ══════════════════════════════════════════════
# TAB 4 – ניהול עמדות (מנהל)
# ══════════════════════════════════════════════
if st.session_state.is_admin:
    with tabs[3]:
        settings_df = load_settings()
        st.markdown('<div class="card"><div class="card-title">⚙️ ניהול עמדות</div>', unsafe_allow_html=True)

        edited_df = st.data_editor(
            settings_df,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "עמדה":  st.column_config.TextColumn("עמדה", width=200),
                "סבבים": st.column_config.TextColumn("סבבים (מופרדים בפסיק)", width=350),
                "תקן":   st.column_config.NumberColumn("תקן", min_value=1, max_value=20, step=1),
            }
        )
        st.markdown("</div>", unsafe_allow_html=True)

        col_s, col_r = st.columns(2)
        with col_s:
            if st.button("💾 שמור שינויים", use_container_width=True):
                for _, row in edited_df.iterrows():
                    save_setting_row({"עמדה": row["עמדה"], "סבבים": row["סבבים"], "תקן": int(row["תקן"])})
                st.success("✅ ההגדרות נשמרו")
                st.rerun()
        with col_r:
            if st.button("🔄 אפס לברירת מחדל", use_container_width=True):
                reset_settings_to_default()
                st.success("✅ הוחזר לברירת מחדל")
                st.rerun()

        st.markdown("""
        <div class="info-box">
        <strong>פורמט סבבים:</strong> הפרד בפסיק. סבב כפול עם <code>+</code><br>
        דוגמה: <code>02-06+14-18,06-10+18-22,10-14+22-02</code>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:rgba(255,255,255,0.25);font-size:0.78rem;padding:10px 0">'
    'מערכת ניהול תורנויות • גזרה אזרחית'
    '</div>',
    unsafe_allow_html=True
)
