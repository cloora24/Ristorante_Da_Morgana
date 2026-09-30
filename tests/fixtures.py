"""Dati per i test e la sola anteprima: letti dagli INSERT della traccia.

Nessuna connessione a MySQL. I calcoli qui preparano risposte simulate;
nell'app vera tutti i calcoli rimangono nelle query di database.py.
"""

import ast
from decimal import Decimal
from pathlib import Path
import re


def dati_iniziali():
    testo = (Path(__file__).resolve().parents[1] / "ristorante.sql").read_text(encoding="utf-8")
    dati = {}
    for tabella in ("categorie", "piatti", "tavoli", "ordinazioni"):
        corpo = re.search(
            r"INSERT INTO " + tabella + r"\s*\([^;]*?\)\s*VALUES\s*(.*?);",
            testo, re.DOTALL,
        ).group(1)
        dati[tabella] = ast.literal_eval("[" + re.sub(r"\bNULL\b", "None", corpo) + "]")

    categorie = {i: nome for i, (nome, ordine) in enumerate(dati["categorie"], 1)}
    piatti = [
        {"id_piatto": i, "nome": nome, "descrizione": descrizione,
         "prezzo": Decimal(str(prezzo)).quantize(Decimal("0.01")),
         "categoria": categorie[categoria], "id_categoria": categoria}
        for i, (categoria, nome, descrizione, prezzo) in enumerate(dati["piatti"], 1)
    ]
    menu = sorted(piatti, key=lambda p: (p["id_categoria"], p["nome"]))
    tavoli = [
        {"id_tavolo": i, "numero": numero, "posti": posti, "zona": zona}
        for i, (numero, posti, zona) in enumerate(dati["tavoli"], 1)
    ]
    ordinazioni = []
    for i, (id_tavolo, id_piatto, quantita, stato) in enumerate(dati["ordinazioni"], 1):
        p = piatti[id_piatto - 1]
        ordinazioni.append({
            "id_ordinazione": i, "id_tavolo": id_tavolo, "id_piatto": id_piatto,
            "nome": p["nome"], "prezzo": p["prezzo"], "quantita": quantita,
            "stato": stato, "subtotale": p["prezzo"] * quantita,
            "numero_tavolo": tavoli[id_tavolo - 1]["numero"],
            "zona": tavoli[id_tavolo - 1]["zona"],
            "ora": "2026-09-30 20:15:00", "ora_testo": "20:15",
        })
    occupati = []
    for t in tavoli:
        righe = [o for o in ordinazioni if o["id_tavolo"] == t["id_tavolo"]]
        if righe:
            occupati.append({**t, "porzioni": sum(o["quantita"] for o in righe),
                             "totale": sum(o["subtotale"] for o in righe)})
    classifica = []
    for p in piatti:
        porzioni = sum(o["quantita"] for o in ordinazioni if o["id_piatto"] == p["id_piatto"])
        if porzioni:
            classifica.append({"nome": p["nome"], "porzioni": porzioni})
    classifica.sort(key=lambda p: (-p["porzioni"], p["nome"]))
    cucina = [o for o in ordinazioni if o["stato"] == "in preparazione"]
    return {
        "menu": menu, "tavoli": tavoli, "ordinazioni": ordinazioni,
        "occupati": occupati, "cucina": cucina, "classifica": classifica,
        "numeri": {"tavoli_occupati": len(occupati), "in_preparazione": len(cucina),
                   "incasso": sum(o["subtotale"] for o in ordinazioni)},
    }
