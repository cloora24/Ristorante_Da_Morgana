# Trattoria Da Mario

Progetto scolastico Flask + MySQL: menù, gestione dei tavoli, ordinazioni, cucina e statistiche. Comprende i tre bonus della traccia e una grafica Bootstrap 5 adatta a desktop e tablet.

## Gruppo e ripartizione

Sostituire i segnaposto qui e nel footer di `templates/base.html` con i nomi reali.

| Autore | Lavoro previsto dalla traccia |
|---|---|
| Studente A | Menù, tavoli, struttura condivisa e grafica |
| Studente B | Ordinazioni del tavolo, conto e bonus − / conto alla romana |
| Studente C | Cucina e statistiche |

`app.py` e `database.py` sono divisi nelle tre sezioni corrispondenti. Le funzioni condivise sono riutilizzate, ad esempio il menù di A nella pagina di B.

## 1. Importare il database in MySQL Workbench

L'app **non importa né reinizializza automaticamente il database**.

1. Avviare il servizio **MySQL80**.
2. Aprire MySQL Workbench e la connessione **Local instance MySQL80**, come utente `root` con la propria password.
3. Scegliere **File → Open SQL Script…** e aprire `ristorante.sql` nella cartella di questo progetto.
4. Premere il fulmine per eseguire tutto lo script, quindi aggiornare **Schemas**.
5. Controllare il database `ristorante` e le quattro tabelle: `categorie`, `piatti`, `tavoli`, `ordinazioni`.

**Attenzione:** lo script contiene `DROP DATABASE`: rieseguirlo cancella tutte le ordinazioni correnti e ripristina i dati iniziali. Il file incluso è identico a quello fornito nella traccia.

Lo script crea l'utente locale **studente**, password **studente**, usato in `database.py`. La password di root resta in Workbench e non va inserita nel codice o su GitHub. Se l'utente studente esisteva già con un'altra password, `CREATE USER IF NOT EXISTS` non la cambia: dalla connessione root di Workbench impostare la password prevista nella gestione degli utenti (**Administration → Users and Privileges**).

## 2. Installare e avviare

Con Python 3.10 o successivo, aprire PowerShell nella cartella del progetto:

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe app.py
```

L'ambiente virtuale di questo PC è già stato preparato e contiene le dipendenze. L'uso diretto del suo eseguibile evita problemi con l'attivazione degli script PowerShell.

Se `python` non è riconosciuto ma è disponibile il launcher di Windows, usare `py -m venv venv`. Su altri PC creare il proprio ambiente virtuale: la cartella `venv` non si consegna e non si carica su GitHub.

Aprire **http://127.0.0.1:5000**. Fermare il server con **Ctrl+C**. `debug=True` è previsto per lo sviluppo locale dell'esercizio.

Bootstrap 5.3.3 viene caricato dal CDN indicato nella guida: per la grafica completa serve una connessione Internet.

## Le cinque pagine

| URL | Template | Contenuto |
|---|---|---|
| `/` | `index.html` | Menù ordinato per categoria e nome, descrizioni e prezzi |
| `/tavoli` | `pagina2.html` | Tavoli occupati, porzioni, conto e card di tutti i tavoli |
| `/tavolo/4` | `pagina3.html` | Ordinazioni, stato, conto, quota alla romana e menù con + |
| `/cucina` | `pagina4.html` | Ordinazioni in preparazione, dalla più vecchia, con link Servito |
| `/statistiche` | `pagina5.html` | Tre indicatori, piatti più ordinati e conto per tavolo |

Tutti i template estendono `base.html`. La navbar contiene Menù, Tavoli, Cucina e Statistiche; il dettaglio di un tavolo si apre dalla pagina Tavoli.

## Azioni e bonus

- **+**: `/tavolo/<id_tavolo>/aggiungi/<id_piatto>` inserisce una nuova ordinazione di una porzione, anche se lo stesso piatto era già stato ordinato.
- **−**: `/tavolo/<id_tavolo>/riduci/<id_ordinazione>` toglie una porzione da quella riga. Se ne restava una, elimina la riga; funziona anche sulle righe servite.
- **Chiudi conto**: `/tavolo/<id_tavolo>/chiudi` cancella tutte le ordinazioni del tavolo, che torna libero.
- **Servito**: `/ordinazione/<id_ordinazione>/servito` cambia lo stato e torna in cucina.
- **Conto alla romana**: totale diviso per i posti del tavolo, calcolato in SQL e arrotondato a due decimali.
- **Lista dei tavoli occupati**: comprende anche il totale di ogni conto.

Non ci sono form: le azioni sono link GET, come richiesto dall'esercizio. Gli ID errati e le ordinazioni appartenenti a un altro tavolo restituiscono 404 senza modifiche.

Un tavolo è occupato finché ha almeno un'ordinazione, anche se tutte le sue righe sono servite. Le statistiche riguardano solo i conti aperti, non uno storico degli incassi: chiudere il conto ne rimuove i dati. “Piatti in preparazione” conta le **righe di ordinazione** (inizialmente 5), mentre le quantità sono espresse nelle card e nella classifica dei piatti.

## Come è scritto il codice

- `database.py`: solo SQL esplicito, una funzione per query, parametri `%s`, JOIN semplici e nessun ORM. Ogni modifica usa `commit()`; `finally` chiude cursore e connessione anche in caso di errore.
- `app.py`: una funzione per pagina e una per azione; legge i dati e li passa ai template tramite `render_template`.
- `templates/`: solo variabili, attributi, cicli, condizioni, `extends` e `block` della dispensa Jinja2. Nessun filtro o macro aggiuntivo.
- `static/style.css`: personalizzazioni Bootstrap, colori caldi, stati testuali, pulsanti di almeno 44 px e tabelle scorrevoli sugli schermi piccoli.

Per provare alcune query in sola lettura, dopo l'importazione:

```powershell
.\venv\Scripts\python.exe database.py
```

## Verifica e test

Eseguire i test delle rotte e dei template:

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```

I test usano il client Flask e risposte simulate delle funzioni del database: **non si collegano a MySQL e non modificano i conti reali**. Verificano pagine, link, redirect, bonus, stati vuoti, errori e protezione degli ID. Non sostituiscono il collaudo delle query sul server MySQL.

Per controllare i dati reali dopo l'importazione:

```powershell
.\venv\Scripts\python.exe tests\verifica_mysql.py
```

Questo controllo esegue solo SELECT. Va eseguito sui dati iniziali, prima di provare le azioni.

| Prova manuale sui dati iniziali | Risultato |
|---|---|
| Menù | 16 piatti, categorie Antipasti → Primi → Secondi → Dolci → Bevande |
| Tavoli | 8 card; occupati 2, 4, 5 con 6, 8, 4 porzioni |
| Tavolo 2 / tavolo 4 | € 42.50 / € 112.00 |
| Tavolo libero, ad esempio 1 | Messaggio di tavolo libero, totale e quota € 0.00 |
| Statistiche | 3 tavoli, 5 ordinazioni in preparazione, € 190.50; Spaghetti alle vongole primi |
| + Caffè al tavolo 4 | Nuova riga, totale € 113.50 |
| − sulla nuova riga Caffè | Riga eliminata, totale € 112.00 |
| − su Spaghetti al tavolo 4 | Da 3 a 2 porzioni; totale € 98.00, quota € 16.33 |
| Servito su una card in cucina | La card sparisce; la riga del conto è verde e il totale non cambia |
| Chiudi conto tavolo 5 | Il tavolo sparisce dagli occupati e il suo conto è vuoto |
| `/tavolo/999` o riduzione di una riga di un altro tavolo | 404, nessun dato modificato |

Le prove manuali di modifica cambiano i conti: per ripartire dai dati iniziali reimportare consapevolmente il file SQL in Workbench.

## GitHub e consegna

Repository del progetto: [Ristorante_Da_Morgana](https://github.com/cloora24/Ristorante_Da_Morgana).

Il caricamento iniziale contiene il progetto completo. La ripartizione A/B/C rimane un modello da compilare con i nomi reali; gli studenti devono conservare una cronologia reale del proprio lavoro. Il capogruppo invita gli altri due studenti come collaboratori nella repository.

Il capogruppo prepara la struttura condivisa su `main` come indicato nella guida. Poi ciascuno crea il proprio branch (`studente-a`, `studente-b`, `studente-c`) e lavora nella propria sezione. Esempio per B, dopo aver clonato il repository:

```powershell
git checkout -b studente-b
git add .
git commit -m "Aggiunta gestione del tavolo e conto"
git push -u origin studente-b
```

Aprire una pull request verso `main`, farla revisionare da un compagno e unire il lavoro. Aggiornare il proprio branch dopo ogni merge:

```powershell
git checkout main
git pull
git checkout studente-b
git merge main
```

Usare commit chiari e frequenti, mantenere una cronologia reale del lavoro, compilare i nomi e consegnare il link GitHub. Non caricare `venv/` o `__pycache__/`.

## Problemi frequenti

| Problema | Controllo |
|---|---|
| Pagina di errore MySQL (503) | Seguire le indicazioni mostrate: accesso rifiutato, database assente o servizio spento; per gli altri errori leggere il terminale |
| `Access denied for user 'studente'` | Importare il file SQL come root; controllare password e permessi dell'utente locale studente |
| `Unknown database 'ristorante'` | Il file SQL non è stato eseguito completamente |
| `Can't connect to MySQL server` | Avviare MySQL80 dai Servizi di Windows |
| `python` non riconosciuto | Usare `py` per creare venv, oppure avviare l'eseguibile Python installato |
| `ModuleNotFoundError` | Installare requirements usando lo stesso Python dell'ambiente virtuale |
| Pagina senza stile Bootstrap | Verificare l'accesso Internet al CDN |
| Porta 5000 occupata | Chiudere l'altro server Flask avviato sul PC |
