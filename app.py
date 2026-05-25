
import streamlit as st
import pandas as pd
import plotly.express as px
import math
from streamlit_gsheets import GSheetsConnection

# Configurazione della pagina
st.set_page_config(page_title="Money Management Automation", layout="wide")

# CONNESSONE A GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNZIONE MATEMATICA MASANIELLO ---
def calcola_tutti_step_masaniello(cassa_impostata, quota_media, eventi_totali, eventi_attesi):
    if eventi_totali <= 0 or eventi_attesi <= 0 or eventi_attesi > eventi_totali:
        return 0.0
    num = math.comb(eventi_totali - 1, eventi_attesi - 1) * (quota_media ** eventi_attesi)
    den = sum(math.comb(eventi_totali, i) * (quota_media ** i) for i in range(eventi_attesi, eventi_totali + 1))
    if den == 0: return 0.0
    return round(cassa_impostata * (num / den), 2)

st.title("🛡️ Calcolatore Automatico Money Management")
st.markdown("Imposta la tua cassa di riferimento. Il sistema calcolerà automaticamente gli stake.")
st.divider()

# --- PROGETTI DISPONIBILI ---
CONFIG_PROGETTI = {
    "📊 Matrix a 4 Stazioni": {"tipo": "Matrix", "sheet": "Matrix"},
    "🍷 Masaniello Strategico": {"tipo": "Masaniello", "sheet": "Masaniello"}
}

progetto_scelto = st.selectbox("🗂️ Seleziona il Sottofoglio da visualizzare:", list(CONFIG_PROGETTI.keys()))
config = CONFIG_PROGETTI[progetto_scelto]

# 1. LETTURA DATI PROTETTA
try:
    df = conn.read(worksheet=config["sheet"], ttl=0)
    if df is None or df.empty or "Stake Calcolato" not in df.columns:
        df = pd.DataFrame(columns=["Data", "Evento", "Quota", "Stake Calcolato", "Esito", "Profitto Netto"])
except Exception:
    df = pd.DataFrame(columns=["Data", "Evento", "Quota", "Stake Calcolato", "Esito", "Profitto Netto"])

if not df.empty:
    df = df.dropna(subset=["Evento"])

# 2. IMPOSTAZIONE CASSA MANUALE
st.subheader("⚙️ Impostazione Cassa di Riferimento")
cassa_riferimento = st.number_input("Inserisci il Capitale da cui calcolare gli stake (€):", min_value=10.0, value=1000.0, step=50.0, format="%.2f")

st.divider()

# 3. GENERATORE AUTOMATICO DI STAKE
st.subheader("🎯 Tabella degli Stake Calcolati")

if config["tipo"] == "Matrix":
    st1 = cassa_riferimento * 0.01
    st2 = cassa_riferimento * 0.025
    st3 = cassa_riferimento * 0.05
    st4 = cassa_riferimento * 0.10
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔴 S-Small (1%)", f"{st1:.2f} €")
    c2.metric("🟠 Small (2.5%)", f"{st2:.2f} €")
    c3.metric("🔵 Medium (5%)", f"{st3:.2f} €")
    c4.metric("🟣 Large (10%)", f"{st4:.2f} €")
    
    scelta_stazione = st.radio("Quale stazione stai giocando adesso?", ["S-Small (1%)", "Small (2.5%)", "Medium (5%)", "Large (10%)"])
    if "S-Small" in scelta_stazione: stake_da_giocare = st1
    elif "Small" in scelta_stazione: stake_da_giocare = st2
    elif "Medium" in scelta_stazione: stake_da_giocare = st3
    else: stake_da_giocare = st4

elif config["tipo"] == "Masaniello":
    col_q, col_tot, col_ok = st.columns(3)
    with col_q: q_med = st.number_input("Quota Media Masa", min_value=1.01, value=2.00, step=0.05)
    with col_tot: t_ev = st.number_input("Eventi Totali", min_value=1, value=10, step=1)
    with col_ok: p_ev = st.number_input("Eventi Attesi (Prese)", min_value=1, value=6, step=1)
    
    stake_da_giocare = calcola_tutti_step_masaniello(cassa_riferimento, q_med, t_ev, p_ev)
    st.metric("🍷 Stake Masaniello Suggerito dello Step Attuale", f"{stake_da_giocare:.2f} €")

st.divider()

# 4. FORM DI INSERIMENTO OTTIMIZZATO (SENZA AUTO-RERUN PROBLEMATICI)
st.subheader("📝 Registra la Giocata Effettuata")
st.write(f"Lo stake bloccato per questa giocata è di **{stake_da_giocare:.2f} €**")

with st.form(key="inserimento_giocata", clear_on_submit=True):
    col_ev, col_qu, col_es = st.columns(3)
    with col_ev:
        evento_g = st.text_input("Partita / Evento", placeholder="Es. Inter - Juventus")
    with col_qu:
        quota_g = st.number_input("Quota Effettiva Giocata", min_value=1.01, value=2.00, step=0.01, format="%.2f")
    with col_es:
        esito_g = st.selectbox("Esito Finale", ["Vinto", "Perso", "In attesa"])
        
    registra = st.form_submit_button(label="🚀 Registra Operazione nel Registro")

if registra:
    if esito_g == "Vinto":
        profitto_netto = (stake_da_giocare * quota_g) - stake_da_giocare
    elif esito_g == "Perso":
        profitto_netto = -stake_da_giocare
    else:
        profitto_netto = 0.0

    nuova_riga = pd.DataFrame([{
        "Data": pd.Timestamp.now().strftime("%Y-%m-%d"),
        "Evento": str(evento_g),
        "Quota": float(quota_g),
        "Stake Calcolato": float(round(stake_da_giocare, 2)),
        "Esito": str(esito_g),
        "Profitto Netto": float(round(profitto_netto, 2))
    }])
    
    df = pd.concat([df, nuova_riga], ignore_index=True)
    
    try:
        conn.update(worksheet=config["sheet"], data=df)
        st.success("🎯 Giocata registrata correttamente sia sulla Dashboard che su Google Fogli! Aggiorna la pagina se necessario.")
    except Exception:
        st.warning("⚠️ Giocata salvata localmente nella tabella in basso. Controlla la sincronizzazione di Google Fogli.")

st.divider()

# 5. RENDICONTO E GRAFICI
if not df.empty and len(df) > 0:
    st.subheader("📋 Registro Storico delle Giocate Convalidate")
    st.dataframe(df, use_container_width=True)
    
    try:
        df["Profitto Netto"] = pd.to_numeric(df["Profitto Netto"])
        df["Profitto Progressivo"] = df["Profitto Netto"].cumsum()
        
        st.subheader("📈 Profitto Netto Progressivo (€)")
        fig = px.line(df, x=df.index, y="Profitto Progressivo", markers=True)
        fig.update_traces(line_color="#2ecc71", width=3)
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        pass
else:
    st.info("ℹ️ Nessuna giocata inserita in questo registro.")
