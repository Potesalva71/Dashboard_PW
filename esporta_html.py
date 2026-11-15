"""Passo 4e - esporta i risultati dei modelli in una dashboard HTML autonoma (nessuna installazione).
Uso: python esporta_html.py   -> dashboard_condivisibile.html"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd, joblib
warnings.filterwarnings("ignore")
from scoring import *
import spiega
D = Path(__file__).parent / "dati_dashboard"
M = joblib.load(D / "modelli.joblib")
AC = pd.read_csv(D / "cicli_autoclave.csv"); CUR = pd.read_csv(D / "curve_autoclave.csv.gz"); PR = pd.read_csv(D / "cicli_pressa.csv")
REP = json.load(open(D / "reparto.json")); CP = pd.read_csv(D / "curva_conformita_vs_vuoto.csv"); POL = pd.read_csv(D / "politica_vuoto_finale.csv")
def nn(v): return None if (isinstance(v, float) and np.isnan(v)) else v
def lab(r):
    extra = f" · {r.note}" if isinstance(r.note, str) and r.note else (f" · anomalia: {r.anomalia.replace('_', ' ')}" if isinstance(r.anomalia, str) and r.anomalia != "nessuna" else "")
    return f"{r.id_ciclo} · {'reale' if r.provenienza == 'R' else 'simulato'}{extra}"
auto = []
thr = M["ad"]["soglia_mahal"]
for i in AC.index:
    r = AC.loc[[i]]; x = r.iloc[0]; res = ad_autoclave(M, r); m = float(res["mahal"][0]); al = bool(res["allarme"][0])
    cu = CUR[CUR.id_ciclo == x.id_ciclo].sort_values("h"); step = max(1, len(cu) // 260); cu = cu.iloc[::step]
    Xr = feat_ad(r).fillna(M["ad"]["mediana"])[M["ad"]["colonne"]]
    fa = spiega.frasi_anomalia(res["z"].values[0], M["ad"]["colonne"], Xr.values[0], M["ad"]["mediana"].values)
    q = []
    for fin in FINESTRE:
        h, p = qualita_autoclave(M, r, fin); q.append([("fine ciclo" if fin == "fine" else f"{fin} h"), round(float(h[0]), 2), round(float(p[0]), 3)])
    X, sh, cols = shap_autoclave(M, r)
    fq = spiega.frasi_qualita(cols, X.values[0], sh[0])
    top = pd.Series(sh[0], index=[eti(c)[0] for c in cols]).sort_values(key=abs, ascending=False).head(8)
    auto.append(dict(label=lab(x), prov=x.provenienza, durata=round(float(x.durata_h), 1), mahal=round(m, 1), allarme=al,
        esito=spiega.esito_ad(al, m, thr), perche_ad=fa, q=q, h2o_oss=nn(None if pd.isna(x.h2o_g_h_t) else round(float(x.h2o_g_h_t), 2)),
        troncata=bool(x.curva_troncata == 1), perche_q=fq, shap=[[k, round(float(v), 3)] for k, v in top.items()],
        nota=(x.note if isinstance(x.note, str) else ""), curva=dict(h=[round(float(v), 2) for v in cu.h], T=[round(float(v), 1) for v in cu.T_media], P=[round(float(max(v, .05)), 3) for v in cu.P_mbar])))
pr = []
PRs = PR.assign(_o=(PR.famiglia != "avvolgimento").astype(int)).sort_values(["_o", "id"])
for i in PRs.index:
    r = PRs.loc[[i]]; x = r.iloc[0]; res = pressa(M, r); al = bool(res["allarme"][0]); h = altezza(r).iloc[0]
    fp = spiega.frasi_anomalia(res["z"].values[0], M["pressa"]["colonne_ad"], feat_pressa_ad(r).values[0], M["pressa"]["scaler"].mean_)
    ok = x.famiglia == "avvolgimento" and not np.isnan(h.scarto_mm)
    pr.append(dict(label=f"{x.id} · {x.data} · {x.famiglia} · {str(x.lavorazione).lower()}{' · ALLARME' if x.allarme == 1 else ''}", forza=round(float(x.forza_fine_t), 1), tempo=round(float(x.tempo_ciclo_s), 1),
        dq=round(float(x.delta_quote_mm), 2), allarme_mod=al, mahal=round(float(res["mahal"][0]), 1), soglia=round(float(M["pressa"]["soglia_mahal"]), 1), allarme_mac=bool(x.allarme == 1),
        p=round(float(res["p_conforme"][0]), 3), perche=fp, alt=(round(float(h.altezza_misurata_mm), 0) if ok else None), nom=(round(float(x.altezza_nominale_mm), 0) if ok else None),
        scarto=(round(float(h.scarto_mm), 1) if ok else None), msg=messaggio_altezza(h.scarto_mm)))
classi = {}
for c, g in CP.groupby("classe", sort=False):
    pol = POL[POL.classe == c]
    classi[c] = dict(V=g.V_h.round(2).tolist(), P=g.P_media.round(4).tolist(), lo=g.P_p05.round(4).tolist(), hi=g.P_p95.round(4).tolist(),
        pol={f"{s}|{'c' if cau else 'n'}": float(pol[pol.soglia_P == s][("V_raccomandato_cautelativo_h" if cau else "V_raccomandato_h")].iloc[0]) for s in (0.95, 0.99) for cau in (0, 1)})
sc = pd.DataFrame(REP["scenari_4d"]); sc = sc[sc.arrivi_x == 1.0] if "arrivi_x" in sc else sc
scen = sc[["scenario", "durata_carico_h_media", "lt_medio_gg_media", "ut_autoclave_media", "pool_autoclave_media", "rischio_aggiuntivo_media"]].round(3).values.tolist()
DATA = dict(kpi=REP["kpi"], ic=REP["ic95"], serie=REP["serie"], gantt=REP["gantt"], scen=scen, auto=auto, pr=pr, classi=classi, soglia_ad=round(float(thr), 1))
import base64, guida
def img(n): return "data:image/jpeg;base64," + base64.b64encode((D / "guida" / n).read_bytes()).decode()
GUIDA = dict(intro=guida.INTRO, colori=guida.COLORI, glossario=guida.GLOSSARIO, cautele=guida.CAUTELE,
             sezioni=[dict({k: v for k, v in s.items() if k != "immagine"}, img=img(s["immagine"])) for s in guida.SEZIONI])
tpl = (Path(__file__).parent / "modello_dashboard.html").read_text(encoding="utf-8")
out = tpl.replace("/*__DATA__*/null", json.dumps(DATA, ensure_ascii=False, allow_nan=False))
out = out.replace("/*__GUIDA__*/null", json.dumps(GUIDA, ensure_ascii=False))
(Path(__file__).parent / "dashboard_condivisibile.html").write_text(out, encoding="utf-8"); print("ok", len(out) // 1024, "KB")
