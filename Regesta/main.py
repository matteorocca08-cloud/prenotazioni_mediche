import flet as ft
from database import inizializza_db
import viste as v
import viste_medici as vm


def main(page: ft.Page):
    # Configurazione moderna dell'aspetto grafico
    page.title = "Medical Booking Hub"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0F172A"
    
    # --- CONFIGURAZIONE SCHERMO INTERO NATIVO ---
    page.window_maximized = True
    page.window_borderless = True
    page.update()
    # --------------------------------------------
    
    # Allineamento dei componenti al centro esatto dello schermo
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    inizializza_db()

    contenitore_app = ft.Container(
        padding=40,
    )

    def mostra_home(e=None):
        contenitore_app.content = vista_home
        page.update()

    def vai_a_prenota(e):
        contenitore_app.content = v.crea_vista_prenota(page, mostra_home)
        page.update()

    def vai_a_visualizza(e):
        contenitore_app.content = v.crea_vista_visualizza(page, mostra_home)
        page.update()

    def vai_a_disdici(e):
        contenitore_app.content = v.crea_vista_disdici(page, mostra_home)
        page.update()

    def vai_a_medici(e):
        contenitore_app.content = vm.crea_vista_medici(page, mostra_home)
        page.update()

    # --- FUNZIONI DI SUPPORTO PER IL NUOVO FRONT-END ---
    def crea_card_home(titolo, sottotitolo, icona, colore_icona, on_click):
        """Genera una card moderna con effetto hover per la dashboard."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icona, size=44, color=colore_icona),
                    ft.Container(height=12),
                    ft.Text(titolo, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Container(height=4),
                    ft.Text(sottotitolo, size=12, color=ft.Colors.BLUE_GREY_200, text_align=ft.TextAlign.CENTER),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=220,
            height=220,
            bgcolor="#1E293B",
            border_radius=16,
            padding=20,
            on_click=on_click,
            # Effetto dinamico al passaggio del mouse
            on_hover=lambda e: edita_stato_hover(e),
        )

    def edita_stato_hover(e):
        e.control.bgcolor = "#273549" if e.data == "true" else "#1E293B"
        e.control.update()

    # --- NUOVO FRONT-END: INTERFACCIA A GRIGLIA (DASHBOARD) ---
    vista_home = ft.Column(
        controls=[
            ft.Container(
                content=ft.Column([
                    ft.Text("Medical Hub", size=40, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
                    ft.Text("Seleziona un'operazione per iniziare", size=14, color=ft.Colors.BLUE_GREY_300),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                margin=ft.Margin(0, 0, 0, 40),
            ),
            ft.Row(
                [
                    crea_card_home("Prenota", "Fissa un nuovo appuntamento", ft.Icons.CALENDAR_MONTH, ft.Colors.GREEN_400, vai_a_prenota),
                    crea_card_home("I tuoi appuntamenti", "Visualizza i ticket attivi", ft.Icons.SPACE_DASHBOARD, ft.Colors.BLUE_400, vai_a_visualizza),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=24,
            ),
            ft.Container(height=4),
            ft.Row(
                [
                    crea_card_home("Disdici", "Annulla una prenotazione", ft.Icons.CANCEL_OUTLINED, ft.Colors.RED_400, vai_a_disdici),
                    crea_card_home("Area Medici", "Accesso protetto personale", ft.Icons.LOCK_PERSON, ft.Colors.ORANGE_400, vai_a_medici),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=24,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # Avvio dell'applicazione impostando la home come schermata iniziale
    contenitore_app.content = vista_home
    page.add(contenitore_app)


if __name__ == "__main__":
    ft.app(target=main)