-- =====================================================================
--  PROGETTO 2 — Trattoria "Da Mario" (menù, tavoli e cucina)
--  Database: ristorante                               MySQL 8
-- =====================================================================
--  COME CARICARE QUESTO FILE (va eseguito con l'utente root)
--
--  MySQL Workbench:
--     1. Aprite la connessione "Local instance MySQL80" (utente root)
--     2. File > Open SQL Script...  > scegliete ristorante.sql
--     3. Premete il FULMINE (Execute)  e poi aggiornate il pannello Schemas
--
--  Da terminale (Prompt dei comandi):
--     cd "C:\Program Files\MySQL\MySQL Server 8.0\bin"
--     mysql -u root -p < C:\percorso\ristorante.sql
--
--  Lo script crea anche l'utente  studente / studente  usato da database.py.
--  ATTENZIONE: rieseguendo lo script si torna ai dati iniziali.
-- =====================================================================

SET NAMES utf8mb4;

DROP DATABASE IF EXISTS ristorante;
CREATE DATABASE ristorante CHARACTER SET utf8mb4;
USE ristorante;

CREATE USER IF NOT EXISTS 'studente'@'localhost' IDENTIFIED BY 'studente';
GRANT ALL PRIVILEGES ON ristorante.* TO 'studente'@'localhost';
FLUSH PRIVILEGES;

-- ---------------------------------------------------------------------
--  TABELLE
-- ---------------------------------------------------------------------
CREATE TABLE categorie (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nome         VARCHAR(30) NOT NULL,
    ordine       INT NOT NULL            -- ordine in cui compare nel menù
);

CREATE TABLE piatti (
    id_piatto    INT AUTO_INCREMENT PRIMARY KEY,
    id_categoria INT NOT NULL,
    nome         VARCHAR(100) NOT NULL,
    descrizione  VARCHAR(255),
    prezzo       DECIMAL(6,2) NOT NULL,
    FOREIGN KEY (id_categoria) REFERENCES categorie(id_categoria)
);

CREATE TABLE tavoli (
    id_tavolo INT AUTO_INCREMENT PRIMARY KEY,
    numero    INT NOT NULL,
    posti     INT NOT NULL,
    zona      VARCHAR(20) NOT NULL       -- Sala, Veranda, Esterno
);

-- Ogni riga è un piatto ordinato da un tavolo
CREATE TABLE ordinazioni (
    id_ordinazione INT AUTO_INCREMENT PRIMARY KEY,
    id_tavolo      INT NOT NULL,
    id_piatto      INT NOT NULL,
    quantita       INT NOT NULL DEFAULT 1,
    stato          VARCHAR(20) NOT NULL DEFAULT 'in preparazione',  -- 'in preparazione' oppure 'servito'
    ora            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_tavolo) REFERENCES tavoli(id_tavolo),
    FOREIGN KEY (id_piatto) REFERENCES piatti(id_piatto)
);

-- ---------------------------------------------------------------------
--  DATI DI ESEMPIO
-- ---------------------------------------------------------------------
INSERT INTO categorie (nome, ordine) VALUES
('Antipasti', 1), ('Primi', 2), ('Secondi', 3), ('Dolci', 4), ('Bevande', 5);

INSERT INTO piatti (id_categoria, nome, descrizione, prezzo) VALUES
(1, 'Bruschette al pomodoro',        'Pane casereccio, pomodoro fresco e basilico', 6.00),
(1, 'Tagliere di salumi e formaggi', 'Selezione di prodotti locali',               14.00),
(1, 'Arancini al ragù',              'Due pezzi',                                   7.00),
(2, 'Spaghetti alle vongole',        'Vongole veraci, aglio e prezzemolo',         14.00),
(2, 'Pasta alla Norma',              'Pomodoro, melanzane fritte, ricotta salata', 11.00),
(2, 'Lasagne al forno',              'Ragù, besciamella e parmigiano',             12.00),
(2, 'Carbonara',                     'Guanciale, uovo, pecorino e pepe',           11.00),
(3, 'Tagliata di manzo',             'Con rucola e grana',                         20.00),
(3, 'Pesce spada alla griglia',      'Con limone e origano',                       18.00),
(3, 'Frittura di calamari',          'Calamari in pastella leggera',               16.00),
(4, 'Cannolo',                       'Ricotta e gocce di cioccolato',               5.00),
(4, 'Tiramisù',                      'Fatto in casa',                               6.00),
(4, 'Panna cotta',                   'Con frutti di bosco',                         5.00),
(5, 'Acqua 1 L',                     NULL,                                          2.50),
(5, 'Vino della casa 1/2 L',         NULL,                                          8.00),
(5, 'Caffè',                         NULL,                                          1.50);

INSERT INTO tavoli (numero, posti, zona) VALUES
(1, 2, 'Sala'), (2, 4, 'Sala'), (3, 4, 'Sala'), (4, 6, 'Sala'),
(5, 6, 'Veranda'), (6, 8, 'Veranda'), (7, 2, 'Esterno'), (8, 4, 'Esterno');

-- Tavoli 2, 4 e 5 hanno ordinato; gli altri sono liberi
INSERT INTO ordinazioni (id_tavolo, id_piatto, quantita, stato) VALUES
(2,  1, 1, 'servito'),
(2,  5, 2, 'servito'),
(2, 14, 1, 'servito'),
(2, 12, 2, 'in preparazione'),
(4,  2, 1, 'servito'),
(4,  4, 3, 'in preparazione'),
(4,  8, 2, 'in preparazione'),
(4, 15, 2, 'servito'),
(5,  3, 2, 'in preparazione'),
(5,  7, 2, 'in preparazione');

-- ---------------------------------------------------------------------
--  QUERY DI ESEMPIO
--  Servono solo a vedere i dati e a ricordare la sintassi.
--  NON sono le query del progetto: quelle le dovete scrivere voi,
--  provandole prima qui in Workbench.
-- ---------------------------------------------------------------------

-- 1) Piatti che costano meno di 10 euro
SELECT nome, prezzo
FROM piatti
WHERE prezzo < 10
ORDER BY prezzo;

-- 2) Quanti tavoli e quanti posti ci sono in ogni zona (GROUP BY)
SELECT zona, COUNT(*) AS tavoli, SUM(posti) AS posti_totali
FROM tavoli
GROUP BY zona;
