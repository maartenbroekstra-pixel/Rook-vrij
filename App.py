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
    page_title="Maarten & Laura — Diner Pot",
    page_icon="🥂",
    layout="centered",
    initial_sidebar_state="collapsed"
)

DATA_FILE = "rookvrij_v2_data.json"

# --- HIGH-CONTRAST MOBILE UX CSS ---
st.markdown("""
<style>
    /* Forceer een helder, warm en super-leesbaar thema op elk toestel */
    .stApp {
        background-color: #F4F6F9 !important;
        color: #0F172A !important;
    }

    /* Zorg dat ALLE standaard Streamlit teksten, labels en knoppen donker en scherp leesbaar zijn */
    .stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp div {
        color: #0F172A;
    }

    /* Verberg onnodige balken */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 520px !important;
    }

    /* Bovenste Bistro Header Kaart */
    .header-box {
        background: #FFFFFF;
        border: 2px solid #E2E8F0;
        border-radius: 20px;
        padding: 18px 16px;
        margin-bottom: 14px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
    }
    .header-title {
        font-size: 1.45rem;
        font-weight: 800;
        color: #0F172A !important;
        margin: 0 0 4px 0;
    }
    .header-sub {
        font-size: 0.9rem;
        color: #475569 !important;
        margin: 0;
    }

    /* Drie Score-Kaarten naast elkaar */
    .score-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        margin: 12px 0;
    }
    .score-card {
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 16px;
        padding: 12px 6px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
    }
    .score-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        color: #475569 !important;
        margin-bottom: 4px;
    }
    .score-val-green {
        font-size: 1.35rem;
        font-weight: 800;
        color: #059669 !important;
    }
    .score-val-amber {
        font-size: 1.35rem;
        font-weight: 800;
        color: #D97706 !important;
    }
    .score-val-red {
        font-size: 1.35rem;
        font-weight: 800;
        color: #DC2626 !important;
    }
    .score-sub {
        font-size: 0.72rem;
        color: #64748B !important;
        margin-top: 2px;
    }

    /* Diner Doel Kaart */
    .dinner-box {
        background: #ECFDF5;
        border: 2px solid #A7F3D0;
        border-radius: 18px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .milestone-pill {
        display: inline-block;
        background: #FEF3C7;
        color: #92400E !important;
        border: 1px solid #FDE68A;
        border-radius: 999px;
        padding: 4px 12px;
        font-size: 0.82rem;
        font-weight: 700;
        margin-top: 8px;
    }

    /* Motivatie Flashcard */
    .quote-box {
        background: #FFFBEB;
        border: 2px solid #FDE68A;
        border-left: 6px solid #F59E0B;
        border-radius: 16px;
        padding: 20px;
        margin: 14px 0;
        font-size: 1.05rem;
        font-weight: 600;
        line-height: 1.5;
        color: #1E293B !important;
    }

    /* Ademhalings-cirkel */
    @keyframes pulse-circle {
        0%, 100% { transform: scale(0.7); background-color: #E0F2FE; border-color: #0284C7; }
        25% { transform: scale(1.12); background-color: #D1FAE5; border-color: #059669; }
        60% { transform: scale(1.12); background-color: #FEF3C7; border-color: #D97706; }
    }
    .breath-wrap {
        background: #FFFFFF;
        border: 2px solid #E2E8F0;
        border-radius: 20px;
        padding: 28px 14px;
        text-align: center;
        margin-top: 12px;
    }
    .breath-ball {
        width: 135px;
        height: 135px;
        margin: 10px auto;
        border-radius: 50%;
        border: 4px solid #059669;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 0.95rem;
        color: #0F172A !important;
        animation: pulse-circle 19s infinite ease-in-out;
    }

    /* Tabbladen goed zichtbaar en passend op 1 mobiel scherm */
    button[data-baseweb="tab"] {
        font-size: 0.88rem !important;
        font-weight: 700 !important;
        padding: 8px 10px !important;
        color: #334155 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #059669 !important;
    }

    /* Duidelijke knoppen */
    div.stButton > button[kind="primary"] {
        background-color: #059669 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 14px !important;
        font-weight: 800 !important;
        padding: 0.75rem 1rem !important;
    }
    div.stButton > button[kind="primary"] p, div.stButton > button[kind="primary"] span {
        color: #FFFFFF !important;
    }
    div.stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 2px solid #CBD5E1 !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        padding: 0.75rem 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- PERSOONLIJKE MOTIVATIEKAARTEN ---
DEFAULT_QUOTES = {
    "🛋️ 20:00 Op de bank": [
        "De kinderen liggen op bed: jullie avond begint. Je brein zoekt nu ontspanning, géén rook. Pak wat lekkers te drinken en zet € 0,65 in jullie diner-pot!",
        "Om 20:00 uur in de kou gaan staan haalt je juist uit je rust. Blijf lekker op de bank zitten; over 5 minuten ben je blij dat je niet bent gegaan.",
        "Als je straks nog even bij de slapende kinderen kijkt, ruik je fris in plaats van naar koude rook.",
        "Dat stemmetje om 20:00 uur is alleen een oude gewoonte. Elke keer dat je blijft zitten, wordt die automatische prikkel zwakker.",
        "Twee avonden niet roken op de bank is alweer een speciaalbier of een goed glas wijn tijdens jullie etentje!"
    ],
    "🍺 Borrel & Gezelligheid": [
        "Een goed glas wijn of bier smaakt veel rijker als je smaakpapillen niet verdoofd worden door tabaksrook.",
        "Een sigaret bij een borrel geeft géén extra ontspanning: het heft alleen tijdelijk de onrust op die de vorige sigaret heeft achtergelaten.",
        "Niet roken tijdens het drinken scheelt je morgenochtend de helft van je brakheid. Koolmonoxide uit rook versterkt een kater enorm.",
        "Spreek met jezelf af: ik drink eerst een groot glas ijskoud water en wacht 5 minuten. Daarna is de ergste drang altijd gezakt.",
        "Gezelligheid zit in het proosten en het gesprek aan tafel, niet in het buiten staan met een peuk."
    ],
    "🍽️ Samen Uit Eten": [
        "Elke 10 sigaretten die jullie samen laten liggen is € 6,50: dat is alweer een borrelplank of een dessert tijdens jullie avond uit!",
        "Hoe lekker smaakt jullie diner straks als je weet dat de hele avond — inclusief wijn — betaald is van niet-gerookte sigaretten?",
        "Samen stoppen maakt jullie twee keer zo sterk. Als de één twijfelt, houdt de ander de poot stijf voor de diner-pot!",
        "Zonder rook proef je binnen een week veel meer details in lekker eten en goede wijn."
    ],
    "☀️ Morgenochtend & Frisse Start": [
        "Denk even aan morgenochtend 07:30 uur: niemand wordt ooit wakker met de gedachte 'had ik gisteravond maar wél gerookt'.",
        "Een golf van trek duurt biologisch gezien nooit langer dan 3 tot 8 minuten. Of je nu rookt of niet, de drang zakt zo vanzelf weg.",
        "Na één rookvrije avond is het zuurstofgehalte in je bloed morgenochtend weer 100% en slaap je vannacht dieper.",
        "Je ontzegt jezelf niets; je trakteert jezelf op een fris lichaam en een geweldige avond uit met z'n tweeën."
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
        "type": event_type,
        "count": int(count),
        "trigger": trigger,
        "amount_eur": round(int(count) * cig_price, 2),
        "note": note
    })
    save_data(data)

def send_push_notification(topic, title_ascii, message_utf8):
    if not topic:
        return False, "Vul eerst een ntfy-kanaalnaam in."
    try:
        # LET OP: HTTP headers moeten puur ASCII/latin-1 zijn (geen emoji's in Title header!)
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
            return response.status == 200, f"Melding succesvol verzonden naar '{topic}'!"
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
        return "☕ Op weg naar: Eerste borrelhapjes (€ 15)"
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

# --- BOVENSTE HEADER ---
st.markdown(f"""
<div class="header-box">
    <p class="header-title">🥂 Maarten & Laura Rookvrij</p>
    <p class="header-sub">Elke niet-gerookte sigaret = <b>€ {cig_price:.2f}</b> voor jullie etentje</p>
</div>
""", unsafe_allow_html=True)

# --- DUIDELIJKE WIE-IS-WIE KNOPPEN ---
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

# Statistieken ophalen
resisted_cigs, smoked_cigs, saved_gross, spent_gross, net_saved = get_user_stats(data["logs"], active_profile)
_, _, _, _, total_team_saved = get_user_stats(data["logs"], "Samen")
_, _, _, _, maarten_saved = get_user_stats(data["logs"], "Maarten")
_, _, _, _, laura_saved = get_user_stats(data["logs"], "Laura")

# --- KORTE TABBLADEN ZODAT ZE ALTIJD OP 1 MOBIEL SCHERM PASSEN ---
tab_dash, tab_borrel, tab_sos, tab_push = st.tabs([
    "🍽️ Diner",
    "🍺 Borrel",
    "🧘 SOS",
    "🔔 20:00"
])

# ==========================================
# TAB 1: DINER-POT & 1-KLIK LOGGEN
# ==========================================
with tab_dash:
    st.markdown(f"""
    <div class="score-grid">
        <div class="score-card">
            <div class="score-label">Netto ({active_profile})</div>
            <div class="score-val-green">€ {net_saved:.2f}</div>
            <div class="score-sub">{resisted_cigs} weerstaan 💪</div>
        </div>
        <div class="score-card">
            <div class="score-label">Diner-Pot Samen</div>
            <div class="score-val-amber">€ {total_team_saved:.2f}</div>
            <div class="score-sub">M: €{maarten_saved:.0f} | L: €{laura_saved:.0f}</div>
        </div>
        <div class="score-card">
            <div class="score-label">Gerookt ({active_profile})</div>
            <div class="score-val-red">€ {spent_gross:.2f}</div>
            <div class="score-sub">{smoked_cigs} stuks 🚬</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Diner-Pot Voortgang
    milestone_text = get_dinner_milestone(total_team_saved)
    goal_target = max(1.0, float(data["settings"]["goal_amount"]))
    progress_pct = min(1.0, total_team_saved / goal_target)
    cigs_left = max(0, int(round((goal_target - total_team_saved) / cig_price)))

    st.markdown(f"""
    <div class="dinner-box">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-weight:800; font-size:1rem;">{data['settings']['goal_name']}</span>
            <span style="font-weight:800; color:#059669;">€ {total_team_saved:.2f} / € {goal_target:.0f}</span>
        </div>
        <div class="milestone-pill">{milestone_text}</div>
        <p style="font-size:0.82rem; color:#334155; margin-top:8px; margin-bottom:0;">
            Nog <b>{cigs_left}</b> niet-gerookte sigaretten tot jullie volledige diner-doel!
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.progress(progress_pct)

    # Snel registreren
    acting_user = "Maarten" if active_profile == "Samen" else active_profile
    st.markdown(f"##### ⚡ Snel bijwerken voor **{acting_user}**")
    
    if active_profile == "Samen":
        who_col1, who_col2 = st.columns(2)
        with who_col1:
            acting_user = st.radio("Op wiens naam log je?", ["Maarten", "Laura"], horizontal=True)

    col_t, col_n = st.columns([3, 1])
    with col_t:
        trigger_choice = st.selectbox(
            "Moment",
            [
                "🛋️ 20:00 Op de bank",
                "🍺 Borrel / Drankje",
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
            st.toast(f"Lekker {acting_user}! + € {cigs_count * cig_price:.2f} voor jullie etentje!", icon="🥂")
            time.sleep(0.4)
            st.rerun()
    with b2:
        if st.button(f"🚬 Gerookt (- € {cigs_count * cig_price:.2f})", type="secondary", use_container_width=True):
            add_log(acting_user, "smoked", cigs_count, trigger_choice)
            st.toast("Eerlijk gelogd. Pak de draad direct weer op!", icon="🔄")
            time.sleep(0.4)
            st.rerun()

    # Wissen & Resetten (voor testen of foutjes)
    st.write("")
    with st.expander("🧹 Sigaretten Wissen / Test-Reset"):
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
# TAB 2: BORREL-MODUS
# ==========================================
with tab_borrel:
    borrel_user = "Maarten" if active_profile == "Samen" else active_profile
    st.subheader(f"🍺 Borrel-Modus ({borrel_user})")
    st.write("Wel genieten van een glas wijn of bier, zonder te roken.")

    today_str = date.today().strftime("%Y-%m-%d")
    u_commit = data["borrel_commit"].get(borrel_user, {"active": False, "date": "", "max_drinks": 3, "note": ""})
    is_active = u_commit.get("active", False) and u_commit.get("date") == today_str

    if not is_active:
        max_dr = st.slider("Hoeveel glazen drink je vanavond maximaal?", 1, 8, 3)
        plan = st.selectbox(
            "Wat doe je zodra je trek krijgt in een sigaret?",
            [
                "Ik drink eerst een groot glas ijskoud water",
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
            add_log(borrel_user, "resisted", 3, "🍺 Borrel / Drankje", "Borrel-afspraak gehaald")
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
            <div class="dinner-box" style="text-align:center;">
                <h2 style="margin:0;">⏳ {m:02d}:{sec:02d}</h2>
                <p style="margin-top:6px; margin-bottom:0;">Drink nu eerst een glas koud water. De piek zakt zo vanzelf weg!</p>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(1)
        p_bar.progress(1.0)
        t_box.success(f"🎉 De trek is voorbij! Log je + € {cig_price:.2f} bij het eerste tabblad!")

# ==========================================
# TAB 3: SOS & MOTIVATIEKAARTEN
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
    <div class="quote-box">
        “{st.session_state.curr_q}”
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
    st.subheader("🌬️ Ademhalings-Coach (1 minuut)")
    st.markdown("""
    <div class="breath-wrap">
        <div class="breath-ball">Adem rustig<br>mee</div>
        <p style="font-size:0.85rem; margin-top:12px; margin-bottom:0;">
            <b>Groter</b> = 4s Inademen &nbsp;•&nbsp; <b>Geel</b> = 7s Vasthouden &nbsp;•&nbsp; <b>Kleiner</b> = 8s Uitblazen
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# TAB 4: 20:00 BANK-MELDING
# ==========================================
with tab_push:
    st.subheader("🔔 De 20:00 'Op de bank'-Melding")
    st.write(f"Jullie ntfy-kanaal: **`{data['settings']['ntfy_topic']}`**")
    st.markdown(f"""
    * Rond **20:00 uur** liggen de kinderen op bed en schakelt je brein over naar ontspanning.
    * Doorbreek de gewoonte: loop om 20:00 uur eerst naar de keuken voor een lekker drankje en zet direct **+ € {cig_price:.2f}** in jullie Diner-Pot.
    """)

    if st.button(f"📲 Stuur testmelding naar '{data['settings']['ntfy_topic']}'", type="primary", use_container_width=True):
        # ASCII-veilige titel zodat latin-1 nooit crasht, emoji's in het bericht zelf!
        ok, msg = send_push_notification(
            data["settings"]["ntfy_topic"],
            "20:00 Avond Check-in voor Maarten en Laura",
            f"🥂 Kinderen op bed? Plof lekker op de bank ZONDER sigaret! Jullie diner-pot staat al op € {total_team_saved:.2f}."
        )
        if ok:
            st.success(msg + " Kijk nu in je ntfy-app!")
        else:
            st.error(msg)
