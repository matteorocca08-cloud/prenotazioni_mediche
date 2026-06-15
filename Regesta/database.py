import sqlite3
import uuid
from datetime import datetime, timedelta

DB_NAME = "clinica.db"

def inizializza_db():
    connessione = sqlite3.connect(DB_NAME)
    cursore = connessione.cursor()
    cursore.execute("""
    CREATE TABLE IF NOT EXISTS prenotazioni (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paziente TEXT NOT NULL,
        tipo_visita TEXT NOT NULL,
        data_ora TEXT NOT NULL,
        ora_fine TEXT NOT NULL,
        ticket TEXT UNIQUE NOT NULL
    )
    """)
    connessione.commit()
    connessione.close()

def ottieni_visite_db():
    connessione = sqlite3.connect(DB_NAME)
    cursore = connessione.cursor()
    cursore.execute("SELECT data_ora, tipo_visita, ticket FROM prenotazioni ORDER BY data_ora ASC")
    visite = cursore.fetchall()
    connessione.close()
    return visite

def inserisci_prenotazione_db(nome, tipo, data, ora):
    connessione = sqlite3.connect(DB_NAME)
    cursore = connessione.cursor()
    codice_ticket = f"TX-{uuid.uuid4().hex[:6].upper()}"
    
    durate = {"Controllo Generale": 20, "Dentista": 45, "Visita Specialistica": 60}
    durata = durate.get(tipo, 30)
    ora_inizio = datetime.strptime(ora, "%H:%M")
    ora_fine = (ora_inizio + timedelta(minutes=durata)).strftime("%H:%M")
    
    cursore.execute("""
        INSERT INTO prenotazioni (paziente, tipo_visita, data_ora, ora_fine, ticket)
        VALUES (?, ?, ?, ?, ?)
    """, (nome, tipo, f"{data} {ora}", ora_fine, codice_ticket))
    connessione.commit()
    connessione.close()
    return codice_ticket

def elimina_prenotazione_db(ticket):
    connessione = sqlite3.connect(DB_NAME)
    cursore = connessione.cursor()
    cursore.execute("DELETE FROM prenotazioni WHERE ticket = ?", (ticket,))
    connessione.commit()
    connessione.close()