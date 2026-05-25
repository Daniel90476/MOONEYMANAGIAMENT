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
    st.session_state.obiettivi = {
        "Target Mensile": {"valore": 300.0, "colore": "#2ecc71"},
        "Target Annuale": {"valore": 1500.0, "colore": "#3498db"}
    }

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

# --- BARRA LATERALE: NAVIGAZIONE E CONFIGURAZIONE OBIETTIVI ---
st.sidebar.title("📌 Navigazione Hub")
pagine_disponibili = ["🏠 Dashboard Generale"] + list(st.session_state.progetti.keys())
pagina_corrente = st.sidebar.radio("Vai a:", pagine_disponibili)

st.sidebar.divider()
st.sidebar.subheader("⚙️ Pannello Gestione Obiettivi")

# Configurazione dinamica di più obiettivi
for ob_nome, ob_info in st.session_state.obiettivi.items():
    st.session_state.obiettivi[ob_nome]["valore"] = st.sidebar.number_input(
        f"{ob_nome} (€)", 
        min_value=10.0, 
        value=float(ob_info["valore"]), 
        step=50.0
    )

# Possibilità di aggiungere un nuovo obiettivo al volo
with st.sidebar.expander("➕ Aggiungi un altro Obiettivo"):
    nuovo_ob_nome = st.text_input("Nome Obiettivo", placeholder="Es. Obiettivo Vacanze")
    nuovo_ob_val = st.number_input("Valore Target (€)", min_value=10.0, value=500.0, step=50.0)
    colore_scelto = st.selectbox("Colore Grafico", ["#9b59b6", "#f1c40f", "#e67e22", "#e74c3c"])
    if st.button("Inserisci Obiettivo"):
        if nuovo_ob_nome and nuevo_ob_nome not in st.session_state.obiettivi:
            st.session_state.obiettivi[nuovo_ob_nome] = {"valore": nuovo_ob_val, "colore": colore_scelto}
            st.rerun()


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
                    st.session_state.progetti[nome_p] = {
                        "tipo": tipo_p,
                        "cassa_iniziale": cassa_p,
                        "cassa_attuale": cassa_p,
                        "giocate": pd.DataFrame(columns=["Step", "Evento", "Quota", "Stake", "Esito", "Profitto Netto"]),
                        "parametri": {"quota_media": q_m, "totali": t_e, "attesi": p_e} if tipo_p == "Masaniello" else {}
                    }
                    st.success(f"Progetto '{nome_p}' creato con successo!")
                    st.rerun()
                else:
                    st.error("Nome non valido o già esistente.")

    st.divider()

    # --- CALCOLO METRICHE E PROFITTO GLOBALE ---
    profitto_totale = 0.0
    for p_nome, p_dati in st.session_state.progetti.items():
        if not p_dati["giocate"].empty:
            profitto_totale += p_dati["giocate"]["Profitto Netto"].sum()

    # --- SEZIONE MULTI-OBIETTIVI CON GRAFICO GAUGE PROGRESSIVO ---
    st.subheader("🎯 Monitoraggio Multi-Obiettivi Finanziari")
    st.write(f"Profitto Netto Totale Accumulato: **{profitto_totale:+.2f} €**")
    
    # Creazione dinamica di una riga di grafici per ogni obiettivo impostato
    com_ob = st.columns(len(st.session_state.obiettivi) if st.session_state.obiettivi else 1)
    
    for i, (ob_nome, ob_info) in enumerate(st.session_state.obiettivi.items()):
        with com_ob[i]:
            target_v = ob_info["valore"]
            # Evitiamo divisioni per zero
            percentuale_completata = min(100.0, (profitto_totale / target_v) * 100) if profitto_totale > 0 else 0.0
            
            fig_target = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = profitto_totale,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': f"{ob_nome}<br><span style='font-size:0.8em;color:gray'>Target: {target_v} € ({percentuale_completata:.1f}%)</span>", 'font': {'size': 16}},
                gauge = {
                    'axis': {'range': [0, max(target_v, profitto_totale * 1.2)]},
                    'bar': {'color': ob_info["colore"]},
                    'bgcolor': "white",
                    'borderwidth': 1,
                    'bordercolor': "#dcdde1"
                }
            ))
            fig_target.update_layout(height=220, margin=dict(l=30, r=30, t=50, b=10))
            st.plotly_chart(fig_target, use_container_width=True)

    st.divider()

    # --- PROGETTI ATTIVI E ANDAMENTO GRAFICO ---
    st.subheader("📈 Panoramica Progetti Attivi")
    if st.session_state.progetti:
        c_attivi, c_graf = st.columns([1, 2])
        
        with c_attivi:
            for p_nome, p_dati in st.session_state.progetti.items():
                p_prof = p_dati["giocate"]["Profitto Netto"].sum() if not p_dati["giocate"].empty else 0.0
                st.metric(
                    label=f"📂 {p_nome} ({p_dati['tipo']})", 
                    value=f"{p_dati['cassa_attuale']:.2f} €", 
                    delta=f"{p_prof:+.2f} € Profitto"
                )
        
        with c_graf:
            p_nomi = list(st.session_state.progetti.keys())
            p_profitti = [st.session_state.progetti[p]["giocate"]["Profitto Netto"].sum() if not st.session_state.progetti[p]["giocate"].empty else 0.0 for p in p_nomi]
            
            df_comp = pd.DataFrame({"Progetto": p_nomi, "Profitto Netto (€)": p_profitti})
            fig_comp = px.bar(
                df_comp, x="Progetto", y="Profitto Netto (€)", color="Profitto Netto (€)",
                color_continuous_scale=["#e74c3c", "#2ecc71"], title="Profitti Ripartiti per Progetto"
            )
            fig_comp.update_layout(height=300, margin=dict(t=40, b=10))
            st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.info("ℹ️ Nessun progetto attivo. Clicca sul pulsante '⚽ Nuovo Progetto' in alto per iniziare.")


# ==============================================================================
# 📂 PAGINA DEDICATA AL SINGOLO PROGETTO (RIGA PER RIGA)
# ==============================================================================
else:
    p_nome = pagina_corrente
    p_dati = st.session_state.progetti[p_nome]
    
    st.title(f"📂 Gestione Sistema: {p_nome}")
    st.markdown(f"Strategia utilizzata: **{p_dati['tipo']}** | Cassa Iniziale: **{p_dati['cassa_iniziale']:.2f} €**")
    st.divider()

    df_g = p_dati["giocate"]
    vinte = len(df_g[df_g["Esito"] == "Vinto"])
    perse = len(df_g[df_g["Esito"] == "Perso"])
    step_attuale = len(df_g) + 1

    # --- CALCOLO DELLO STAKE IN BASE AL MODELLO ---
    if p_dati["tipo"] == "Masaniello":
        pars = p_dati["parametri"]
        stake_suggerito = calcola_stake_masaniello(p_dati["cassa_iniziale"], pars["quota_media"], pars["totali"], pars["attesi"], vinte, perse)
        st.info(f"📊 **Parametri Masaniello**: {pars['totali']} totali, {pars['attesi']} attesi. Calcolato su quota media {pars['quota_media']:.2f}")
    else:
        # Modello Matrix a 4 stazioni (Risolto l'errore del NameError)
        st.subheader("🎛️ Seleziona Stazione Matrix")
        scelta_staz = st.radio("Livello:", ["S-Small (1%)", "Small (2.5%)", "Medium (5%)", "Large (10%)"], horizontal=True)
        
        # Correzione qui: usiamo la variabile italiana 'percentuale' coerentemente
        if "S-Small" in scelta_staz: percentuale = 0.01
        elif "Small" in scelta_staz: percentuale = 0.025
        elif "Medium" in scelta_staz: percentuale = 0.05
        else: percentuale = 0.10
        
        stake_suggerito = round(p_dati["cassa_attuale"] * percentuale, 2)

    # Mostra lo stake calcolato per il prossimo step
    st.metric(label=f"🎯 Stake Consigliato per lo Step {step_attuale}", value=f"{stake_suggerito:.2f} €")

    # --- FORM INSERIMENTO GIOCATA RIGA PER RIGA ---
    st.subheader(f"📝 Registra Giocata #{step_attuale}")
    with st.form(key=f"form_{p_nome}", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1: ev_input = st.text_input("Partita / Evento", placeholder="Es. Roma - Milan")
        with c2: qu_input = st.number_input("Quota Giocata", min_value=1.01, value=2.00, step=0.01, format="%.2f")
        with c3: es_input = st.selectbox("Esito", ["Vinto", "Perso"])
        
        submit_g = st.form_submit_button("⚡ Convalida ed Inserisci nel Registro")

    if submit_g:
        if ev_input:
            if es_input == "Vinto":
                prof_netto = (stake_suggerito * qu_input) - stake_suggerito
            else:
                prof_netto = -stake_suggerito

            nuova_g = pd.DataFrame([{
                "Step": step_attuale,
                "Evento": str(ev_input),
                "Quota": float(qu_input),
                "Stake": float(stake_suggerito),
                "Esito": str(es_input),
                "Profitto Netto": float(round(prof_netto, 2))
            }])
            
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
        
        df_g_Att = p_dati["giocate"].copy()
        df_g_Att["Progressivo"] = df_g_Att["Profitto Netto"].cumsum()
        
        fig_p = px.line(df_g_Att, x="Step", y="Progressivo", markers=True, title="Trend Profitto Lineare (€)")
        fig_p.update_traces(line_color="#3498db", width=3)
        st.plotly_chart(fig_p, use_container_width=True)
    else:
        st.info("Nessuna giocata presente per questo specifico progetto.")
