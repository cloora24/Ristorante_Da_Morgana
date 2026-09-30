"""Collaudo dei dati iniziali MySQL: solo funzioni SELECT dell'app."""

from decimal import Decimal
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mysql.connector import Error
import database


def verifica():
    menu = database.query_menu()
    assert len(menu) == 16, "Il menù deve contenere 16 piatti"
    categorie = list(dict.fromkeys(p["categoria"] for p in menu))
    assert categorie == ["Antipasti", "Primi", "Secondi", "Dolci", "Bevande"]
    assert len(database.query_tutti_tavoli()) == 8
    assert [(t["numero"], int(t["porzioni"])) for t in database.query_tavoli_occupati()] == [(2, 6), (4, 8), (5, 4)]
    assert database.query_totale_tavolo(2)["totale"] == Decimal("42.50")
    assert database.query_totale_tavolo(4)["totale"] == Decimal("112.00")
    assert database.query_conto_alla_romana(4, 6)["quota"] == Decimal("18.67")
    assert database.query_totale_tavolo(1)["totale"] == Decimal("0.00")
    assert database.query_conto_alla_romana(1, 2)["quota"] == Decimal("0.00")
    assert len(database.query_ordinazioni_tavolo(4)) == 4
    assert database.query_tavolo(999) is None
    assert database.query_piatto(16)["nome"] == "Caffè"
    assert database.query_ordinazione(6)["quantita"] == 3
    cucina = database.query_da_preparare()
    assert len(cucina) == 5
    assert cucina == sorted(cucina, key=lambda o: (o["ora"], o["id_ordinazione"]))
    numeri = database.query_numeri_serata()
    assert numeri["tavoli_occupati"] == 3
    assert numeri["in_preparazione"] == 5
    assert numeri["incasso"] == Decimal("190.50")
    assert database.query_piatti_piu_ordinati()[0]["nome"] == "Spaghetti alle vongole"
    assert [t["totale"] for t in database.query_conto_per_tavolo()] == [Decimal("42.50"), Decimal("112.00"), Decimal("36.00")]
    print("Dati iniziali e query di lettura verificati. Nessuna ordinazione modificata.")


if __name__ == "__main__":
    try:
        verifica()
    except Error as errore:
        print("MySQL non disponibile: importare ristorante.sql in Workbench e riprovare.", file=sys.stderr)
        print(str(errore), file=sys.stderr)
        sys.exit(1)
    except AssertionError as errore:
        print("Controllo fallito: il database non corrisponde ai dati iniziali della traccia.", file=sys.stderr)
        print(str(errore), file=sys.stderr)
        sys.exit(1)
