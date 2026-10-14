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

# --- 100% LEESBARE LIGHT-LUXURY MOBILE CSS (GEEN DONKERE VLAKKEN MEER) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

    /* 1. Algemene app achtergrond: fris, helder en altijd donkere tekst */
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #F4F7F6 !important;
        color: #0F172A !important;
    }

    /* Verberg standaard Streamlit balken */
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

    /* 2. Forceer ALLE tekst in de app standaard op diep donkerblauw/zwart */
    p, span, label, h1, h2, h3, h4, h5, h6, li,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stWidgetLabel"] p,
    [data-testid="stCaptionContainer"] p {
        color: #0F172A !important;
    }

    /* 3. Forceer ALLE Streamlit invoervelden, dropdowns, expanders en sidebar naar WIT met DONKERE tekst
       (voorkomt dat Dark Mode op een telefoon zwarte tekst op donkergrijze knoppen/menu's zet) */
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }
    div[data-baseweb="select"] > div,
    div[data-baseweb="base-input"],
    div[data-baseweb="input"],
    input {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        border-color: #CBD5E1 !important;
        border-radius: 12px !important;
    }
    /* Dropdown uitklapmenu's */
    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    ul[role="listbox"],
    li[role="option"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }
    li[role="option"]:hover, li[role="option"][aria-selected="true"] {
        background-color: #ECFDF5 !important;
        color: #065F46 !important;
        font-weight: 700 !important;
    }
    /* Plus en min knoppen bij getallen */
    button[data-testid="stNumberInputStepUp"],
    button[data-testid="stNumberInputStepDown"] {
        background-color: #F1F5F9 !important;
        color: #0F172A !important;
    }
    /* Uitvouwbalken (Expanders) */
    details[data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 16px !important;
        padding: 4px 8px !important;
    }
    details[data-testid="stExpander"] summary,
    details[data-testid="stExpander"] summary p,
    details[data-testid="stExpander"] summary svg {
        color: #0F172A !important;
        fill: #0F172A !important;
        font-weight: 700 !important;
    }

    /* 4. Heldere Luxe Hero Card bovenin (Geen donkere achtergrond meer!) */
    .hero-banner {
        background: linear-gradient(135deg, #FFFFFF 0%, #ECFDF5 60%, #FEF3C7 100%);
        border: 2px solid #6EE7B7;
        border-radius: 24px;
        padding: 20px 18px;
        box-shadow: 0 8px 20px -4px rgba(5, 150, 105, 0.12);
        margin-bottom: 14px;
    }
    .hero-badge {
        display: inline-block;
        background: #FEF3C7;
        color: #92400E !important;
        border: 1px solid #F59E0B;
        font-size: 0.75rem;
        font-weight: 800;
        padding: 4px 12px;
        border-radius: 999px;
        margin-bottom: 8px;
    }
    .hero-title {
        font-size: 1.4rem;
        font-weight: 800;
        color: #064E3B !important;
        margin: 0 0 4px 0;
        line-height: 1.25;
    }
    .hero-sub {
        font-size: 0.85rem;
        color: #334155 !important;
        font-weight: 600;
        margin: 0 0 14px 0;
    }
    .hero-amount-row {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 6px;
    }
    .hero-big-amount {
        font-size: 2.05rem;
        font-weight: 800;
        color: #059669 !important;
        line-height: 1;
    }
    .hero-goal-lbl {
        font-size: 0.84rem;
        font-weight: 700;
        color: #334155 !important;
    }
    .custom-prog-bg {
        width: 100%;
        height: 12px;
        background: #E2E8F0;
        border-radius: 999px;
        overflow: hidden;
        margin-bottom: 10px;
        border: 1px solid #CBD5E1;
    }
    .custom-prog-fill {
        height: 100%;
        background: linear-gradient(90deg, #059669 0%, #10B981 60%, #F59E0B 100%);
        border-radius: 999px;
    }
    .hero-footer {
        display: flex;
        justify-content: space-between;
        font-size: 0.8rem;
        color: #0F172A !important;
        font-weight: 700;
        background: rgba(255, 255, 255, 0.75);
        padding: 6px 10px;
        border-radius: 10px;
    }

    /* 5. Bento Grid Score Kaarten */
    .bento-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        margin: 12px 0 16px 0;
    }
    .bento-card {
        background: #FFFFFF;
        border: 1.5px solid #CBD5E1;
        border-radius: 18px;
        padding: 12px 6px;
        text-align: center;
        box-shadow: 0 3px 8px rgba(15, 23, 42, 0.04);
    }
    .bento-lbl {
        font-size: 0.68rem;
        font-weight: 800;
        text-transform: uppercase;
        color: #475569 !important;
        margin-bottom: 4px;
    }
    .bento-val-emerald {
        font-size: 1.25rem;
        font-weight: 800;
        color: #059669 !important;
    }
    .bento-val-amber {
        font-size: 1.25rem;
        font-weight: 800;
        color: #D97706 !important;
    }
    .bento-val-rose {
        font-size: 1.25rem;
        font-weight: 800;
        color: #E11D48 !important;
    }
    .bento-sub {
        font-size: 0.7rem;
        color: #475569 !important;
        font-weight: 600;
        margin-top: 2px;
    }

    /* 6. Gezondheid & Subdoel Kaarten */
    .health-summary-card {
        background: #ECFDF5;
        border: 2px solid #6EE7B7;
        border-radius: 20px;
        padding: 16px;
        margin-bottom: 14px;
    }
    .health-item {
        background: #FFFFFF;
        border: 1.5px solid #CBD5E1;
        border-radius: 18px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }
    .health-item-done {
        background: #F0FDF4;
        border: 2px solid #34D399;
        border-left: 6px solid #059669;
        border-radius: 18px;
        padding: 14px 16px;
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
        font-size: 0.74rem;
        font-weight: 800;
        padding: 3px 9px;
        border-radius: 999px;
        background: #D1FAE5;
        color: #065F46 !important;
    }
    .health-desc {
        font-size: 0.8rem;
        color: #334155 !important;
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

    /* 7. Motivatie Flashcard & Ademhaling */
    .flashcard {
        background: #FFFBEB;
        border: 2px solid #F59E0B;
        border-radius: 22px;
        padding: 22px 18px;
        margin: 14px 0;
        text-align: center;
    }
    .flashcard-quote {
        font-size: 1.05rem;
        font-weight: 700;
        color: #78350F !important;
        line-height: 1.55;
        margin: 0;
    }

    @keyframes breathe-anim {
        0%, 100% { transform: scale(0.7); background-color: #E0F2FE; border-color: #0284C7; }
        25% { transform: scale(1.12); background-color: #D1FAE5; border-color: #059669; }
        60% { transform: scale(1.12); background-color: #FEF3C7; border-color: #D97706; }
    }
    .breath-card {
        background: #FFFFFF;
        border: 1.5px solid #CBD5E1;
        border-radius: 22px;
        padding: 26px 16px;
        text-align: center;
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
        font-size: 0.92rem;
        color: #0F172A !important;
        animation: breathe-anim 19s infinite ease-in-out;
    }

    /* 8. Tabbladen balk */
    div[data-baseweb="tab-list"] {
        gap: 3px !important;
        background-color: #E2E8F0 !important;
        padding: 4px !important;
        border-radius: 14px !important;
    }
    button[data-baseweb="tab"] {
        flex: 1 !important;
        font-size: 0.76rem !important;
        font-weight: 800 !important;
        padding: 8px 4px !important;
        border-radius: 10px !important;
        color: #334155 !important;
        background-color: transparent !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #059669 !important;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.1) !important;
    }

    /* 9. Knoppen met gegarandeerd contrast */
    div.stButton > button[kind="primary"] {
        background: #059669 !important;
        color: #FFFFFF !important;
        border: 2px solid #047857 !important;
        border-radius: 16px !important;
        font-weight: 800 !important;
        padding: 0.75rem 1rem !important;
    }
    div.stButton > button[kind="primary"] *,
    div.stButton > button[kind="primary"] p,
    div.stButton > button[kind="primary"] span {
        color: #FFFFFF !important;
    }
    div.stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 2px solid #CBD5E1 !important;
        border-radius: 16px !important;
        font-weight: 800 !important;
        padding: 0.75rem 1rem !important;
    }
    div.stButton > button[kind="secondary"] *,
    div.stButton > button[kind="secondary"] p,
    div.stButton > button[kind="secondary"] span {
        color: #0F172A !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SUBDOELEN OP BASIS VAN WEERSTANE SIGARETTEN ---
CIG_SUBGOALS = [
    {
        "target_cigs": 5,
        "title": "🎯 Subdoel 1: De Eerste 5 Weerstaan",
        "reward": "+55 min extra levenstijd & 50 mg teer bespaard"
    },
    {
        "target_cigs": 20,
        "title": "🎯 Subdoel 2: Heel Pakje Uitgespaard (20 stuks)",
        "reward": "+3,5 uur extra levenstijd & 200 mg teer uit je longen"
    },
    {
        "target_cigs": 50,
        "title": "🎯 Subdoel 3: Vijftig Keer Sterk Gebleven",
        "reward": "+9 uur extra levenstijd & een halve gram teer vermeden"
    },
    {
        "target_cigs": 100,
        "title": "🎯 Subdoel 4: De Mijlpaal van 100 Sigaretten",
        "reward": "+18 uur extra levenstijd & 1 volle gram teer bespaard!"
    }
]

# --- MEDISCHE GEZONDHEIDSVOORDELEN (TIJD ROOKVRIJ) ---
HEALTH_MILESTONES = [
    {
        "title": "💓 Subdoel 20 min: Hartslag & Bloeddruk rustig",
        "hours": 0.33,
        "desc": "Je hartslag en bloeddruk dalen direct terug naar hun normale niveau. Je handen en voeten worden warmer."
    },
    {
        "title": "🩸 Subdoel 8 uur: Zuurstofpeil naar 100%",
        "hours": 8,
        "desc": "De helft van de nicotine en koolmonoxide is uit je bloed. Je spieren en hersenen krijgen weer volop zuurstof."
    },
    {
        "title": "🫁 Subdoel 24 uur: Koolmonoxide-vrij",
        "hours": 24,
        "desc": "Na één dag is alle koolmonoxide uit je lichaam verdwenen. Je longen starten met het opruimen van slijm."
    },
    {
        "title": "🍷 Subdoel 48 uur: Smaak & Reuk terug (Diner-boost!)",
        "hours": 48,
        "desc": "Alle nicotine is uit je lijf. Je smaak- en reukzenuwen herstellen: lekker eten en goede wijn smaken nu veel rijker!"
    },
    {
        "title": "⚡ Subdoel 72 uur: Meer lucht & Energie",
        "hours": 72,
        "desc": "Na 3 dagen ontspannen je luchtpijpvertakkingen. Ademhalen gaat makkelijker en je hebt direct meer energie."
    },
    {
        "title": "🏃‍♂️ Subdoel 2 weken: Betere bloedsomloop & Conditie",
        "hours": 336,
        "desc": "Het bloed stroomt veel makkelijker door je hele lichaam. Wandelen, traplopen en sporten gaan merkbaar lichter."
    },
    {
        "title": "🛡️ Subdoel 1 tot 3 mnd: Tot 30% meer longcapaciteit",
        "hours": 1440,
        "desc": "De trilhaartjes in je luchtwegen zijn hersteld en houden je longen schoon. Je longfunctie is tot wel 30% verbeterd."
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
    "🍷 Borrel & Gezelligheid": [
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
        "Elke sigaret die je níét rookt, levert je direct 11 minuten extra gezonde levenstijd op én € 0,65 voor jullie etentje.",
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

def format_life_gained(cigs_resisted):
    total_mins = int(cigs_resisted * 11)
    if total_mins < 60:
        return f"+{total_mins} min"
    else:
        h = total_mins // 60
        m = total_mins % 60
        return f"+{h}u {m}m"

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

# --- HELDERE LUXE HERO BANNER (ALTIJD SCHERP LEESBAAR) ---
st.markdown(f"""
<div class="hero-banner">
    <div class="hero-badge">{milestone_text}</div>
    <div class="hero-title">🥂 {data['settings']['goal_name']}</div>
    <div class="hero-sub">Elke niet-gerookte sigaret = <b>€ {cig_price:.2f}</b> voor jullie etentje én <b>+11 min</b> levenstijd</div>
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
# TAB 1: DINER-POT & 1-KLIK LOGGEN (MET +11 MIN LANGER LEVEN)
# ==========================================
with tab_dash:
    life_str = format_life_gained(resisted_cigs)
    st.markdown(f"""
    <div class="bento-grid">
        <div class="bento-card">
            <div class="bento-lbl">Netto ({active_profile})</div>
            <div class="bento-val-emerald">€ {net_saved:.2f}</div>
            <div class="bento-sub">{resisted_cigs} weerstaan 💪</div>
        </div>
        <div class="bento-card">
            <div class="bento-lbl">Langer Leven</div>
            <div class="bento-val-amber">{life_str}</div>
            <div class="bento-sub">+11 min / sigaret ❤️</div>
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
            st.toast(f"Top {acting_user}! + € {cigs_count * cig_price:.2f} én +{cigs_count * 11} min levenstijd!", icon="🥂")
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
# TAB 2: GEZONDHEIDSVOORDELEN & SUBDOELEN
# ==========================================
with tab_health:
    health_user = "Maarten" if active_profile == "Samen" else active_profile
    if active_profile == "Samen":
        health_user = st.radio("Bekijk gezondheid & subdoelen van:", ["Maarten", "Laura"], horizontal=True)

    hours_free = get_hours_smoke_free(health_user)
    user_resisted, _, _, _, _ = get_user_stats(data["logs"], health_user)
    
    tar_avoided_mg = user_resisted * 10
    co_avoided_mg = user_resisted * 12
    life_gained_txt = format_life_gained(user_resisted)

    st.markdown(f"""
    <div class="health-summary-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-weight:800; font-size:1.05rem; color:#064E3B;">❤️ Gezondheidswinst ({health_user})</span>
            <span style="font-weight:800; font-size:0.85rem; color:#047857;">⏱️ {format_duration_nl(hours_free)} rookvrij</span>
        </div>
        <p style="font-size:0.82rem; color:#065F46; margin:6px 0 0 0;">
            Elke sigaret die je overslaat telt direct mee voor je lichaam én je subdoelen hieronder.
        </p>
    </div>

    <div class="bento-grid">
        <div class="bento-card">
            <div class="bento-lbl">Langer Leven</div>
            <div class="bento-val-emerald">{life_gained_txt}</div>
            <div class="bento-sub">+11 min / stuk</div>
        </div>
        <div class="bento-card">
            <div class="bento-lbl">Teer Bespaard</div>
            <div class="bento-val-amber">{tar_avoided_mg} mg</div>
            <div class="bento-sub">Schone longen</div>
        </div>
        <div class="bento-card">
            <div class="bento-lbl">Koolmonoxide</div>
            <div class="bento-val-emerald">-{co_avoided_mg} mg</div>
            <div class="bento-sub">Meer zuurstof</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("##### 🏆 Subdoelen: Aantal Weerstane Sigaretten")
    for sg in CIG_SUBGOALS:
        pct_sg = min(100, int((user_resisted / sg["target_cigs"]) * 100))
        done_sg = pct_sg >= 100
        cls_sg = "health-item-done" if done_sg else "health-item"
        badge_sg = "✅ Behaald!" if done_sg else f"{user_resisted} / {sg['target_cigs']} stuks ({pct_sg}%)"
        st.markdown(f"""
        <div class="{cls_sg}">
            <div class="health-top">
                <span class="health-title">{sg['title']}</span>
                <span class="health-pct-badge">{badge_sg}</span>
            </div>
            <div class="health-desc">{sg['reward']}</div>
            <div class="health-bar-bg">
                <div class="health-bar-fill" style="width: {pct_sg}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("##### 🫁 Lichaamsherstel Subdoelen (Sinds laatste sigaret)")
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
        st.caption("Wanneer heb je voor het laatst gerookt? Pas het hier aan zodat je herstel-subdoelen kloppen.")
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
    st.write("Wel genieten van een goed glas wijn of bier, zonder dat je brein automatisch om nicotine vraagt.")

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
    st.write("Krijg je tijdens het borrelen ineens trek? Spreek af: ik beslis pas als deze klok op 00:00 staat.")
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
        <p style="font-size:0.84rem; color:#0F172A; margin-top:12px; margin-bottom:0;">
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
