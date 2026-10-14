import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import time
import random
import requests
from datetime import datetime, date

# --- PAGINA CONFIGURATIE ---
st.set_page_config(
    page_title="Rookvrij & Scherp Dashboard",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

DATA_FILE = "rookvrij_data.json"

# --- STANDAARDINSTELLINGEN & DATA OPSLAG ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "settings": {
            "pack_price": 12.80,          # Prijs pakje Marlboro Gold/Light (20 stuks)
            "cigs_per_pack": 20,
            "baseline_per_week": 20,      # Wat je normaal zou roken per week (of in een weekend)
            "goal_name": "Nieuwe sportgear / Avond uit",
            "goal_amount": 150.0,
            "ntfy_topic": ""              # Unieke kanaalnaam voor ntfy.sh pushmeldingen
        },
        "logs": [],                       # Lijst met events: type ('resisted', 'smoked', 'clean_day')
        "borrel_commit": {
            "active": False,
            "date": "",
            "max_drinks": 3,
            "note": ""
        },
        "custom_quotes": [
            "Een sigaret bij een borrel geeft geen ontspanning; het vult alleen tijdelijk de onrust op die de vorige sigaret heeft veroorzaakt.",
            "Denk aan morgenochtend 07:30 uur: hoe lekker is het om fris, zonder spijt en met 100% longcapaciteit wakker te worden?",
            "Als je straks nog even bij de slapende kinderen kijkt, ruik je fris in plaats van naar koude rook.",
            "Geen koolmonoxide in je bloed vanavond betekent een lagere rusthartslag, beter herstel en meer explosiviteit tijdens het sporten.",
            "De fysieke piek van deze trek duurt maximaal 5 tot 8 minuten. Of je nu rookt of niet, de drang zakt zo vanzelf weer weg."
        ]
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

data = load_data()
cig_price = round(data["settings"]["pack_price"] / data["settings"]["cigs_per_pack"], 2)

# --- HULPFUNCTIES ---
def add_log(event_type, count, trigger, note=""):
    data["logs"].append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date": date.today().strftime("%Y-%m-%d"),
        "type": event_type,  # 'resisted' (weerstand geboden) of 'smoked' (gerookt)
        "count": count,
        "trigger": trigger,
        "amount_eur": round(count * cig_price, 2),
        "note": note
    })
    save_data(data)

def send_push_notification(topic, title, message):
    if not topic:
        return False, "Vul eerst een ntfy-kanaalnaam in bij de instellingen."
    try:
        response = requests.post(
            f"https://ntfy.sh/{topic}",
            data=message.encode("utf-8"),
            headers={
                "Title": title,
                "Priority": "high",
                "Tags": "shield,no_smoking"
            },
            timeout=5
        )
        return response.status_code == 200, "Melding verzonden!"
    except Exception as e:
        return False, str(e)

# --- SIDEBAR: INSTELLINGEN ---
with st.sidebar:
    st.header("⚙️ Instellingen")
    st.caption("Pas hier de Marlboro Light/Gold prijzen en je doelen aan.")
    
    pack_price = st.number_input("Prijs per pakje (€)", value=float(data["settings"]["pack_price"]), step=0.10)
    cigs_per_pack = st.number_input("Sigaretten in pakje", value=int(data["settings"]["cigs_per_pack"]), step=1)
    goal_name = st.text_input("Spaardoel", value=data["settings"]["goal_name"])
    goal_amount = st.number_input("Doelbedrag (€)", value=float(data["settings"]["goal_amount"]), step=10.0)
    ntfy_topic = st.text_input("ntfy.sh kanaalnaam (voor push)", value=data["settings"]["ntfy_topic"], help="Kies een unieke, geheime naam, bijv. rookvrij_dashboard_987")
    
    if st.button("💾 Instellingen Opslaan", use_container_width=True):
        data["settings"]["pack_price"] = pack_price
        data["settings"]["cigs_per_pack"] = cigs_per_pack
        data["settings"]["goal_name"] = goal_name
        data["settings"]["goal_amount"] = goal_amount
        data["settings"]["ntfy_topic"] = ntfy_topic
        save_data(data)
        st.success("Opgeslagen!")
        st.rerun()

# --- BEREKENINGEN VOOR DASHBOARD ---
df_logs = pd.DataFrame(data["logs"])
if not df_logs.empty:
    resisted_cigs = df_logs[df_logs["type"] == "resisted"]["count"].sum()
    smoked_cigs = df_logs[df_logs["type"] == "smoked"]["count"].sum()
    saved_gross = resisted_cigs * cig_price
    spent_gross = smoked_cigs * cig_price
    net_saved = max(0.0, saved_gross - spent_gross)
else:
    resisted_cigs = 0
    smoked_cigs = 0
    saved_gross = 0.0
    spent_gross = 0.0
    net_saved = 0.0

# Toekomstwaarde over 10 jaar (bij 7% beleggingsrendement)
future_value_10y = net_saved * ((1 + 0.07) ** 10)

# --- HOOFDSCHERM & TABS ---
st.title("🛡️ Rookvrij & Scherp")
st.caption(f"Prijs per Marlboro Gold/Light sigaret: **€ {cig_price:.2f}** (€ {data['settings']['pack_price']:.2f} per pakje)")

tab_dash, tab_borrel, tab_sos, tab_push = st.tabs([
    "💰 Besparing & Log",
    "🍺 Borrel-Modus",
    "🧘 SOS & Motivatie",
    "🔔 20:00 Trigger"
])

# ==========================================
# TAB 1: BESPARING & SNEL LOGGEN
# ==========================================
with tab_dash:
    col1, col2, col3 = st.columns(3)
    col1.metric("Netto Bespaard", f"€ {net_saved:.2f}", f"{resisted_cigs} weerstaan")
    col2.metric("Waarde over 10 jr (7%)", f"€ {future_value_10y:.2f}", "Compound effect")
    col3.metric("Gerookt (Kosten)", f"€ {spent_gross:.2f}", f"-{smoked_cigs} stuks", delta_color="inverse")

    # Voortgangsbalk spaardoel
    progress_pct = min(1.0, net_saved / max(1.0, data["settings"]["goal_amount"]))
    st.write(f"**Spaardoel: {data['settings']['goal_name']}** (€ {net_saved:.2f} / € {data['settings']['goal_amount']:.2f})")
    st.progress(progress_pct)

    st.divider()
    st.subheader("⚡ Direct registreren")
    
    trigger_choice = st.selectbox(
        "Wat was het moment / de trigger?",
        ["🛋️ 20:00 Op de bank (kinderen op bed)", "🍺 Borrel / Alcohol", "☕ Na het eten / Koffie", "😤 Stress / Werkdruk", "☀️ Gezelligheid / Terras", "📅 Gewoon een rookvrije dag (Bonus)"]
    )
    
    col_a, col_b = st.columns(2)
    with col_a:
        cigs_count = st.number_input("Aantal sigaretten", min_value=1, max_value=20, value=1)
        if st.button(f"🔥 Trek weerstaan! (+ € {cigs_count * cig_price:.2f})", use_container_width=True, type="primary"):
            add_log("resisted", cigs_count, trigger_choice)
            st.toast(f"Lekker bezig! € {cigs_count * cig_price:.2f} bespaard!", icon="💪")
            time.sleep(0.5)
            st.rerun()
            
    with col_b:
        st.write("")
        st.write("")
        if st.button(f"🚬 Toch gerookt (- € {cigs_count * cig_price:.2f})", use_container_width=True):
            add_log("smoked", cigs_count, trigger_choice)
            st.warning("Eerlijk gelogd. Geen man overboord: zet de streep direct weer in het zand en pak de draad nu meteen weer op.")
            time.sleep(1.2)
            st.rerun()

    # Grafieken als er data is
    if not df_logs.empty:
        st.divider()
        st.subheader("📊 Jouw Trigger-Inzicht")
        
        df_triggers = df_logs.groupby(["trigger", "type"])["count"].sum().reset_index()
        df_triggers["Status"] = df_triggers["type"].map({"resisted": "Weerstaan 💪", "smoked": "Gerookt 🚬"})
        
        fig = px.bar(
            df_triggers,
            x="count",
            y="trigger",
            color="Status",
            orientation="h",
            barmode="group",
            color_discrete_map={"Weerstaan 💪": "#10B981", "Gerookt 🚬": "#EF4444"},
            labels={"count": "Aantal sigaretten", "trigger": "Situatie"}
        )
        fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# TAB 2: BORREL-MODUS (ALCOHOL & ROKEN ONTKOPPELEN)
# ==========================================
with tab_borrel:
    st.subheader("🍺 Borrel-Modus: Wel genieten, niet roken")
    st.markdown("""
    Alcohol verlaagt de remming in je brein én triggert oude gewoontes. 
    Door **vóór je eerste slok** een afspraak met jezelf vast te leggen, halveer je de kans dat je na het derde glas overstag gaat.
    """)

    today_str = date.today().strftime("%Y-%m-%d")
    is_committed_today = data["borrel_commit"]["active"] and data["borrel_commit"]["date"] == today_str

    if not is_committed_today:
        with st.container(border=True):
            st.markdown("#### 🤝 Pre-Commitment voor vanavond")
            max_drinks = st.slider("Hoeveel glazen drink je vanavond maximaal?", 1, 8, 3)
            replacement = st.selectbox(
                "Wat doe je zodra iemand anders gaat roken of jij trek krijgt?",
                [
                    "Ik bestel/pak direct een groot glas ijskoud bruiswater",
                    "Ik neem een sterke suikervrije munt of kauwgom",
                    "Ik blijf binnen / aan tafel zitten als anderen naar buiten lopen",
                    "Ik start eerst de 10-minuten timer in deze app"
                ]
            )
            if st.button("🛡️ Activeer Borrel-Contract voor vanavond", type="primary", use_container_width=True):
                data["borrel_commit"] = {
                    "active": True,
                    "date": today_str,
                    "max_drinks": max_drinks,
                    "note": replacement
                }
                save_data(data)
                st.rerun()
    else:
        st.success(f"**Borrel-Contract Actief voor vandaag!**\n\n- Richtlijn: Max **{data['borrel_commit']['max_drinks']} glazen**, **0 sigaretten**.\n- Jouw afgesproken actie bij trek: *{data['borrel_commit']['note']}*")
        if st.button("Borrel-avond succesvol afgerond (+3 uitgespaarde sigaretten loggen!)", type="primary", use_container_width=True):
            add_log("resisted", 3, "🍺 Borrel / Alcohol", "Borrel-contract gehaald")
            data["borrel_commit"]["active"] = False
            save_data(data)
            st.balloons()
            time.sleep(1)
            st.rerun()

    st.divider()
    st.markdown("#### ⏱️ De 10-Minuten 'Urge Surf' Regel")
    st.caption("Krijg je tijdens het drinken ineens sterke drang? Verbied jezelf niets, maar spreek af: ik mag pas beslissen als deze klok van 3 (of 10) minuten op nul staat.")
    
    wait_minutes = st.radio("Kies je afkoeltijd:", [3, 5, 10], index=1, horizontal=True, format_func=lambda x: f"{x} minuten")
    
    if st.button(f"🚨 Start {wait_minutes}-Minuten Trek-Timer", use_container_width=True):
        timer_placeholder = st.empty()
        progress_bar = st.progress(0.0)
        total_seconds = wait_minutes * 60
        
        for sec in range(total_seconds, 0, -1):
            mins, secs = divmod(sec, 60)
            pct = (total_seconds - sec) / total_seconds
            progress_bar.progress(pct)
            timer_placeholder.markdown(f"""
            ### ⏳ Wacht nog **{mins:02d}:{secs:02d}**
            * **Stap 1:** Drink nu eerst een paar flinke slokken koud water.
            * **Stap 2:** Verander van houding of loop even naar een andere plek.
            * **Besef:** Deze golf van trek bereikt nu zijn piek en zakt binnen enkele minuten vanzelf weg.
            """)
            time.sleep(1)
        
        progress_bar.progress(1.0)
        timer_placeholder.success("🎉 Tijd is om! De ergste piek is voorbij. Log je overwinning bij het eerste tabblad!")
        st.balloons()

# ==========================================
# TAB 3: SOS, ADEMHALING & MOTIVATIE
# ==========================================
with tab_sos:
    st.subheader("🧠 Directe Mentale Reset")
    
    if "current_quote" not in st.session_state:
        st.session_state.current_quote = random.choice(data["custom_quotes"])
        
    st.info(f"💡 **Herinnering voor nu:**\n\n*\"{st.session_state.current_quote}\"*")
    
    if st.button("🔄 Andere motivatie-kaart tonen", use_container_width=True):
        st.session_state.current_quote = random.choice(data["custom_quotes"])
        st.rerun()

    with st.expander("➕ Voeg je eigen persoonlijke reden toe"):
        new_quote = st.text_input("Waarom wil je scherp en rookvrij blijven?")
        if st.button("Voeg toe"):
            if new_quote:
                data["custom_quotes"].append(new_quote)
                save_data(data)
                st.success("Toegevoegd aan je kaarten!")

    st.divider()
    st.subheader("🌬️ 60-Seconden Ademhalings-Reset (4-7-8 Methode)")
    st.caption("Haalt binnen één minuut de fysieke onrust uit je zenuwstelsel als je om 20:00 uur op de bank zit.")
    
    if st.button("▶️ Start begeleide ademhaling (3 cycli)", use_container_width=True, type="primary"):
        breath_box = st.empty()
        breath_bar = st.progress(0)
        
        for cycle in range(1, 4):
            # 4 sec in
            for i in range(1, 5):
                breath_box.markdown(f"### 🟢 Adem rustig IN door je neus... ({i}/4s) — *Cyclus {cycle}/3*")
                breath_bar.progress(int((i / 4) * 100))
                time.sleep(1)
            # 7 sec vast
            for i in range(1, 8):
                breath_box.markdown(f"### 🟡 Houd je adem VAST... ({i}/7s) — *Cyclus {cycle}/3*")
                breath_bar.progress(100)
                time.sleep(1)
            # 8 sec uit
            for i in range(1, 9):
                breath_box.markdown(f"### 🔵 Blaas langzaam UIT door je mond... ({i}/8s) — *Cyclus {cycle}/3*")
                breath_bar.progress(int(((8 - i) / 8) * 100))
                time.sleep(1)
                
        breath_box.success("✨ Klaar! Voel hoe je hartslag en de drang zijn gezakt.")

    st.divider()
    st.subheader("🎥 Korte Motivatie-Video (Urge Surfing)")
    st.caption("Een korte video van 2 minuten om de golf van trek uit te zitten:")
    st.video("https://www.youtube.com/watch?v=Ob6o2x3t25g")

# ==========================================
# TAB 4: 20:00 BANK-TRIGGER & PUSHMELDINGEN
# ==========================================
with tab_push:
    st.subheader("🛋️ De 20:00 'Op de bank'-Trigger")
    st.markdown("""
    Rond **20:00 uur** liggen de kinderen op bed en schakelt je brein over van *zorg- en regelmodus* naar *ontspanning*. 
    Je brein verwart die overgang vaak met trek in een sigaret. 
    
    **De gouden regel voor 20:00 uur:** Verander het startsignaal van je avond. Loop na het naar bed brengen van de kinderen **eerst naar de keuken** voor een kop thee, speciaal fris of een snack voordat je op de bank gaat zitten.
    """)

    st.divider()
    st.subheader("📲 Pushmeldingen naar je telefoon testen")
    st.markdown("""
    Met de gratis app **ntfy** (beschikbaar voor Android en iPhone, geen account nodig) kun je direct pushmeldingen ontvangen:
    1. Installeer de **ntfy** app op je telefoon.
    2. Klik in de app op het **`+`** tekentje en abonneer je op een zelfgekozen, uniek onderwerp (bijv. `rookvrij_coach_2026`).
    3. Vul diezelfde naam links in het zijmenu van deze Streamlit-app in.
    """)
    
    if st.button("🔔 Stuur nu een test-pushmelding naar mijn telefoon", use_container_width=True):
        ok, msg
