import flet as ft
from database import ottieni_visite_db, elimina_prenotazione_db, verifica_login_medico

def crea_vista_medici(page: ft.Page, torna_home):
    reparto_medico = None  

    # --- ELEMENTI GRAFICI LOGIN ---
    input_user = ft.TextField(label="Username Medico", width=300,)
    input_pass = ft.TextField(label="Password", password=True, can_reveal_password=True, width=300,)
    testo_errore = ft.Text("", color=ft.Colors.RED_400, weight=ft.FontWeight.BOLD,)

    # --- ELEMENTI GRAFICI PANNELLO MEDICI ---
    titolo_reparto = ft.Text("", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400, )
    lista_visite_medico = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=400, width=500, )

    contenitore_interno = ft.Container()

    def rinfresca_visite_reparto():
        """Recupera le visite dal cloud e mostra solo quelle del reparto corrente."""
        lista_visite_medico.controls.clear()
        tutte_le_visite = ottieni_visite_db()
        
        # Filtro per reparto usando la chiave corretta dei dizionari ('tipo_visita')
        visite_filtrate = []
        for v in tutte_le_visite:
            if isinstance(v, dict):
                if v.get("tipo_visita") == reparto_medico:
                    visite_filtrate.append(v)

        if not visite_filtrate:
            lista_visite_medico.controls.append(
                ft.Text("Nessuna visita in attesa per questo reparto.", color="#BA0000", size=16)
            )
        else:
            for v in visite_filtrate:
                # Estraiamo i campi in modo sicuro dal dizionario
                data_ora = v.get("data_ora", "N/D")
                ticket = v.get("ticket", "N/D")
                paziente = v.get("paziente", "N/D") # Ora possiamo leggere anche il nome del paziente!

                lista_visite_medico.controls.append(
                    ft.Container(
                        content=ft.ListTile(
                            leading=ft.Icon(ft.Icons.MEDICATION, color="#1A6B4A"),
                            title=ft.Text(f"Orario: {data_ora} - Paziente: {paziente}"),
                            subtitle=ft.Text(f"Ticket: {ticket}"),
                            trailing=ft.ElevatedButton(
                                content=ft.Text("Concludi Visita", color="#FFFFFF"),
                                bgcolor="#1A6B4A",
                                on_click=lambda e, t=ticket: esegui_conclusione_visita(t)
                            ),
                        ),
                        bgcolor="#FFFFFF",
                        border_radius=10,
                        padding=5
                    )
                )
        page.update()

    def esegui_conclusione_visita(ticket):
        """Richiama il metodo di eliminazione per concludere ed eliminare la visita."""
        if elimina_prenotazione_db(ticket):
            rinfresca_visite_reparto()

    def gestisci_login(e):
        nonlocal reparto_medico
        username = input_user.value
        password = input_pass.value

        reparto_trovato = verifica_login_medico(username, password)
        
        if reparto_trovato:
            reparto_medico = reparto_trovato
            testo_errore.value = ""
            mostra_pannello_medico()
        else:
            testo_errore.value = "Credenziali errate! Riprova."
            page.update()

    def mostra_pannello_medico():
        titolo_reparto.value = f"Pannello Medico: {reparto_medico}"
        titolo_reparto.color = "#1A6B4A"
        contenitore_interno.content = ft.Column(
            controls=[
                titolo_reparto,
                ft.Container(height=10),
                lista_visite_medico,
                ft.Container(height=20),
                ft.Row([
                    ft.ElevatedButton("Aggiorna Lista",bgcolor="#1A6B4A", on_click=lambda e: rinfresca_visite_reparto(),color="#FFFFFF"),
                    ft.ElevatedButton("Esci / Log out",bgcolor="#1A6B4A", on_click=torna_home, color="#FFFFFF"),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=500)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        rinfresca_visite_reparto()

    # Layout Schermata Login Iniziale
    vista_login = ft.Column(
        controls=[
            ft.Text("Accesso Riservato Medici", size=28, weight=ft.FontWeight.BOLD, color="#1A6B4A",),
            ft.Container(height=20),
            input_user,
            input_pass,
            testo_errore,
            ft.Container(height=10),
            ft.ElevatedButton("Accedi", color="#1A6B4A", on_click=gestisci_login, width=300, height=50, bgcolor="#FFFFFF",),
            ft.ElevatedButton("Torna alla Home Clienti", color="#1A6B4A", on_click=torna_home, bgcolor="#FFFFFF",),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    contenitore_interno.content = vista_login
    return contenitore_interno