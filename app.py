import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import math

# Configurazione della pagina
st.set_page_config(page_title="Multi-Project Money Management", layout="wide", page_icon="⚽")

# --- INIZIALIZZAZIONE MEMORIA DATI (SESSION STATE) ---
if "progetti" not in st.session_state:
    st.session_state.progetti = {}
if "obiettivi" not in st.session_state:
    st.session_state.obiettivi = {"Target Guadagno": 500.0, "Cassa Iniziale": 1000.0}

# --- FUNZIONE MATEMATICA MASANIELLO ---
def calcola_stake_masaniello(cassa, q_med, tot_ev, pag_ev, vinte, perse):
    rimanenti_tot = tot_ev - (vinte + perse)
    rimanenti_vincere = pag_ev - vinte
    if rimanenti_tot <= 0 or rimanenti_vincere <= 0 or rimanenti_vincere > rimanenti_tot:
        return 0.0
    num = math.comb(rimanenti_tot - 1, rimanenti_vincere - 1) * (q_med ** rimanenti_vincere)
    den = sum(math.comb(rimanenti_tot, i) * (q_med ** i) for i in range(rimanenti_vincere, rimanenti_tot + 1))
    if den == 0: return 0.0
    return round(cassa * (num / den), 2)

# --- BARRA LATERALE: NAVIGAZIONE ---
st.sidebar.title("📌 Navigazione Hub")
pagine_disponibili = ["🏠 Dashboard Generale"] + list(st.session_state.progetti.keys())
pagina_corrente = st.sidebar.radio("Vai a:", pagine_disponibili)

st.sidebar.divider()
st.sidebar.subheader("⚙️ Impostazioni Obiettivi")
st.session_state.obiettivi["Cassa Iniziale"] = st.sidebar.number_input("Cassa Totale Disponibile (€)", min_value=10.0, value=st.session_state.obiettivi["Cassa Iniziale"], step=50.0)
st.session_state.obiettivi["Target Guadagno"] = st.sidebar.number_input("Target Profitto Globale (€)", min_value=10.0, value=st.session_state.obiettivi["Target Guadagno"], step=50.0)


# ==============================================================================
# 🏠 PAGINA PRINCIPALE: DASHBOARD GENERALE
# ==============================================================================
if pagina_corrente == "🏠 Dashboard Generale":
    st.title("📊 Controllo Centralizzato Investimenti")
    st.markdown("Crea nuovi sistemi di Money Management, monitora l'andamento globale e tieni d'occhio i tuoi obiettivi finanziari.")
    st.divider()

    # --- POP-UP NUOVO PROGETTO (PULSANTE ⚽) ---
    col_btn, _ = st.columns([1, 3])
    with col_btn:
        with st.popover("⚽ Nuovo Progetto", use_container_width=True):
            st.subheader("Crea un nuovo sistema")
            nome_p = st.text_input("Nome Progetto", placeholder="Es. Masaniello 14/30 Win HT")
            tipo_p = st.selectbox("Strategia", ["Masaniello", "Matrix a 4 Stazioni"])
            cassa_p = st.number_input("Cassa Dedicata (€)", min_value=10.0, value=200.0, step=10.0)
            
            if tipo_p == "Masaniello":
                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1: q_m = st.number_input("Quota Media", min_value=1.05, value=2.00, step=0.05)
                with col_m2: t_e = st.number_input("Eventi Totali", min_value=1, value=30)
                with col_m3: p_e = st.number_input("Eventi Attesi", min_value=1, value=14)
            
            if st.button("🚀 Inizializza Progetto", use_container_width=True):
                if nome_p and nome_p not in st.session_state.progetti:
                    # Struttura dati per il singolo progetto
                    st.session_state.progetti[nome_p] = {
                        "tipo": tipo_p,
                        "cassa_iniziale": cassa_p,
                        "cassa_attuale": cassa_p,
                        "giocate": pd.DataFrame(columns=["Step", "Evento", "Quota", "Stake", "Esito", "Profitto Netto"]),
                        "parametri": {"quota_media": q_m, "totali": t_e, "attesi": p_e} if tipo_p == "Masaniello" else {}
                    }
                    st.success(f"Progetto '{nome_p}' creato! Selezionalo nella barra laterale.")
                    st.rerun()
                else:
                    st.error("Nome non valido o già esistente.")

    st.divider()

    # --- CALCOLO METRICHE GLOBALI ---
    profitto_totale = 0.0
    for p_nome, p_dati in st.session_state.progetti.items():
        if not p_dati["giocate"].empty:
            profitto_totale += p_dati["giocate"]["Profitto Netto"].sum()

    # --- SEZIONE GRAFICO OBIETTIVI (GAUGE CHART) ---
    st.subheader("🎯 Stato di Avanzamento Obiettivo")
    
    fig_target = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = profitto_totale,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Profitto Progressivo (€) rispetto al Target", 'font': {'size': 18}},
        delta = {'reference': st.session_state.obiettivi["Target Guadagno"], 'increasing': {'color': "green"}},
        gauge = {
            'axis': {'range': [None, st.session_state.obiettivi["Target Guadagno"] * 1.2]},
            'bar': {'color': "#2ecc71"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, st.session_state.obiettivi["Target Guadagno"]], 'color': '#f1f2f6'}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': st.session_state.obiettivi["Target Guadagno"]}}))
    
    fig_target.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_target, use_container_width=True)

    # --- PROGETTI ATTIVI E ANDAMENTO GRAFICO ---
    st.subheader("📈 Panoramica Progetti Attivi")
    if st.session_state.progetti:
        c_attivi, c_graf = st.columns([1, 2])
        
        with c_attivi:
            for p_nome, p_dati in st.session_state.progetti.items():
                p_prof = p_dati["giocate"]["Profitto Netto"].sum() if not p_dati["giocate"].empty else 0.0
                color = "green" if p_prof >= 0 else "red"
                st.metric(label=f"📂 {p_nome} ({p_dati['tipo']})", value=f"{p_dati['cassa_attuale']:.2f} €", delta=f"{p_prof:+.2f} € Profitto")
        
        with c_graf:
            # Grafico comparativo profitti dei progetti
            p_nomi = list(st.session_state.progetti.keys())
            p_profitti = [st.session_state.progetti[p]["giocate"]["Profitto Netto"].sum() if not st.session_state.progetti[p]["giocate"].empty else 0.0 for p in p_nomi]
            
            df_comp = pd.DataFrame({"Progetto": p_nomi, "Profitto Netto (€)": p_profitti})
            fig_comp = px.bar(df_comp, x="Progetto", y="Profitto Netto (€)", color="Profitto Netto (€)",
                             color_continuous_scale=["#e74c3c", "#2ecc71"], title="Profitti Ripartiti per Progetto")
            fig_comp.update_layout(height=300)
            st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.info("ℹ️ Nessun progetto attivo. Clicca sul pulsante '⚽ Nuovo Progetto' in alto per iniziare.")


# ==============================================================================
# 📂 PAGINA DEDICATA AL SINGOLO PROGETTO
# ==============================================================================
else:
    p_nome = pagina_corrente
    p_dati = st.session_state.progetti[p_nome]
    
    st.title(f"📂 Gestione Sistema: {p_nome}")
    st.markdown(f"Strategia utilizzata: **{p_dati['tipo']}** | Cassa Iniziale: **{p_dati['cassa_iniziale']:.2f} €**")
    st.divider()

    # Calcolo situazione attuale delle giocate convalidate
    df_g = p_dati["giocate"]
    vinte = len(df_g[df_g["Esito"] == "Vinto"])
    perse = len(df_g[df_g["Esito"] == "Perso"])
    step_attuale = len(df_g) + 1

    # --- CALCOLO DELLO STAKE IN BASE AL MODELLO ---
    if p_dati["tipo"] == "Masaniello":
        pars = p_dati["parametri"]
        stake_suggerito = calcola_stake_masaniello(p_dati["cassa_iniziale"], pars["quota_media"], pars["totali"], pars["attesi"], vinte, perse)
        st.info(f"📊 **Parametri Masaniello**: {pars['totali']} eventi totali, {pars['attesi']} attesi. Rendimento calcolato su quota media {pars['quota_media']:.2f}")
    else:
        # Modello Matrix a 4 stazioni applicato alla cassa corrente del progetto
        st.subheader("🎛️ Seleziona Stazione Matrix")
        scelta_staz = st.radio("Livello:", ["S-Small (1%)", "Small (2.5%)", "Medium (5%)", "Large (10%)"], horizontal=True)
        percentuale = 0.01 if "S-Small" in scelta_staz else 0.025 if "Small" in scelta_staz else 0.05 if "Medium" in scelta_staz else 0.10
        stake_suggerito = round(p_dati["cassa_attuale"] * percentage, 2)

    # Mostra lo stake calcolato per il prossimo step
    st.metric(label=f"🎯 Stake Consigliato per lo Step {step_attuale}", value=f"{stake_suggerito:.2f} €")

    # --- FORM INSERIMENTO GIOCATA RIGA PER RIGA ---
    st.subheader(f"📝 Registra Giocata #{step_attuale}")
    with st.form(key=f"form_{p_nome}", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1: ev_input = st.text_input("Partita / Evento", placeholder="Es. Inter - Milan")
        with c2: qu_input = st.number_input("Quota Giocata", min_value=1.01, value=2.00, step=0.01, format="%.2f")
        with c3: es_input = st.selectbox("Esito", ["Vinto", "Perso"])
        
        submit_g = st.form_submit_button("⚡ Convalida ed Inserisci nel Registro")

    if submit_g:
        if ev_input:
            # Calcolo profitto della giocata
            if es_input == "Vinto":
                prof_netto = (stake_suggerito * qu_input) - stake_suggerito
            else:
                prof_netto = -stake_suggerito

            # Creazione nuova riga
            nuova_g = pd.DataFrame([{
                "Step": step_attuale,
                "Evento": str(ev_input),
                "Quota": float(qu_input),
                "Stake": float(stake_suggerito),
                "Esito": str(es_input),
                "Profitto Netto": float(round(prof_netto, 2))
            }])
            
            # Aggiornamento dati del progetto
            p_dati["giocate"] = pd.concat([df_g, nuova_g], ignore_index=True)
            p_dati["cassa_attuale"] = round(p_dati["cassa_attuale"] + prof_netto, 2)
            st.success("Giocata inserita con successo!")
            st.rerun()
        else:
            st.error("Inserisci il nome dell'evento prima di salvare.")

    st.divider()

    # --- ELENCO GIOCATE E GRAFICO DEL PROGETTO ---
    if not p_dati["giocate"].empty:
        st.subheader("📋 Registro Storico Giocate del Progetto")
        st.dataframe(p_dati["giocate"], use_container_width=True)
        
        # Grafico lineare del profitto progressivo di questa specifica sessione
        df_g_Att = p_dati["giocate"].copy()
        df_g_Att["Progressivo"] = df_g_Att["Profitto Netto"].cumsum()
        
        fig_p = px.line(df_g_Att, x="Step", y="Progressivo", markers=True, title="Trend Profitto Lineare (€)")
        fig_p.update_traces(line_color="#3498db", width=3)
        st.plotly_chart(fig_p, use_container_width=True)
    else:
        st.info("Nessuna giocata presente per questo specifico progetto.")
