# Dashboard di monitoraggio del reparto costruzione avvolgimenti (Passo 4e)

Due modi di usarla, con gli stessi modelli e gli stessi dati:

1. **Pagina HTML condivisibile** — aprire `dashboard_condivisibile.html` con un browser. Nessuna installazione; risultati precalcolati.
2. **App Streamlit** (calcolo dal vivo, es. peso e ore di vuoto nella pagina di raccomandazione):

   ```
   pip install -r requirements.txt
   streamlit run app.py
   ```

   `dati_dashboard/` contiene già i dati e `modelli.joblib`. Per rigenerarli dai dati del progetto:
   `python prepara_dati.py <percorso>/Elaborato_Finale` (richiede i risultati dei Passi 4b-4d).
   Per rigenerare la pagina HTML dopo aver cambiato modelli o dati: `python esporta_html.py`.

Sezioni: Stato del reparto · Ciclo di autoclave con allarme · Qualità e probabilità di conformità · Raccomandazione sul vuoto finale · Pressatura e verifica dell'altezza · **Guida alla lettura**.

**Guida alla lettura**: per ogni scheda spiega cosa mostra ogni grafico, come interpretare i risultati (soglie e azioni), con esempio, indicazioni per l'operatore e approfondimento per la commissione. È una sezione dedicata (schermate annotate) e un espansore «Come leggere questa scheda» in testa a ogni scheda; nella pagina HTML è il pulsante «Guida alla lettura» e il link «Come leggere questa scheda →». I testi stanno in `guida.py`; le schermate annotate in `dati_dashboard/guida/` si rigenerano con `python crea_immagini_guida.py <cartella figure>` (richiede Pillow); dopo ogni modifica ai testi rigenerare la pagina con `python esporta_html.py`.

Ogni esempio riporta la provenienza (REALE / SIMULATO). Prototipo di supporto alle decisioni: non comanda alcuna macchina.
