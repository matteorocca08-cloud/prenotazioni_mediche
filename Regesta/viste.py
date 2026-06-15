import flet as ft
from datetime import datetime

from database import (
    inserisci_prenotazione_db,
    ottieni_visite_db,
    elimina_prenotazione_db,
    conta_visite_concorrenti,
    CONFIG_MEDICI,  # <-- ASSICURATI CHE CI SIA QUESTA RIGA QUI!
)

def crea_vista_prenota(page: ft.Page, torna_home):
    data_selezionata = ""
    ora_selezionata = ""

    # 1. POP-UP DI CONFERMA PRENOTAZIONE (Caricato preventivamente in memoria)
    testo_ticket_dinamico = ft.Text(
        "", 
        size=22, 
        weight=ft.FontWeight.BOLD, 
        color=ft.Colors.BLACK
    )

    def chiudi_mio_dialog(e):
        dialog_conferma.open = False
        page.update()
        torna_home(e)

    dialog_conferma = ft.AlertDialog(
        modal=True,
        title=ft.Text(
            "Prenotazione Confermata", 
            color=ft.Colors.GREEN_400
        ),
        content=ft.Column(
            [
                ft.Text(
                    "Il tuo ticket univoco è:", 
                    weight=ft.FontWeight.BOLD
                ),
                ft.Container(
                    content=testo_ticket_dinamico,
                    bgcolor=ft.Colors.AMBER_300,
                    padding=10,
                    border_radius=8,
                ),
            ],
            tight=True,
        ),
        actions=[
            ft.TextButton("OK", on_click=chiudi_mio_dialog)
        ],
    )
    
    page.overlay.append(dialog_conferma)

    # 2. CREAZIONE DEI COMPONENTI GRAFICI DELL'INTERFACCIA
    input_nome = ft.TextField(
        label="Nome Paziente",
        border_color=ft.Colors.BLUE_400,
    )

    dropdown_visita = ft.Dropdown(
        label="Tipo di Visita",
        border_color=ft.Colors.BLUE_400,
        options=[
            ft.dropdown.Option("Controllo Generale"),
            ft.dropdown.Option("Dentista"),
            ft.dropdown.Option("Visita Specialistica"),
        ],
    )

    testo_data = ft.Text(
        "Nessun giorno selezionato",
        size=16,
        color=ft.Colors.GREY_400,
    )

    testo_ora = ft.Text(
        "Nessun orario selezionato",
        size=16,
        color=ft.Colors.GREY_400,
    )

    griglia_orari = ft.Row(
        wrap=True,
        visible=False,
    )

    def aggiorna_griglia_orari():
        if not data_selezionata or not dropdown_visita.value:
            griglia_orari.visible = False
            page.update()
            return

        griglia_orari.controls.clear()
        
        tipo = dropdown_visita.value
        if tipo == "Controllo Generale":
            orari_disponibili = ["09:00", "09:20", "09:40", "10:00", "10:20", "10:40", "11:00", "15:00", "15:20", "15:40"]
        elif tipo == "Dentista":
            orari_disponibili = ["09:00", "09:45", "10:30", "11:15", "15:00", "15:45", "16:30"]
        elif tipo == "Visita Specialistica":
            orari_disponibili = ["09:00", "10:00", "11:00", "12:00", "15:00", "16:00", "17:00"]
        else:
            orari_disponibili = ["09:00", "10:00", "11:00", "15:00", "16:00"]

        max_medici = CONFIG_MEDICI.get(tipo, 1)

        for ora in orari_disponibili:
            # Controllo disponibilità medici dal database
            occupati = conta_visite_concorrenti(tipo, data_selezionata, ora)
            is_completo = occupati >= max_medici

            # Corretto: Passiamo la stringa direttamente come primo argomento senza "text="
            if is_completo:
                pulsante = ft.OutlinedButton(
                    f"{ora} (Completo)",
                    disabled=True,
                    style=ft.ButtonStyle(
                        color=ft.Colors.RED_400,
                        side=ft.BorderSide(1, ft.Colors.RED_900)
                    )
                )
            else:
                pulsante = ft.OutlinedButton(
                    ora,
                    disabled=False,
                    style=ft.ButtonStyle(
                        color=ft.Colors.GREEN_400,
                        side=ft.BorderSide(1, ft.Colors.GREEN_700)
                    ),
                    on_click=lambda e, o=ora: cambio_ora(o),
                )

            griglia_orari.controls.append(pulsante)
        
        griglia_orari.visible = True
        page.update()

    def quando_cambia_visita(e):
        # Risoluzione Bug Stato Orfano: resetta l'orario se l'utente cambia tipo di visita
        nonlocal ora_selezionata
        ora_selezionata = ""
        testo_ora.value = "Nessun orario selezionato"
        aggiorna_griglia_orari()

    dropdown_visita.on_change = quando_cambia_visita

    def cambio_data(e):
        nonlocal data_selezionata, ora_selezionata
        if date_picker.value:
            data_selezionata = date_picker.value.strftime("%Y-%m-%d")
            testo_data.value = (
                f"📅 Data: {date_picker.value.strftime('%d/%m/%Y')}"
            )
            # Risoluzione Bug Stato Orfano: resetta l'orario se l'utente cambia il giorno sul calendario
            ora_selezionata = ""
            testo_ora.value = "Nessun orario selezionato"
            aggiorna_griglia_orari()

    def cambio_ora(ora):
        nonlocal ora_selezionata
        ora_selezionata = ora
        testo_ora.value = f"⏰ Ora: {ora}"
        page.update()

    # Risoluzione Bug Passato Remoto: prima data selezionabile impostata a OGGI
    date_picker = ft.DatePicker(
        first_date=datetime.now(),
        on_change=cambio_data,
    )

    def apri_calendario(e):
        date_picker.open = True
        page.update()

    page.overlay.append(date_picker)

    # 3. LOGICA DI CONFERMA MESSA IN SICUREZZA
    def conferma(e):
        # Risoluzione Bug Spazio Vuoto: controllo con .strip() sui campi di testo
        if (
            not input_nome.value or not input_nome.value.strip()
            or not dropdown_visita.value
            or not data_selezionata
            or not ora_selezionata
        ):
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Compila tutti i campi correttamente!")
            )
            page.snack_bar.open = True
            page.update()
            return

        # Risoluzione Bug Doppio Clic: disabilita subito il bottone durante l'operazione
        conferma_btn.disabled = True
        conferma_btn.text = "Salvataggio..."
        page.update()

        try:
            ticket = inserisci_prenotazione_db(
                input_nome.value.strip(),
                dropdown_visita.value,
                data_selezionata,
                ora_selezionata,
            )

            testo_ticket_dinamico.value = ticket
            dialog_conferma.open = True
            
        finally:
            # Ripristina lo stato del bottone se l'utente dovesse tornare sulla pagina
            conferma_btn.disabled = False
            conferma_btn.text = "Conferma Prenotazione"
            page.update()

    conferma_btn = ft.ElevatedButton(
        "Conferma Prenotazione",
        icon=ft.Icons.CHECK,
        on_click=conferma,
    )

    return ft.Column(
        [
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                on_click=torna_home,
            ),

            ft.Text(
                "Nuova Prenotazione",
                size=24,
                weight=ft.FontWeight.BOLD,
            ),

            input_nome,
            dropdown_visita,

            ft.ElevatedButton(
                "Seleziona Giorno",
                icon=ft.Icons.CALENDAR_MONTH,
                on_click=apri_calendario,
            ),

            testo_data,
            griglia_orari,
            testo_ora,

            ft.Divider(),
            
            conferma_btn,
        ],
        spacing=15,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


def crea_vista_visualizza(torna_home):
    lista_visite = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    dati = ottieni_visite_db()

    if not dati:
        lista_visite.controls.append(
            ft.Text(
                "Nessuna visita prenotata.",
                color=ft.Colors.GREY_500,
            )
        )
    else:
        for data_ora, tipo, ticket in dati:
            lista_visite.controls.append(
                ft.Card(
                    content=ft.Container(
                        padding=15,
                        content=ft.Column(
                            [
                                ft.Text(
                                    f"📅 Data/Ora: {data_ora}",
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(f"🩺 Tipo visita: {tipo}"),
                                ft.Text(
                                    f"🎫 Ticket: {ticket}",
                                    color=ft.Colors.BLUE_300,
                                ),
                            ]
                        ),
                    )
                )
            )

    return ft.Column(
        [
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                on_click=torna_home,
            ),

            ft.Text(
                "Le Tue Visite",
                size=24,
                weight=ft.FontWeight.BOLD,
            ),

            lista_visite,
        ],
        expand=True,
    )

def crea_vista_visualizza(page: ft.Page, torna_home):
    lista_visite = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    # 1. POP-UP PER MOSTRARE IL TICKET IN GRANDE
    testo_dettaglio_ticket = ft.Text("", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)
    testo_dettaglio_info = ft.Text("", size=16, color=ft.Colors.WHITE)

    def chiudi_dialog_ticket(e):
        dialog_ticket.open = False
        page.update()

    dialog_ticket = ft.AlertDialog(
        title=ft.Text("Dettaglio Prenotazione", weight=ft.FontWeight.BOLD),
        content=ft.Column(
            [
                ft.Text("Mostra questo ticket al personale:"),
                ft.Container(
                    content=testo_dettaglio_ticket,
                    bgcolor=ft.Colors.AMBER_400,
                    padding=15,
                    border_radius=8,
                    alignment=ft.Alignment(0, 0), # <-- Sostituito qui! Centro perfetto
                ),
                ft.Divider(),
                testo_dettaglio_info,
            ],
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        actions=[
            ft.TextButton("Chiudi", on_click=chiudi_dialog_ticket)
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # Agganciamo il dialog all'overlay della pagina per renderlo visibile
    page.overlay.append(dialog_ticket)

    # 2. FUNZIONE CHE APRE IL POP-UP CON I DATI DELLA VISITA CLICCATA
    def mostra_ticket_grande(data_ora, tipo, ticket):
        testo_dettaglio_ticket.value = ticket
        testo_dettaglio_info.value = f"📅 Data/Ora: {data_ora}\n🩺 Tipo visita: {tipo}"
        dialog_ticket.open = True
        page.update()

    # 3. CARICAMENTO DATI DAL DB
    dati = ottieni_visite_db()

    if not dati:
        lista_visite.controls.append(
            ft.Text(
                "Nessuna visita prenotata.",
                color=ft.Colors.GREY_500,
            )
        )
    else:
        for data_ora, tipo, ticket in dati:
            lista_visite.controls.append(
                # Il GestureDetector intercetta il click su tutta la card
                ft.GestureDetector(
                    on_tap=lambda e, d=data_ora, t=tipo, tk=ticket: mostra_ticket_grande(d, t, tk),
                    mouse_cursor=ft.MouseCursor.CLICK, # Fa spuntare l'icona della manina
                    content=ft.Card(
                        content=ft.Container(
                            padding=15,
                            content=ft.Column(
                                [
                                    ft.Text(
                                        f"📅 Data/Ora: {data_ora}",
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(f"🩺 Tipo visita: {tipo}"),
                                    ft.Text(
                                        f"🎫 Ticket: {ticket}",
                                        color=ft.Colors.BLUE_300,
                                    ),
                                ]
                            ),
                        )
                    )
                )
            )

    return ft.Column(
        [
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                on_click=torna_home,
            ),

            ft.Text(
                "Le Tue Visite",
                size=24,
                weight=ft.FontWeight.BOLD,
            ),

            lista_visite,
        ],
        expand=True,
    )


def crea_vista_disdici(page: ft.Page, torna_home):
    # Supporto di memoria per sapere quale riga l'utente ha intenzione di eliminare
    ticket_da_cancellare = ""

    lista_disdici = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    # 4. GESTIONE DEL POP-UP DI SICUREZZA PER L'ELIMINAZIONE
    def chiudi_dialog_elimina(e):
        dialog_elimina.open = False
        page.update()

    def conferma_ed_elimina(e):
        nonlocal ticket_da_cancellare
        if ticket_da_cancellare:
            elimina_prenotazione_db(ticket_da_cancellare)
            ticket_da_cancellare = ""  # Svuota il contenitore temporaneo
            dialog_elimina.open = False
            rinfresca()  # Ricarica la lista aggiornata a schermo
            
            # Piccolo feedback visivo in basso ad avvenuta operazione
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Prenotazione annullata con successo.")
            )
            page.snack_bar.open = True
            page.update()

    dialog_elimina = ft.AlertDialog(
        modal=True,
        title=ft.Text("Conferma Annullamento"),
        content=ft.Text("Sei sicuro di voler disdire questa visita? L'operazione non è reversibile."),
        actions=[
            ft.TextButton("No, mantieni", on_click=chiudi_dialog_elimina),
            ft.TextButton(
                "Sì, disdici", 
                icon=ft.Icons.DELETE_FOREVER,
                icon_color=ft.Colors.RED_500,
                on_click=conferma_ed_elimina
            ),
        ],
    )
    
    page.overlay.append(dialog_elimina)

    def richiedi_cancellazione(ticket):
        nonlocal ticket_da_cancellare
        ticket_da_cancellare = ticket  # Memorizza il ticket corrente
        dialog_elimina.open = True     # Attiva l'interruttore del pop-up
        page.update()

    def rinfresca():
        lista_disdici.controls.clear()

        dati = ottieni_visite_db()

        if not dati:
            lista_disdici.controls.append(
                ft.Text(
                    "Nessuna visita da disdire.",
                    color=ft.Colors.GREY_500,
                )
            )
        else:
            for data_ora, tipo, ticket in dati:
                lista_disdici.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(
                            ft.Icons.CANCEL,
                            color=ft.Colors.RED_400,
                        ),
                        title=ft.Text(data_ora),
                        subtitle=ft.Text(
                            f"{tipo} | Ticket: {ticket}"
                        ),
                        trailing=ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_color=ft.Colors.RED_500,
                            # Agganciato il controllo preventivo anziché la cancellazione immediata
                            on_click=lambda e, t=ticket: richiedi_cancellazione(t),
                        ),
                    )
                )

        page.update()

    rinfresca()

    return ft.Column(
        [
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                on_click=torna_home,
            ),

            ft.Text(
                "Annulla una Visita",
                size=24,
                weight=ft.FontWeight.BOLD,
            ),

            lista_disdici,
        ],
        expand=True,
    )