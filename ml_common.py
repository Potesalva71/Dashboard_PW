"""Passo 4c - funzioni condivise: percorsi, metriche, soglia operativa, stile dei grafici."""
import os, numpy as np, pandas as pd
from sklearn.metrics import (roc_auc_score, average_precision_score, precision_recall_curve,
                             roc_curve, precision_score, recall_score, f1_score, brier_score_loss)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLU, ARANCIO, ACQUA, GRIGIO, INK = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984", "#0b0b0b"
SEED = 42
RECALL_OB1 = 0.80   # soglia di successo OB1 (par. 5.5): richiamo >= 0,80, precisione >= 0,70

def percorsi(base):
    """base = cartella Elaborato_Finale"""
    p = dict(dati4b=os.path.join(base, "dati", "4b"), dati4c=os.path.join(base, "dati", "4c"),
             fig=os.path.join(base, "figure"))
    os.makedirs(p["dati4c"], exist_ok=True); os.makedirs(p["fig"], exist_ok=True)
    return p

def stile():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False,
        "axes.spines.right": False, "axes.edgecolor": "#52514e", "axes.labelcolor": "#0b0b0b",
        "axes.grid": True, "grid.color": "#e6e5e1", "grid.linewidth": 0.6, "figure.dpi": 150,
        "axes.axisbelow": True, "legend.frameon": False})

def soglia_per_richiamo(score_val, y_val, richiamo=RECALL_OB1):
    """Soglia (score >= soglia => allarme) scelta sulla validazione per ottenere il richiamo richiesto."""
    pos = np.asarray(score_val)[np.asarray(y_val) == 1]
    return float(np.quantile(pos, 1 - richiamo)) if len(pos) else float(np.inf)

def metriche_ad(y, s, soglia):
    y = np.asarray(y); s = np.asarray(s); yp = (s >= soglia).astype(int)
    tn = int(((yp == 0) & (y == 0)).sum()); fp = int(((yp == 1) & (y == 0)).sum())
    out = dict(n=len(y), n_pos=int(y.sum()),
               auc_roc=roc_auc_score(y, s) if 0 < y.sum() < len(y) else np.nan,
               auc_pr=average_precision_score(y, s) if y.sum() > 0 else np.nan,
               precisione=precision_score(y, yp, zero_division=0), richiamo=recall_score(y, yp, zero_division=0),
               f1=f1_score(y, yp, zero_division=0), fpr=fp / max(fp + tn, 1))
    out["ob1_ok"] = bool(out["richiamo"] >= 0.80 and out["precisione"] >= 0.70)
    return out

def soglia_f1(score_val, y_val):
    p, r, t = precision_recall_curve(y_val, score_val)
    f = 2 * p * r / np.maximum(p + r, 1e-9)
    return float(t[np.argmax(f[:-1])])
