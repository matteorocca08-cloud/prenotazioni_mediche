import flet as ft
from database import inizializza_db
import viste as v


def main(page: ft.Page):
    page.title = "Medical Booking Hub"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0F172A"

    page.window_width = 390
    page.window_height = 800
    page.window_resizable = False

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
        contenitore_app.content = v.crea_vista_visualizza(mostra_home)
        page.update()

    def vai_a_disdici(e):
        contenitore_app.content = v.crea_vista_disdici(page, mostra_home)
        page.update()

    vista_home = ft.Column(
        controls=[
            ft.Container(height=20),

            ft.Text(
                "Benvenuto nella tua App Medica",
                size=24,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            ),

            ft.Text( 
                "Cosa desideri fare oggi?",
                size=16,
                color=ft.Colors.GREY_400,
                text_align=ft.TextAlign.CENTER,
            ),

            ft.Container(height=20),

            ft.ElevatedButton(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.ADD_CIRCLE),
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