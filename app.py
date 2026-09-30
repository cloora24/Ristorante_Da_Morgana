"""Le cinque pagine e le azioni della Trattoria Da Mario."""

from flask import Flask, abort, redirect, render_template
from mysql.connector import Error

import database

app = Flask(__name__)


# =============================================
# STUDENTE A - pagine 1 e 2
# =============================================

@app.route("/")
def index():
    piatti = database.query_menu()
    return render_template("index.html", piatti=piatti, pagina_attiva="menu")


@app.route("/tavoli")
def tavoli():
    occupati = database.query_tavoli_occupati()
    tutti = database.query_tutti_tavoli()
    # La JOIN contiene solo i tavoli occupati; qui aggiungiamo lo stato alle card.
    id_occupati = [t["id_tavolo"] for t in occupati]
    for t in tutti:
        t["occupato"] = t["id_tavolo"] in id_occupati
    return render_template(
        "pagina2.html", occupati=occupati, tavoli=tutti, pagina_attiva="tavoli"
    )


# =============================================
# STUDENTE B - pagina 3 e azioni del tavolo
# =============================================

@app.route("/tavolo/<int:id_tavolo>")
def tavolo(id_tavolo):
    t = database.query_tavolo(id_tavolo)
    if t is None:
        abort(404)
    ordinazioni = database.query_ordinazioni_tavolo(id_tavolo)
    conto = database.query_totale_tavolo(id_tavolo)
    romana = database.query_conto_alla_romana(id_tavolo, t["posti"])
    piatti = database.query_menu()
    return render_template(
        "pagina3.html", tavolo=t, ordinazioni=ordinazioni,
        totale=conto["totale"], quota=romana["quota"], piatti=piatti,
        pagina_attiva="tavoli",
    )


@app.route("/tavolo/<int:id_tavolo>/aggiungi/<int:id_piatto>")
def tavolo_aggiungi(id_tavolo, id_piatto):
    if database.query_tavolo(id_tavolo) is None:
        abort(404)
    if database.query_piatto(id_piatto) is None:
        abort(404)
    database.aggiungi_ordinazione(id_tavolo, id_piatto)
    return redirect("/tavolo/" + str(id_tavolo))


@app.route("/tavolo/<int:id_tavolo>/chiudi")
def tavolo_chiudi(id_tavolo):
    if database.query_tavolo(id_tavolo) is None:
        abort(404)
    database.chiudi_conto(id_tavolo)
    return redirect("/tavoli")


@app.route("/tavolo/<int:id_tavolo>/riduci/<int:id_ordinazione>")
def tavolo_riduci(id_tavolo, id_ordinazione):
    if database.query_tavolo(id_tavolo) is None:
        abort(404)
    ordinazione = database.query_ordinazione(id_ordinazione)
    if ordinazione is None or ordinazione["id_tavolo"] != id_tavolo:
        abort(404)
    if ordinazione["quantita"] > 1:
        database.riduci_ordinazione(id_tavolo, id_ordinazione)
    else:
        database.elimina_ordinazione(id_tavolo, id_ordinazione)
    return redirect("/tavolo/" + str(id_tavolo))


# =============================================
# STUDENTE C - pagine 4 e 5
# =============================================

@app.route("/cucina")
def cucina():
    ordinazioni = database.query_da_preparare()
    return render_template(
        "pagina4.html", ordinazioni=ordinazioni, pagina_attiva="cucina"
    )


@app.route("/ordinazione/<int:id_ordinazione>/servito")
def ordinazione_servito(id_ordinazione):
    if database.query_ordinazione(id_ordinazione) is None:
        abort(404)
    database.segna_servito(id_ordinazione)
    return redirect("/cucina")


@app.route("/statistiche")
def statistiche():
    numeri = database.query_numeri_serata()
    piatti = database.query_piatti_piu_ordinati()
    conti = database.query_conto_per_tavolo()
    return render_template(
        "pagina5.html", numeri=numeri, piatti=piatti, conti=conti,
        pagina_attiva="statistiche",
    )


# Le pagine di errore usano la base comune, senza aggiungere un sesto template.
@app.errorhandler(404)
def pagina_non_trovata(errore):
    return render_template(
        "base.html", titolo_errore="Pagina non trovata",
        messaggio_errore="Questo tavolo, piatto o ordinazione non esiste.",
        pagina_attiva="",
    ), 404


@app.errorhandler(Error)
def database_non_disponibile(errore):
    # I dettagli tecnici rimangono nel terminale, utili per controllare MySQL.
    app.logger.exception("Impossibile accedere al database ristorante")
    titolo = "Un momento di pausa"
    messaggio = "Il servizio è momentaneamente non disponibile. Riprova tra poco."
    if errore.errno == 1045:
        titolo = "Collegamento a MySQL da completare"
        messaggio = (
            "MySQL rifiuta l'accesso dell'utente studente. "
            "Importa ristorante.sql in MySQL Workbench come root. "
            "Se lo hai già importato, verifica la password e i permessi "
            "dell'utente studente, come spiegato nel README."
        )
    elif errore.errno == 1049:
        titolo = "Il database ristorante non è ancora presente"
        messaggio = "Apri ristorante.sql in MySQL Workbench ed esegui tutto lo script come root."
    elif errore.errno in (2002, 2003):
        titolo = "MySQL non è raggiungibile"
        messaggio = "Avvia il servizio MySQL80 dai Servizi di Windows, poi aggiorna questa pagina."
    return render_template(
        "base.html", titolo_errore=titolo, messaggio_errore=messaggio,
        pagina_attiva="",
    ), 503


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
