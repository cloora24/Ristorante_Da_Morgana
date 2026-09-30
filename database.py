"""Query della trattoria: una funzione per query, senza ORM."""

import mysql.connector


def connetti():
    return mysql.connector.connect(
        host="localhost",
        user="studente",
        password="studente",
        database="ristorante",
        charset="utf8mb4",
        connection_timeout=5,
    )


# =============================================
# STUDENTE A - pagine 1 e 2
# =============================================

def query_menu():
    conn = connetti()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT p.id_piatto, p.nome, p.descrizione, p.prezzo,
                   c.nome AS categoria
            FROM piatti p
            JOIN categorie c ON c.id_categoria = p.id_categoria
            ORDER BY c.ordine, p.nome
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def query_tavoli_occupati():
    conn = connetti()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT t.id_tavolo, t.numero, t.zona,
                   SUM(o.quantita) AS porzioni,
                   CAST(SUM(p.prezzo * o.quantita) AS DECIMAL(10, 2)) AS totale
            FROM tavoli t
            JOIN ordinazioni o ON o.id_tavolo = t.id_tavolo
            JOIN piatti p ON p.id_piatto = o.id_piatto
            GROUP BY t.id_tavolo, t.numero, t.zona
            ORDER BY t.numero
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def query_tutti_tavoli():
    conn = connetti()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM tavoli ORDER BY numero")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


# =============================================
# STUDENTE B - pagina 3 e azioni del tavolo
# =============================================

def query_tavolo(id_tavolo):
    conn = connetti()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM tavoli WHERE id_tavolo = %s", (id_tavolo,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def query_ordinazioni_tavolo(id_tavolo):
    conn = connetti()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT o.id_ordinazione, o.quantita, o.stato,
                   p.nome, p.prezzo,
                   CAST(p.prezzo * o.quantita AS DECIMAL(10, 2)) AS subtotale
            FROM ordinazioni o
            JOIN piatti p ON p.id_piatto = o.id_piatto
            WHERE o.id_tavolo = %s
            ORDER BY o.ora, o.id_ordinazione
        """, (id_tavolo,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def query_totale_tavolo(id_tavolo):
    conn = connetti()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT CAST(COALESCE(SUM(p.prezzo * o.quantita), 0)
                        AS DECIMAL(10, 2)) AS totale
            FROM ordinazioni o
            JOIN piatti p ON p.id_piatto = o.id_piatto
            WHERE o.id_tavolo = %s
        """, (id_tavolo,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def query_conto_alla_romana(id_tavolo, posti):
    """Il numero dei posti proviene dal tavolo letto dal database."""
    conn = connetti()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT CAST(COALESCE(ROUND(SUM(p.prezzo * o.quantita) / %s, 2), 0)
                        AS DECIMAL(10, 2)) AS quota
            FROM ordinazioni o
            JOIN piatti p ON p.id_piatto = o.id_piatto
            WHERE o.id_tavolo = %s
        """, (posti, id_tavolo))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def query_piatto(id_piatto):
    conn = connetti()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM piatti WHERE id_piatto = %s", (id_piatto,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def query_ordinazione(id_ordinazione):
    conn = connetti()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM ordinazioni WHERE id_ordinazione = %s",
            (id_ordinazione,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def aggiungi_ordinazione(id_tavolo, id_piatto):
    conn = connetti()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO ordinazioni (id_tavolo, id_piatto, quantita, stato)
            VALUES (%s, %s, 1, 'in preparazione')
        """, (id_tavolo, id_piatto))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def chiudi_conto(id_tavolo):
    conn = connetti()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM ordinazioni WHERE id_tavolo = %s", (id_tavolo,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def riduci_ordinazione(id_tavolo, id_ordinazione):
    conn = connetti()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE ordinazioni SET quantita = quantita - 1
            WHERE id_tavolo = %s AND id_ordinazione = %s AND quantita > 1
        """, (id_tavolo, id_ordinazione))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def elimina_ordinazione(id_tavolo, id_ordinazione):
    conn = connetti()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            DELETE FROM ordinazioni
            WHERE id_tavolo = %s AND id_ordinazione = %s AND quantita = 1
        """, (id_tavolo, id_ordinazione))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


# =============================================
# STUDENTE C - pagine 4 e 5
# =============================================

def query_da_preparare():
    conn = connetti()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT o.id_ordinazione, o.quantita, o.ora,
                   TIME_FORMAT(o.ora, '%H:%i') AS ora_testo,
                   t.numero AS numero_tavolo, t.zona, p.nome
            FROM ordinazioni o
            JOIN tavoli t ON t.id_tavolo = o.id_tavolo
            JOIN piatti p ON p.id_piatto = o.id_piatto
            WHERE o.stato = 'in preparazione'
            ORDER BY o.ora, o.id_ordinazione
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def segna_servito(id_ordinazione):
    conn = connetti()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE ordinazioni SET stato = 'servito'
            WHERE id_ordinazione = %s
        """, (id_ordinazione,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def query_numeri_serata():
    conn = connetti()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT COUNT(DISTINCT o.id_tavolo) AS tavoli_occupati,
                   COALESCE(SUM(CASE WHEN o.stato = 'in preparazione'
                                     THEN 1 ELSE 0 END), 0) AS in_preparazione,
                   CAST(COALESCE(SUM(p.prezzo * o.quantita), 0)
                        AS DECIMAL(10, 2)) AS incasso
            FROM ordinazioni o
            JOIN piatti p ON p.id_piatto = o.id_piatto
        """)
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def query_piatti_piu_ordinati():
    conn = connetti()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT p.id_piatto, p.nome, SUM(o.quantita) AS porzioni
            FROM piatti p
            JOIN ordinazioni o ON o.id_piatto = p.id_piatto
            GROUP BY p.id_piatto, p.nome
            ORDER BY porzioni DESC, p.nome
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def query_conto_per_tavolo():
    conn = connetti()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT t.id_tavolo, t.numero,
                   CAST(SUM(p.prezzo * o.quantita) AS DECIMAL(10, 2)) AS totale
            FROM tavoli t
            JOIN ordinazioni o ON o.id_tavolo = t.id_tavolo
            JOIN piatti p ON p.id_piatto = o.id_piatto
            GROUP BY t.id_tavolo, t.numero
            ORDER BY t.numero
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    # Solo letture: questa prova non modifica le ordinazioni.
    print(query_menu())
    print(query_totale_tavolo(4))
    print(query_numeri_serata())
