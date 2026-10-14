import streamlit as st
import pandas as pd
import json
import os
import time
import random
import urllib.request
from datetime import datetime, date, timedelta

# --- PAGINA CONFIGURATIE ---
st.set_page_config(
    page_title="Maarten & Laura — Rookvrij & Diner-Pot",
    page_icon="🥂",
    layout="centered",
    initial_sidebar_state="collapsed"
)

DATA_FILE = "rookvrij_v3_data.json"

# --- PREMIUM MOBILE APP CSS (APPLE HEALTH / STOPTOBER DESIGN) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    /* Forceer modern lettertype en rustige, heldere achtergrond */
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }

    /* Zorg dat standaard Streamlit-elementen ALTIJD scherp leesbaar zijn */
    .stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5 {
        color: #0F172A;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 3.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 480px !important;
    }

    /* Luxe Donkere Hero Card (Met geforceerde witte/gouden tekst) */
    .hero-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border-radius: 24px;
        padding: 22px 20px;
        color: #FFFFFF !important;
        box-shadow: 0 12px 28px -6px rgba(15, 23, 42, 0.25);
        margin-bottom: 14px;
        position: relative;
        overflow: hidden;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(251, 191, 36, 0.18);
        color: #FCD34D !important;
        border: 1px solid rgba(251, 191, 36, 0.4);
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        padding: 4px 10px;
        border-radius: 999px;
        margin-bottom: 8px;
    }
    .hero-title {
        font-size: 1.45rem;
        font-weight: 800;
        color: #FFFFFF !important;
        margin: 0 0 4px 0;
        line-height: 1.2;
    }
    .hero-sub {
        font-size: 0.85rem;
        color: #CBD5E1 !important;
        margin: 0 0 16px 0;
    }
    .hero-amount-row {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 6px;
    }
    .hero-big-amount {
        font-size: 2rem;
        font-weight: 800;
        color: #34D399 !important;
        line-height: 1;
    }
    .hero-goal-lbl {
        font-size: 0.82rem;
        font-weight: 600;
        color: #94A3B8 !important;
    }
    .custom-prog-bg {
        width: 100%;
        height: 10px;
        background: rgba(255, 255, 255, 0.12);
        border-radius: 999px;
        overflow: hidden;
        margin-bottom: 10px;
    }
    .custom-prog-fill {
        height: 100%;
        background: linear-gradient(90deg, #10B981 0%, #FBBF24 100%);
        border-radius: 999px;
        transition: width 0.4s ease;
    }
    .hero-footer {
        display: flex;
        justify-content: space-between;
        font-size: 0.78rem;
        color: #E2E8F0 !important;
        font-weight: 600;
    }

    /* Bento Grid KPI Kaarten */
    .bento-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        margin: 12px 0 16px 0;
    }
    .bento-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 18px;
        padding: 13px 8px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03);
    }
    .bento-lbl {
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #64748B !important;
        margin-bottom: 4px;
    }
    .bento-val-emerald {
        font-size: 1.28rem;
        font-weight: 800;
        color: #059669 !important;
    }
    .bento-val-amber {
        font-size: 1.28rem;
        font-weight: 800;
        color: #D97706 !important;
    }
    .bento-val-rose {
        font-size: 1.28rem;
        font-weight: 800;
        color: #E11D48 !important;
    }
    .bento-sub {
        font-size: 0.7rem;
        color: #94A3B8 !important;
        font-weight: 600;
        margin-top: 2px;
    }

    /* Stoptober Gezondheidskaarten */
    .health-summary-card {
        background: linear-gradient(135deg, #ECFDF5 0%, #F0FDF4 100%);
        border: 1px solid #A7F3D0;
        border-radius: 20px;
        padding: 16px;
        margin-bottom: 14px;
    }
    .health-item {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 18px;
        padding: 15px 16px;
        margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
    }
    .health-item-done {
        background: #F8FAFC;
        border: 1px solid #A7F3D0;
        border-left: 5px solid #10B981;
        border-radius: 18px;
        padding: 15px 16px;
        margin-bottom: 10px;
    }
    .health-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 4px;
    }
    .health-title {
        font-size: 0.92rem;
        font-weight: 800;
        color: #0F172A !important;
    }
    .health-pct-badge {
        font-size: 0.75rem;
        font-weight: 800;
        padding: 3px 9px;
        border-radius: 999px;
        background: #ECFDF5;
        color: #059669 !important;
    }
    .health-desc {
        font-size: 0.8rem;
        color: #475569 !important;
        margin-bottom: 8px;
        line-height: 1.4;
    }
    .health-bar-bg {
        width: 100%;
        height: 8px;
        background: #E2E8F0;
        border-radius: 999px;
        overflow: hidden;
    }
    .health-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #10B981, #059669);
        border-radius: 999px;
    }

    /* Motivatie Flashcard */
    .flashcard {
        background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
        border: 1px solid #FDE68A;
        border-radius: 22px;
        padding: 24px 20px;
        margin: 14px 0;
        box-shadow: 0 8px 20px rgba(217, 119, 6, 0.08);
        text-align: center;
    }
    .flashcard-quote {
        font-size: 1.05rem;
        font-weight: 700;
        color: #78350F !important;
        line-height: 1.55;
        margin: 0;
    }

    /* Ademhalings-cirkel */
    @keyframes breathe-anim {
        0%, 100% { transform: scale(0.68); background-color: #E0F2FE; border-color: #0284C7; }
        25% { transform: scale(1.12); background-color: #D1FAE5; border-color: #059669; }
        60% { transform: scale(1.12); background-color: #FEF3C7; border-color: #D97706; }
    }
    .breath-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 22px;
        padding: 28px 16px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03);
    }
    .breath-orb {
        width: 130px;
        height: 130px;
        margin: 12px auto;
        border-radius: 50%;
        border: 4px solid #059669;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 0.9rem;
        color: #0F172A !important;
        animation: breathe-anim 19s infinite ease-in-out;
    }

    /* Navigatie-tabs strak en passend op 1 scherm */
    div[data-baseweb="tab-list"] {
        gap: 2px !important;
        background-color: #E2E8F0 !important;
        padding: 4px !important;
        border-radius: 14px !important;
    }
    button[data-baseweb="tab"] {
        flex: 1 !important;
        font-size: 0.76rem !important;
        font-weight: 700 !important;
        padding: 7px 4px !important;
        border-radius: 10px !important;
        color: #475569 !important;
        background-color: transparent !important;
        border: none !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.08) !important;
    }

    /* Knoppen styling */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 16px !important;
        font-weight: 800 !important;
        padding: 0.75rem 1rem !important;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.25) !important;
    }
    div.stButton > button[kind="primary"] p, div.stButton > button[kind="primary"] span {
        color: #FFFFFF !important;
    }
    div.stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 16px !important;
        font-weight: 700 !important;
        padding: 0.75rem 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- STOPTOBER MEDISCHE MIJLPALEN ---
HEALTH_MILESTONES = [
    {
        "title": "💓 Bloeddruk & Hartslag normaal",
        "hours": 0.33,  # 20 minuten
        "desc": "Je hartslag en bloeddruk dalen direct terug naar hun normale, gezonde rustniveau."
    },
    {
        "title": "🩸 Zuurstofpeil in bloed naar 100%",
        "hours": 8,
        "desc": "De hoeveelheid nicotine en koolmonoxide in je bloed is al met de helft gedaald."
    },
    {
        "title": "🫁 Koolmonoxide volledig uit je lijf",
        "hours": 24,
        "desc": "Na 24 uur is alle koolmonoxide verdwenen. Je longen starten nu met de grote schoonmaak van slijm en teer."
    },
    {
        "title": "🍷 Smaak & Reuk herstellen (Diner-boost!)",
        "hours": 48,
        "desc": "Na 2 dagen is alle nicotine uit je lichaam. Je smaak- en reukzenuwen herstellen: goed eten en wijn smaken nu merkbaar rijker!"
    },
    {
        "title": "⚡ Meer lucht & Energie (Bronchiën open)",
        "hours": 72,
        "desc": "Na 3 dagen ontspannen je luchtpijpvertakkingen. Ademhalen gaat makkelijker en je hebt direct meer energie."
    },
    {
        "title": "🏃‍♂️ Bloedsomloop & Conditie (+15%)",
        "hours": 336,  # 14 dagen
        "desc": "Na 2 weken stroomt het bloed veel makkelijker door je spieren en organen. Wandelen en sporten gaan lichter."
    },
    {
        "title": "🧹 Trilhaartjes & Longen tot 30% schoner",
        "hours": 672,  # 28 dagen (Stoptober-doel!)
        "desc": "Na 4 weken zijn de trilhaartjes in je longen hersteld en is je nuttige longcapaciteit tot wel 30% verbeterd."
    },
    {
        "title": "🛡️ Volledig herstelde longreiniging",
        "hours": 2160,  # 90 dagen (3 maanden)
        "desc": "Na 3 maanden zijn je longen grotendeels schoon van oud slijm en werken je luchtwegen weer op volle kracht."
    }
]

# --- PERSOONLIJKE MOTIVATIEKAARTEN ---
DEFAULT_QUOTES = {
    "🛋️ 20:00 Op de bank": [
        "De kinderen liggen op bed: jullie avond begint. Je brein zoekt nu ontspanning, géén rook. Pak wat lekkers te drinken en zet € 0,65 in jullie diner-pot!",
        "Om 20:00 uur in de kou gaan staan haalt je juist uit je rust. Blijf lekker zitten; over 5 minuten ben je blij dat je niet bent opgestaan.",
        "Als je straks nog even bij de slapende kinderen kijkt, ruik je fris en warm in plaats van naar koude rook.",
        "Dat stemmetje om 20:00 uur is alleen een oude gewoonte. Elke keer dat je blijft zitten, wordt die prikkel zwakker.",
        "Twee avonden niet roken op de bank is alweer een speciaalbier of een goed glas wijn tijdens jullie etentje!"
    ],
    "🍺 Borrel & Gezelligheid": [
        "Een goed glas wijn of bier smaakt veel rijker als je smaakpapillen niet verdoofd worden door tabaksrook.",
        "Een sigaret bij een borrel geeft géén extra ontspanning: het vult alleen tijdelijk het onrustgevoel op dat de vorige sigaret heeft achtergelaten.",
        "Niet roken tijdens het drinken scheelt je morgenochtend de helft van je brakheid. Koolmonoxide uit rook versterkt een kater enorm.",
        "Spreek met jezelf af: ik drink eerst een groot glas ijskoud water en wacht 5 minuten. Daarna is de ergste drang altijd gezakt.",
        "Gezelligheid zit in het proosten en het gesprek aan tafel, niet in het buiten staan met een peuk."
    ],
    "🍽️ Samen Uit Eten": [
        "Elke 10 sigaretten die jullie samen laten liggen is € 6,50: dat is alweer een borrelplank of een dessert tijdens jullie avond uit!",
        "Hoe lekker smaakt jullie diner straks als je weet dat de hele avond — inclusief wijn — betaald is van niet-gerookte sigaretten?",
        "Samen stoppen maakt jullie twee keer zo sterk. Als de één twijfelt, houdt de ander de rug recht voor de diner-pot!",
        "Al na 48 uur zonder sigaret zijn je smaakpapillen hersteld en proef je subtiele smaken in goed eten en mooie wijn."
    ],
    "☀️ Morgenochtend & Gezondheid": [
        "Denk even aan morgenochtend 07:30 uur: niemand wordt ooit wakker met de gedachte 'had ik gisteravond maar wél gerookt'.",
        "Elke sigaret die je níét rookt, bespaart je longen direct 10 mg teer en levert je 11 minuten extra gezonde levensduur op.",
        "Na één rookvrije avond is het zuurstofgehalte in je bloed morgenochtend weer 100% en slaap je vannacht dieper.",
        "Een golf van trek duurt biologisch gezien nooit langer dan 3 tot 8 minuten. Adem rustig uit en laat de golf voorbijrollen."
    ]
}

# --- DATA LADEN & OPSLAAN ---
def load_data():
    default_start = (datetime.now() - timedelta(hours=18)).strftime("%Y-%m-%d %H:%M:%S")
    default_data = {
        "settings": {
            "cig_price": 0.65,
            "goal_name": "Samen uitgebreid uit eten",
            "goal_amount": 150.0,
            "ntfy_topic": "Rookvrij-alerts",
            "quit_start": {
                "Maarten": default_start,
                "Laura": default_start
            }
        },
        "logs": [],
        "borrel_commit": {
            "Maarten": {"active": False, "date": "", "max_drinks": 3, "note": ""},
            "Laura": {"active": False, "date": "", "max_drinks": 3, "note": ""}
        },
        "custom_quotes": []
    }
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                default_data["settings"].update(saved.get("settings", {}))
                if "quit_start" not in default_data["settings"]:
                    default_data["settings"]["quit_start"] = {"Maarten": default_start, "Laura": default_start}
                default_data["logs"] = saved.get("logs", [])
                if "borrel_commit" in saved and "Maarten" in saved["borrel_commit"]:
                    default_data["borrel_commit"] = saved["borrel_commit"]
                default_data["custom_quotes"] = saved.get("custom_quotes", [])
                return default_data
        except Exception:
            return default_data
    return default_data

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

data = load_data()
cig_price = float(data["settings"].get("cig_price", 0.65))

# --- HULPFUNCTIES ---
def add_log(user, event_type, count, trigger, note=""):
    now_full = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data["logs"].append({
        "id": int(time.time() * 1000) + random.randint(1, 999),
        "timestamp": datetime.now().strftime("%d-%m %H:%M"),
        "full_ts": now_full,
        "date": date.today().strftime("%Y-%m-%d"),
        "user": user,
        "type": event_type,
        "count": int(count),
        "trigger": trigger,
        "amount_eur": round(int(count) * cig_price, 2),
        "note": note
    })
    # Als er gerookt is, start de herstelklok voor die persoon opnieuw vanaf nu
    if event_type == "smoked":
        data["settings"]["quit_start"][user] = now_full
    save_data(data)

def get_hours_smoke_free(user):
    start_str = data["settings"]["quit_start"].get(user, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    try:
        start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
    except Exception:
        start_dt = datetime.now() - timedelta(hours=12)
    diff = datetime.now() - start_dt
    return max(0.05, diff.total_seconds() / 3600.0)

def format_duration_nl(hours):
    if hours < 1:
        return f"{int(hours * 60)} minuten"
    elif hours < 48:
        h = int(hours)
        m = int((hours - h) * 60)
        return f"{h} uur en {m} min"
    else:
        days = int(hours // 24)
        rem_h = int(hours % 24)
        return f"{days} dagen en {rem_h} uur"

def send_push_notification(topic, title_ascii, message_utf8):
    if not topic:
        return False, "Vul eerst een ntfy-kanaalnaam in."
    try:
        safe_title = title_ascii.encode("ascii", "ignore").decode("ascii")
        req = urllib.request.Request(
            f"https://ntfy.sh/{topic.strip()}",
            data=message_utf8.encode("utf-8"),
            headers={
                "Title": safe_title,
                "Priority": "high",
                "Tags": "clinking_glasses,no_smoking"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status == 200, f"Melding verzonden naar '{topic}'!"
    except Exception as e:
        return False, f"Kon melding niet versturen: {e}"

def get_user_stats(logs_list, user_filter=None):
    if not logs_list:
        return 0, 0, 0.0, 0.0, 0.0
    df = pd.DataFrame(logs_list)
    if "user" not in df.columns:
        df["user"] = "Maarten"
    if user_filter and user_filter != "Samen":
        df = df[df["user"] == user_filter]
    if df.empty:
        return 0, 0, 0.0, 0.0, 0.0
    resisted = int(df[df["type"] == "resisted"]["count"].sum())
    smoked = int(df[df["type"] == "smoked"]["count"].sum())
    saved_gross = round(resisted * cig_price, 2)
    spent_gross = round(smoked * cig_price, 2)
    net_saved = round(max(0.0, saved_gross - spent_gross), 2)
    return resisted, smoked, saved_gross, spent_gross, net_saved

def get_dinner_milestone(amount):
    if amount < 15:
        return "☕ Op weg naar: Borrelhapjes (€ 15)"
    elif amount < 35:
        return "🥂 Bereikt: Aperitief & Borrelplank!"
    elif amount < 75:
        return "🍷 Bereikt: Voorgerechten & Goede fles wijn!"
    elif amount < 120:
        return "🍽️ Bereikt: 3-gangen diner voor twee!"
    elif amount < 175:
        return "🦞 Bereikt: Luxe 4-gangen diner met wijn!"
    else:
        return "🌟 Sterren-diner bereikt! Tijd om te reserveren!"

# --- SIDEBAR: INSTELLINGEN ---
with st.sidebar:
    st.header("⚙️ Instellingen")
    new_cig_price = st.number_input(
        "Prijs per sigaret (€)",
        min_value=0.10,
        max_value=2.50,
        value=float(cig_price),
        step=0.05,
        format="%.2f"
    )
    new_goal_name = st.text_input("Jullie doel", value=data["settings"]["goal_name"])
    new_goal_amount = st.number_input("Doelbedrag etentje (€)", value=float(data["settings"]["goal_amount"]), step=10.0)
    new_ntfy_topic = st.text_input("ntfy.sh kanaal", value=data["settings"]["ntfy_topic"])
    
    if st.button("💾 Opslaan", use_container_width=True, type="primary"):
        data["settings"]["cig_price"] = round(new_cig_price, 2)
        data["settings"]["goal_name"] = new_goal_name
        data["settings"]["goal_amount"] = new_goal_amount
        data["settings"]["ntfy_topic"] = new_ntfy_topic.strip()
        save_data(data)
        st.success("Opgeslagen!")
        time.sleep(0.4)
        st.rerun()

# --- PROFIEL SELECTIE BOVENIN ---
if "active_user" not in st.session_state:
    st.session_state.active_user = "Maarten"

u_col1, u_col2, u_col3 = st.columns(3)
with u_col1:
    if st.button("👤 Maarten", type="primary" if st.session_state.active_user == "Maarten" else "secondary", use_container_width=True):
        st.session_state.active_user = "Maarten"
        st.rerun()
with u_col2:
    if st.button("👤 Laura", type="primary" if st.session_state.active_user == "Laura" else "secondary", use_container_width=True):
        st.session_state.active_user = "Laura"
        st.rerun()
with u_col3:
    if st.button("🥂 Samen", type="primary" if st.session_state.active_user == "Samen" else "secondary", use_container_width=True):
        st.session_state.active_user = "Samen"
        st.rerun()

active_profile = st.session_state.active_user

# Statistieken berekenen
resisted_cigs, smoked_cigs, saved_gross, spent_gross, net_saved = get_user_stats(data["logs"], active_profile)
team_resisted, _, _, _, total_team_saved = get_user_stats(data["logs"], "Samen")
_, _, _, _, maarten_saved = get_user_stats(data["logs"], "Maarten")
_, _, _, _, laura_saved = get_user_stats(data["logs"], "Laura")

goal_target = max(1.0, float(data["settings"]["goal_amount"]))
progress_pct = min(100, int((total_team_saved / goal_target) * 100))
cigs_left = max(0, int(round((goal_target - total_team_saved) / cig_price)))
milestone_text = get_dinner_milestone(total_team_saved)

# --- LUXE HERO BANNER (ALTIJD ZICHTBAAR BOVENIN) ---
st.markdown(f"""
<div class="hero-banner">
    <div class="hero-badge">{milestone_text}</div>
    <div class="hero-title">🥂 {data['settings']['goal_name']}</div>
    <div class="hero-sub">Elke niet-gerookte sigaret = <b>€ {cig_price:.2f}</b> in jullie gezamenlijke diner-pot</div>
    <div class="hero-amount-row">
        <span class="hero-big-amount">€ {total_team_saved:.2f}</span>
        <span class="hero-goal-lbl">Doel: € {goal_target:.0f} ({progress_pct}%)</span>
    </div>
    <div class="custom-prog-bg">
        <div class="custom-prog-fill" style="width: {progress_pct}%;"></div>
    </div>
    <div class="hero-footer">
        <span>👤 Maarten: € {maarten_saved:.2f}</span>
        <span>👤 Laura: € {laura_saved:.2f}</span>
        <span>Nog {cigs_left} stuks 🍽️</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 5 STRAKKE MOBIELE TABS ---
tab_dash, tab_health, tab_borrel, tab_sos, tab_push = st.tabs([
    "🍽️ Diner",
    "❤️ Lichaam",
    "🍷 Borrel",
    "🧘 SOS",
    "🔔 20:00"
])

# ==========================================
# TAB 1: DINER-POT & 1-KLIK LOGGEN
# ==========================================
with tab_dash:
    st.markdown(f"""
    <div class="bento-grid">
        <div class="bento-card">
            <div class="bento-lbl">Netto ({active_profile})</div>
            <div class="bento-val-emerald">€ {net_saved:.2f}</div>
            <div class="bento-sub">{resisted_cigs} weerstaan 💪</div>
        </div>
        <div class="bento-card">
            <div class="bento-lbl">Teer Bespaard</div>
            <div class="bento-val-amber">{resisted_cigs * 10} mg</div>
            <div class="bento-sub">Schone longen 🫁</div>
        </div>
        <div class="bento-card">
            <div class="bento-lbl">Gerookt ({active_profile})</div>
            <div class="bento-val-rose">€ {spent_gross:.2f}</div>
            <div class="bento-sub">{smoked_cigs} stuks 🚬</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    acting_user = "Maarten" if active_profile == "Samen" else active_profile
    st.markdown(f"##### ⚡ Snel bijwerken voor **{acting_user}**")
    
    if active_profile == "Samen":
        acting_user = st.radio("Op wiens naam log je?", ["Maarten", "Laura"], horizontal=True)

    col_t, col_n = st.columns([3, 1])
    with col_t:
        trigger_choice = st.selectbox(
            "Moment",
            [
                "🛋️ 20:00 Op de bank",
                "🍷 Borrel / Drankje",
                "☕ Na het eten / Koffie",
                "😤 Stress / Druk",
                "☀️ Terras / Gezelligheid",
                "🌟 Rookvrije avond"
            ]
        )
    with col_n:
        cigs_count = st.number_input("Aantal", min_value=1, max_value=20, value=1)

    b1, b2 = st.columns(2)
    with b1:
        if st.button(f"🔥 Weerstaan (+ € {cigs_count * cig_price:.2f})", type="primary", use_container_width=True):
            add_log(acting_user, "resisted", cigs_count, trigger_choice)
            st.toast(f"Top {acting_user}! + € {cigs_count * cig_price:.2f} voor jullie etentje!", icon="🥂")
            time.sleep(0.4)
            st.rerun()
    with b2:
        if st.button(f"🚬 Gerookt (- € {cigs_count * cig_price:.2f})", type="secondary", use_container_width=True):
            add_log(acting_user, "smoked", cigs_count, trigger_choice)
            st.toast("Eerlijk gelogd. Pak de draad direct weer op!", icon="🔄")
            time.sleep(0.4)
            st.rerun()

    st.write("")
    with st.expander("🧹 Correctie, Sigaretten Wissen & Test-Reset"):
        if data["logs"]:
            last = data["logs"][-1]
            status_lbl = "Weerstaan 💪" if last["type"] == "resisted" else "Gerookt 🚬"
            st.info(f"**Laatste actie:** {last.get('user','Maarten')} — {last['count']}x {status_lbl} (€ {last['amount_eur']:.2f})")
            
            r_col1, r_col2 = st.columns(2)
            with r_col1:
                if st.button("↩️ Wis laatste actie", use_container_width=True):
                    data["logs"].pop()
                    save_data(data)
                    st.rerun()
            with r_col2:
                if st.button("🗑️ Reset ALLES naar € 0", use_container_width=True):
                    data["logs"] = []
                    save_data(data)
                    st.rerun()

            st.divider()
            options = {
                f"{idx+1}. {r.get('timestamp','')} - {r.get('user','Maarten')}: {r['count']}x {'Weerstaan' if r['type']=='resisted' else 'Gerookt'} (€{r['amount_eur']:.2f})": idx
                for idx, r in enumerate(reversed(data["logs"]))
            }
            pick = st.selectbox("Of kies een specifieke invoer om te wissen:", list(options.keys()))
            if st.button("❌ Verwijder gekozen regel", use_container_width=True):
                rev_i = options[pick]
                real_i = len(data["logs"]) - 1 - rev_i
                data["logs"].pop(real_i)
                save_data(data)
                st.rerun()
        else:
            st.caption("De teller staat op € 0,00 (geen registraties om te wissen).")

# ==========================================
# TAB 2: STOPTOBER GEZONDHEIDSHERSTEL (NIEUW!)
# ==========================================
with tab_health:
    health_user = "Maarten" if active_profile == "Samen" else active_profile
    if active_profile == "Samen":
        health_user = st.radio("Bekijk lichaamsherstel van:", ["Maarten", "Laura"], horizontal=True)

    hours_free = get_hours_smoke_free(health_user)
    user_resisted, _, _, _, _ = get_user_stats(data["logs"], health_user)
    
    # Bereken fysieke metrics (gebaseerd op Stoptober / Trimbos cijfers)
    tar_avoided_mg = user_resisted * 10          # ~10 mg teer per sigaret
    co_avoided_mg = user_resisted * 12           # ~12 mg koolmonoxide per sigaret
    minutes_gained = user_resisted * 11          # +11 min levensverwachting per sigaret
    lung_clean_pct = min(100, int((hours_free / 672.0) * 100))  # 28 dagen = 100% Stoptober mijlpaal

    st.markdown(f"""
    <div class="health-summary-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-weight:800; font-size:1.05rem; color:#065F46;">🫁 Herstel van {health_user}</span>
            <span style="font-weight:800; font-size:0.85rem; color:#047857;">⏱️ {format_duration_nl(hours_free)} rookvrij</span>
        </div>
        <p style="font-size:0.82rem; color:#065F46; margin:6px 0 0 0;">
            Stoptober Long-Schoonmaak (28-dagen cyclus): <b>{lung_clean_pct}%</b> voltooid
        </p>
    </div>

    <div class="bento-grid">
        <div class="bento-card">
            <div class="bento-lbl">Teer Vermeden</div>
            <div class="bento-val-emerald">{tar_avoided_mg} mg</div>
            <div class="bento-sub">Schone luchtwegen</div>
        </div>
        <div class="bento-card">
            <div class="bento-lbl">Koolmonoxide</div>
            <div class="bento-val-amber">-{co_avoided_mg} mg</div>
            <div class="bento-sub">100% zuurstof</div>
        </div>
        <div class="bento-card">
            <div class="bento-lbl">Extra Levenstijd</div>
            <div class="bento-val-emerald">+{minutes_gained} m</div>
            <div class="bento-sub">11 min / sigaret</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("##### 📊 Live Medische Mijlpalen (Stoptober)")

    for m in HEALTH_MILESTONES:
        pct = min(100, int((hours_free / m["hours"]) * 100))
        is_done = pct >= 100
        card_cls = "health-item-done" if is_done else "health-item"
        badge_txt = "✅ 100% Bereikt" if is_done else f"⏳ {pct}%"
        
        st.markdown(f"""
        <div class="{card_cls}">
            <div class="health-top">
                <span class="health-title">{m['title']}</span>
                <span class="health-pct-badge">{badge_txt}</span>
            </div>
            <div class="health-desc">{m['desc']}</div>
            <div class="health-bar-bg">
                <div class="health-bar-fill" style="width: {pct}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with st.expander(f"⏱️ Pas rookvrije starttijd aan voor {health_user}"):
        st.caption("Wanneer heb je voor het laatst gerookt? Pas het hier aan zodat je percentages precies kloppen.")
        preset = st.selectbox(
            "Snel instellen:",
            [
                "Zojuist (zet klok op 0 minuten)",
                "Gisteravond om 20:00 uur",
                "2 dagen geleden (48 uur rookvrij)",
                "4 dagen geleden",
                "1 week geleden (7 dagen rookvrij)",
                "2 weken geleden (14 dagen rookvrij)"
            ]
        )
        if st.button(f"🔄 Starttijd voor {health_user} bijwerken", use_container_width=True):
            now = datetime.now()
            if "Zojuist" in preset:
                new_dt = now
            elif "Gisteravond" in preset:
                yest = now - timedelta(days=1)
                new_dt = yest.replace(hour=20, minute=0, second=0)
            elif "2 dagen" in preset:
                new_dt = now - timedelta(days=2)
            elif "4 dagen" in preset:
                new_dt = now - timedelta(days=4)
            elif "1 week" in preset:
                new_dt = now - timedelta(days=7)
            else:
                new_dt = now - timedelta(days=14)
            data["settings"]["quit_start"][health_user] = new_dt.strftime("%Y-%m-%d %H:%M:%S")
            save_data(data)
            st.success(f"Herstelklok voor {health_user} bijgewerkt!")
            time.sleep(0.4)
            st.rerun()

# ==========================================
# TAB 3: BORREL-MODUS
# ==========================================
with tab_borrel:
    borrel_user = "Maarten" if active_profile == "Samen" else active_profile
    st.subheader(f"🍷 Borrel-Modus ({borrel_user})")
    st.caption("Wel genieten van een goed glas wijn of bier, zonder dat je brein automatisch om nicotine vraagt.")

    today_str = date.today().strftime("%Y-%m-%d")
    u_commit = data["borrel_commit"].get(borrel_user, {"active": False, "date": "", "max_drinks": 3, "note": ""})
    is_active = u_commit.get("active", False) and u_commit.get("date") == today_str

    if not is_active:
        max_dr = st.slider("Hoeveel glazen drink je vanavond maximaal?", 1, 8, 3)
        plan = st.selectbox(
            "Wat doe je zodra je trek krijgt in een sigaret?",
            [
                "Ik drink eerst een groot glas ijskoud bruiswater",
                "Ik neem direct een sterke munt of kauwgom",
                "Ik blijf gezellig aan tafel zitten als anderen naar buiten gaan",
                "Ik zet eerst de 5-minuten timer hieronder aan"
            ]
        )
        if st.button(f"🥂 Activeer Borrel-Afspraak voor {borrel_user}", type="primary", use_container_width=True):
            data["borrel_commit"][borrel_user] = {
                "active": True,
                "date": today_str,
                "max_drinks": max_dr,
                "note": plan
            }
            save_data(data)
            st.rerun()
    else:
        st.success(f"**Afspraak voor {borrel_user} staat aan!**\n\n- Max **{u_commit['max_drinks']} glazen**, **0 sigaretten**.\n- Jouw actie bij trek: *{u_commit['note']}*")
        if st.button(f"🎉 Borrel rookvrij gehaald! (+ € {3 * cig_price:.2f} in de pot)", type="primary", use_container_width=True):
            add_log(borrel_user, "resisted", 3, "🍷 Borrel / Drankje", "Borrel-afspraak gehaald")
            data["borrel_commit"][borrel_user]["active"] = False
            save_data(data)
            st.balloons()
            time.sleep(0.7)
            st.rerun()

    st.divider()
    st.markdown("##### ⏱️ De 5-Minuten Afkoel-Klok")
    st.caption("Krijg je tijdens het borrelen ineens trek? Spreek af: ik beslis pas als deze klok op 00:00 staat.")
    wait_m = st.radio("Afkoeltijd:", [3, 5, 10], index=1, horizontal=True, format_func=lambda x: f"{x} min")
    if st.button(f"🚨 Start {wait_m}-Minuten Klok", type="secondary", use_container_width=True):
        t_box = st.empty()
        p_bar = st.progress(0.0)
        tot = wait_m * 60
        for s in range(tot, 0, -1):
            m, sec = divmod(s, 60)
            p_bar.progress((tot - s) / tot)
            t_box.markdown(f"""
            <div class="health-summary-card" style="text-align:center;">
                <h2 style="margin:0; color:#065F46;">⏳ {m:02d}:{sec:02d}</h2>
                <p style="margin-top:6px; margin-bottom:0; color:#047857;">Drink nu eerst een glas koud water. De piek zakt zo vanzelf weg!</p>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(1)
        p_bar.progress(1.0)
        t_box.success(f"🎉 De trek is voorbij! Log je + € {cig_price:.2f} bij het eerste tabblad!")

# ==========================================
# TAB 4: SOS & MOTIVATIEKAARTEN
# ==========================================
with tab_sos:
    st.subheader("💡 Persoonlijke Motivatiekaarten")
    cat = st.selectbox(
        "Kies het onderwerp:",
        ["🔄 Alle kaarten (Willekeurig)"] + list(DEFAULT_QUOTES.keys()) + ["❤️ Eigen kaarten"]
    )

    if cat == "🔄 Alle kaarten (Willekeurig)":
        pool = [q for qs in DEFAULT_QUOTES.values() for q in qs] + data["custom_quotes"]
    elif cat == "❤️ Eigen kaarten":
        pool = data["custom_quotes"] if data["custom_quotes"] else ["Voeg hieronder jullie eerste eigen motivatiekaart toe!"]
    else:
        pool = DEFAULT_QUOTES[cat]

    if "curr_q" not in st.session_state or st.session_state.get("last_c") != cat:
        st.session_state.curr_q = random.choice(pool)
        st.session_state.last_c = cat

    st.markdown(f"""
    <div class="flashcard">
        <p class="flashcard-quote">“{st.session_state.curr_q}”</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔀 Volgende Motivatiekaart", type="primary", use_container_width=True):
        st.session_state.curr_q = random.choice(pool)
        st.rerun()

    with st.expander("➕ Eigen kaart toevoegen voor jezelf of voor Laura"):
        new_q = st.text_input("Jullie eigen motivatietekst:")
        if st.button("Opslaan"):
            if new_q.strip():
                data["custom_quotes"].append(new_q.strip())
                save_data(data)
                st.session_state.curr_q = new_q.strip()
                st.success("Kaart opgeslagen!")
                st.rerun()

    st.divider()
    st.subheader("🌬️ Ademhalings-Coach (4-7-8 Reset)")
    st.markdown("""
    <div class="breath-card">
        <div class="breath-orb">Adem rustig<br>mee</div>
        <p style="font-size:0.82rem; color:#475569; margin-top:12px; margin-bottom:0;">
            <b>Groter</b> = 4s Inademen &nbsp;•&nbsp; <b>Geel</b> = 7s Vasthouden &nbsp;•&nbsp; <b>Kleiner</b> = 8s Uitblazen
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# TAB 5: 20:00 BANK-MELDING
# ==========================================
with tab_push:
    st.subheader("🔔 De 20:00 'Op de bank'-Melding")
    st.write(f"Jullie ntfy-kanaal: **`{data['settings']['ntfy_topic']}`**")
    st.markdown(f"""
    * Rond **20:00 uur** liggen de kinderen op bed en schakelt je brein over naar ontspanning.
    * Doorbreek de gewoonte: loop om 20:00 uur eerst naar de keuken voor een lekker drankje en zet direct **+ € {cig_price:.2f}** in jullie Diner-Pot.
    """)

    if st.button(f"📲 Stuur testmelding naar '{data['settings']['ntfy_topic']}'", type="primary", use_container_width=True):
        ok, msg = send_push_notification(
            data["settings"]["ntfy_topic"],
            "20:00 Avond Check-in voor Maarten en Laura",
            f"🥂 Kinderen op bed? Plof lekker op de bank ZONDER sigaret! Jullie diner-pot staat al op € {total_team_saved:.2f}."
        )
        if ok:
            st.success(msg + " Kijk nu in je ntfy-app!")
        else:
            st.error(msg)
