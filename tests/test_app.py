"""Test delle rotte reali Flask con risposte database simulate."""

from decimal import Decimal
import unittest
from unittest.mock import patch

from mysql.connector import Error

import app as sito
import database
from fixtures import dati_iniziali


class TestPagineEAzioni(unittest.TestCase):
    def setUp(self):
        sito.app.config["TESTING"] = True
        self.client = sito.app.test_client()
        self.dati = dati_iniziali()
        self.query = {}
        # Ogni funzione del database viene intercettata: mai accesso ai conti reali.
        for nome in dir(database):
            if nome.startswith("query_") or nome in (
                "aggiungi_ordinazione", "chiudi_conto", "riduci_ordinazione",
                "elimina_ordinazione", "segna_servito",
            ):
                p = patch.object(database, nome)
                self.query[nome] = p.start()
                self.addCleanup(p.stop)
        self.query["query_menu"].return_value = self.dati["menu"]
        self.query["query_tavoli_occupati"].return_value = self.dati["occupati"]
        self.query["query_tutti_tavoli"].return_value = self.dati["tavoli"]
        self.query["query_tavolo"].side_effect = lambda i: next((t for t in self.dati["tavoli"] if t["id_tavolo"] == i), None)
        self.query["query_piatto"].side_effect = lambda i: next((p for p in self.dati["menu"] if p["id_piatto"] == i), None)
        self.query["query_ordinazione"].side_effect = lambda i: next((o for o in self.dati["ordinazioni"] if o["id_ordinazione"] == i), None)
        self.query["query_ordinazioni_tavolo"].side_effect = lambda i: [o for o in self.dati["ordinazioni"] if o["id_tavolo"] == i]
        self.query["query_totale_tavolo"].return_value = {"totale": Decimal("112.00")}
        self.query["query_conto_alla_romana"].return_value = {"quota": Decimal("18.67")}
        self.query["query_da_preparare"].return_value = self.dati["cucina"]
        self.query["query_numeri_serata"].return_value = self.dati["numeri"]
        self.query["query_piatti_piu_ordinati"].return_value = self.dati["classifica"]
        self.query["query_conto_per_tavolo"].return_value = self.dati["occupati"]

    def leggi_html(self, url):
        risposta = self.client.get(url)
        self.assertEqual(risposta.status_code, 200)
        return risposta.get_data(as_text=True)

    def assert_nessuna_modifica(self):
        for nome in ("aggiungi_ordinazione", "chiudi_conto", "riduci_ordinazione", "elimina_ordinazione", "segna_servito"):
            self.query[nome].assert_not_called()

    def test_cinque_pagine_e_navigazione(self):
        for url in ("/", "/tavoli", "/tavolo/4", "/cucina", "/statistiche"):
            with self.subTest(url=url):
                html = self.leggi_html(url)
                for destinazione in ("/", "/tavoli", "/cucina", "/statistiche"):
                    self.assertIn('href="' + destinazione + '"', html)
                self.assertNotIn("<form", html)
                self.assertNotIn("{{", html)

    def test_menu_completo_ordinato_e_null(self):
        html = self.leggi_html("/")
        self.assertEqual(html.count('class="category-badge"'), 16)
        self.assertLess(html.index("Arancini al ragù"), html.index("Carbonara"))
        self.assertLess(html.index("Carbonara"), html.index("Frittura di calamari"))
        self.assertLess(html.index("Frittura di calamari"), html.index("Cannolo"))
        self.assertLess(html.index("Cannolo"), html.index("Acqua 1 L"))
        self.assertNotIn("None", html)
        self.assertIn("€ 1.50", html)

    def test_tavoli_con_stato_e_bonus_totale(self):
        html = self.leggi_html("/tavoli")
        self.assertEqual(html.count("table-card h-100"), 8)
        self.assertIn("€ 42.50", html)
        self.assertIn("€ 112.00", html)
        self.assertIn("€ 36.00", html)
        self.assertEqual(html.count(">Occupato</span>"), 3)
        self.assertEqual(html.count(">Libero</span>"), 5)

    def test_tavolo_con_conto_e_quota(self):
        html = self.leggi_html("/tavolo/4")
        self.assertIn("€ 112.00", html)
        self.assertIn("€ 18.67", html)
        self.assertIn('href="/tavolo/4/aggiungi/16"', html)
        self.assertIn('href="/tavolo/4/riduci/6"', html)
        self.assertIn('href="/tavolo/4/chiudi"', html)
        self.assertIn("status-free", html)
        self.query["query_conto_alla_romana"].assert_called_once_with(4, 6)

    def test_tavolo_libero(self):
        self.query["query_totale_tavolo"].return_value = {"totale": Decimal("0.00")}
        self.query["query_conto_alla_romana"].return_value = {"quota": Decimal("0.00")}
        html = self.leggi_html("/tavolo/1")
        self.assertIn("Tavolo libero, aggiungi il primo piatto", html)
        self.assertIn("€ 0.00", html)
        self.assertNotIn('href="/tavolo/1/chiudi"', html)
        self.assertIn('href="/tavolo/1/aggiungi/16"', html)

    def test_cucina_iniziale(self):
        html = self.leggi_html("/cucina")
        self.assertEqual(html.count("kitchen-card h-100"), 5)
        self.assertIn("20:15", html)
        self.assertIn("3 ×", html)

    def test_statistiche_iniziali(self):
        html = self.leggi_html("/statistiche")
        self.assertIn("€ 190.50", html)
        self.assertIn('class="stat-value">3</strong>', html)
        self.assertIn('class="stat-value">5</strong>', html)
        self.assertLess(html.index("Spaghetti alle vongole"), html.index("Arancini al ragù"))

    def test_stati_vuoti(self):
        self.query["query_menu"].return_value = []
        self.assertIn("Il menù è in preparazione", self.leggi_html("/"))
        self.query["query_tavoli_occupati"].return_value = []
        self.assertIn("La sala è pronta", self.leggi_html("/tavoli"))
        self.query["query_da_preparare"].return_value = []
        self.assertIn("Cucina tranquilla 😊", self.leggi_html("/cucina"))
        self.query["query_numeri_serata"].return_value = {"tavoli_occupati": 0, "in_preparazione": 0, "incasso": Decimal("0.00")}
        self.query["query_piatti_piu_ordinati"].return_value = []
        self.query["query_conto_per_tavolo"].return_value = []
        html = self.leggi_html("/statistiche")
        self.assertIn("€ 0.00", html)
        self.assertIn("Nessun conto aperto", html)

    def test_aggiunta_e_redirect(self):
        risposta = self.client.get("/tavolo/4/aggiungi/16")
        self.assertEqual(risposta.status_code, 302)
        self.assertEqual(risposta.location, "/tavolo/4")
        self.query["aggiungi_ordinazione"].assert_called_once_with(4, 16)

    def test_riduzione_quantita_maggiore_di_uno(self):
        risposta = self.client.get("/tavolo/4/riduci/6")
        self.assertEqual(risposta.status_code, 302)
        self.assertEqual(risposta.location, "/tavolo/4")
        self.query["riduci_ordinazione"].assert_called_once_with(4, 6)
        self.query["elimina_ordinazione"].assert_not_called()

    def test_eliminazione_ultima_porzione_anche_servita(self):
        risposta = self.client.get("/tavolo/4/riduci/5")
        self.assertEqual(risposta.status_code, 302)
        self.query["elimina_ordinazione"].assert_called_once_with(4, 5)
        self.query["riduci_ordinazione"].assert_not_called()

    def test_chiusura_e_redirect(self):
        risposta = self.client.get("/tavolo/5/chiudi")
        self.assertEqual(risposta.status_code, 302)
        self.assertEqual(risposta.location, "/tavoli")
        self.query["chiudi_conto"].assert_called_once_with(5)

    def test_servito_e_redirect(self):
        risposta = self.client.get("/ordinazione/6/servito")
        self.assertEqual(risposta.status_code, 302)
        self.assertEqual(risposta.location, "/cucina")
        self.query["segna_servito"].assert_called_once_with(6)

    def test_id_errati_non_modificano_dati(self):
        for url in (
            "/tavolo/999", "/tavolo/999/aggiungi/16", "/tavolo/4/aggiungi/999",
            "/tavolo/999/chiudi", "/tavolo/999/riduci/6", "/tavolo/4/riduci/999",
            "/tavolo/2/riduci/6", "/ordinazione/999/servito", "/tavolo/testo",
        ):
            with self.subTest(url=url):
                risposta = self.client.get(url)
                self.assertEqual(risposta.status_code, 404)
                self.assertIn("Pagina non trovata", risposta.get_data(as_text=True))
                self.assert_nessuna_modifica()

    def test_testi_del_database_sono_escapati(self):
        self.dati["menu"][0]["nome"] = '<script>alert("ciao")</script>'
        html = self.leggi_html("/")
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn('<script>alert(', html)

    def test_database_non_disponibile(self):
        self.query["query_menu"].side_effect = Error("Access denied for user studente")
        with self.assertLogs(sito.app.logger, level="ERROR"):
            risposta = self.client.get("/")
        self.assertEqual(risposta.status_code, 503)
        html = risposta.get_data(as_text=True)
        self.assertIn("Un momento di pausa", html)
        self.assertNotIn("Access denied", html)

    def test_errori_configurazione_mysql_spiegano_come_risolvere(self):
        casi = (
            (1045, "MySQL rifiuta l&#39;accesso", "Importa ristorante.sql"),
            (1049, "Il database ristorante non è ancora presente", "esegui tutto lo script"),
            (2003, "MySQL non è raggiungibile", "servizio MySQL80"),
        )
        for codice, titolo, istruzione in casi:
            with self.subTest(codice=codice):
                self.query["query_menu"].side_effect = Error("Errore tecnico riservato", errno=codice)
                with self.assertLogs(sito.app.logger, level="ERROR"):
                    risposta = self.client.get("/")
                self.assertEqual(risposta.status_code, 503)
                html = risposta.get_data(as_text=True)
                self.assertIn(titolo, html)
                self.assertIn(istruzione, html)
                self.assertNotIn("Errore tecnico riservato", html)


if __name__ == "__main__":
    unittest.main()
