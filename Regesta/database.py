import uuid
from datetime import datetime, timedelta
from supabase import create_client, Client

# Credenziali di Supabase (Ricordati di incollare la tua chiave reale)
SUPABASE_URL = "https://hdenvzrmgaadxsyxsrrz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhkZW52enJtZ2FhZHhzeXhzcnJ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE2MTAyOTksImV4cCI6MjA5NzE4NjI5OX0.Amv_LUyJnzOOz8P7WZYUoxAbdIkz7Hi1KH5nB-jHcsE"  # Metti la tua chiave completa qui

# Inizializzazione del client Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ARRAY CONFIGURAZIONE MEDICI
CONFIG_MEDICI = {
    "Controllo Generale": 3,
    "Dentista": 1,
    "Visita Specialistica": 2
}

def inizializza_db():
    """Conferma semplicemente che la connessione a Supabase è inizializzata."""
    print("Connessione a Supabase inizializzata correttamente.")

def ottieni_visite_db():
    """Legge le visite da Supabase per la schermata 'Visualizza' e 'Disdici'."""
    try:
        risposta = supabase.table("prenotazioni").select("data_ora, tipo_visita, ticket").order("data_ora").execute()
        
        # Trasformiamo l'output nel formato a tuple (data_ora, tipo_visita, ticket) atteso da viste.py
        visite = []
        for riga in risposta.data:
            visite.append((
                riga.get("data_ora"),
                riga.get("tipo_visita"),
                riga.get("ticket")
            ))
        return visite
    except Exception as e:
        print(f"Errore durante ottieni_visite_db: {e}")
        return []

def conta_visite_concorrenti(tipo_visita, data, ora):
    """Conta quante prenotazioni esistono già su Supabase a quell'orario."""
    try:
        data_ora_test = f"{data} {ora}"
        risposta = supabase.table("prenotazioni")\
            .select("id")\
            .eq("tipo_visita", tipo_visita)\
            .eq("data_ora", data_ora_test)\
            .execute()
        return len(risposta.data)
    except Exception as e:
        print(f"Errore durante il conteggio delle visite: {e}")
        return 0

def inserisci_prenotazione_db(nome, tipo, data, ora):
    """Gestisce la logica dei tempi, controlla l'overbooking e salva su Supabase."""
    # Controllo Overbooking basato sulla configurazione dei medici
    medici_disponibili = CONFIG_MEDICI.get(tipo, 1)
    gia_prenotati = conta_visite_concorrenti(tipo, data, ora)
    if gia_prenotati >= medici_disponibili:
        raise Exception("Overbooking: Tutti i medici per questo orario sono occupati!")

    # Calcolo del codice ticket unico e dell'orario di fine
    codice_ticket = f"TX-{uuid.uuid4().hex[:6].upper()}"
    durate = {"Controllo Generale": 20, "Dentista": 45, "Visita Specialistica": 60}
    durata = durate.get(tipo, 30)
    
    ora_inizio = datetime.strptime(ora, "%H:%M")
    ora_fine_dt = ora_inizio + timedelta(minutes=durata)
    ora_fine = ora_fine_dt.strftime("%H:%M")
    
    data_ora_completa = f"{data} {ora}"

    try:
        # Struttura dati per Supabase
        dati = {
            "paziente": nome,
            "tipo_visita": tipo,
            "data_ora": data_ora_completa,
            "ora_fine": ora_fine,
            "ticket": codice_ticket
        }
        supabase.table("prenotazioni").insert(dati).execute()
        print("Prenotazione salvata in Cloud con successo.")
        return codice_ticket
    except Exception as e:
        print(f"Errore durante il salvataggio su Supabase: {e}")
        raise e

def elimina_prenotazione_db(ticket):
    """Rimuove la riga dal Cloud di Supabase cercando il codice ticket."""
    try:
        risposta = supabase.table("prenotazioni").delete().eq("ticket", ticket).execute()
        if hasattr(risposta, 'data') and len(risposta.data) > 0:
            print(f"Prenotazione con ticket {ticket} eliminata con successo dal Cloud.")
            return True
        else:
            print(f"Nessuna prenotazione trovata nel Cloud con il ticket: {ticket}")
            return False
    except Exception as e:
        print(f"Errore durante l'eliminazione da Supabase: {e}")
        return False
    
# CREDENZIALI FISSE PER I MEDICI
CREDENZIALI_MEDICI = {
    "generale": {"password": "password123", "reparto": "Controllo Generale"},
    "dentista": {"password": "dentistapass", "reparto": "Dentista"},
    "specialista": {"password": "specialistapass", "reparto": "Visita Specialistica"}
}

def verifica_login_medico(username, password):
    """Verifica se l'username e la password corrispondono a un medico e restituisce il reparto."""
    user = username.lower().strip()
    if user in CREDENZIALI_MEDICI:
        if CREDENZIALI_MEDICI[user]["password"] == password:
            return CREDENZIALI_MEDICI[user]["reparto"]
    return None