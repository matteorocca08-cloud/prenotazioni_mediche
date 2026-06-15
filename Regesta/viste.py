import flet as ft

from database import (
    inserisci_prenotazione_db,
    ottieni_visite_db,
    elimina_prenotazione_db,
)


import flet as ft

from database import (
    inserisci_prenotazione_db,
    ottieni_visite_db,
    elimina_prenotazione_db,
)


def crea_vista_prenota(page: ft.Page, torna_home):
    data_selezionata = ""
    ora_selezionata = ""

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
    
    # Correzione dell'errore: assegniamo l'evento on_change qui sotto
    dropdown_visita.on_change = lambda e: aggiorna_griglia_orari()

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

    def cambio_data(e):
        nonlocal data_selezionata

        if date_picker.value:
            data_selezionata = date_picker.value.strftime("%Y-%m-%d")

            testo_data.value = (
                f"📅 Data: {date_picker.value.strftime('%d/%m/%Y')}"
            )

            aggiorna_griglia_orari()

    def cambio_ora(ora):
        nonlocal ora_selezionata

        ora_selezionata = ora
        testo_ora.value = f"⏰ Ora: {ora}"
        page.update()

    date_picker = ft.DatePicker(
        on_change=cambio_data,
    )

    page.overlay.append(date_picker)

    griglia_orari = ft.Row(
        wrap=True,
        visible=False,
    )

    # Funzione dinamica che genera gli orari in base alla tipologia di visita
    def aggiorna_griglia_orari():
        if not data_selezionata or not dropdown_visita.value:
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

        for ora in orari_disponibili:
            griglia_orari.controls.append(
                ft.OutlinedButton(
                    ora,
                    on_click=lambda e, o=ora: cambio_ora(o),
                )
            )
        
        griglia_orari.visible = True
        page.update()

    def conferma(e):
        if (
            not input_nome.value
            or not dropdown_visita.value
            or not data_selezionata
            or not ora_selezionata
        ):
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Compila tutti i campi!")
            )
            page.snack_bar.open = True
            page.update()
            return

        ticket = inserisci_prenotazione_db(
            input_nome.value,
            dropdown_visita.value,
            data_selezionata,
            ora_selezionata,
        )

        def chiudi_dialog(e):
            dialog.open = False
            page.update()
            torna_home(e)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Prenotazione Confermata",
                color=ft.Colors.GREEN_400,
            ),
            content=ft.Column(
                [
                    ft.Text(
                        "Il tuo ticket univoco è:",
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(
                        content=ft.Text(
                            ticket,
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLACK,
                        ),
                        bgcolor=ft.Colors.AMBER_300,
                        padding=10,
                        border_radius=8,
                    ),
                ],
                tight=True,
            ),
            actions=[
                ft.TextButton(
                    "OK",
                    on_click=chiudi_dialog,
                )
            ],
        )

        page.open(dialog)

    date_picker = ft.DatePicker(
        on_change=cambio_data,
    )

    # Inserisci questa funzione qui:
    def apri_calendario():
        date_picker.open = True  # Dice a Flet di mostrare il calendario
        page.update()            # Forza l'aggiornamento grafico della pagina

    page.overlay.append(date_picker)
    
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
                on_click=lambda _: apri_calendario(), # Chiama la funzione di apertura
            ),

            testo_data,
            griglia_orari,
            testo_ora,

            ft.Divider(),

            ft.ElevatedButton(
                "Conferma Prenotazione",
                icon=ft.Icons.CHECK,
                on_click=conferma,
            ),
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


def crea_vista_disdici(page: ft.Page, torna_home):
    lista_disdici = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    def cancella(ticket):
        elimina_prenotazione_db(ticket)
        rinfresca()

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
                            on_click=lambda e, t=ticket: cancella(t),
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


def crea_vista_disdici(page: ft.Page, torna_home):
    lista_disdici = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    def cancella(ticket):
        elimina_prenotazione_db(ticket)
        rinfresca()

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
                            on_click=lambda e, t=ticket: cancella(t),
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