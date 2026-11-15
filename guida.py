"""Guida alla lettura della dashboard: contenuti condivisi da app Streamlit (app.py) e pagina HTML (esporta_html.py).
Ogni scheda ha: cosa mostra (elementi numerati come nella schermata annotata), come leggere i risultati (indicatore / significato / cosa fare),
un esempio di lettura, indicazioni per l'operatore, approfondimento per la commissione e limiti. I numeri citati negli esempi provengono dalle schermate
fig_4e_* (caso base del simulatore, ciclo R01, ciclo simulato S0252, ciclo di pressa P008)."""

INTRO = ("Questa guida spiega, scheda per scheda, che cosa mostra ciascun grafico e come interpretarne i risultati. "
         "Ogni scheda ha una schermata annotata (i numeri nei cerchi corrispondono all'elenco «Cosa mostra»), una tabella di lettura "
         "con le soglie e le azioni suggerite, un esempio e i limiti da tenere presenti. "
         "Il blocco «Per l'operatore» dice cosa guardare e cosa fare; il blocco «Per la commissione» spiega che cosa dimostra la scheda e con quale metodo.")

COLORI = [
    ("Etichetta verde «REALE»", "Il dato proviene da misure reali anonimizzate (autoclave, registro dei trattamenti, pressa)."),
    ("Etichetta arancio «SIMULATO»", "Il dato proviene dal simulatore o dal sensore virtuale: serve a completare i dati mancanti e a confrontare scenari. Non è una misura di reparto."),
    ("Riquadro verde", "Esito favorevole (ciclo regolare, probabilità di conformità ≥ 95%)."),
    ("Riquadro giallo", "Cautela (probabilità di conformità tra 80% e 95%, curva incompleta, avvisi sui dati)."),
    ("Riquadro rosso", "Attenzione (ciclo segnalato come anomalo, probabilità di conformità < 80%)."),
    ("Riquadro blu", "Informazione o suggerimento, senza giudizio di conformità."),
]

GLOSSARIO = [
    ("WIP (Work In Progress)", "Numero di unità (avvolgimenti o fasi assemblate) in lavorazione in un dato momento."),
    ("Tempo di attraversamento", "Giorni che un'unità impiega dall'ingresso in reparto al rilascio. «p90» = 9 unità su 10 sono completate entro quel valore."),
    ("Utilizzo", "Percentuale di tempo in cui una risorsa (avvolgitrici, pressa, autoclave) è occupata."),
    ("Collo di bottiglia", "La risorsa più satura: è quella che determina quanto produce il reparto e dove si formano le code."),
    ("Vuoto finale", "Fase conclusiva del ciclo di essiccazione in autoclave in cui si mantiene il vuoto spinto per estrarre l'acqua residua."),
    ("Acqua estratta (g/h/t)", "Grammi di acqua estratta per ora e per tonnellata di carico, indicatore di umidità residua. Il limite usato nella dashboard è 10 g/h/t: sotto il limite l'essiccazione è conforme."),
    ("Punteggio di anomalia", "Distanza di Mahalanobis del ciclo dai cicli «tipici»: misura quanto il ciclo si scosta tenendo conto delle relazioni tra le variabili. Più è alto, più il ciclo è insolito. Si confronta con una soglia."),
    ("Soglia di allarme", "Valore del punteggio oltre il quale il ciclo è segnalato: 72,5 per l'autoclave, 40,8 per la pressa. È stata scelta sul set di validazione in modo da individuare circa l'80% dei cicli anomali (richiamo 0,80), accettando qualche falso allarme."),
    ("SHAP", "Metodo che attribuisce a ogni variabile il suo contributo alla previsione: una barra arancio spinge verso più umidità residua, una blu verso meno."),
    ("Intervallo al 90%", "Fascia entro cui cade la probabilità stimata nel 90% delle ricostruzioni statistiche (bootstrap): più è larga, più la stima è incerta."),
    ("pp (punti percentuali)", "Differenza tra due percentuali: da 98% a 95% sono −3 pp."),
    ("Finestra osservata", "Ore di ciclo già trascorse (24, 48, 72 h) o ciclo completo («fine ciclo») su cui si basa la previsione di qualità."),
]

SEZIONI = [
 dict(
  id="stato", titolo="Stato del reparto", immagine="g1_stato.jpg",
  scopo="Fotografia del reparto simulato a regime (60 settimane di simulazione, caso base): quanto produce, quanto tempo impiega un'unità ad attraversarlo e dove si accumulano le code. "
        "Non è lo stato in tempo reale del reparto: serve a capire dove intervenire e a confrontare scenari.",
  elementi=[
   ("Indicatori in alto", "Unità rilasciate a settimana (con ± = intervallo di confidenza al 95%), tempo di attraversamento medio e p90, unità in lavorazione (WIP), utilizzo dell'autoclave e utilizzo di avvolgitrici e pressa."),
   ("Utilizzo dell'autoclave", "L'etichetta «collo di bottiglia» indica la risorsa più satura del reparto."),
   ("Grafico «WIP e code»", "Andamento giornaliero delle unità in lavorazione (blu), della coda in attesa di autoclave (arancio) e della coda alle avvolgitrici (verde)."),
   ("Grafico «Carichi in autoclave»", "Ogni blocco è un carico: la larghezza è la durata, la sigla «Nu» il numero di unità caricate. Con una sola autoclave i blocchi non si sovrappongono."),
   ("Tabella degli scenari", "Confronto tra durata del vuoto finale attuale (caso base) e due politiche di riduzione: durata del carico, tempo di attraversamento, utilizzo e coda dell'autoclave, rischio aggiuntivo di non conformità."),
  ],
  lettura=[
   ("Utilizzo risorse", "Quota di tempo occupato. Nel caso base: autoclave 86%, avvolgitrici 83%, pressa 41%.", "Una risorsa molto satura (oltre l'80-85%, regola pratica) genera code: è lì che l'ottimizzazione rende. La pressa, al 41%, ha capacità libera."),
   ("Tempo di attraversamento", "Nel caso base 15,9 giorni in media, 26 giorni il p90 (9 unità su 10 entro 26 giorni).", "Un p90 molto più alto della media indica code irregolari: guardare il grafico delle code."),
   ("Coda arancio (attesa autoclave)", "I picchi sono momenti in cui più unità attendono un carico completo.", "Picchi frequenti e alti = l'autoclave non smaltisce il flusso: valutare di accorciare i cicli (v. «Raccomandazione sul vuoto finale»)."),
   ("Blocchi in autoclave", "Blocchi quasi contigui = autoclave sempre occupata; più unità per carico = migliore saturazione.", "Spazi vuoti larghi indicherebbero capacità inutilizzata; blocchi molto lunghi, cicli più lunghi della media."),
   ("Tabella scenari", "Nel caso base il carico dura 97,9 h; con la politica P ≥ 0,95 scende a 82,4 h (attraversamento 15,1 gg, utilizzo autoclave 80,6%) con circa +2 pp di rischio aggiuntivo di non conformità; con la politica cautelativa 87,6 h e +0,4 pp.", "Leggere insieme il guadagno (ore, attraversamento, coda) e il costo (pp di rischio). Il numero di unità rilasciate a settimana non cambia (lo limita la domanda, non la capacità): il guadagno è in attese e code. La scelta dipende dal rischio accettabile."),
  ],
  esempio="Con l'autoclave all'86% e la pressa al 41%, accelerare l'avvolgitura o la pressatura non accorcia l'attraversamento: l'attesa si forma davanti all'autoclave. "
          "Una riduzione delle ore di vuoto finale, invece, agisce direttamente sul collo di bottiglia: nello scenario P ≥ 0,95 la coda per l'autoclave passa da 2,93 a 2,64 unità e l'attraversamento da 15,9 a 15,1 giorni.",
  operatore=["Usare la scheda per capire dove si accumula il lavoro, non per controllare lo stato di oggi: i dati sono simulati.",
             "Se si propone di cambiare un tempo di ciclo, guardare prima se la risorsa interessata è il collo di bottiglia (autoclave): altrimenti il beneficio sul flusso è modesto."],
  commissione=["Dimostra l'obiettivo OB4 (flusso e code) con il Digital Twin descrittivo: simulatore a eventi discreti (SimPy) di avvolgitura → serraggio a freddo → autoclave → pressa a caldo, calibrato su registro dei trattamenti, dati di pressa e ore di commessa (Capitoli 5-6).",
               "I KPI sono medie su 30 repliche; gli scenari su 100 repliche appaiate con intervalli di confidenza al 95% (Capitolo 7). I confronti tra scenari vanno letti sulle differenze appaiate, non sui singoli valori.",
               "Con arrivi +20% il caso base peggiora (attraversamento medio da 15,9 a 24,9 giorni) e il beneficio della politica sul tempo di attraversamento non è più significativo: resta quello su utilizzo e coda dell'autoclave."],
  limiti=["Dati simulati: nessun valore rappresenta una misura di reparto.",
          "Ipotesi di scenario (ad esempio una persona per postazione per turno) dichiarate nel Capitolo 5.",
          "Il «rischio aggiuntivo» deriva dal modello sul registro (49 carichi reali): è una stima, non un'osservazione."],
 ),
 dict(
  id="autoclave", titolo="Ciclo di autoclave con allarme", immagine="g2_autoclave.jpg",
  scopo="Mostra le curve di temperatura e pressione di un singolo ciclo di essiccazione e dice se il ciclo si discosta dal comportamento dei cicli regolari (anomaly detection), indicando le tre variabili che pesano di più.",
  elementi=[
   ("Selettore del ciclo", "Elenco di 59 cicli (9 reali R01-R09 e 50 simulati). L'etichetta riporta la provenienza e, per i simulati, l'anomalia nota inserita nel sensore virtuale."),
   ("Etichetta di provenienza", "REALE o SIMULATO."),
   ("Grafico «Temperatura media delle sonde»", "Media delle cinque sonde nel tempo (ore dall'avvio): rampa di riscaldamento, plateau, raffreddamento finale."),
   ("Grafico «Pressione» (scala logaritmica)", "1000 mbar è la pressione ambiente; ogni «valle» è una fase di vuoto. Più il valore scende, più il vuoto è spinto."),
   ("Indicatori", "Durata del ciclo, punteggio di anomalia con la soglia (72,5) e segnalazione ANOMALO/regolare."),
   ("Riquadro di esito", "Rosso se il punteggio supera la soglia, verde altrimenti."),
   ("«Perché»", "Le tre variabili che più si scostano dai cicli regolari, con valore del ciclo, valore tipico e scostamento in deviazioni standard."),
  ],
  lettura=[
   ("Temperatura", "Rampa iniziale fino a circa 100 °C, plateau con piccole oscillazioni, calo finale quando il ciclo si conclude.", "Rampa lenta, plateau più basso del solito o oscillazioni ampie sono segnali di un riscaldamento non regolare."),
   ("Pressione", "Nel grafico, valli profonde (verso 1 mbar) separate da risalite a pressione ambiente.", "Una valle che non scende quanto le altre, si interrompe o risale prima del tempo indica una possibile perdita di vuoto: verificare la tenuta."),
   ("Punteggio di anomalia", "Confronto con la soglia 72,5. Sotto soglia: ciclo nella norma. Poco sopra: caso limite. Molto sopra o «> 1000»: ciclo molto lontano dalla norma.", "Caso limite: controllare le tre cause indicate. Anomalia netta: fermarsi a verificare prima di considerare buono il ciclo."),
   ("«Perché»", "Ogni frase riporta variabile, valore, valore tipico e scostamento (in deviazioni standard). Più è alto lo scostamento, più la variabile spiega l'allarme.", "Partire dalla variabile con lo scostamento maggiore e confrontarla con le curve sopra."),
  ],
  esempio="Ciclo S0252 (simulato, anomalia «perdita di vuoto»): punteggio 73,1 contro soglia 72,5, quindi ANOMALO ma vicino alla soglia. "
          "Nel grafico della pressione l'ultima fase di vuoto non resta al minimo come le precedenti ma si interrompe e risale: è il segnale che il modello ha colto. "
          "Per i 9 cicli reali, invece, l'allarme scatta sempre (il modello è addestrato su cicli simulati): l'app lo segnala con un avviso giallo e in quel caso conta il punteggio relativo, cioè quale ciclo reale è più lontano dagli altri.",
  operatore=["Con un ciclo segnalato, aprire le curve e controllare la variabile indicata in «Perché» (ad esempio pressione che risale = tenuta del vuoto).",
             "Un allarme non dice che il carico è da scartare: dice che il ciclo merita un controllo. La conferma sull'essiccazione si ha dalla scheda «Qualità e probabilità di conformità».",
             "Sui cicli reali ignorare l'etichetta ANOMALO e confrontare i punteggi tra loro."],
  commissione=["Dimostra l'obiettivo OB1 (anomaly detection, soglie di successo: richiamo ≥ 0,80 e precisione ≥ 0,70): distanza di Mahalanobis su 28 caratteristiche di curva (24 di base + 4 fisiche aggiuntive), soglia scelta sulla validazione per richiamo 0,80 (Capitoli 6-7). Sul test simulato il richiamo è 0,79 con precisione 0,94 e 1,2% di falsi allarmi: OB1 è quasi soddisfatto.",
               "Il modello è addestrato sui cicli simulati regolari del dataset (609 cicli: 9 reali + 600 simulati con anomalie etichettate); il sensore virtuale è stato calibrato sui 9 cicli reali.",
               "Il confronto con altri rivelatori (Isolation Forest, One-Class SVM) e il richiamo per tipo di anomalia sono nel Capitolo 7: guasto di sonda, interruzione e blackout con riavvio sono riconosciuti sempre, la perdita di vuoto solo nel 40% dei casi."],
  limiti=["Scarto simulato-reale: tutti i 9 cicli reali risultano «anomali». È un limite dichiarato, non un difetto di quel ciclo.",
          "Le anomalie dei cicli simulati sono quelle inserite nel generatore: il richiamo misura il riconoscimento di anomalie note, non di guasti inattesi.",
          "R08 è una curva troncata e R06 un ciclo di prova."],
 ),
 dict(
  id="qualita", titolo="Qualità e probabilità di conformità", immagine="g3_qualita.jpg",
  scopo="Prevede quanta acqua sarà estratta (indice di umidità residua) e con quale probabilità l'essiccazione sarà conforme, usando solo le ore di ciclo già disponibili. Serve come allerta precoce.",
  elementi=[
   ("Selettore del ciclo", "Stessi 59 cicli della scheda precedente."),
   ("Grafico «Acqua estratta prevista (g/h/t)»", "Previsione a 24, 48, 72 h e a fine ciclo. La linea tratteggiata nera è il limite di 10 g/h/t; la linea arancio è il valore osservato nel registro, quando disponibile."),
   ("Grafico «Probabilità di essiccazione conforme»", "Una barra per finestra osservata (grigie: previsioni anticipate; blu: a fine ciclo). La linea tratteggiata è la soglia di 0,95."),
   ("Riquadro di sintesi", "Valore a fine ciclo: acqua estratta prevista e probabilità di conformità. Verde se ≥ 95%, giallo tra 80% e 95%, rosso sotto 80%."),
   ("«Perché»", "Le tre variabili con il contributo maggiore alla previsione a fine ciclo, in frasi."),
   ("Grafico dei contributi SHAP", "Le otto variabili principali: barre arancio = più umidità residua, barre blu = meno."),
  ],
  lettura=[
   ("Acqua estratta prevista", "Sotto 10 g/h/t = essiccazione conforme; sopra = umidità residua oltre il limite.", "Una previsione vicina al limite (± 2 g/h/t) va letta insieme alla probabilità, non da sola."),
   ("Probabilità di conformità", "Verde ≥ 95%, giallo 80-95%, rosso < 80%.", "Rosso a fine ciclo: valutare un vuoto finale più lungo o una verifica dell'umidità prima del montaggio."),
   ("Finestre 24/48/72 h", "Più ore di ciclo si osservano, più la previsione è affidabile. A 24 h è poco informativa.", "Per decidere se prolungare il vuoto finale è più sensato guardare le finestre di 48-72 h che quella di 24 h."),
   ("Osservata vs prevista", "La linea arancio è il valore misurato nel registro, dove esiste.", "Se prevista e osservata sono entrambe oltre il limite il modello ha colto il caso; una forte distanza indica che il caso è fuori dai dati noti."),
   ("SHAP", "Le variabili in cima spiegano la previsione. Il segno è l'effetto sulla previsione, non una relazione causale.", "Usarle per capire su cosa si può agire (ad esempio la durata del vuoto finale), non come prova di una causa."),
  ],
  esempio="Ciclo R01 (reale): acqua estratta prevista a fine ciclo 11,2 g/h/t contro un osservato di 12,8 (entrambi sopra il limite di 10), probabilità di conformità 40%, quindi riquadro rosso. "
          "Le tre variabili principali sono pressione minima del vuoto finale (0,52 mbar), peso del carico (1407 kg) e durata del vuoto finale (11 h): tutte spingono verso più umidità residua. "
          "Il carico è leggero (< 1.900 kg) e il vuoto finale di 11 h è inferiore alle 11,5 h che la scheda «Raccomandazione sul vuoto finale» indica come minimo per la politica P ≥ 0,95.",
  operatore=["Guardare la probabilità a 48-72 h: se è già in rosso, è il momento di valutare un vuoto finale più lungo.",
             "Un ciclo con l'avviso «curva troncata» non ha previsione a fine ciclo significativa: ignorare il riquadro di sintesi.",
             "Una previsione verde non sostituisce la misura dell'umidità, quando è prevista dalla procedura."],
  commissione=["Dimostra l'obiettivo OB2 (predizione della qualità; soglia: errore sull'acqua estratta inferiore di almeno il 20% a quello di un predittore costante): modelli di regressione per l'acqua estratta e classificazione della non conformità su finestre iniziali di 0, 24, 48, 72 h e fine ciclo (Capitoli 6-7).",
               "Sul registro reale i carichi sono 49 (di cui 1 non conforme): le prestazioni sui dati simulati sono ottimistiche per costruzione, perché l'acqua estratta simulata deriva dal registro reale (circolarità).",
               "SHAP è usato per l'interpretabilità richiesta dal caso d'uso di supporto alla decisione."],
  limiti=["Le prestazioni sui cicli simulati sono ottimistiche per costruzione.",
          "A 24 h la previsione è poco informativa.",
          "Previsione statistica, non misura: nessun esito della dashboard sostituisce il controllo di qualità."],
 ),
 dict(
  id="vuoto", titolo="Raccomandazione sul vuoto finale", immagine="g4_vuoto.jpg",
  scopo="Dati il peso del carico e le ore di vuoto finale previste, mostra quante ore si potrebbero risparmiare mantenendo una probabilità di conformità accettabile. È un supporto alla decisione, non un comando.",
  elementi=[
   ("Campi di ingresso", "Peso del carico (kg), ore di vuoto finale previste e politica: «P ≥ 0,95», «P ≥ 0,99» o «Cautelativa (intervallo al 90%)». Cambiano i risultati in tempo reale."),
   ("Indicatori", "Classe di peso (leggero < 1.900 kg, medio 1.900-4.500 kg, pesante > 4.500 kg), durata minima suggerita, ore risparmiate, probabilità di conformità e sua variazione rispetto alla durata attuale."),
   ("Curva blu", "Probabilità che l'acqua estratta sia sotto 10 g/h/t in funzione delle ore di vuoto finale, per la classe di peso scelta."),
   ("Banda azzurra", "Intervallo al 90% della curva: l'incertezza della stima."),
   ("Punto arancio e triangolo verde", "Arancio: durata attuale. Verde: durata suggerita dalla politica."),
   ("Linea tratteggiata a 0,95", "Soglia di probabilità della politica P ≥ 0,95."),
   ("Riquadro blu", "Frase di sintesi: ore risparmiate e probabilità prima e dopo."),
  ],
  lettura=[
   ("Durata minima suggerita", "Ore minime per cui la probabilità di conformità raggiunge la soglia scelta. Mai meno di 3 h; l'app non propone mai di allungare.", "Se coincide con la durata attuale o è più bassa, non c'è riduzione proponibile."),
   ("Ore risparmiate", "Differenza tra durata attuale e suggerita.", "Sono ore di autoclave liberate: contano soprattutto perché l'autoclave è il collo di bottiglia."),
   ("Probabilità e variazione in pp", "Ad esempio passare da 98% a 95% significa −3 pp.", "Accettare la riduzione dipende dal rischio che si è disposti a correre."),
   ("Banda azzurra", "Più è larga, più la stima è incerta (pochi carichi osservati).", "Dove la banda è larga preferire la politica cautelativa."),
   ("Politiche", "P ≥ 0,95 e P ≥ 0,99 usano la curva media; la cautelativa usa il limite inferiore dell'intervallo al 90% e quindi dà durate più lunghe.", "Ordine di prudenza: P ≥ 0,95 < cautelativa < P ≥ 0,99."),
   ("Forma della curva", "La curva sale rapidamente nelle prime ore e poi si appiattisce.", "Oltre il tratto piatto le ore aggiuntive di vuoto aumentano poco la probabilità."),
  ],
  esempio="Carico medio di 3.000 kg con 18 h di vuoto finale previste e politica P ≥ 0,95: durata suggerita 11 h, 7 h risparmiate, probabilità di conformità da 98% a 95% (−3 pp). "
          "Con la politica cautelativa la durata suggerita sale a 22,5 h, più delle 18 h previste: in quel caso non si propone alcuna riduzione.",
  operatore=["Inserire il peso reale e le ore previste dal programma, scegliere la politica e leggere il suggerimento come base di discussione con il responsabile di processo.",
             "Non modificare le ricette in automatico: la raccomandazione è una correlazione osservata e va validata in reparto.",
             "Con carichi pesanti o con banda molto larga, tenere la politica più prudente."],
  commissione=["Dimostra l'obiettivo OB3 (durata minima del ciclo che mantiene la probabilità di conformità sopra una soglia): surrogato log-lineare dell'acqua estratta sul registro reale (49 carichi) con pressione finale come mediatore e bootstrap per l'intervallo; validazione leave-one-out (Capitolo 7).",
               "L'effetto sul reparto si legge nella scheda «Stato del reparto» (scenari) con simulatore a 100 repliche appaiate.",
               "Politica per classi di peso (terzili del registro) ricavata dal surrogato."],
  limiti=["Solo 49 carichi reali, di cui 1 non conforme: le probabilità vicine a 1 hanno poca evidenza empirica.",
          "Correlazione osservata, non causalità: da validare in reparto prima di qualunque modifica di ricetta.",
          "Nessun controllo automatico delle macchine."],
 ),
 dict(
  id="pressa", titolo="Pressatura e verifica dell'altezza", immagine="g5_pressa.jpg",
  scopo="Per un ciclo di pressatura (dati reali) segnala se il ciclo è anomalo rispetto ai cicli regolari, stima la probabilità di conformità e, per gli avvolgimenti singoli, confronta l'altezza ottenuta con quella nominale.",
  elementi=[
   ("Selettore del ciclo", "140 cicli di test (92 avvolgimenti e 48 fasi assemblate) con ID anonimi (P001…), data, famiglia, lavorazione (freddo/caldo) e la dicitura «ALLARME» se la macchina lo ha registrato."),
   ("Indicatori", "Forza di fine pressata (t), tempo di ciclo (s), differenza tra le quote (mm), segnalazione del modello e probabilità di conformità."),
   ("Riquadro di esito", "Punteggio di anomalia contro la soglia (40,8) e allarme registrato dalla macchina (sì/no)."),
   ("Altezza misurata e nominale", "Altezza calcolata dal ciclo (ipotesi di calcolo) e altezza nominale, con la differenza in mm."),
   ("Barra «Scarto dal nominale»", "Arancio verso sinistra: avvolgimento più basso del nominale. Blu verso destra: più alto."),
   ("Riquadro blu", "Messaggio sullo scarto: indica di consultare produzione e ufficio tecnico."),
   ("«Perché»", "Le tre variabili che più si scostano dai cicli regolari."),
  ],
  lettura=[
   ("Modello vs allarme della macchina", "Quattro combinazioni: nessuno dei due segnala = ciclo regolare; solo il modello = possibile segnale precoce; solo la macchina = allarme che il modello non conferma; entrambi = anomalia confermata.", "Il caso «solo il modello» è quello che aggiunge valore: verificare il ciclo anche se la macchina non ha allarmato."),
   ("Punteggio e soglia", "Soglia 40,8: sotto = nella norma, sopra = anomalo.", "Come per l'autoclave, valori molto sopra la soglia indicano un ciclo lontano dal comportamento abituale."),
   ("Probabilità di conformità", "Ciclo conforme = nessun allarme della macchina e differenza tra le quote non superiore a 2 mm. La stima usa le variabili di fine ciclo (tempo di assestamento della terza fase, tempo di ciclo, forza finale).", "Valori bassi con ciclo regolare vanno approfonditi con forza e tempo di ciclo. Prima del ciclo (solo ricetta e anagrafica) la previsione non ha capacità predittiva."),
   ("Scarto dall'altezza nominale", "Altezza = quota di fine pressata − spessore piastra base − spessore distanziale (ipotesi di lavoro). Si riportano solo scarto e segno.", "Nessuna tolleranza è fissata: lo scarto va discusso con produzione e ufficio tecnico, che valutano se servono compensazioni."),
   ("Avvolgimenti e fasi", "La verifica dell'altezza vale solo per gli avvolgimenti singoli; le fasi assemblate sono escluse.", "Per le fasi usare solo la parte di anomalia e conformità."),
  ],
  esempio="Ciclo P008 (reale, avvolgimento, pressatura a freddo): forza 58 t, tempo di ciclo 60 s, differenza tra le quote 1,11 mm, punteggio 15,1 contro soglia 40,8, quindi ciclo regolare, nessun allarme della macchina e probabilità di conformità 98%. "
          "Eppure l'altezza calcolata è 2115 mm contro 2148 nominali (−33 mm): un ciclo regolare per la macchina può comunque produrre un avvolgimento più basso del previsto. "
          "Le due verifiche sono indipendenti e vanno lette insieme.",
  operatore=["Usare il confronto tra segnale del modello e allarme macchina per decidere se controllare un ciclo che la macchina non ha segnalato.",
             "Con uno scarto di altezza, riportare il valore e il segno a produzione e ufficio tecnico; la dashboard non indica compensazioni numeriche.",
             "Il tempo di ciclo molto più breve del tipico, come in P008 (4,11 in scala logaritmica contro 5,62), è spiegato nel «Perché»: confrontarlo con la procedura."],
  commissione=["Dimostra OB1 e OB2 su dati reali di pressa (3.427 cicli di circa 6 anni, split temporale prima/dopo il 2025, Capitolo 7): anomaly detection semi-supervisionata (addestrata sui soli cicli regolari; sul test Mahalanobis ha precisione 0,997 e richiamo 0,80) e predizione della conformità (Random Forest e XGBoost AUC 0,89 a fine ciclo, contro la soglia OB2 di 0,80), con SHAP.",
               "Sono mostrati i cicli del set di test, quindi non usati per l'addestramento.",
               "Gli allarmi della pressa sono cicli interrotti (tempo di ciclo e forza finale molto bassi): il modello li riconosce a ciclo concluso, non li anticipa.",
               "La verifica dell'altezza è un esempio di Digital Twin descrittivo basato sulle quote registrate dalla pressa."],
  limiti=["La formula dell'altezza è un'ipotesi di lavoro e nessuna tolleranza è fissata.",
          "I messaggi rinviano a produzione e ufficio tecnico: non sono indicate compensazioni.",
          "Dati reali anonimizzati: nessun nome di azienda, stabilimento o commessa."],
 ),
]

CAUTELE = [
    "La dashboard non comanda alcuna macchina: ogni indicazione è un supporto alla decisione da validare in reparto.",
    "Distinguere sempre REALE e SIMULATO: le prestazioni sui dati simulati sono ottimistiche per costruzione.",
    "Un allarme non è un guasto e una previsione non è una misura: servono sempre il giudizio dell'operatore e i controlli previsti dalla procedura.",
    "La pagina HTML condivisibile contiene risultati precalcolati dei modelli (i cicli sono quelli dell'elenco); l'app Streamlit esegue gli stessi modelli dal vivo.",
]


def md_sezione(s, livello="completa"):
    """Markdown di una scheda. livello: 'breve' (per l'espansore dentro la scheda) o 'completa'."""
    out = [f"**Scopo.** {s['scopo']}", "", "**Cosa mostra**"]
    out += [f"{i}. **{t}.** {d}" for i, (t, d) in enumerate(s["elementi"], 1)]
    out += ["", "**Come leggere i risultati**", "", "| Indicatore | Significato | Cosa fare |", "|---|---|---|"]
    out += [f"| {a} | {b} | {c} |" for a, b, c in s["lettura"]]
    if livello == "breve": return "\n".join(out)
    out += ["", f"**Esempio di lettura.** {s['esempio']}", "", "**Per l'operatore**"] + [f"- {x}" for x in s["operatore"]]
    return "\n".join(out)

def md_commissione(s):
    return "\n".join(["**Per la commissione**"] + [f"- {x}" for x in s["commissione"]] + ["", "**Limiti da tenere presenti**"] + [f"- {x}" for x in s["limiti"]])
