import streamlit as st
import pandas as pd
import json
import os
import time
import random
import urllib.request
from datetime import datetime, date

# --- PAGINA CONFIGURATIE ---
st.set_page_config(
    page_title="Rookvrij & Uit Eten",
    page_icon="🥂",
    layout="centered",
    initial_sidebar_state="collapsed"
)

DATA_FILE = "rookvrij_diner_data.json"

# --- CUSTOM UX/UI CSS STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Verberg standaard Streamlit ruis voor echte app-look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background: transparent !important;}
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 4rem !important;
        max-width: 540px !important;
    }

    /* Hero Diner Card */
    .hero-card {
        background: linear-gradient(135deg, #064E3B 0%, #047857 55%, #0F766E 100%);
        color: #FFFFFF;
        padding: 24px 22px;
        border-radius: 24px;
        box-shadow: 0 14px 30px -10px rgba(6, 78, 59, 0.45);
        margin-bottom: 18px;
        position: relative;
        overflow: hidden;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.18);
        backdrop-filter: blur(8px);
        padding: 5px 12px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        margin-bottom: 10px;
        color: #ECFDF5;
    }
    .hero-amount {
        font-size: 2.75rem;
        font-weight: 800;
        line-height: 1.05;
        margin: 4px 0 6px 0;
        letter-spacing: -0.02em;
        color: #FFFFFF;
    }
    .hero-sub {
        font-size: 0.92rem;
        color: #D1FAE5;
        margin-bottom: 16px;
    }

    /* Custom Progress Bar in Hero */
    .progress-track {
        background: rgba(255, 255, 255, 0.22);
        border-radius: 999px;
        height: 12px;
        width: 100%;
        overflow: hidden;
        margin: 10px 0 14px 0;
    }
    .progress-fill {
        background: linear-gradient(90deg, #FBBF24 0%, #F59E0B 100%);
        height: 100%;
        border-radius: 999px;
        transition: width 0.5s ease;
    }

    /* Team Bijdrage Pills */
    .team-row {
        display: flex;
        gap: 10px;
        margin-top: 12px;
    }
    .team-pill {
        flex: 1;
        background: rgba(255, 255, 255, 0.13);
        border: 1px solid rgba(255, 255, 255, 0.18);
        padding: 10px 12px;
        border-radius: 14px;
        font-size: 0.84rem;
        color: #FFFFFF;
    }
    .team-pill strong {
        display: block;
        font-size: 1.05rem;
        color: #FDE68A;
    }

    /* Stat Mini Cards */
    .stat-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 10px;
        margin-bottom: 18px;
    }
    .stat-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 12px 10px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
    }
    .stat-label {
        font-size: 0.72rem;
        color: #6B7280;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .stat-val {
        font-size: 1.2rem;
        font-weight: 800;
        color: #111827;
        margin-top: 2px;
    }

    /* Motivatie Flashcard */
    .quote-card {
        background: linear-gradient(145deg, #FFFBEB 0%, #FEF3C7 100%);
        border: 1px solid #FDE68A;
        border-radius: 22px;
        padding: 26px 22px;
        margin: 12px 0 18px 0;
        box-shadow: 0 8px 20px -6px rgba(245, 158, 11, 0.18);
    }
    .quote-cat {
        display: inline-block;
        background: #F59E0B;
        color: #FFFFFF;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 999px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 12px;
    }
    .quote-text {
        font-size: 1.18rem;
        font-weight: 700;
        color: #78350F;
        line-height: 1.45;
    }

    /* Ademhalings-cirkel animatie */
    @keyframes pulseOrb {
        0%   { transform: scale(0.85); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.45); }
        50%  { transform: scale(1.12); box-shadow: 0 0 0 22px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.85); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    .breath-orb {
        width: 130px;
        height: 130px;
        border-radius: 50%;
        background: radial-gradient(circle, #34D399 0%, #059669 100%);
        margin: 22px auto;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 800;
        font-size: 1.1rem;
        animation: pulseOrb 5s infinite ease-in-out;
    }

    /* Mooiere afgeronde knoppen */
    div.stButton > button {
        border-radius: 14px !important;
        font-weight: 700 !important;
        padding: 0.65rem 1rem !important;
        transition: all 0.15s ease !important;
    }
</style>
""", unsafe_allow_html=True)

# --- STANDAARDMOTIVATIEKAARTEN (PERSOONLIJK & GECATEGORISEERD) ---
DEFAULT_QUOTES = [
    {"cat": "🍽️ Samen Uit Eten", "text": "Elke sigaret die jullie laten liggen is direct € 0,64 extra op de rekening van jullie volgende avond uitgebreid tafelen."},
    {"cat": "🍽️ Samen Uit Eten", "text": "Zestien weerstane sigaretten van jullie samen is alweer een heerlijke cocktail of een goed glas wijn tijdens jullie diner."},
    {"cat": "🍽️ Samen Uit Eten", "text": "Proef het verschil: zonder rook proef en ruik je straks elk detail van een goed gerecht en een mooi glas wijn veel intenser."},
    {"cat": "👶 Kinderen & Thuis", "text": "Als je straks nog even bij de slapende kinderen kijkt of ze een kus geeft, ruik je fris en vertrouwd in plaats van naar koude rook."},
    {"cat": "👶 Kinderen & Thuis", "text": "Het mooiste cadeau voor de kinderen is niet alleen gezonde ouders, maar ook het voorbeeld dat je oude gewoontes de baas kunt zijn."},
    {"cat": "🛋️ 20:00 Op de Bank", "text": "Om 20:00 uur ben je niet verslaafd aan nicotine, maar zoekt je brein een beloning omdat de spits met de kinderen voorbij is. Pak iets lekkers te drinken!"},
    {"cat": "🛋️ 20:00 Op de Bank", "text": "Op de bank ploffen voelt tien keer zo ontspannen als je niet eerst de kou in hoeft om je hartslag kunstmatig op te jagen met koolmonoxide."},
    {"cat": "🛋️ 20:00 Op de Bank", "text": "Doorbreek de 20:00-automatische piloot: loop na het naar bed brengen van de kinderen eerst naar de keuken voor een glas fris, thee of een goede snack."},
    {"cat": "🍷 De Borrel de Baas", "text": "Een sigaret bij een borrel geeft geen extra gezelligheid; het vult alleen tijdelijk de onrust op die de vorige sigaret heeft achtergelaten."},
    {"cat": "🍷 De Borrel de Baas", "text": "Alcohol zonder nicotine betekent morgenochtend twee keer zo fris opstaan. Een kater komt voor de helft door de koolmonoxide van het meesnaaien."},
    {"cat": "🍷 De Borrel de Baas", "text": "Geef jezelf bij een glas wijn of bier 10 minuten speeltijd: drink eerst een glas koud water. Na 8 minuten is de fysieke piek van de trek altijd voorbij."},
    {"cat": "⚡ Frisse Ochtend", "text": "Denk aan morgenochtend 07:30 uur: hoe lekker is het om wakker te worden met een schone keel, frisse adem en nul spijt van gisteravond?"},
    {"cat": "⚡ Frisse Ochtend", "text": "Je hebt nog nooit de volgende ochtend gedacht: 'Wat ben ik blij dat ik gisteravond laat toch nog die sigaret heb gerookt.'"},
    {"cat": "💪 Samen Sterk", "text": "Maarten & Laura: als één van jullie twijfelt, is dat hét moment om samen een streep te trekken en direct € 1,28 in de diner-pot te tikken."}
]

# --- DATA LADEN & OPSLAAN ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                # Zorg dat nieuwe velden altijd bestaan
                if "cig_price" not in loaded.get("settings", {}):
                    loaded["settings"]["cig_price"] = 0.64
                if not loaded.get("settings", {}).get("ntfy_topic"):
                    loaded["settings"]["ntfy_topic"] = "Rookvrij-alerts"
                if "quotes" not in loaded or not isinstance(loaded["quotes"], list):
                    loaded["quotes"] = DEFAULT_QUOTES
                return loaded
        except Exception:
            pass
    return {
        "settings": {
            "cig_price": 0.64,
            "goal_name": "Luxe Diner voor Maarten & Laura",
            "goal_amount": 150.0,
            "ntfy_topic": "Rookvrij-alerts"
        },
        "logs": [],
        "borrel_commits": {
            "Maarten": {"active": False, "date": "", "max_drinks": 3, "note": ""},
            "Laura": {"active": False, "date": "", "max_drinks": 3, "note": ""}
        },
        "quotes": DEFAULT_QUOTES
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

data = load_data()
cig_price = float(data["settings"].get("cig_price", 0.64))

# --- HULPFUNCTIES ---
def add_log(user, event_type, count, trigger, note=""):
    data["logs"].append({
        "id": int(time.time() * 1000) + random.randint(1, 999),
        "timestamp": datetime.now().strftime("%d-%m %H:%M"),
        "date": date.today().strftime("%Y-%m-%d"),
        "user": user,
        "type": event_type,  # 'resisted' of 'smoked'
        "count": int(count),
        "trigger": trigger,
        "amount_eur": round(int(count) * cig_price, 2),
        "note": note
    })
    save_data(data)

def get_diner_milestone(amount):
    if amount < 15:
        return "🥂 Stap 1: Op weg naar het Aperitief & Broodplankje (€ 15)"
    elif amount < 45:
        return "🍤 Stap 2: Aperitief binnen! Nu op naar de Voorgerechten (€ 45)"
    elif amount < 90:
        return "🍷 Stap 3: Voorgerechten binnen! Op naar Goede Wijn & Hoofdgerechten (€ 90)"
    elif amount < 150:
        return "🍰 Stap 4: Bijna daar! Op naar het Dessert & Koffie Compleet (€ 150)"
    else:
        return "🌟 Doel Bereikt! Jullie Luxe Diner voor Twee is 100% verdiend!"

def send_push_notification(topic, title, message):
    if not topic:
        return False, "Geen ntfy-kanaal ingesteld."
    try:
        req = urllib.request.Request(
            f"https://ntfy.sh/{topic.strip()}",
            data=message.encode("utf-8"),
            headers={
                "Title": title,
                "Priority": "high",
                "Tags": "clinking_glasses,no_smoking"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status == 200, f"Pushmelding verzonden naar '{topic}'!"
    except Exception as e:
        return False, f"Kon melding niet versturen: {e}"

# --- SIDEBAR: INSTELLINGEN ---
with st.sidebar:
    st.header("⚙️ Instellingen")
    new_cig_price = st.number_input(
        "Prijs per losse sigaret (€)",
        min_value=0.10,
        max_value=2.50,
        value=float(cig_price),
        step=0.01,
        format="%.2f"
    )
    new_goal_name = st.text_input("Naam van jullie doel", value=data["settings"]["goal_name"])
    new_goal_amount = st.number_input("Streefbedrag Etentje (€)", value=float(data["settings"]["goal_amount"]), step=10.0)
    new_ntfy = st.text_input("ntfy.sh kanaalnaam", value=data["settings"]["ntfy_topic"])

    if st.button("💾 Opslaan", use_container_width=True, type="primary"):
        data["settings"]["cig_price"] = round(new_cig_price, 2)
        data["settings"]["goal_name"] = new_goal_name
        data["settings"]["goal_amount"] = new_goal_amount
        data["settings"]["ntfy_topic"] = new_ntfy.strip()
        save_data(data)
        st.success("Instellingen bijgewerkt!")
        time.sleep(0.5)
        st.rerun()

# --- PROFIEL KIEZER BOVENAAN ---
st.markdown("### 🥂 Rookvrij & Samen Uit Eten")
active_profile = st.radio(
    "Wie gebruikt de app nu?",
    ["Maarten", "Laura", "Samen (Overzicht)"],
    horizontal=True,
    label_visibility="collapsed"
)
current_user = "Maarten" if active_profile == "Samen (Overzicht)" else active_profile

# --- BEREKENINGEN ---
df_logs = pd.DataFrame(data["logs"])

def calc_user_stats(user_filter=None):
    if df_logs.empty:
        return 0, 0, 0.0, 0.0, 0.0
    sub = df_logs if user_filter is None else df_logs[df_logs["user"] == user_filter]
    if sub.empty:
        return 0, 0, 0.0, 0.0, 0.0
    res = int(sub[sub["type"] == "resisted"]["count"].sum())
    smk = int(sub[sub["type"] == "smoked"]["count"].sum())
    saved_val = res * cig_price
    spent_val = smk * cig_price
    net_val = max(0.0, saved_val - spent_val)
    return res, smk, saved_val, spent_val, net_val

tot_res, tot_smk, tot_saved, tot_spent, tot_net = calc_user_stats(None)
m_res, m_smk, m_saved, m_spent, m_net = calc_user_stats("Maarten")
l_res, l_smk, l_saved, l_spent, l_net = calc_user_stats("Laura")

goal_target = max(1.0, float(data["settings"]["goal_amount"]))
progress_pct = min(100, int((tot_net / goal_target) * 100))
milestone_text = get_diner_milestone(tot_net)

# --- HERO DINER CARD (ALTIJD ZICHTBAAR BOVENAAN) ---
st.markdown(f"""
<div class="hero-card">
    <div class="hero-badge">🍽️ {data['settings']['goal_name']} • € {cig_price:.2f} / sigaret</div>
    <div class="hero-amount">€ {tot_net:.2f} <span style="font-size:1.1rem; font-weight:500; opacity:0.85;">/ € {goal_target:.0f}</span></div>
    <div class="hero-sub">{milestone_text}</div>
    <div class="progress-track">
        <div class="progress-fill" style="width: {progress_pct}%;"></div>
    </div>
    <div class="team-row">
        <div class="team-pill">
            👤 Maarten
            <strong>€ {m_net:.2f}</strong>
            <span>{m_res} weerstaan • {m_smk} gerookt</span>
        </div>
        <div class="team-pill">
            👤 Laura
            <strong>€ {l_net:.2f}</strong>
            <span>{l_res} weerstaan • {l_smk} gerookt</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- TABS ---
tab_log, tab_borrel, tab_sos, tab_push = st.tabs([
    "🍽️ Log & Pot",
    "🍷 Borrel-Modus",
    "🧘 Reset & Motivatie",
    "🔔 20:00 Melding"
])

# ==========================================
# TAB 1: SNEL LOGGEN, STATISTIEKEN & RESET/CORRECTIE
# ==========================================
with tab_log:
    if active_profile == "Samen (Overzicht)":
        u_res, u_smk, u_saved, u_spent, u_net = tot_res, tot_smk, tot_saved, tot_spent, tot_net
        who_label = "Samen"
    else:
        u_res, u_smk, u_saved, u_spent, u_net = calc_user_stats(active_profile)
        who_label = active_profile

    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-card">
            <div class="stat-label">{who_label} Weerstaan</div>
            <div class="stat-val" style="color:#059669;">{u_res} stuks</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Gezonde uren erbij</div>
            <div class="stat-val" style="color:#0284C7;">+{round(u_res * 11 / 60, 1)} uur</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">{who_label} Gerookt</div>
            <div class="stat-val" style="color:#DC2626;">{u_smk} stuks</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(f"#### ⚡ Snel registreren voor **{current_user}**")
        if active_profile == "Samen (Overzicht)":
            current_user = st.segmented_control("Voor wie log je?", ["Maarten", "Laura"], default="Maarten") or "Maarten"

        col_trig, col_cnt = st.columns([3, 1])
        with col_trig:
            trigger_choice = st.selectbox(
                "Wat was het moment?",
                [
                    "🛋️ 20:00 Op de bank (kinderen op bed)",
                    "🍷 Borrel / Wijntje / Biertje",
                    "☕ Na
