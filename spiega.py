"""Passo 4e - Spiegazioni in italiano per il tecnico di reparto, a partire dai contributi SHAP o dagli scostamenti standardizzati."""
import numpy as np
from scoring import eti, valore

def frasi_qualita(colonne, X_row, shap_row, n=3):
    """Frasi sui contributi SHAP (log dell'acqua estratta): contributo positivo = piu' umidita' residua prevista."""
    idx = np.argsort(-np.abs(shap_row))[:n]; out = []
    for i in idx:
        nome = colonne[i]; lab, u = eti(nome); v = valore(nome, X_row[i]); u = (" " + u) if u else ""
        if shap_row[i] > 0: out.append(f"{lab.capitalize()} = {v}{u}: fa salire l'umidità residua prevista.")
        else: out.append(f"{lab.capitalize()} = {v}{u}: fa scendere l'umidità residua prevista.")
    return out

def frasi_anomalia(z_row, colonne, X_row, mediane, n=3):
    """Variabili che si scostano di piu' dal comportamento dei cicli regolari (z-score sull'insieme di addestramento)."""
    idx = np.argsort(-np.abs(z_row))[:n]; out = []
    for i in idx:
        nome = colonne[i]; lab, u = eti(nome); v = valore(nome, X_row[i]); t = valore(nome, mediane[i]); u = (" " + u) if u else ""
        verso = "più alto" if z_row[i] > 0 else "più basso"
        out.append(f"{lab.capitalize()} = {v}{u}, {verso} del tipico ({t}{u}); scostamento di {abs(z_row[i]):.1f} deviazioni standard.")
    return out

def _p(v): return "oltre 1000" if v > 1000 else f"{v:.1f}"
def esito_ad(allarme, mahal, soglia):
    if allarme: return f"Ciclo SEGNALATO come anomalo (punteggio {_p(mahal)} contro soglia {soglia:.1f})."
    return f"Ciclo nella norma (punteggio {_p(mahal)}, soglia {soglia:.1f})."
