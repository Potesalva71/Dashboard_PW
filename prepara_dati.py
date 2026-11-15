"""Passo 4e - Prepara modelli e dati per la dashboard (app Streamlit e pagina HTML).
Uso: python prepara_dati.py <Elaborato_Finale>. Scrive in <Elaborato_Finale>/codice/dashboard/dati_dashboard/."""
import sys, os, json, warnings, joblib, numpy as np, pandas as pd
warnings.filterwarnings("ignore")
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.covariance import EmpiricalCovariance
from sklearn.model_selection import KFold
import lightgbm as lgb
from ml_common import soglia_per_richiamo, SEED
from scoring import *
import spiega

B = sys.argv[1]; D4B, D4C, D4D = (f"{B}/dati/{x}" for x in ("4b", "4c", "4d")); OUT = f"{B}/codice/dashboard/dati_dashboard"; os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(SEED)

# =============== AUTOCLAVE: unione delle tabelle ===============
a = pd.read_csv(f"{D4B}/autoclave_cicli.csv").merge(pd.read_csv(f"{D4C}/feature_extra.csv"), on="id_ciclo", how="left")
W = pd.read_csv(f"{D4C}/feature_finestre.csv")
for fin in FINESTRE[:3]:
    w = W[W.finestra_h == fin].set_index("id_ciclo")[CURVA].add_prefix(f"w{fin}__"); a = a.merge(w, left_on="id_ciclo", right_index=True, how="left")
S = a[a.provenienza == "S"]; tr, va, te = [S[S.split_random == k] for k in ("train", "validazione", "test")]; trva = pd.concat([tr, va])

# anomaly detection (come nel 4c: solo cicli regolari, soglia sul richiamo 0,80 in validazione)
Xtr = feat_ad(tr[tr.anomalia_flag == 0]); med = Xtr.median(); cols = list(Xtr.columns)
sc = StandardScaler().fit(Xtr.fillna(med)); Ztr = sc.transform(Xtr.fillna(med))
cov = EmpiricalCovariance().fit(Ztr); iso = IsolationForest(n_estimators=300, random_state=SEED).fit(Ztr)
Zv = sc.transform(feat_ad(va).fillna(med)[cols]); thr = soglia_per_richiamo(cov.mahalanobis(Zv), va.anomalia_flag)
AD = dict(scaler=sc, cov=cov, iso=iso, mediana=med, colonne=cols, soglia_mahal=thr)

# predizione dell'acqua estratta: un modello LightGBM per finestra, residui fuori campione per la probabilita' di conformita'
mk = lambda: lgb.LGBMRegressor(n_estimators=400, learning_rate=0.03, num_leaves=8, min_child_samples=10, subsample=0.8, subsample_freq=1, colsample_bytree=0.8, random_state=SEED, verbose=-1)
H2O = {}
for fin in FINESTRE:
    X = feat_qualita(trva, fin); y = np.log(trva.h2o_g_h_t.values); oof = np.zeros(len(X))
    for i, j in KFold(5, shuffle=True, random_state=SEED).split(X): oof[j] = mk().fit(X.iloc[i], y[i]).predict(X.iloc[j])
    H2O[fin] = dict(modello=mk().fit(X, y), colonne=list(X.columns), residui=y - oof)

# =============== PRESSA ===============
p = pd.read_csv(f"{D4B}/pressa_cicli.csv", parse_dates=["data"]).sort_values("data").reset_index(drop=True)
ptr = p[p.split_temporale == "train"]; pte = p[p.split_temporale == "test"]; cut = ptr.data.quantile(0.75); pfit = ptr[ptr.data <= cut]; pval = ptr[ptr.data > cut]
Xa = feat_pressa_ad(pfit[pfit.allarme == 0]); psc = StandardScaler().fit(Xa); pcov = EmpiricalCovariance().fit(psc.transform(Xa))
pthr = soglia_per_richiamo(pcov.mahalanobis(psc.transform(feat_pressa_ad(pval))), pval.allarme)
colq = list(feat_pressa_q(p, []).columns) if False else None
Xq_all = pd.get_dummies(p[["lavorazione", "famiglia", "tipo", "modello", "impianto"]].fillna("nd"), dtype=float)
colq = list(Xq_all.columns) + ["sp_piastra_base_mm", "sp_distanziale_mm", "ricetta_manuale", "T_olio_C", "diametro_interno_mm", "altezza_nominale_mm", "tempo_ciclo_s",
        "t_assestamento1_s", "t_assestamento2_s", "t_assestamento3_s", "t_assestamento_tot_s", "quota_fine_mm", "forza_fine_t"]
trv = pd.concat([pfit, pval])
clf = lgb.LGBMClassifier(n_estimators=400, learning_rate=0.03, num_leaves=15, subsample=0.8, subsample_freq=1, colsample_bytree=0.8, random_state=SEED, verbose=-1).fit(feat_pressa_q(trv, colq), trv.conforme_pressa)
PR = dict(scaler=psc, cov=pcov, soglia_mahal=pthr, colonne_ad=list(Xa.columns), clf=clf, colonne_q=colq)

M = dict(ad=AD, h2o=H2O, pressa=PR); joblib.dump(M, f"{OUT}/modelli.joblib", compress=3)

# =============== CICLI DI AUTOCLAVE PER LA DASHBOARD (solo test simulato non usato in addestramento + 9 reali) ===============
reali = a[a.provenienza == "R"]
sel_s = pd.concat([te[te.anomalia_flag == 1], te[te.anomalia_flag == 0].sample(31, random_state=SEED)])
ex = pd.concat([reali, sel_s]).reset_index(drop=True)
keep = ["id_ciclo", "provenienza", "anomalia", "anomalia_flag", "ciclo_prova", "ciclo_completato", "curva_troncata", "h2o_g_h_t", "essiccazione_conforme", "setting", "ore_per_tonnellata"] + CURVA + EXTRA + CARICO + [c for c in ex.columns if c.startswith("w") and "__" in c]
ex = ex[keep].copy(); ex["note"] = ex.apply(lambda r: "ciclo di prova" if r.ciclo_prova == 1 else ("ciclo troncato (incompleto)" if r.curva_troncata == 1 else ""), axis=1)
ex.to_csv(f"{OUT}/cicli_autoclave.csv", index=False)
cur = pd.concat([pd.read_csv(f"{D4B}/autoclave_curve_reali.csv.gz"), pd.read_csv(f"{D4B}/autoclave_curve_simulate.csv.gz")])
cur = cur[cur.id_ciclo.isin(ex.id_ciclo)].copy(); cur["T_media"] = cur[["T1", "T2", "T3", "T4"]].mean(axis=1).round(1)
cur["step"] = cur.groupby("id_ciclo").cumcount(); cur = cur[(cur.step % 3 == 0) | (cur.id_ciclo.str.startswith("R"))]
cur[["id_ciclo", "h", "T_media", "T5", "P_mbar"]].round({"h": 3, "P_mbar": 3}).to_csv(f"{OUT}/curve_autoclave.csv.gz", index=False)

# =============== CICLI DI PRESSA ===============
pc = pte.copy(); pc["allarme_mod"] = 0
sel_p = pd.concat([pc[pc.allarme == 1].sample(40, random_state=SEED), pc[(pc.allarme == 0) & (pc.famiglia == "avvolgimento") & (pc.lavorazione == "Caldo")].sample(60, random_state=SEED),
                   pc[(pc.allarme == 0) & (pc.famiglia == "fase")].sample(20, random_state=SEED), pc[(pc.allarme == 0) & (pc.lavorazione == "Freddo")].sample(20, random_state=SEED)]).sort_values("data")
sel_p = sel_p.reset_index(drop=True); sel_p["id"] = ["P%03d" % (i + 1) for i in range(len(sel_p))]
sel_p["data"] = sel_p.data.dt.strftime("%Y-%m-%d")
sel_p.drop(columns=["commessa_anon", "id_ciclo_pressa"]).to_csv(f"{OUT}/cicli_pressa.csv", index=False)

# =============== STATO DEL REPARTO (simulatore, una replica) ===============
sys.path.insert(0, f"{B}/codice/simulatore"); os.chdir(f"{B}/codice/simulatore"); import simulatore as sm
k, rep, lt, Sm = sm.run(0, 60, 8)
w0 = 8 * 168; df = pd.DataFrame(rep.samples, columns=["t", "wip", "q_avv", "q_press", "q_pool"]); df = df[df.t >= w0]; df["giorno"] = ((df.t - w0) // 24).astype(int)
dd = df.groupby("giorno")[["wip", "q_avv", "q_press", "q_pool"]].mean().round(2).reset_index()
car = pd.DataFrame([c for c in rep.carichi if c["t0"] >= w0 + 40 * 168 - 40 * 168 and c["t0"] >= 44 * 168 and c["t0"] < 52 * 168])
gantt = [dict(t0=round((c.t0 - 44 * 168) / 24, 2), dur=round(c.dur / 24, 2), n=int(c.n), kg=int(c.kg)) for c in car.itertuples()]
kb = pd.read_csv(f"{B}/codice/simulatore/kpi_caso_base.csv", index_col=0); sens = pd.read_csv(f"{B}/codice/simulatore/scenari_sensibilita.csv"); val = pd.read_csv(f"{B}/codice/simulatore/validazione_vs_reale.csv")
sc4d = pd.read_csv(f"{D4D}/scenari_sintesi.csv")
reparto = dict(kpi=kb["media"].round(3).to_dict(), ic95=kb["ic95"].round(3).to_dict(), serie=dd.to_dict("list"), gantt=gantt, sensibilita=sens.round(3).to_dict("records"),
               validazione=val.round(3).to_dict("records"), scenari_4d=sc4d.round(4).to_dict("records"))
json.dump(reparto, open(f"{OUT}/reparto.json", "w"))
for f in ["curva_conformita_vs_vuoto.csv", "politica_vuoto_finale.csv"]: pd.read_csv(f"{D4D}/{f}").to_csv(f"{OUT}/{f}", index=False)
print("ok", len(ex), len(sel_p), len(dd), len(gantt), round(thr, 1), round(pthr, 1))
