import flet as ft
from datetime import datetime

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

    # 1. POP-UP DI CONFERMA PRENOTAZIONE
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

    # 2. SELETTORE DI PRESTAZIONE AD ALTA COMPATIBILITÀ (Sostituto totale del Dropdown)
    testo_prestazione_selezionata = ft.Text(
        "Nessuna prestazione selezionata",
        size=16,
        weight=ft.FontWeight.W_500,
        color=ft.Colors.AMBER_400
    )

    # Contenitore dei bottoni opzione (Finto dropdown a scomparsa)
    opzioni_visite = ft.Column(visible=False, spacing=5)

    def mostra_nascondi_opzioni(e):
        opzioni_visite.visible = not opzioni_visite.visible
        page.update()

    def seleziona_prestazione(tipo):
        nonlocal tipo_visita_scelta, data_selezionata, ora_selezionata
        tipo_visita_scelta = tipo
        testo_prestazione_selezionata.value = f"🩺 Prestazione: {tipo}"
        testo_prestazione_selezionata.color = ft.Colors.GREEN_400
        
        # AZZERAMENTO TOTALE E ISTANTANEO delle selezioni temporali precedenti
        data_selezionata = ""
        ora_selezionata = ""
        testo_data.value = "Visita modificata. Seleziona nuovamente il giorno."
        testo_data.color = ft.Colors.AMBER_400
        testo_ora.value = "Nessun orario selezionato"
        testo_ora.color = ft.Colors.GREY_400
        
        # Nascondiamo sia le opzioni aperte che la vecchia griglia orari
        opzioni_visite.visible = False
        griglia_orari.visible = False
        page.update()

    # Popoliamo le opzioni usando la proprietà 'content' universale per i testi
    opzioni_visite.controls = [
        ft.TextButton(content=ft.Text("Controllo Generale", size=16), on_click=lambda e: seleziona_prestazione("Controllo Generale")),
        ft.TextButton(content=ft.Text("Dentista", size=16), on_click=lambda e: seleziona_prestazione("Dentista")),
        ft.TextButton(content=ft.Text("Visita Specialistica", size=16), on_click=lambda e: seleziona_prestazione("Visita Specialistica")),
    ]

    pulsante_menu = ft.ElevatedButton(
        "Scegli il Tipo di Visita",
        icon=ft.Icons.ARROW_DROP_DOWN_CIRCLE,
        width=340,
        height=50,
        on_click=mostra_nascondi_opzioni
    )

    input_nome = ft.TextField(
        label="Nome Paziente",
        border_color=ft.Colors.BLUE_400,
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
        if not data_selezionata or not tipo_visita_scelta:
            griglia_orari.visible = False
            page.update()
            return

        griglia_orari.controls.clear()
        
        tipo = tipo_visita_scelta
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
            occupati = conta_visite_concorrenti(tipo, data_selezionata, ora)
            is_completo = occupati >= max_medici

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

    def cambio_data(e):
        nonlocal data_selezionata, ora_selezionata
        if e.control.value:
            from datetime import timedelta
            
            data_corretta = e.control.value + timedelta(hours=3)
            data_selezionata = f"{data_corretta.year}-{data_corretta.month:02d}-{data_corretta.day:02d}"
            testo_data.value = f"📅 Data: {data_corretta.day:02d}/{data_corretta.month:02d}/{data_corretta.year}"
            testo_data.color = ft.Colors.WHITE
            
            ora_selezionata = ""
            testo_ora.value = "Nessun orario selezionato"
            testo_ora.color = ft.Colors.GREY_400  
            aggiorna_griglia_orari()

    def cambio_ora(ora):
        nonlocal ora_selezionata
        ora_selezionata = ora
        testo_ora.value = f"⏰ Ora selezionata: {ora}"
        testo_ora.color = ft.Colors.GREEN_400  
        page.update()

    date_picker = ft.DatePicker(
        first_date=datetime.now(),
        on_change=cambio_data,
    )

    def apri_calendario(e):
        if not tipo_visita_scelta:
            testo_data.value = "⚠️ Errore: Seleziona prima il tipo di visita!"
            testo_data.color = ft.Colors.RED_400
            griglia_orari.visible = False
            page.update()
            return
            
        date_picker.open = True
        page.update()

    page.overlay.append(date_picker)

    # 3. LOGICA DI CONFERMA SICURA
    def conferma(e):
        nome_pulito = input_nome.value.strip() if input_nome.value else ""

        if not nome_pulito or not tipo_visita_scelta or not data_selezionata or not ora_selezionata:
            testo_ora.value = "⚠️ ERRORE: Non hai compilato tutti i campi!"
            testo_ora.color = ft.Colors.RED_400  
            page.update()
            return  

        conferma_btn.disabled = True
        conferma_btn.text = "Salvataggio..."
        page.update()

        try:
            ticket = inserisci_prenotazione_db(
                nome_pulito,
                tipo_visita_scelta,
                data_selezionata,
                ora_selezionata,
            )

            testo_ticket_dinamico.value = ticket
            dialog_conferma.open = True
            
        except Exception as ex:
            testo_ora.value = f"❌ {str(ex)}"
            testo_ora.color = ft.Colors.RED_400
        finally:
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
            pulsante_menu,
            opzioni_visite,
            testo_prestazione_selezionata,
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

def crea_vista_visualizza(page: ft.Page, torna_home):
    lista_visite = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
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
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Divider(),
                testo_dettaglio_info,
            ],
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        actions=[ft.TextButton("Chiudi", on_click=chiudi_dialog_ticket)],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    if dialog_ticket not in page.overlay:
        page.overlay.append(dialog_ticket)

    def mostra_ticket_grande(data_ora, tipo, ticket):
        testo_dettaglio_ticket.value = ticket
        testo_dettaglio_info.value = f"📅 Data/Ora: {data_ora}\n🩺 Tipo visita: {tipo}"
        dialog_ticket.open = True
        page.update()

    dati = ottieni_visite_db()
    if not dati:
        lista_visite.controls.append(ft.Text("Nessuna visita prenotata.", color=ft.Colors.GREY_500))
    else:
        for data_ora, tipo, ticket in dati:
            lista_visite.controls.append(
                ft.GestureDetector(
                    on_tap=lambda e, d=data_ora, t=tipo, tk=ticket: mostra_ticket_grande(d, t, tk),
                    mouse_cursor=ft.MouseCursor.CLICK,
                    content=ft.Card(
                        content=ft.Container(
                            padding=15,
                            content=ft.Column(
                                [
                                    ft.Text(f"📅 Data/Ora: {data_ora}", weight=ft.FontWeight.BOLD),
                                    ft.Text(f"🩺 Tipo visita: {tipo}"),
                                    ft.Text(f"🎫 Ticket: {ticket}", color=ft.Colors.BLUE_300),
                                ]
                            ),
                        )
                    )
                )
            )

    return ft.Column(
        [
            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=torna_home),
            ft.Text("Le Tue Visite", size=24, weight=ft.FontWeight.BOLD),
            lista_visite,
        ],
        expand=True,
    )

def crea_vista_disdici(page: ft.Page, torna_home):
    ticket_da_cancellare = ""
    lista_disdici = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def chiudi_dialog_elimina(e):
        dialog_elimina.open = False
        page.update()

    def conferma_ed_elimina(e):
        nonlocal ticket_da_cancellare
        if ticket_da_cancellare:
            elimina_prenotazione_db(ticket_da_cancellare)
            ticket_da_cancellare = ""
            dialog_elimina.open = False
            rinfresca()
            page.snack_bar = ft.SnackBar(content=ft.Text("Prenotazione annullata con successo."))
            page.snack_bar.open = True
            page.update()

    dialog_elimina = ft.AlertDialog(
        modal=True,
        title=ft.Text("Conferma Annullamento"),
        content=ft.Text("Sei sicuro di voler disdire questa visita? L'operazione non è reversibile."),
        actions=[
            ft.TextButton("No, mantieni", on_click=chiudi_dialog_elimina),
            ft.TextButton("Sì, disdici", icon=ft.Icons.DELETE_FOREVER, icon_color=ft.Colors.RED_500, on_click=conferma_ed_elimina),
        ],
    )
    
    page.overlay.append(dialog_elimina)

    def requesting_cancellazione(ticket):
        nonlocal ticket_da_cancellare
        ticket_da_cancellare = ticket
        dialog_elimina.open = True
        page.update()

    def rinfresca():
        lista_disdici.controls.clear()
        dati = ottieni_visite_db()
        if not dati:
            lista_disdici.controls.append(ft.Text("Nessuna visita da disdire.", color=ft.Colors.GREY_500))
        else:
            for data_ora, tipo, ticket in dati:
                lista_disdici.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.CANCEL, color=ft.Colors.RED_400),
                        title=ft.Text(data_ora),
                        subtitle=ft.Text(f"{tipo} | Ticket: {ticket}"),
                        trailing=ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_color=ft.Colors.RED_500,
                            on_click=lambda e, t=ticket: requesting_cancellazione(t),
                        ),
                    )
                )
        page.update()

    rinfresca()

    return ft.Column(
        [
            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=torna_home),
            ft.Text("Annulla una Visita", size=24, weight=ft.FontWeight.BOLD),
            lista_disdici,
        ],
        expand=True,
    )

#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhkZW52enJtZ2FhZHhzeXhzcnJ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE2MTAyOTksImV4cCI6MjA5NzE4NjI5OX0.Amv_LUyJnzOOz8P7WZYUoxAbdIkz7Hi1KH5nB-jHcsE