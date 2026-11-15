"""Passo 4e - Dashboard di monitoraggio del reparto costruzione avvolgimenti (Streamlit).
Avvio: streamlit run app.py   (dopo: python prepara_dati.py <Elaborato_Finale>). Dati reali anonimizzati (R) e simulati (S), sempre etichettati."""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd, joblib, streamlit as st, plotly.graph_objects as go
from plotly.subplots import make_subplots
warnings.filterwarnings("ignore")
from scoring import *
import spiega, guida

D = Path(__file__).parent / "dati_dashboard"
BLU, ARANCIO, ACQUA, GRIGIO = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984"
st.set_page_config(page_title="Digital Twin del reparto avvolgimenti", layout="wide")

@st.cache_resource
def modelli(): return joblib.load(D / "modelli.joblib")
@st.cache_data
def tabelle():
    return (pd.read_csv(D / "cicli_autoclave.csv"), pd.read_csv(D / "curve_autoclave.csv.gz"), pd.read_csv(D / "cicli_pressa.csv"),
            json.load(open(D / "reparto.json")), pd.read_csv(D / "curva_conformita_vs_vuoto.csv"), pd.read_csv(D / "politica_vuoto_finale.csv"))
M = modelli(); AC, CUR, PR, REP, CURVA_P, POL = tabelle()

def badge(prov):
    col = ACQUA if prov == "R" else ARANCIO
    return f"<span style='background:{col};color:white;padding:2px 10px;border-radius:10px;font-weight:600'>{'REALE' if prov == 'R' else 'SIMULATO'}</span>"
def come_leggere(sid):
    """Espansore con la guida breve della scheda (la guida completa è nella sezione «Guida alla lettura»)."""
    s = next(x for x in guida.SEZIONI if x["id"] == sid)
    with st.expander("Come leggere questa scheda"):
        st.markdown(guida.md_sezione(s, "breve")); st.caption("Esempi, indicazioni per operatori e commissione e schermata annotata: sezione «Guida alla lettura».")
def etichetta_ciclo(r):
    extra = f" · {r.note}" if isinstance(r.note, str) and r.note else (f" · anomalia: {r.anomalia.replace('_', ' ')}" if r.anomalia not in ("nessuna",) and isinstance(r.anomalia, str) else "")
    return f"{r.id_ciclo} · {'reale' if r.provenienza == 'R' else 'simulato'}{extra}"

st.sidebar.title("Digital Twin del reparto avvolgimenti")
pagina = st.sidebar.radio("Sezione", ["Stato del reparto", "Ciclo di autoclave con allarme", "Qualità e probabilità di conformità", "Raccomandazione sul vuoto finale", "Pressatura e verifica dell'altezza", "Guida alla lettura"])
st.sidebar.caption("Prototipo di supporto alle decisioni: nessun controllo automatico delle macchine. I dati sono reali anonimizzati (R) oppure simulati (S) e ogni esempio riporta la propria provenienza.")

if pagina == "Stato del reparto":
    st.header("Stato del reparto"); come_leggere("stato")
    st.markdown(badge("S") + " &nbsp; Simulatore a eventi discreti (replica di 60 settimane, caso base). Sensibilità e scenari provengono dal simulatore e dal supporto all'ottimizzazione.", unsafe_allow_html=True)
    k, ic = REP["kpi"], REP["ic95"]
    c = st.columns(5)
    c[0].metric("Unità rilasciate / settimana", f"{k['throughput_sett']:.1f}", f"± {ic['throughput_sett']:.1f}", delta_color="off")
    c[1].metric("Tempo di attraversamento", f"{k['lt_medio_gg']:.1f} gg", f"p90 {k['lt_p90_gg']:.0f} gg", delta_color="off")
    c[2].metric("Unità in lavorazione (WIP)", f"{k['wip_medio']:.1f}")
    c[3].metric("Utilizzo autoclave", f"{100 * k['ut_autoclave']:.0f}%", "collo di bottiglia", delta_color="off")
    c[4].metric("Utilizzo avvolgitrici / pressa", f"{100 * k['ut_avvolgitrici']:.0f}% / {100 * k['ut_pressa']:.0f}%")
    s = pd.DataFrame(REP["serie"])
    f = go.Figure(); f.add_scatter(x=s.giorno, y=s.wip, name="Unità in lavorazione", line=dict(color=BLU, width=2))
    f.add_scatter(x=s.giorno, y=s.q_pool, name="Coda in attesa di autoclave", line=dict(color=ARANCIO, width=2)); f.add_scatter(x=s.giorno, y=s.q_avv, name="Coda avvolgitrici", line=dict(color=ACQUA, width=2))
    f.update_layout(height=320, margin=dict(l=10, r=10, t=30, b=10), xaxis_title="Giorno simulato (dopo il riscaldamento)", yaxis_title="Unità", title="WIP e code (media giornaliera)", legend=dict(orientation="h", y=-0.3))
    st.plotly_chart(f, use_container_width=True)
    g = REP["gantt"]; f = go.Figure()
    for i, x in enumerate(g): f.add_bar(x=[x["dur"]], base=[x["t0"]], y=[0], orientation="h", marker=dict(color=BLU, line=dict(color="white", width=2)), showlegend=False, hovertemplate=f"{x['n']} unità · {x['kg']} kg · {x['dur']*24:.0f} h<extra></extra>", text=f"{x['n']}u", textposition="inside")
    f.update_layout(height=170, margin=dict(l=10, r=10, t=30, b=10), xaxis_title="Giorni (8 settimane simulate)", yaxis=dict(visible=False), title="Carichi in autoclave (una autoclave: nessuna sovrapposizione)", barmode="overlay")
    st.plotly_chart(f, use_container_width=True)
    sc = pd.DataFrame(REP["scenari_4d"]); sc = sc[sc.arrivi_x == 1.0] if "arrivi_x" in sc else sc
    st.subheader("Scenari sulla durata del vuoto finale ")
    t = sc[["scenario", "durata_carico_h_media", "lt_medio_gg_media", "ut_autoclave_media", "pool_autoclave_media", "rischio_aggiuntivo_media"]].copy()
    t.columns = ["Scenario", "Durata del carico (h)", "Tempo di attraversamento (gg)", "Utilizzo autoclave", "Coda per l'autoclave", "Rischio aggiuntivo di non conformità"]
    t["Utilizzo autoclave"] = (100 * t["Utilizzo autoclave"]).round(1).astype(str) + "%"; t["Rischio aggiuntivo di non conformità"] = (100 * t["Rischio aggiuntivo di non conformità"]).round(1).astype(str) + " pp"
    st.dataframe(t.round(2), hide_index=True, use_container_width=True)

elif pagina == "Ciclo di autoclave con allarme":
    st.header("Ciclo di autoclave con allarme"); come_leggere("autoclave")
    sel = st.selectbox("Ciclo", AC.index, format_func=lambda i: etichetta_ciclo(AC.loc[i]), index=0); r = AC.loc[[sel]]; x = r.iloc[0]
    res = ad_autoclave(M, r); thr = M["ad"]["soglia_mahal"]; m = float(res["mahal"][0]); al = bool(res["allarme"][0])
    st.markdown(badge(x.provenienza), unsafe_allow_html=True)
    cu = CUR[CUR.id_ciclo == x.id_ciclo]
    f = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, subplot_titles=("Temperatura media delle sonde (°C)", "Pressione (mbar, scala logaritmica)"))
    f.add_scatter(x=cu.h, y=cu.T_media, line=dict(color=BLU, width=1.6), name="T media", row=1, col=1)
    f.add_scatter(x=cu.h, y=cu.P_mbar.clip(lower=0.05), line=dict(color=ARANCIO, width=1.6), name="Pressione", row=2, col=1); f.update_yaxes(type="log", row=2, col=1)
    f.update_layout(height=470, margin=dict(l=10, r=10, t=40, b=10), showlegend=False, xaxis2_title="Ore dall'avvio"); st.plotly_chart(f, use_container_width=True)
    c = st.columns(3); c[0].metric("Durata", f"{x.durata_h:.0f} h"); c[1].metric("Punteggio di anomalia", (f"{m:.1f}" if m <= 1000 else "> 1000"), f"soglia {thr:.1f}", delta_color="off"); c[2].metric("Segnalazione", "ANOMALO" if al else "regolare")
    (st.error if al else st.success)(spiega.esito_ad(al, m, thr))
    if x.provenienza == "R": st.warning("Per i cicli reali il modello, addestrato su cicli simulati, segnala tutti i cicli (scarto simulato-reale, v. Capitolo 7): si considerino il punteggio relativo e la graduatoria, non l'allarme.")
    st.markdown("**Perché**: variabili che si scostano di più dal comportamento dei cicli regolari")
    Xr = feat_ad(r).fillna(M["ad"]["mediana"])[M["ad"]["colonne"]]; z = res["z"].values[0]
    for ftxt in spiega.frasi_anomalia(z, M["ad"]["colonne"], Xr.values[0], M["ad"]["mediana"].values): st.markdown("- " + ftxt)
    if isinstance(x.note, str) and x.note: st.caption(f"Nota sul ciclo: {x.note}.")
    elif x.provenienza == "S": st.caption(f"Etichetta nota (dato simulato): {x.anomalia.replace('_', ' ')}.")

elif pagina == "Qualità e probabilità di conformità":
    st.header("Qualità e probabilità di conformità dell'essiccazione"); come_leggere("qualita")
    sel = st.selectbox("Ciclo", AC.index, format_func=lambda i: etichetta_ciclo(AC.loc[i]), index=1); r = AC.loc[[sel]]; x = r.iloc[0]
    st.markdown(badge(x.provenienza), unsafe_allow_html=True)
    rows = []
    for fin in FINESTRE:
        h, p = qualita_autoclave(M, r, fin); rows.append(dict(finestra=("fine ciclo" if fin == "fine" else f"{fin} h"), h2o=float(h[0]), p=float(p[0])))
    q = pd.DataFrame(rows)
    f = make_subplots(rows=1, cols=2, subplot_titles=("Acqua estratta prevista (g/h/t)", "Probabilità di essiccazione conforme"))
    f.add_scatter(x=q.finestra, y=q.h2o, mode="lines+markers", line=dict(color=BLU, width=2), name="prevista", row=1, col=1)
    f.add_hline(y=10, line_dash="dot", line_color="black", row=1, col=1, annotation_text="limite 10")
    if not np.isnan(x.h2o_g_h_t): f.add_hline(y=x.h2o_g_h_t, line_color=ARANCIO, row=1, col=1, annotation_text=f"osservata {x.h2o_g_h_t:.1f}")
    f.add_bar(x=q.finestra, y=q.p, marker_color=[GRIGIO] * 3 + [BLU], row=1, col=2); f.add_hline(y=0.95, line_dash="dot", line_color="black", row=1, col=2); f.update_yaxes(range=[0, 1.02], row=1, col=2)
    f.update_layout(height=340, margin=dict(l=10, r=10, t=40, b=10), showlegend=False, xaxis_title="Finestra osservata", xaxis2_title="Finestra osservata"); st.plotly_chart(f, use_container_width=True)
    pf = q.p.iloc[-1]; (st.success if pf >= 0.95 else st.warning if pf >= 0.8 else st.error)(f"A fine ciclo: acqua estratta prevista {q.h2o.iloc[-1]:.1f} g/h/t; probabilità di essiccazione conforme {100 * pf:.0f}%.")
    if x.curva_troncata == 1: st.warning("Ciclo incompleto (curva troncata): la previsione a fine ciclo non è significativa.")
    st.markdown("**Perché** (contributi alla previsione a fine ciclo)")
    X, sh, cols = shap_autoclave(M, r)
    for ftxt in spiega.frasi_qualita(cols, X.values[0], sh[0]): st.markdown("- " + ftxt)
    top = pd.Series(sh[0], index=[eti(c)[0] for c in cols]).sort_values(key=abs, ascending=False).head(8)[::-1]
    f = go.Figure(go.Bar(x=top.values, y=top.index, orientation="h", marker_color=[ARANCIO if v > 0 else BLU for v in top.values])); f.update_layout(height=320, margin=dict(l=10, r=10, t=30, b=10), title="Contributi SHAP (arancio: più umidità residua; blu: meno)")
    st.plotly_chart(f, use_container_width=True)
    st.caption("L'allerta precoce migliora con l'avanzare del ciclo: a 24 h la previsione è poco informativa (Capitolo 7). Sui dati simulati le prestazioni sono ottimistiche per costruzione.")

elif pagina == "Raccomandazione sul vuoto finale":
    st.header("Raccomandazione sulla durata del vuoto finale"); come_leggere("vuoto")
    st.markdown(badge("R") + " &nbsp; Modello costruito sul registro reale dei carichi (49 carichi); è una correlazione osservata, da validare in reparto.", unsafe_allow_html=True)
    c = st.columns(3); peso = c[0].number_input("Peso del carico (kg)", 300, 8000, 3000, 100); va = c[1].number_input("Ore di vuoto finale previste (attuale)", 3.0, 80.0, 18.0, 0.5)
    pol = c[2].selectbox("Politica", ["P ≥ 0,95", "P ≥ 0,99", "Cautelativa (intervallo al 90%)"])
    cl = int(np.searchsorted([1900.0, 4500.0], peso, side="right")); nome = POL.classe.unique()[cl]; g = CURVA_P[CURVA_P.classe == nome]
    pf = lambda v: float(np.interp(v, g.V_h, g.P_media)); sel_ = POL[(POL.classe == nome)]
    vs = float(sel_[sel_.soglia_P == (0.99 if "0,99" in pol else 0.95)][("V_raccomandato_cautelativo_h" if "Caut" in pol else "V_raccomandato_h")].iloc[0])
    vs = max(vs, 3.0); rid = max(va - vs, 0)
    m = st.columns(4); m[0].metric("Classe di peso", nome.split(" ")[0]); m[1].metric("Durata minima suggerita", f"{vs:.1f} h"); m[2].metric("Ore risparmiate", f"{rid:.1f} h")
    m[3].metric("Probabilità di conformità", f"{100 * pf(min(va, vs) if rid > 0 else va):.0f}%", f"{100 * (pf(vs) - pf(va)):+.0f} pp rispetto all'attuale" if rid > 0 else "invariata", delta_color="off")
    f = go.Figure(); f.add_scatter(x=g.V_h, y=g.P_p95, line=dict(width=0), showlegend=False, hoverinfo="skip"); f.add_scatter(x=g.V_h, y=g.P_p05, fill="tonexty", fillcolor="rgba(42,120,214,0.15)", line=dict(width=0), name="intervallo 90%")
    f.add_scatter(x=g.V_h, y=g.P_media, line=dict(color=BLU, width=2.2), name="probabilità di conformità")
    f.add_scatter(x=[va], y=[pf(va)], mode="markers", marker=dict(size=11, color=ARANCIO, line=dict(color="white", width=2)), name="durata attuale")
    f.add_scatter(x=[vs], y=[pf(vs)], mode="markers", marker=dict(size=11, color=ACQUA, symbol="triangle-down", line=dict(color="white", width=2)), name="durata suggerita")
    f.add_hline(y=0.95, line_dash="dot", line_color="black"); f.update_layout(height=380, margin=dict(l=10, r=10, t=30, b=10), xaxis_title="Ore di vuoto finale", yaxis_title="Probabilità di acqua estratta < 10 g/h/t", yaxis_range=[0.4, 1.01], xaxis_range=[0, 60], legend=dict(orientation="h", y=-0.25))
    st.plotly_chart(f, use_container_width=True)
    if rid > 0: st.info(f"Con {vs:.1f} h di vuoto finale invece di {va:.1f} h si risparmiano circa {rid:.0f} h di autoclave; la probabilità di essiccazione conforme passa da {100 * pf(va):.0f}% a {100 * pf(vs):.0f}%.")
    else: st.success("La durata prevista è già pari o inferiore a quella suggerita: nessuna riduzione proponibile (il modello non propone di allungare).")

elif pagina == "Guida alla lettura":
    st.header("Guida alla lettura della dashboard")
    st.markdown(guida.INTRO)
    c1, c2 = st.columns(2)
    with c1, st.expander("Colori ed etichette"):
        for a, b in guida.COLORI: st.markdown(f"- **{a}**: {b}")
    with c2, st.expander("Glossario"):
        for a, b in guida.GLOSSARIO: st.markdown(f"- **{a}**: {b}")
    with st.expander("Cautele generali", expanded=True):
        for x in guida.CAUTELE: st.markdown("- " + x)
    schede = st.tabs([s["titolo"] for s in guida.SEZIONI])
    for tab, s in zip(schede, guida.SEZIONI):
        with tab:
            st.image(str(D / "guida" / s["immagine"]), caption="Schermata annotata: i numeri nei cerchi corrispondono all'elenco «Cosa mostra».")
            st.markdown(guida.md_sezione(s))
            with st.expander("Per la commissione: cosa dimostra e limiti"): st.markdown(guida.md_commissione(s))

else:
    st.header("Pressatura e verifica dell'altezza"); come_leggere("pressa")
    PRs = PR.assign(_o=(PR.famiglia != 'avvolgimento').astype(int)).sort_values(['_o','id']); sel = st.selectbox("Ciclo di pressa", PRs.index, format_func=lambda i: f"{PRs.loc[i,'id']} · {PRs.loc[i,'data']} · {PRs.loc[i,'famiglia']} · {PRs.loc[i,'lavorazione'].lower()}{' · ALLARME' if PRs.loc[i,'allarme'] == 1 else ''}", index=0)
    r = PRs.loc[[sel]]; x = r.iloc[0]; res = pressa(M, r); al = bool(res["allarme"][0]); pc = float(res["p_conforme"][0]); h = altezza(r).iloc[0]
    st.markdown(badge("R"), unsafe_allow_html=True)
    c = st.columns(5); c[0].metric("Forza di fine pressata", f"{x.forza_fine_t:.0f} t"); c[1].metric("Tempo di ciclo", f"{x.tempo_ciclo_s:.0f} s"); c[2].metric("Differenza tra le quote", f"{x.delta_quote_mm:.2f} mm")
    c[3].metric("Segnalazione modello", "ANOMALO" if al else "regolare"); c[4].metric("Probabilità di conformità", f"{100 * pc:.0f}%")
    (st.error if al else st.success)(f"Il modello {'segnala' if al else 'non segnala'} un ciclo anomalo (punteggio {res['mahal'][0]:.1f}, soglia {M['pressa']['soglia_mahal']:.1f}); allarme registrato dalla macchina: {'sì' if x.allarme == 1 else 'no'}.")
    st.subheader("Verifica dell'altezza dell'avvolgimento")
    if x.famiglia == "avvolgimento" and not np.isnan(h.scarto_mm):
        a, b = st.columns(2); a.metric("Altezza misurata (ipotesi di calcolo)", f"{h.altezza_misurata_mm:.0f} mm"); b.metric("Altezza nominale", f"{x.altezza_nominale_mm:.0f} mm", f"{h.scarto_mm:+.0f} mm", delta_color="off")
        f = go.Figure(go.Bar(x=[h.scarto_mm], y=[""], orientation="h", marker_color=ARANCIO if h.scarto_mm < 0 else BLU)); f.add_vline(x=0, line_color="black"); f.update_layout(height=140, margin=dict(l=10, r=10, t=30, b=10), title="Scarto dal nominale (mm)")
        st.plotly_chart(f, use_container_width=True)
    st.info(messaggio_altezza(h.scarto_mm))
    st.caption("Altezza misurata = quota di fine pressata − spessore piastra base − spessore distanziale (ipotesi di lavoro). Nessuna tolleranza è fissata: si riportano lo scarto e il segno. La verifica riguarda solo gli avvolgimenti singoli; le fasi assemblate sono escluse.")
    st.markdown("**Perché** (variabili che si scostano di più dai cicli regolari)")
    for ftxt in spiega.frasi_anomalia(res["z"].values[0], M["pressa"]["colonne_ad"], feat_pressa_ad(r).values[0], M["pressa"]["scaler"].mean_): st.markdown("- " + ftxt)
