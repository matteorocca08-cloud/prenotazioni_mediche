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
    # Usiamo le proprietà classiche che non spaccano l'avvio
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

    

    # Struttura dei bottoni con la sintassi pulita
    vista_home = ft.Column(
        controls=[
            ft.Container(
                content=ft.Text(
                    "Medical Hub",
                    size=40,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_400,
                ),
                margin=ft.Margin(0, 0, 0, 40),
            ),
            ft.ElevatedButton(
                content=ft.Row([ft.Icon(ft.Icons.CALENDAR_MONTH), ft.Text("Prenota una Visita", size=18, weight=ft.FontWeight.W_500)], alignment=ft.MainAxisAlignment.CENTER),
                height=70, width=450, on_click=vai_a_prenota,
            ),
            ft.ElevatedButton(
                content=ft.Row([ft.Icon(ft.Icons.FORMAT_LIST_BULLETED), ft.Text("Vedi Visite Prenotate", size=18, weight=ft.FontWeight.W_500)], alignment=ft.MainAxisAlignment.CENTER),
                height=70, width=450, on_click=vai_a_visualizza,
            ),
            ft.ElevatedButton(
                content=ft.Row([ft.Icon(ft.Icons.DELETE), ft.Text("Disdici una Visita", size=18, weight=ft.FontWeight.W_500)], alignment=ft.MainAxisAlignment.CENTER),
                height=70, width=450, on_click=vai_a_disdici,
            ),
            ft.ElevatedButton(
                content=ft.Row([ft.Icon(ft.Icons.LOCK_PERSON), ft.Text("Area Riservata Medici", size=18, weight=ft.FontWeight.W_500)], alignment=ft.MainAxisAlignment.CENTER),
                height=70, width=450, on_click=vai_a_medici,
                style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_GREY_800) # Colore diverso per distinguerlo
            ),
        ],
        spacing=20,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    contenitore_app.content = vista_home
    page.add(contenitore_app)


if __name__ == "__main__":
    # Torniamo a ft.app che è supportato ovunque ed evita il TypeError del terminale
    ft.app(target=main)