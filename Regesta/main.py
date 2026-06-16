import flet as ft
from database import inizializza_db
import viste as v


def main(page: ft.Page):
    page.title = "Medical Booking Hub"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0F172A"

    # --- CONFIGURAZIONE SMARTPHONE SIMULATOR ---
    page.window_width = 390          # Larghezza standard di un telefono
    page.window_height = 800         # Altezza standard di un telefono
    page.window_resizable = False    # Impedisce di ridimensionarla per non rompere il layout
    # --------------------------------------------

    inizializza_db()

    contenitore_app = ft.Container(
        expand=True,
        padding=20,
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

    vista_home = ft.Column(
        controls=[
            # Sostituito ft.margin.only con ft.Margin(0, 40, 0, 40) per massima compatibilità
            ft.Container(
                content=ft.Text(
                    "Medical Hub",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_400,
                ),
                margin=ft.Margin(0, 40, 0, 40), # (sinistra, sopra, destra, sotto)
            ),
            ft.ElevatedButton(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.CALENDAR_MONTH),
                        ft.Text(
                            "Prenota una Visita",
                            size=18,
                            weight=ft.FontWeight.W_500,
                        ),
                    ]
                ),
                height=70,
                width=340,
                on_click=vai_a_prenota,
            ),
            ft.ElevatedButton(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.FORMAT_LIST_BULLETED),
                        ft.Text(
                            "Vedi Visite Prenotate",
                            size=18,
                            weight=ft.FontWeight.W_500,
                        ),
                    ]
                ),
                height=70,
                width=340,
                on_click=vai_a_visualizza,
            ),
            ft.ElevatedButton(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.DELETE),
                        ft.Text(
                            "Disdici una Visita",
                            size=18,
                            weight=ft.FontWeight.W_500,
                        ),
                    ]
                ),
                height=70,
                width=340,
                on_click=vai_a_disdici,
            ),
        ],
        spacing=15,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    contenitore_app.content = vista_home

    page.add(contenitore_app)


if __name__ == "__main__":
    ft.app(target=main)