"""Passo 4e - Funzioni di punteggio condivise da preparazione dati, app Streamlit e pagina HTML.
Le stesse variabili e gli stessi modelli del Passo 4c (autoclave, pressa) e del Passo 4d (politica sul vuoto finale)."""
import numpy as np, pandas as pd

CURVA = ["durata_h", "t_rampa_90C_h", "n_eventi_vuoto", "vuoto_finale_h", "t_inizio_vuoto_finale_h", "p_min_finale_mbar", "p_min_intermedi_media_mbar",
         "dur_intermedi_media_h", "distanza_intermedi_h", "ore_sotto_2mbar", "plateau_T1_C", "plateau_T2_C", "plateau_T3_C", "plateau_T4_C", "plateau_T5_C",
         "spread_sonde_C", "T_media_plateau_C", "T_sd_plateau_C", "oscillazione_C", "rmse_profilo_nominale_C", "calo_T_vuoto_C", "T_acqua_max", "T_acqua_media", "P_baseline_mbar"]
EXTRA = ["calo_T_fuori_vuoto_C", "ore_sotto_85C_post_rampa", "max_var_T_5min", "quota_sonda_costante_max"]
CARICO = ["peso_kg", "n_unita", "n_fasi", "n_avv", "kg_per_unita"]
FINESTRE = [24, 48, 72, "fine"]

ETICHETTE = {  # nome leggibile e unita'
    "durata_h": ("durata del ciclo", "h"), "t_rampa_90C_h": ("tempo per raggiungere 90 °C", "h"), "n_eventi_vuoto": ("numero di eventi di vuoto", ""),
    "vuoto_finale_h": ("durata del vuoto finale", "h"), "ore_sotto_2mbar": ("ore sotto 2 mbar", "h"), "log10_p_min_finale_mbar": ("pressione minima del vuoto finale", "mbar"),
    "log10_p_min_intermedi_media_mbar": ("pressione minima dei vuoti intermedi", "mbar"), "peso_kg": ("peso del carico", "kg"), "n_unita": ("unità nel carico", ""),
    "n_fasi": ("fasi nel carico", ""), "n_avv": ("avvolgimenti nel carico", ""), "kg_per_unita": ("peso medio per unità", "kg"), "calo_T_vuoto_C": ("calo di temperatura nei vuoti", "°C"),
    "calo_T_fuori_vuoto_C": ("calo di temperatura fuori dal vuoto", "°C"), "ore_sotto_85C_post_rampa": ("ore sotto 85 °C dopo la rampa", "h"), "max_var_T_5min": ("massima variazione di T in 5 min", "°C"),
    "quota_sonda_costante_max": ("quota di campioni costanti di una sonda", ""), "rmse_profilo_nominale_C": ("scostamento dal profilo nominale", "°C"), "spread_sonde_C": ("scarto tra le sonde", "°C"),
    "oscillazione_C": ("oscillazione del termostato", "°C"), "T_media_plateau_C": ("temperatura media di plateau", "°C"), "ore_per_tonnellata": ("ore di ciclo per tonnellata", "h/t"),
    "t_inizio_vuoto_finale_h": ("inizio del vuoto finale", "h"), "setting_manuale": ("impostazione manuale", ""), "dur_intermedi_media_h": ("durata media dei vuoti intermedi", "h"),
    "distanza_intermedi_h": ("distanza tra vuoti intermedi", "h"), "T_sd_plateau_C": ("variabilità della temperatura di plateau", "°C"), "T_acqua_max": ("temperatura massima dell'acqua", "°C"),
    "T_acqua_media": ("temperatura media dell'acqua", "°C"), "P_baseline_mbar": ("pressione di riferimento", "mbar"),
    "tempo_ciclo_s": ("tempo di ciclo", "s"), "t_assestamento1_s": ("assestamento 1", "s"), "t_assestamento2_s": ("assestamento 2", "s"), "t_assestamento3_s": ("assestamento 3", "s"),
    "t_assestamento_tot_s": ("assestamento totale", "s"), "quota_fine_mm": ("quota di fine pressata", "mm"), "forza_fine_t": ("forza di fine pressata", "t"), "delta_quote_mm": ("differenza tra le quote", "mm"),
    "T_olio_C": ("temperatura olio", "°C"), "log_tempo": ("tempo di ciclo (log)", ""), "log_forza": ("forza (log)", ""), "caldo": ("pressatura a caldo", ""), "fase": ("fase assemblata", ""),
}
for p in ["plateau_T1_C", "plateau_T2_C", "plateau_T3_C", "plateau_T4_C", "plateau_T5_C"]: ETICHETTE[p] = ("temperatura di plateau " + p.split("_")[1], "°C")

def eti(nome):
    return ETICHETTE.get(nome, (nome.replace("_", " "), ""))

def valore(nome, v):
    """Valore leggibile (le colonne log10_ sono riportate in unita' originali)."""
    if v is None or (isinstance(v, float) and np.isnan(v)): return "n.d."
    if nome.startswith("log10_"): v = 10 ** v
    return f"{v:.2f}" if abs(v) < 10 else f"{v:.0f}"

def prep(df, cols):
    X = df[cols].copy()
    for c in ["p_min_finale_mbar", "p_min_intermedi_media_mbar"]:
        if c in X: X["log10_" + c] = np.log10(X[c].clip(lower=1e-3)); X = X.drop(columns=c)
    return X

def feat_ad(df):
    return prep(df, CURVA + EXTRA)

def feat_qualita(df, fin):
    """Caratteristiche per la predizione dell'acqua estratta con la finestra osservata `fin` (24, 48, 72 oppure 'fine')."""
    X = df[CARICO].copy(); X["setting_manuale"] = (df["setting"] == "S1+Manuale").astype(int)
    if fin == "fine":
        c = prep(df, CURVA); c["ore_per_tonnellata"] = df["ore_per_tonnellata"].values
    else:
        w = df[[f"w{fin}__{k}" for k in CURVA]].copy(); w.columns = CURVA; c = prep(w, CURVA)
    return pd.concat([X, c], axis=1)

# ---------------- autoclave ----------------
def ad_autoclave(M, df):
    """Punteggio di anomalia (distanza di Mahalanobis e Isolation Forest) e allarme del modello."""
    A = M["ad"]; X = feat_ad(df).fillna(A["mediana"]); Z = A["scaler"].transform(X[A["colonne"]])
    m = A["cov"].mahalanobis(Z); i = -A["iso"].decision_function(Z)
    # contributi per variabile: scostamento standardizzato
    return dict(mahal=m, iso=i, allarme=(m >= A["soglia_mahal"]).astype(int), z=pd.DataFrame(Z, columns=A["colonne"], index=df.index))

def qualita_autoclave(M, df, fin):
    mod = M["h2o"][fin]; X = feat_qualita(df, fin)[mod["colonne"]]
    mu = mod["modello"].predict(X); res = mod["residui"]
    h2o = np.exp(mu); p = np.array([(np.exp(m + res) < 10).mean() for m in mu])
    return h2o, p

def shap_autoclave(M, df):
    import shap
    mod = M["h2o"]["fine"]; X = feat_qualita(df, "fine")[mod["colonne"]]
    return X, shap.TreeExplainer(mod["modello"]).shap_values(X), mod["colonne"]

# ---------------- pressa ----------------
def feat_pressa_ad(df):
    X = df[["tempo_ciclo_s", "t_assestamento1_s", "t_assestamento2_s", "t_assestamento3_s", "t_assestamento_tot_s", "quota_fine_mm", "forza_fine_t", "delta_quote_mm", "T_olio_C"]].copy()
    X["caldo"] = (df.lavorazione == "Caldo").astype(int); X["fase"] = (df.famiglia == "fase").astype(int)
    X["log_tempo"] = np.log1p(df.tempo_ciclo_s); X["log_forza"] = np.log1p(df.forza_fine_t); return X

def feat_pressa_q(df, colonne):
    cat = ["lavorazione", "famiglia", "tipo", "modello", "impianto"]
    X = pd.get_dummies(df[cat].fillna("nd"), dtype=float)
    for c in ["sp_piastra_base_mm", "sp_distanziale_mm", "ricetta_manuale", "T_olio_C", "diametro_interno_mm", "altezza_nominale_mm",
              "tempo_ciclo_s", "t_assestamento1_s", "t_assestamento2_s", "t_assestamento3_s", "t_assestamento_tot_s", "quota_fine_mm", "forza_fine_t"]: X[c] = df[c].values
    return X.reindex(columns=colonne, fill_value=0.0)

def pressa(M, df):
    P = M["pressa"]; Z = P["scaler"].transform(feat_pressa_ad(df)); m = P["cov"].mahalanobis(Z)
    pc = P["clf"].predict_proba(feat_pressa_q(df, P["colonne_q"]))[:, 1]
    return dict(mahal=m, allarme=(m >= P["soglia_mahal"]).astype(int), p_conforme=pc, z=pd.DataFrame(Z, columns=P["colonne_ad"], index=df.index))

def altezza(df):
    """Altezza misurata dell'avvolgimento singolo = quota fine - piastra base - distanziale (ipotesi di lavoro); scarto dal nominale."""
    h = df["quota_fine_mm"] - df["sp_piastra_base_mm"] - df["sp_distanziale_mm"]
    ok = (df["famiglia"] == "avvolgimento") & (df["quota_fine_mm"] > 0) & (df["altezza_nominale_mm"] > 0)
    out = pd.DataFrame({"altezza_misurata_mm": h.where(ok), "scarto_mm": (h - df["altezza_nominale_mm"]).where(ok)}); return out

def messaggio_altezza(scarto):
    if scarto is None or (isinstance(scarto, float) and np.isnan(scarto)): return "Verifica non applicabile (fase assemblata o misura mancante)."
    if scarto < 0: return f"Altezza inferiore al nominale di {abs(scarto):.0f} mm: consultare i responsabili di produzione e dell'ufficio tecnico per valutare le compensazioni."
    if scarto > 0: return f"Altezza superiore al nominale di {scarto:.0f} mm: consultare l'ufficio tecnico per stabilire come intervenire."
    return "Altezza pari al nominale."
