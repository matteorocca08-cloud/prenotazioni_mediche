import uuid
from datetime import datetime, timedelta
from supabase import create_client, Client

# Sostituisci questi due valori con quelli presi dal tuo pannello Supabase (Settings -> API)
SUPABASE_URL = "https://hdenvzrmgaadxsyxsrrz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhkZW52enJtZ2FhZHhzeXhzcnJ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE2MTAyOTksImV4cCI6MjA5NzE4NjI5OX0.Amv_LUyJnzOOz8P7WZYUoxAbdIkz7Hi1KH5nB-jHcsE"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configurazione del numero di medici per prestazione
CONFIG_MEDICI = {
    "Controllo Generale": 3,
    "Dentista": 1,
    "Visita Specialistica": 2
}

def inizializza_db():
    # Con Supabase la tabella viene creata direttamente online, 
    # quindi questa funzione non deve fare nulla ma la teniamo per non rompere main.py
    pass

def ottieni_visite_db():
    try:
        # Recupera tutte le prenotazioni ordinate per data e ora
        risposta = supabase.table("prenotazioni").select("data_ora, tipo_visita, ticket").order("data_ora").execute()
        # Converte il formato JSON di Supabase in una lista di tuple compatibile con viste.py
        return [(v["data_ora"], v["tipo_visita"], v["ticket"]) for v in risposta.data]
    except Exception as e:
        print(f"Errore caricamento dati dal Cloud: {e}")
        return []

def elimina_prenotazione_db(ticket):
    try:
        # Elimina la riga dal cloud in base al ticket
        supabase.table("prenotazioni").delete().eq("ticket", ticket).execute()
    except Exception as e:
        print(f"Errore eliminazione sul Cloud: {e}")

def conta_visite_concorrenti(tipo_visita, data, ora):
    try:
        data_ora_test = f"{data} {ora}"
        risposta = supabase.table("prenotazioni").select("id").eq("tipo_visita", tipo_visita).eq("data_ora", data_ora_test).execute()
        return len(risposta.data)
    except Exception as e:
        print(f"Errore conteggio medici occupati: {e}")
        return 0

def inserisci_prenotazione_db(nome, tipo, data, ora):
    medici_disponibili = CONFIG_MEDICI.get(tipo, 1)
    gia_prenotati = conta_visite_concorrenti(tipo, data, ora)
    if gia_prenotati >= medici_disponibili:
        raise Exception("Overbooking: Tutti i medici per questo orario sono occupati!")

    codice_ticket = f"TX-{uuid.uuid4().hex[:6].upper()}"
    
    durate = {"Controllo Generale": 30, "Dentista": 45, "Visita Specialistica": 60}
    durata = durate.get(tipo, 30)
    
    ora_inizio = datetime.strptime(ora, "%H:%M")
    ora_fine = (ora_inizio + timedelta(minutes=durata)).strftime("%H:%M")
    
    data_ora_completa = f"{data} {ora}"
    ora_fine_completa = f"{data} {ora_fine}"

    # Prepariamo il dizionario da inviare al database online
    nuova_prenotazione = {
        "paziente": nome,
        "tipo_visita": tipo,
        "data_ora": data_ora_completa,
        "ora_fine": ora_fine_completa,
        "ticket": codice_ticket
    }
    
    # Inserimento effettivo nel Cloud tramite API
    supabase.table("prenotazioni").insert(nuova_prenotazione).execute()
    return codice_ticket