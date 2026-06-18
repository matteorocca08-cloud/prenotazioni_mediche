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

    # 1. POP-UP DI CONFERMA PRENOTAZIONE (Inalterato)
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

    # 2. SELETTORE DI PRESTAZIONE GRAFICO A CARD MODERNE
    testo_prestazione_selezionata = ft.Text(
        "Nessuna prestazione selezionata",
        size=16,
        weight=ft.FontWeight.W_500,
        color=ft.Colors.AMBER_400
    )

    def seleziona_prestazione(tipo, container_selezionato):
        nonlocal tipo_visita_scelta, data_selezionata, ora_selezionata
        tipo_visita_scelta = tipo
        testo_prestazione_selezionata.value = f"🩺 Prestazione: {tipo}"
        testo_prestazione_selezionata.color = ft.Colors.GREEN_400
        
        # Azzeramento logico originale delle selezioni temporali
        data_selezionata = ""
        ora_selezionata = ""
        testo_data.value = "Visita modificata. Seleziona nuovamente il giorno."
        testo_data.color = ft.Colors.AMBER_400
        testo_ora.value = "Nessun orario selezionato"
        testo_ora.color = ft.Colors.GREY_400
        
        # Feedback visivo di selezione sulle card (Effetto bottone attivo)
        for c in mazzo_card:
            if c == container_selezionato:
                c.bgcolor = ft.Colors.BLUE_800
            else:
                c.bgcolor = "#1E293B"
            c.update()

        griglia_orari.visible = False
        page.update()

    def crea_card_reparto(nome, icona, colore):
        c = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icona, size=32, color=colore),
                    ft.Text(
                        nome, 
                        size=12, 
                        weight=ft.FontWeight.BOLD, 
                        text_align=ft.TextAlign.CENTER,
                        max_lines=2,
                    )
                ], 
                alignment=ft.MainAxisAlignment.CENTER, 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8
            ),
            width=140,
            height=100,
            border_radius=12,
            bgcolor="#1E293B",
            padding=10
        )
        c.on_click = lambda e: seleziona_prestazione(nome, c)
        return c

    # Definizione delle card grafiche stabili
    card_generale = crea_card_reparto("Controllo Generale", ft.Icons.LOCAL_HOSPITAL, ft.Colors.BLUE_400)
    card_dentista = crea_card_reparto("Dentista", ft.Icons.HEALING, ft.Colors.TEAL_400)
    card_specialista = crea_card_reparto("Visita Specialistica", ft.Icons.ASSIGNMENT_IND, ft.Colors.PURPLE_400)
    
    mazzo_card = [card_generale, card_dentista, card_specialista]

    input_nome = ft.TextField(
        label="Nome Paziente",
        border_color=ft.Colors.BLUE_400,
        width=440
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
        width=440,
        alignment=ft.MainAxisAlignment.CENTER
    )

    # LA TUA LOGICA DI GENERAZIONE SLOT DINAMICI (Inalterata e protetta)
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
            # Ripristinato l'ordine esatto dei tuoi parametri: tipo, data, ora
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

    # --- FUNZIONE MANCANTE RIPRISTINATA ---
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

    # LA TUA LOGICA DI CONFERMA FINALE SU SUPABASE (Inalterata)
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
            # Chiamata originale sicura al 100% con i 4 parametri esatti
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
        width=440,
        height=50,
        bgcolor=ft.Colors.BLUE_600,
        style=ft.ButtonStyle(color=ft.Colors.WHITE)
    )

    # NUOVO CORREDO GRAFICO ORDINATO A COLONNA CENTRATA
    return ft.Column(
        [
            ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=torna_home, icon_color=ft.Colors.BLUE_400),
                ft.Text("Nuova Prenotazione", size=24, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.START, width=440),
            
            ft.Container(height=10),
            input_nome,
            
            ft.Container(height=10),
            ft.Text("Seleziona il Reparto Medico", size=14, color=ft.Colors.BLUE_GREY_300),
            ft.Row([card_generale, card_dentista, card_specialista], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            testo_prestazione_selezionata,
            
            ft.Container(height=10),
            ft.ElevatedButton(
                "Seleziona Giorno",
                icon=ft.Icons.CALENDAR_MONTH,
                on_click=apri_calendario,
                width=440,
                height=50
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
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

def crea_vista_visualizza(page: ft.Page, torna_home):
    lista_visite = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=15)
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

    # Recupero dati originale da Supabase
    dati = ottieni_visite_db()
    if not dati:
        lista_visite.controls.append(
            ft.Container(
                content=ft.Text("Nessuna visita prenotata al momento.", color=ft.Colors.BLUE_GREY_400, size=16),
                padding=20,
                # RISOLTO: Rimosso completamente l'allineamento problematico
            )
        )
    else:
        for data_ora, tipo, ticket in dati:
            icona_visita = ft.Icons.LOCAL_HOSPITAL
            colore_icona = ft.Colors.BLUE_400
            if tipo == "Dentista":
                icona_visita = ft.Icons.HEALING
                colore_icona = ft.Colors.TEAL_400
            elif tipo == "Visita Specialistica":
                icona_visita = ft.Icons.ASSIGNMENT_IND
                colore_icona = ft.Colors.PURPLE_400

            lista_visite.controls.append(
                ft.GestureDetector(
                    on_tap=lambda e, d=data_ora, t=tipo, tk=ticket: mostra_ticket_grande(d, t, tk),
                    mouse_cursor=ft.MouseCursor.CLICK,
                    content=ft.Container(
                        padding=18,
                        bgcolor="#1E293B",
                        border_radius=14,
                        content=ft.Row(
                            [
                                # Icona identificativa sulla sinistra
                                ft.Container(
                                    content=ft.Icon(icona_visita, size=30, color=colore_icona),
                                    bgcolor="#0F172A",
                                    padding=12,
                                    border_radius=10,
                                ),
                                # Dettagli centrali dell'appuntamento
                                ft.Column(
                                    [
                                        ft.Text(tipo, size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                        ft.Text(f"📅 {data_ora}", size=14, color=ft.Colors.BLUE_GREY_200),
                                    ],
                                    spacing=4,
                                    expand=True,
                                ),
                                # Badge del Ticket sulla destra
                                ft.Container(
                                    content=ft.Text(ticket, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
                                    bgcolor="#0F172A",
                                    padding=12,
                                    border_radius=8,
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    )
                )
            )

    return ft.Column(
        [
            ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=torna_home, icon_color=ft.Colors.BLUE_400),
                ft.Text("Le Tue Visite", size=24, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.START, width=440),
            
            ft.Container(height=10),
            ft.Text("Clicca su un appuntamento per mostrare il promemoria completo", size=13, color=ft.Colors.BLUE_GREY_400),
            ft.Container(height=5),
            lista_visite,
        ],
        expand=True,
        width=440,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

def crea_vista_disdici(page: ft.Page, torna_home):
    lista_disdici = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=15)
    ticket_da_cancellare = None

    def conferma_eliminazione(e):
        nonlocal ticket_da_cancellare
        if ticket_da_cancellare:
            esito = elimina_prenotazione_db(ticket_da_cancellare)
            if esito:
                dialog_elimina.open = False
                rinfresca()
            else:
                dialog_elimina.title = ft.Text("Errore durante l'eliminazione", color=ft.Colors.RED_400)
                page.update()

    def chiudi_dialog_elimina(e):
        dialog_elimina.open = False
        page.update()

    dialog_elimina = ft.AlertDialog(
        title=ft.Text("Conferma Annullamento", weight=ft.FontWeight.BOLD),
        content=ft.Text("Sei sicuro di voler disdire questa visita medica? L'azione è irreversibile."),
        actions=[
            ft.TextButton("No, mantieni", on_click=chiudi_dialog_elimina),
            ft.TextButton("Sì, disdici", on_click=conferma_eliminazione, style=ft.ButtonStyle(color=ft.Colors.RED_400)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    if dialog_elimina not in page.overlay:
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
            lista_disdici.controls.append(
                ft.Container(
                    content=ft.Text("Nessuna visita da disdire.", color=ft.Colors.BLUE_GREY_400, size=16),
                    padding=20
                )
            )
        else:
            for data_ora, tipo, ticket in dati:
                lista_disdici.controls.append(
                    ft.Container(
                        padding=15,
                        bgcolor="#1E293B",
                        border_radius=14,
                        content=ft.Row(
                            [
                                # Icona Cestino/Alert sulla sinistra
                                ft.Container(
                                    content=ft.Icon(ft.Icons.REPORT_PROBLEM, size=24, color=ft.Colors.RED_400),
                                    bgcolor="#2A1F2D",
                                    padding=10,
                                    border_radius=10,
                                ),
                                # Dettagli centrali dell'appuntamento da rimuovere
                                ft.Column(
                                    [
                                        ft.Text(tipo, size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                        ft.Text(f"📅 {data_ora}", size=13, color=ft.Colors.BLUE_GREY_200),
                                        ft.Text(f"Ticket: {ticket}", size=11, color=ft.Colors.BLUE_400, weight=ft.FontWeight.W_500),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                                # Pulsante Elimina Professionale sulla destra
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_FOREVER,
                                    icon_color=ft.Colors.RED_400,
                                    icon_size=26,
                                    tooltip="Annulla questo appuntamento",
                                    on_click=lambda e, t=ticket: requesting_cancellazione(t),
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    )
                )
        page.update()

    rinfresca()

    return ft.Column(
        [
            ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=torna_home, icon_color=ft.Colors.BLUE_400),
                ft.Text("Annulla una Visita", size=24, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.START, width=440),
            
            ft.Container(height=10),
            ft.Text("Seleziona l'appuntamento che desideri cancellare definitivamente:", size=13, color=ft.Colors.BLUE_GREY_400),
            ft.Container(height=5),
            lista_disdici,
        ],
        expand=True,
        width=440,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhkZW52enJtZ2FhZHhzeXhzcnJ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE2MTAyOTksImV4cCI6MjA5NzE4NjI5OX0.Amv_LUyJnzOOz8P7WZYUoxAbdIkz7Hi1KH5nB-jHcsE