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
    page_title="Maarten & Laura — Rookvrij naar jullie Diner",
    page_icon="🥂",
    layout="centered",
    initial_sidebar_state="collapsed"
)

DATA_FILE = "rookvrij_v2_data.json"

# --- CUSTOM UX/UI CSS STYLING ---
st.markdown("""
<style>
    /* Algemene achtergrond en typografie */
    .stApp {
        background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
        color: #F8FAFC;
    }
    
    /* Verberg standaard Streamlit ruis */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Luxe Header Kaart */
    .hero-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid rgba(251, 191, 36, 0.3);
        border-radius: 22px;
        padding: 22px 20px;
        margin-bottom: 18px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
        text-align: center;
    }
    .hero-title {
        font-size: 1.65rem;
        font-weight: 800;
        background: linear-gradient(90deg, #FDE68A, #F59E0B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
    .hero-subtitle {
        color: #94A3B8;
        font-size: 0.92rem;
        margin-bottom: 0;
    }

    /* KPI / Metric Kaarten */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        margin-bottom: 16px;
    }
    .metric-card {
        background: rgba(30, 41, 59, 0.85);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 18px;
        padding: 14px 10px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    .metric-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94A3B8;
        margin-bottom: 4px;
    }
    .metric-value-green {
        font-size: 1.45rem;
        font-weight: 800;
        color: #34D399;
    }
    .metric-value-gold {
        font-size: 1.45rem;
        font-weight: 800;
        color: #FBBF24;
    }
    .metric-value-red {
        font-size: 1.45rem;
        font-weight: 800;
        color: #F87171;
    }
    .metric-sub {
        font-size: 0.72rem;
        color: #CBD5E1;
        margin-top: 2px;
    }

    /* Diner Tracker Kaart */
    .dinner-card {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.14) 0%, rgba(245, 158, 11, 0.12) 100%);
        border: 1px solid rgba(52, 211, 153, 0.35);
        border-radius: 20px;
        padding: 18px;
        margin-bottom: 20px;
    }
    .milestone-badge {
        display: inline-block;
        background: rgba(251, 191, 36, 0.2);
        color: #FDE68A;
        border: 1px solid rgba(251, 191, 36, 0.4);
        border-radius: 999px;
        padding: 4px 12px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 8px;
    }

    /* Motivatie Flashcard */
    .quote-card {
        background: linear-gradient(135deg, #1E293B 0%, #334155 100%);
        border-left: 5px solid #F59E0B;
        border-radius: 18px;
        padding: 22px;
        margin: 14px 0;
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        font-size: 1.08rem;
        line-height: 1.55;
        color: #F8FAFC;
        font-style: italic;
    }

    /* Ademhalings-animatie (vervangt kapotte video) */
    @keyframes breathe {
        0%, 100% { transform: scale(0.65); background: rgba(56, 189, 248, 0.25); border-color: #38BDF8; }
        21% { transform: scale(1.15); background: rgba(52, 211, 153, 0.35); border-color: #34D399; }
        58% { transform: scale(1.15); background: rgba(251, 191, 36, 0.35); border-color: #FBBF24; }
    }
    .breath-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 35px 15px;
        background: rgba(15, 23, 42, 0.6);
        border-radius: 22px;
        border: 1px solid rgba(148, 163, 184, 0.15);
        margin: 15px 0;
    }
    .breath-circle {
        width: 140px;
        height: 140px;
        border-radius: 50%;
        border: 4px solid #34D399;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.95rem;
        color: #F8FAFC;
        text-align: center;
        animation: breathe 19s infinite ease-in-out;
        box-shadow: 0 0 30px rgba(52, 211, 153, 0.25);
    }

    /* Knoppen mooi afronden */
    div.stButton > button {
        border-radius: 14px !important;
        font-weight: 700 !important;
        padding: 0.65rem 1rem !important;
        transition: all 0.2s ease;
    }
</style>
""", unsafe_allow_html=True)

# --- PERSOONLIJKE MOTIVATIEKAARTEN PER CATEGORIE ---
DEFAULT_QUOTES = {
    "🛋️ 20:00 Bank-moment": [
        "De kinderen liggen op bed: je taak zit erop. Je brein zoekt nu een beloning, geen rook. Pak een koud glas fris of thee en plof met een trots gevoel op de bank.",
        "Om 20:00 uur naar buiten lopen in de kou doorbreekt juist je rust. Blijf lekker warm zitten; over 5 minuten ben je blij dat je niet bent opgestaan.",
        "Als je straks voor het slapengaan nog even bij de kinderen kijkt, ruik je fris en warm in plaats van naar koude asbak.",
        "Dat stemmetje om 20:00 uur is alleen maar een oude Pavlov-reactie. Geef je brein een nieuw signaal: kinderen op bed = voeten omhoog en € 0,65 in de diner-pot!",
        "Eén avond niet roken op de bank bespaart jullie direct het eerste glas wijn of speciaalbier tijdens jullie volgende etentje."
    ],
    "🍺 Borrel & Gezelligheid": [
        "Een glas wijn of bier smaakt eigenlijk veel rijker en frisser als je smaakpapillen niet verdoofd worden door rook.",
        "Een sigaret bij een borrel geeft géén extra ontspanning: het vult alleen tijdelijk het onrustgevoel op dat de vorige sigaret heeft achtergelaten.",
        "Gezelligheid zit in het gesprek en het proosten met elkaar, niet in het inhaleren van verbrande tabak.",
        "Kijk eens naar rokers tijdens een borrel: ze moeten telkens het gesprek verlaten. Jij kunt gewoon blijven zitten en genieten.",
        "Geen sigaretten bij je drankje vanavond betekent morgenochtend 50% minder brak wakker worden. Rook versterkt het katereffect enorm!",
        "Spreek met jezelf af: ik neem eerst een heel glas ijskoud bruiswater. Heb ik over 10 minuten nóg steeds trek, dan zie ik dan wel weer. (Spoiler: de trek is dan weg)."
    ],
    "🍽️ Samen Uit Eten & Doel": [
        "Elke 10 sigaretten die jullie samen laten liggen is € 6,50: dat is alweer een heerlijke borrelplank of een dessert tijdens jullie avond uit.",
        "Hoe tof is het om straks in een goed restaurant te bestellen en te weten: dit hele diner inclusief wijn is betaald van sigaretten die we níét hebben gerookt?",
        "Samen stoppen maakt jullie twee keer zo sterk. Als de één even twijfelt, houdt de ander de rug recht voor jullie diner-pot!",
        "Na een paar rookvrije weken proef je subtiele smaken in goed eten en mooie wijn die je als roker simpelweg mist."
    ],
    "☀️ Morgenochtend & Energie": [
        "Spoel de film even door naar morgenochtend 07:30 uur: niemand is ooit wakker geworden met de gedachte 'had ik gisteravond maar wél gerookt'.",
        "Binnen 8 uur zonder sigaret is het koolmonoxidegehalte in je bloed al gehalveerd en stijgt je zuurstofpeil naar 100%. Je slaapt vannacht direct dieper.",
        "De fysieke drang naar nicotine duurt biologisch gezien nooit langer dan 3 tot 8 minuten. Adem drie keer diep in en laat de golf voorbijrollen.",
        "Je bent geen roker die zichzelf iets zieligs ontzegt; je bent iemand die slim kiest voor gezondheid, vrijheid en lekker uit eten gaan."
    ]
}

# --- DATA LADEN & OPSLAAN ---
def load_data():
    default_data = {
        "settings": {
            "cig_price": 0.65,
            "goal_name": "Samen uitgebreid uit eten 🍷🍽️",
            "goal_amount": 150.0,
            "ntfy_topic": "Rookvrij-alerts"
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
                # Merge veilig met defaults
                default_data["settings"].update(saved.get("settings", {}))
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

def send_push_notification(topic, title, message):
    if not topic:
        return False, "Vul eerst een ntfy-kanaalnaam in bij de instellingen."
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
            return response.status == 200, f"Melding verzonden naar '{topic}'!"
    except Exception as e:
        return False, f"Kon melding niet versturen: {e}"

def get_user_stats(logs_list, user_filter=None):
    if not logs_list:
        return 0, 0, 0.0, 0.0, 0.0
    df = pd.DataFrame(logs_list)
    if "user" not in df.columns:
        df["user"] = "Maarten"
    if user_filter and user_filter != "Samen 🥂":
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
        return "☕ Eerste koppen koffie & gebak op het terras", 15
    elif amount < 35:
        return "🥂 Aperitief & Luxe Borrelplank bereikt!", 35
    elif amount < 75:
        return "🍷 Voorgerechten & Goede fles wijn bereikt!", 75
    elif amount < 120:
        return "🍽️ Volledig 3-gangen diner voor twee bereikt!", 120
    elif amount < 175:
        return "🦞 Luxe 4-gangen diner met wijnarrangement!", 175
    else:
        return "🌟 Sterren-avond uit! Tijd om te reserveren!", amount + 50

# --- SIDEBAR: INSTELLINGEN ---
with st.sidebar:
    st.header("⚙️ Instellingen")
    new_cig_price = st.number_input(
        "Prijs per losse sigaret (€)",
        min_value=0.10,
        max_value=2.50,
        value=float(cig_price),
        step=0.05,
        format="%.2f"
    )
    new_goal_name = st.text_input("Jullie Diner-doel", value=data["settings"]["goal_name"])
    new_goal_amount = st.number_input("Doelbedrag voor etentje (€)", value=float(data["settings"]["goal_amount"]), step=10.0)
    new_ntfy_topic = st.text_input("ntfy.sh onderwerp", value=data["settings"]["ntfy_topic"])
    
    if st.button("💾 Opslaan", use_container_width=True, type="primary"):
        data["settings"]["cig_price"] = round(new_cig_price, 2)
        data["settings"]["goal_name"] = new_goal_name
        data["settings"]["goal_amount"] = new_goal_amount
        data["settings"]["ntfy_topic"] = new_ntfy_topic.strip()
        save_data(data)
        st.success("Instellingen bijgewerkt!")
        time.sleep(0.4)
        st.rerun()

# --- HEADER & PROFIEL KEUZE ---
st.markdown(f"""
<div class="hero-card">
    <div class="hero-title">🥂 Maarten & Laura Rookvrij</div>
    <p class="hero-subtitle">Elke sigaret die jullie laten liggen is <b>€ {cig_price:.2f}</b> voor jullie volgende etentje</p>
</div>
""", unsafe_allow_html=True)

active_profile = st.radio(
    "Wie gebruikt de app nu?",
    ["Maarten", "Laura", "Samen 🥂"],
    horizontal=True,
    label_visibility="collapsed"
)

# Statistieken ophalen
resisted_cigs, smoked_cigs, saved_gross, spent_gross, net_saved = get_user_stats(data["logs"], active_profile)
_, _, _, _, total_team_saved = get_user_stats(data["logs"], "Samen 🥂")
_, _, _, _, maarten_saved = get_user_stats(data["logs"], "Maarten")
_, _, _, _, laura_saved = get_user_stats(data["logs"], "Laura")

# --- TABS ---
tab_dash, tab_borrel, tab_sos, tab_push = st.tabs([
    "🍽️ Diner-Pot",
    "🍺 Borrel-Modus",
    "🧘 SOS & Motivatie",
    "🔔 20:00 Melding"
])

# ==========================================
# TAB 1: DINER-POT & REGISTREREN
# ==========================================
with tab_dash:
    # KPI Kaarten voor geselecteerd profiel
    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-label">Netto ({active_profile})</div>
            <div class="metric-value-green">€ {net_saved:.2f}</div>
            <div class="metric-sub">{resisted_cigs} weerstaan 💪</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Samen Gespaard</div>
            <div class="metric-value-gold">€ {total_team_saved:.2f}</div>
            <div class="metric-sub">M: €{maarten_saved:.0f} • L: €{laura_saved:.0f}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Gerookt ({active_profile})</div>
            <div class="metric-value-red">€ {spent_gross:.2f}</div>
            <div class="metric-sub">{smoked_cigs} stuks 🚬</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Gezamenlijke Etentje Progress Card
    milestone_text, _ = get_dinner_milestone(total_team_saved)
    goal_target = max(1.0, float(data["settings"]["goal_amount"]))
    progress_pct = min(1.0, total_team_saved / goal_target)
    cigs_left_for_goal = max(0, int(round((goal_target - total_team_saved) / cig_price)))

    st.markdown(f"""
    <div class="dinner-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-weight:700; font-size:1.05rem;">{data['settings']['goal_name']}</span>
            <span style="font-weight:800; color:#34D399;">€ {total_team_saved:.2f} / € {goal_target:.0f}</span>
        </div>
        <div class="milestone-badge">{milestone_text}</div>
        <p style="font-size:0.8rem; color:#CBD5E1; margin-top:8px; margin-bottom:0;">
            Nog <b>{cigs_left_for_goal}</b> niet-gerookte sigaretten tot jullie volledige diner-doel!
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.progress(progress_pct)

    # Snel loggen
    acting_user = "Maarten" if active_profile == "Samen 🥂" else active_profile
    st.markdown(f"#### ⚡ Snel registreren voor **{acting_user}**")
    if active_profile == "Samen 🥂":
        acting_user = st.segmented_control("Voor wie log je deze actie?", ["Maarten", "Laura"], default="Maarten") or "Maarten"

    col_trig, col_cnt = st.columns([3, 1])
    with col_trig:
        trigger_choice = st.selectbox(
            "Moment / Trigger",
            [
                "🛋️ 20:00 Op de bank (kinderen op bed)",
                "🍺 Borrel / Wijntje / Biertje",
                "☕ Na het eten / Koffie",
                "😤 Stress / Drukke dag",
                "☀️ Terras / Gezelligheid",
                "🌟 Rookvrije avond / Dagbonus"
            ]
        )
    with col_cnt:
        cigs_count = st.number_input("Aantal", min_value=1, max_value=20, value=1)

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button(f"🔥 Weerstaan! (+ € {cigs_count * cig_price:.2f})", use_container_width=True, type="primary"):
            add_log(acting_user, "resisted", cigs_count, trigger_choice)
            st.toast(f"Top {acting_user}! + € {cigs_count * cig_price:.2f} in de diner-pot! 🥂", icon="💪")
            time.sleep(0.4)
            st.rerun()

    with btn_col2:
        if st.button(f"🚬 Gerookt (- € {cigs_count * cig_price:.2f})", use_container_width=True):
            add_log(acting_user, "smoked", cigs_count, trigger_choice)
            st.toast("Eerlijk gelogd. Zet direct de knop weer om!", icon="🔄")
            time.sleep(0.5)
            st.rerun()

    # Overzicht & Correctie / Reset Knoppen
    st.write("")
    with st.expander("🧹 Correctie, Sigaretten Wissen & Test-Reset"):
        st.caption("Heb je getest of per ongeluk verkeerd geklikt? Wis hier eenvoudig één of meerdere registraties.")
        
        if data["logs"]:
            last_entry = data["logs"][-1]
            tipo_nl = "Weerstaan 💪" if last_entry["type"] == "resisted" else "Gerookt 🚬"
            st.info(f"**Laatste invoer:** {last_entry.get('user', 'Maarten')} — {last_entry['count']}x {tipo_nl} (€ {last_entry['amount_eur']:.2f}) op {last_entry['timestamp']}")
            
            c_undo1, c_undo2 = st.columns(2)
            with c_undo1:
                if st.button("↩️ Wis laatste invoer", use_container_width=True):
                    data["logs"].pop()
                    save_data(data)
                    st.success("Laatste invoer gewist!")
                    time.sleep(0.4)
                    st.rerun()
            with c_undo2:
                if st.button("🗑️ Reset ALLES naar € 0,00", use_container_width=True):
                    data["logs"] = []
                    save_data(data)
                    st.success("Alle testdata is gewist! Teller staat weer op 0.")
                    time.sleep(0.4)
                    st.rerun()

            st.divider()
            st.caption("Of kies één specifieke regel uit het logboek om te verwijderen:")
            options = {
                f"{idx}: {row.get('timestamp','')} | {row.get('user','Maarten')} | {row['count']}x {'Weerstaan' if row['type']=='resisted' else 'Gerookt'} (€{row['amount_eur']:.2f})": idx
                for idx, row in enumerate(reversed(data["logs"]))
            }
            selected_to_delete = st.selectbox("Selecteer registratie", list(options.keys()))
            if st.button("❌ Verwijder geselecteerde regel"):
                rev_idx = options[selected_to_delete]
                real_idx = len(data["logs"]) - 1 - rev_idx
                data["logs"].pop(real_idx)
                save_data(data)
                st.success("Regel verwijderd!")
                time.sleep(0.3)
                st.rerun()
        else:
            st.write("Er zijn momenteel nog geen sigaretten geregistreerd.")

# ==========================================
# TAB 2: BORREL-MODUS
# ==========================================
with tab_borrel:
    borrel_user = "Maarten" if active_profile == "Samen 🥂" else active_profile
    st.subheader(f"🍺 Borrel-Modus ({borrel_user})")
    st.caption("Wel genieten van een goed glas wijn of bier, zonder dat je brein automatisch om nicotine vraagt.")

    today_str = date.today().strftime("%Y-%m-%d")
    user_commit = data["borrel_commit"].get(borrel_user, {"active": False, "date": "", "max_drinks": 3, "note": ""})
    is_committed = user_commit.get("active", False) and user_commit.get("date") == today_str

    if not is_committed:
        with st.container(border=True):
            st.markdown(f"##### 🤝 Borrel-afspraak voor {borrel_user} vanavond")
            max_drinks = st.slider("Hoeveel glazen drink je vanavond met smaak?", 1, 8, 3)
            replacement = st.selectbox(
                "Wat is je directe actie als je na glas 2 of 3 trek krijgt?",
                [
                    "Ik drink eerst een groot glas ijskoud bruiswater met citroen",
                    "Ik neem direct een sterke munt of kauwgom",
                    "Ik blijf gezellig aan tafel zitten als anderen naar buiten lopen",
                    "Ik start de 5-minuten afkoel-timer en eet een borrelhapje"
                ]
            )
            if st.button(f"🥂 Activeer Borrel-Modus voor {borrel_user}", type="primary", use_container_width=True):
                data["borrel_commit"][borrel_user] = {
                    "active": True,
                    "date": today_str,
                    "max_drinks": max_drinks,
                    "note": replacement
                }
                save_data(data)
                st.rerun()
    else:
        st.success(f"**Borrel-Contract Actief voor {borrel_user}!**\n\n- Genieten van max **{user_commit['max_drinks']} glazen**, **0 sigaretten**.\n- Jouw afgesproken reflex bij trek: *{user_commit['note']}*")
        if st.button(f"🎉 Borrel rookvrij afgerond! (+ € {3 * cig_price:.2f} voor jullie etentje)", type="primary", use_container_width=True):
            add_log(borrel_user, "resisted", 3, "🍺 Borrel / Wijntje / Biertje", "Borrel-contract gehaald!")
            data["borrel_commit"][borrel_user]["active"] = False
            save_data(data)
            st.balloons()
            time.sleep(0.8)
            st.rerun()

    st.divider()
    st.markdown("##### ⏱️ De Afkoel-Klok (Bij acute trek tijdens een drankje)")
    st.caption("Krijg je tijdens het borrelen ineens trek? Verbied jezelf niets, maar spreek af: ik mag pas beslissen als deze timer op 00:00 staat.")
    
    wait_minutes = st.radio("Kies je pauzetijd:", [3, 5, 10], index=1, horizontal=True, format_func=lambda x: f"{x} minuten")
    if st.button(f"🚨 Start {wait_minutes}-Minuten Trek-Timer", use_container_width=True):
        timer_box = st.empty()
        p_bar = st.progress(0.0)
        total_secs = wait_minutes * 60
        for s in range(total_secs, 0, -1):
            m, sec = divmod(s, 60)
            p_bar.progress((total_secs - s) / total_secs)
            timer_box.markdown(f"""
            <div class="dinner-card" style="text-align:center;">
                <h2 style="margin:0; color:#FBBF24;">⏳ {m:02d}:{sec:02d}</h2>
                <p style="margin-top:8px; margin-bottom:0;">
                    Drink nu eerst een flink glas water en haal diep adem.<br>
                    Deze golf van trek zakt over een paar minuten vanzelf weg!
                </p>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(1)
        p_bar.progress(1.0)
        timer_box.success(f"🎉 De piek is voorbij! Log je overwinning (+ € {cig_price:.2f}) bij de Diner-Pot!")
        st.balloons()

# ==========================================
# TAB 3: SOS, MOTIVATIEKAARTEN & ADEMHALING
# ==========================================
with tab_sos:
    st.subheader("💡 Persoonlijke Motivatiekaarten")
    
    cat_choice = st.selectbox(
        "Kies waar je nu behoefte aan hebt:",
        ["🔄 Alle situaties (Willekeurig)"] + list(DEFAULT_QUOTES.keys()) + ["❤️ Eigen toegevoegde kaarten"]
    )

    if cat_choice == "🔄 Alle situaties (Willekeurig)":
        pool = [q for qs in DEFAULT_QUOTES.values() for q in qs] + data["custom_quotes"]
    elif cat_choice == "❤️ Eigen toegevoegde kaarten":
        pool = data["custom_quotes"] if data["custom_quotes"] else ["Je hebt nog geen eigen kaarten toegevoegd. Voeg er hieronder eentje toe voor jezelf of voor elkaar!"]
    else:
        pool = DEFAULT_QUOTES[cat_choice]

    if "active_quote" not in st.session_state or st.session_state.get("last_cat") != cat_choice:
        st.session_state.active_quote = random.choice(pool)
        st.session_state.last_cat = cat_choice

    st.markdown(f"""
    <div class="quote-card">
        “{st.session_state.active_quote}”
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔀 Nieuwe kaart trekken", use_container_width=True, type="primary"):
        st.session_state.active_quote = random.choice(pool)
        st.rerun()

    with st.expander("➕ Schrijf een eigen motivatiekaart (voor jezelf of voor elkaar)"):
        custom_q = st.text_input("Bijv. 'Denk aan ons etentje bij dat leuke restaurant!'")
        if st.button("Kaart opslaan"):
            if custom_q.strip():
                data["custom_quotes"].append(custom_q.strip())
                save_data(data)
                st.session_state.active_quote = custom_q.strip()
                st.success("Kaart toegevoegd!")
                st.rerun()

    st.divider()
    st.subheader("🌬️ Visuele Ademhalings-Coach (Werkt altijd)")
    st.caption("Kijk 60 seconden naar de cirkel hieronder. Adem in terwijl de cirkel groeit, houd vast als hij goud kleurt, en blaas langzaam uit als hij kleiner wordt.")

    # Vloeiende CSS animatie die nooit vastloopt op mobiel
    st.markdown("""
    <div class="breath-container">
        <div class="breath-circle">
            Adem rustig<br>mee met<br>de cirkel
        </div>
        <p style="color:#94A3B8; font-size:0.82rem; margin-top:18px; margin-bottom:0; text-align:center;">
            🟢 Groter = 4s Inademen &nbsp;•&nbsp; 🟡 Goud = 7s Vasthouden &nbsp;•&nbsp; 🔵 Kleiner = 8s Uitblazen
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# TAB 4: 20:00 BANK-TRIGGER & NTFY PUSH
# ==========================================
with tab_push:
    st.subheader("🔔 De 20:00 'Op de bank'-Melding")
    st.markdown(f"""
    Jullie ntfy-kanaal staat ingesteld op: **`{data['settings']['ntfy_topic']}`**.
    
    * Wanneer de kinderen rond **20:00 uur** op bed liggen, geeft je brein een seintje: *tijd voor ontspanning*.
    * Doorbreek de automatische piloot door om 20:00 uur eerst een lekker drankje of thee in de keuken te pakken en meteen **+ € {cig_price:.2f}** in jullie Diner-Pot te tikken.
    """)

    if st.button(f"📲 Stuur nu een testmelding naar '{data['settings']['ntfy_topic']}'", type="primary", use_container_width=True):
        ok, msg = send_push_notification(
            data["settings"]["ntfy_topic"],
            "🥂 20:00 Bank-Check voor Maarten & Laura!",
            f"Kinderen op bed? Plof lekker op de bank ZONDER sigaret! Jullie diner-pot staat al op EUR {total_team_saved:.2f}."
        )
        if ok:
            st.success(msg + " Kijk nu in je ntfy-app!")
        else:
            st.error(msg)
