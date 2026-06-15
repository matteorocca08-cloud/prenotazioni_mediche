import sqlite3
import uuid
from datetime import datetime, timedelta

DB_NAME = "clinica.db"

# ARRAY CONFIGURAZIONE MEDICI (Modificabile in futuro)
CONFIG_MEDICI = {
    "Controllo Generale": 3,
    "Dentista": 1,
    "Visita Specialistica": 2
}

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

def elimina_prenotazione_db(ticket):
    connessione = sqlite3.connect(DB_NAME)
    cursore = connessione.cursor()
    cursore.execute("DELETE FROM prenotazioni WHERE ticket = ?", (ticket,))
    connessione.commit()
    connessione.close()

def conta_visite_concorrenti(tipo_visita, data, ora):
    """Conta quante prenotazioni esistono già per quel reparto in quel momento"""
    connessione = sqlite3.connect(DB_NAME)
    cursore = connessione.cursor()
    data_ora_test = f"{data} {ora}"
    cursore.execute("""
        SELECT COUNT(*) FROM prenotazioni 
        WHERE tipo_visita = ? AND data_ora = ?
    """, (tipo_visita, data_ora_test))
    conteggio = cursore.fetchone()[0]
    connessione.close()
    return conteggio

def inserisci_prenotazione_db(nome, tipo, data, ora):
    # CONTROLLO AGGIUNTO: Sicurezza basata sul numero di medici configurato
    medici_disponibili = CONFIG_MEDICI.get(tipo, 1)
    gia_prenotati = conta_visite_concorrenti(tipo, data, ora)
    if gia_prenotati >= medici_disponibili:
        raise Exception("Overbooking: Tutti i medici per questo orario sono occupati!")

    # Da qui in poi è esattamente il tuo codice identico riga per riga
    connessione = sqlite3.connect(DB_NAME)
    cursore = connessione.cursor()
    codice_ticket = f"TX-{uuid.uuid4().hex[:6].upper()}"
    
    durate = {"Controllo Generale": 20, "Dentista": 45, "Visita Specialistica": 60}
    durata = durate.get(tipo, 30)
    ora_inizio = datetime.strptime(ora, "%H:%M")
    ora_fine = (ora_inizio + timedelta(minutes=durata)).strftime("%H:%M")
    
    data_ora_completa = f"{data} {ora}"
    
    cursore.execute("""
        INSERT INTO prenotazioni (paziente, tipo_visita, data_ora, ora_fine, ticket)
        VALUES (?, ?, ?, ?, ?)
    """, (nome, tipo, data_ora_completa, ora_fine, codice_ticket))
    
    connessione.commit()
    connessione.close()
    return codice_ticket