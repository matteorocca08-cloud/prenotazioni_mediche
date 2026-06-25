import flet as ft
from datetime import datetime, timedelta
import sys

from database import (
    inserisci_prenotazione_db,
    ottieni_visite_db,
    elimina_prenotazione_db,
    conta_visite_concorrenti,
    CONFIG_MEDICI,
)

def crea_vista_prenota(page: ft.Page, torna_home):
    tipo_visita_scelta = None
    data_selezionata = ""
    ora_selezionata = ""

    # 1. POP-UP DI CONFERMA PRENOTAZIONE (Corretto con ft.Alignment e ft.Border)
    testo_ticket_dinamico = ft.Text(
        "", 
        size=26, 
        weight=ft.FontWeight.BOLD, 
        color="#1A6B4A", 
        text_align=ft.TextAlign.CENTER
    )

    def chiudi_mio_dialog(e):
        dialog_conferma.open = False
        page.update()
        torna_home(e)

    dialog_conferma = ft.AlertDialog(
        modal=True,
        title=ft.Text(
            "Prenotazione Confermata", 
            color="#1A6B4A",
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        ),
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Il tuo ticket univoco è:", 
                        weight=ft.FontWeight.W_500,
                        size=14,
                        color=ft.Colors.BLACK
                    ),
                    ft.Container(
                        content=testo_ticket_dinamico,
                        bgcolor=ft.Colors.WHITE, 
                        padding=15,
                        border_radius=8,
                        alignment=ft.Alignment(0, 0), 
                        border=ft.Border.all(1, "#1A6B4A") # Corretto con la B maiuscola
                    ),
                    ft.Text(
                        "Salvalo o mostralo all'accettazione.", 
                        size=12, 
                        color=ft.Colors.BLUE_GREY_700,
                        text_align=ft.TextAlign.CENTER
                    ),
                ],
                tight=True, 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15
            ),
            width=360,
            padding=10
        ),
        actions=[
            ft.TextButton(
                "OK, Torna alla Home", 
                on_click=chiudi_mio_dialog,
                style=ft.ButtonStyle(color="#1A6B4A")
            )
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )

    page.overlay.append(dialog_conferma)

    # --- ELEMENTI DI INPUT UTENTE ---
    input_nome = ft.TextField(label="Nome e Cognome Paziente", width=400)
    input_cf = ft.TextField(label="Codice Fiscale", width=400)

    # --- CONTENITORI DINAMICI ---
    sezione_orari = ft.Column(spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER, width=400)
    contenitore_calendario = ft.Container()
    testo_stato = ft.Text("", color="#1A6B4A", size=14, weight=ft.FontWeight.BOLD)

    # --- GESTIONE LOGICA SELEZIONI ---
    def seleziona_reparto(e, reparto):
        nonlocal tipo_visita_scelta, data_selezionata, ora_selezionata
        tipo_visita_scelta = reparto
        data_selezionata = ""
        ora_selezionata = ""
        testo_stato.value = f"Reparto: {tipo_visita_scelta} | Scegli una data"
        sezione_orari.controls.clear()
        
        for btn in riga_pulsanti_reparto.controls:
            if btn.content and btn.content.value == reparto:
                btn.style = ft.ButtonStyle(bgcolor="#1A6B4A", color="#FFFFFF")
            else:
                btn.style = ft.ButtonStyle(bgcolor=None, color=None)

        mostra_calendario()
        page.update()

    def cambia_data(e):
        nonlocal data_selezionata, ora_selezionata
        if e.control.value:
            dt = datetime.fromisoformat(str(e.control.value))
            data_selezionata = dt.strftime("%Y-%m-%d")
            ora_selezionata = ""
            testo_stato.value = f"Reparto: {tipo_visita_scelta} | Data: {data_selezionata} | Scegli l'ora"
            mostra_orari_disponibili(data_selezionata)
            page.update()

    # Inizializzazione del DatePicker nativo conforme alle ultime API Flet
    mio_date_picker = ft.DatePicker(
        on_change=cambia_data,
        first_date=datetime.now(),
        last_date=datetime.now() + timedelta(days=30),
    )
    page.overlay.append(mio_date_picker)

    def apri_calendario(e):
        mio_date_picker.open = True
        page.update()

    def montre_calendario():
        pass

    def mostra_calendario():
        contenitore_calendario.content = ft.ElevatedButton(
            content=ft.Text("Apri Calendario"),
            icon=ft.Icons.CALENDAR_TODAY,
            on_click=apri_calendario,
            style=ft.ButtonStyle(bgcolor="#1A6B4A", color="#FFFFFF")
        )

    def mostra_orari_disponibili(data_str):
        sezione_orari.controls.clear()
        orari_standard = ["09:00", "10:00", "11:00", "12:00", "14:00", "15:00", "16:00"]
        
        riga_orari = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            wrap=True,
            run_spacing=10,
            spacing=10,
            width=400
        )
        
        for ora in orari_standard:
            slot_occupati = conta_visite_concorrenti(tipo_visita_scelta, data_str, ora)
            max_medici = CONFIG_MEDICI.get(tipo_visita_scelta, 1)
            disponibili = max_medici - slot_occupati

            if disponibili > 0:
                lbl = f"{ora} ({disponibili})"
                btn = ft.ElevatedButton(content=ft.Text(lbl), on_click=lambda e, o=ora: salva_ora(e, o))
                riga_orari.controls.append(btn)
            else:
                riga_orari.controls.append(ft.ElevatedButton(content=ft.Text(f"{ora} (Pieno)"), disabled=True))
        
        sezione_orari.controls.append(riga_orari)

    def salva_ora(e, ora):
        nonlocal ora_selezionata
        ora_selezionata = ora
        testo_stato.value = f"Pronto! {tipo_visita_scelta} il {data_selezionata} alle {ora_selezionata}"
        
        for btn in e.control.parent.controls:
            if btn.content and btn.content.value.startswith(ora):
                btn.style = ft.ButtonStyle(bgcolor="#1A6B4A", color="#FFFFFF")
            elif not btn.disabled:
                btn.style = ft.ButtonStyle(bgcolor=None, color=None)
        page.update()

    def esegui_invio_prenotazione(e):
        if not input_nome.value.strip() or not input_cf.value.strip():
            testo_stato.value = "Errore: Inserisci Nome e Codice Fiscale!"
            testo_stato.color = "#BA0000"
            page.update()
            return
        if not tipo_visita_scelta or not data_selezionata or not ora_selezionata:
            testo_stato.value = "Errore: Seleziona reparto, data e ora!"
            testo_stato.color = "#BA0000"
            page.update()
            return

        try:
            ticket_generato = inserisci_prenotazione_db(
                nome=input_nome.value.strip(),
                cf=input_cf.value.strip().upper(), 
                tipo=tipo_visita_scelta,
                data=data_selezionata,
                ora=ora_selezionata
            )
            testo_ticket_dinamico.value = ticket_generato
            dialog_conferma.open = True
            page.update()
        except Exception as err:
            import sys
            print(f"\n--- ERRORE DATABASE CRITICO --- \n{str(err)}\n------------------------", file=sys.stderr)
            testo_stato.value = "Impossibile salvare. Controlla il terminale per l'errore."
            testo_stato.color = "#BA0000"
            page.update()

    riga_pulsanti_reparto = ft.Row(
        controls=[
            ft.ElevatedButton(content=ft.Text("Controllo Generale"), on_click=lambda e: seleziona_reparto(e, "Controllo Generale"), color="#1A6B4A"),
            ft.ElevatedButton(content=ft.Text("Dentista"), on_click=lambda e: seleziona_reparto(e, "Dentista"), color="#1A6B4A"),
            ft.ElevatedButton(content=ft.Text("Visita Specialistica"), on_click=lambda e: seleziona_reparto(e, "Visita Specialistica"), color="#1A6B4A"),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        wrap=True,
        run_spacing=10
    )

    return ft.Column(
        [
            ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=torna_home, icon_color="#1A6B4A"),
                ft.Text("Nuova Prenotazione", size=24, weight=ft.FontWeight.BOLD, color="#1A6B4A"),
            ], alignment=ft.MainAxisAlignment.START, width=440),
            
            ft.Container(height=15),
            input_nome,
            ft.Container(height=5),
            input_cf,
            
            ft.Container(height=20),
            ft.Text("1. Seleziona il Reparto / Tipo di Visita:", size=14, weight=ft.FontWeight.BOLD, color="#1A6B4A"),
            ft.Container(height=5),
            riga_pulsanti_reparto,
            
            ft.Container(height=20),
            ft.Text("2. Scegli il Giorno:", size=14, weight=ft.FontWeight.BOLD, color="#1A6B4A"),
            ft.Container(height=5),
            contenitore_calendario,
            
            ft.Container(height=20),
            sezione_orari,
            
            ft.Container(height=15),
            testo_stato,
            ft.Container(height=10),
            
            ft.ElevatedButton(
                content=ft.Text("Conferma Appuntamento"),
                icon=ft.Icons.CHECK_CIRCLE,
                on_click=esegui_invio_prenotazione,
                width=400,
                height=50,
                style=ft.ButtonStyle(bgcolor="#1A6B4A", color="#FFFFFF")
            ),
        ],
        expand=True,
        width=440,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )


def crea_vista_visualizza(page: ft.Page, torna_home):
    lista_visite = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=400)
    input_cf_filtro = ft.TextField(label="Inserisci il tuo Codice Fiscale", width=400)

    # 1. POP-UP DI DETTAGLIO DINAMICO
    testo_dettaglio = ft.Column(spacing=10, tight=True)
    
    dialog_dettaglio = ft.AlertDialog(
        title=ft.Text("Dettaglio Appuntamento", weight=ft.FontWeight.BOLD, color="#1A6B4A"),
        content=ft.Container(content=testo_dettaglio, width=360),
        actions=[
            ft.TextButton("Chiudi", on_click=lambda e: chiudi_dettaglio(), style=ft.ButtonStyle(color="#1A6B4A"))
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dialog_dettaglio)

    def apri_dettaglio(appuntamento):
        testo_dettaglio.controls.clear()
        # QUI cambiamo correttamente i colori di tutte le scritte del pop-up!
        testo_dettaglio.controls.extend([
            ft.Text(f"Codice Ticket: {appuntamento['ticket']}", weight=ft.FontWeight.BOLD, size=18, color="#1A6B4A"),
            ft.Divider(color="#1A6B4A"),
            ft.Text(f"Paziente: {appuntamento['paziente']}", size=15, color="#1A6B4A", weight=ft.FontWeight.W_500),
            ft.Text(f"Reparto/Visita: {appuntamento['reparto']}", size=15, color="#1A6B4A"),
            ft.Text(f"Data: {appuntamento['data']}", size=15, color="#1A6B4A"),
            ft.Text(f"Orario d'Inizio: {appuntamento['ora']}", size=15, color="#1A6B4A"),
        ])
        dialog_dettaglio.open = True
        page.update()

    def chiudi_dettaglio():
        dialog_dettaglio.open = False
        page.update()

    # 2. LOGICA DI RICERCA E RINFRESCO
    def rinfresca(e=None):
        lista_visite.controls.clear()
        cf_cercato = input_cf_filtro.value.strip().upper()
        
        if not cf_cercato:
            lista_visite.controls.append(ft.Text("Inserisci il codice fiscale per vedere i tuoi ticket.", color="#1A6B4A"))
            page.update()
            return

        tutte_le_visite = ottieni_visite_db()
        visite_utente = []

        for v in tutte_le_visite:
            if isinstance(v, dict):
                cf_db = str(v.get("cf", "")).strip().upper()
                if cf_db == cf_cercato:
                    data_ora_str = v.get("data_ora", "N/D")
                    data_pulita, ora_pulita = "N/D", "N/D"
                    if " " in data_ora_str:
                        data_pulita, ora_pulita = data_ora_str.split(" ", 1)

                    # Ripristinata l'estrazione dati corretta e pulita (senza stili qui dentro)
                    visite_utente.append({
                        "ticket": v.get("ticket", "N/D"),
                        "paziente": v.get("paziente", "N/D"),
                        "reparto": v.get("tipo_visita", "N/D"),
                        "data": data_pulita, 
                        "ora": ora_pulita
                    })

        if not visite_utente:
            lista_visite.controls.append(ft.Text("Nessun appuntamento trovato per questo Codice Fiscale.", color="#BA0000"))
        else:
            for appuntamento in visite_utente:
                lista_visite.controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=15,
                            on_click=lambda e, a=appuntamento: apri_dettaglio(a),
                            tooltip="Clicca per vedere i dettagli",
                            content=ft.Column(
                                [
                                    ft.Text(f"Ticket: {appuntamento['ticket']}", weight=ft.FontWeight.BOLD, size=16, color="#1A6B4A"),
                                    ft.Text(f"Paziente: {appuntamento['paziente']}", size=14),
                                    ft.Text(f"Reparto: {appuntamento['reparto']}", size=14),
                                    ft.Text(f"Data: {appuntamento['data']}  |  Ora: {appuntamento['ora']}", size=14, weight=ft.FontWeight.W_500),
                                ]
                            ),
                        )
                    )
                )
        page.update()

    return ft.Column(
        [
            ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=torna_home, icon_color="#1A6B4A"),
                ft.Text("I tuoi Appuntamenti", size=24, weight=ft.FontWeight.BOLD, color="#1A6B4A"),
            ], alignment=ft.MainAxisAlignment.START, width=440),
            
            ft.Container(height=10),
            input_cf_filtro,
            ft.ElevatedButton(content=ft.Text("Cerca Ticket"), on_click=rinfresca, bgcolor="#1A6B4A", color="#FFFFFF"),
            ft.Container(height=10),
            lista_visite,
        ],
        expand=True,
        width=440,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )


def crea_vista_disdici(page: ft.Page, torna_home):
    lista_disdici = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=400)
    input_cf_filtro = ft.TextField(label="Inserisci il tuo Codice Fiscale", width=400)
    
    # Variabile d'appoggio per memorizzare il ticket che si sta per eliminare
    ticket_da_eliminare = None

    # 1. FUNZIONE EFFETTIVA DI CANCELLAZIONE
    def esegui_cancellazione_sicura(e):
        nonlocal ticket_da_eliminare
        if ticket_da_eliminare:
            successo = elimina_prenotazione_db(ticket_da_eliminare)
            dialog_conferma_disdetta.open = False # Chiude il pop-up
            ticket_da_eliminare = None # Resetta la variabile
            
            if successo:
                rinfresca()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Impossibile eliminare l'appuntamento."))
                page.snack_bar.open = True
            page.update()

    def chiudi_dialog_annulla(e):
        nonlocal ticket_da_eliminare
        ticket_da_eliminare = None
        dialog_conferma_disdetta.open = False
        page.update()

    # 2. COSTRUZIONE DEL POP-UP DI CONFERMA
    dialog_conferma_disdetta = ft.AlertDialog(
        modal=True,
        title=ft.Text("Conferma Disdetta", weight=ft.FontWeight.BOLD),
        content=ft.Text("Sei sicuro di voler annullare definitivamente questo appuntamento? L'azione non è reversibile."),
        actions=[
            ft.TextButton("No, mantieni", on_click=chiudi_dialog_annulla),
            ft.ElevatedButton("Sì, annulla", on_click=esegui_cancellazione_sicura, bgcolor="#BA0000", color="#FFFFFF"),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dialog_conferma_disdetta)

    # 3. APERTURA DEL POP-UP AL CLICK SUL CESTINO
    def richiedi_conferma_disdetta(ticket_code):
        nonlocal ticket_da_eliminare
        ticket_da_eliminare = ticket_code # Salva il ticket corrente
        dialog_conferma_disdetta.open = True # Mostra il pop-up
        page.update()

    def rinfresca(e=None):
        lista_disdici.controls.clear()
        cf_cercato = input_cf_filtro.value.strip().upper()

        if not cf_cercato:
            lista_disdici.controls.append(ft.Text("Inserisci il codice fiscale per gestire le disdette.", color="#1A6B4A"))
            page.update()
            return

        tutte_le_visite = ottieni_visite_db()
        visite_utente = []

        for v in tutte_le_visite:
            if isinstance(v, dict):
                cf_db = str(v.get("cf", "")).strip().upper()
                if cf_db == cf_cercato:
                    data_ora_str = v.get("data_ora", "N/D")
                    data_pulita, ora_pulita = "N/D", "N/D"
                    if " " in data_ora_str:
                        data_pulita, ora_pulita = data_ora_str.split(" ", 1)

                    visite_utente.append({
                        "ticket": v.get("ticket", ""),
                        "reparto": v.get("tipo_visita", "N/D"),
                        "data": data_pulita,
                        "ora": ora_pulita
                    })

        if not visite_utente:
            lista_disdici.controls.append(ft.Text("Nessun appuntamento trovato da poter disdire.", color="#BA0000"))
        else:
            for appuntamento in visite_utente:
                lista_disdici.controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=12,
                            content=ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Text(f"Ticket: {appuntamento['ticket']}", weight=ft.FontWeight.BOLD, color="#1A6B4A"),
                                            ft.Text(f"{appuntamento['reparto']} - {appuntamento['data']} ore {appuntamento['ora']}", size=13),
                                        ]
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_FOREVER,
                                        icon_color="#BA0000",
                                        icon_size=26,
                                        tooltip="Annulla questo appuntamento",
                                        # Ora chiama la richiesta di conferma invece di eliminare direttamente
                                        on_click=lambda e, t=appuntamento['ticket']: richiedi_conferma_disdetta(t),
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        )
                    )
                )
        page.update()

    return ft.Column(
        [
            ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=torna_home, icon_color="#1A6B4A"),
                ft.Text("Annulla una Visita", size=24, weight=ft.FontWeight.BOLD, color="#1A6B4A"),
            ], alignment=ft.MainAxisAlignment.START, width=440),
            
            ft.Container(height=10),
            input_cf_filtro,
            ft.ElevatedButton(content=ft.Text("Mostra Appuntamenti"), on_click=rinfresca, bgcolor="#1A6B4A", color="#FFFFFF"),
            ft.Container(height=10),
            lista_disdici,
        ],
        expand=True,
        width=440,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )