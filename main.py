import flet as ft
from database import inizializza_db
import viste as v
import viste_medici as vm


def main(page: ft.Page):
    # Configurazione moderna dell'aspetto grafico
    page.title = "MediPrenota"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#E8F2EC"
    
    # --- ALLINEAMENTO GENERALE ---
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Inizializza la connessione al database
    inizializza_db()

    # Contenitore principale dell'applicazione con padding reattivo
    contenitore_app = ft.Container(
        padding=10,
    )

    # --- FUNZIONI DI NAVIGAZIONE ---
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

    # --- FUNZIONE COSTRUZIONE CARD REATTIVE ---
    def crea_card_home(titolo, sottotitolo, icona, colore_icona, azione):
        return ft.Container(
            content=ft.Column(
                [
                    # Corretto qui: rimosso 'name=' per evitare l'errore di inizializzazione
                    ft.Icon(icona, color=colore_icona, size=36),
                    ft.Container(height=4),
                    ft.Text(titolo, size=18, weight=ft.FontWeight.BOLD, color="#1A6B4A"),
                    ft.Container(height=2),
                    ft.Text(sottotitolo, size=11, color="#1A6B4A", text_align=ft.TextAlign.CENTER),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=160,  # Dimensione ottimale per schermi mobile stretti
            height=150,
            bgcolor="#FFFFFF",  # Colore di sfondo coerente con il tema
            border_radius=16,
            padding=10,
            on_click=azione,
        )

    # --- VISTA HOME RESPONSIVA ---
    vista_home = ft.Column(
        [
            ft.Container(
                content=ft.Column([
                    ft.Text("💚", size=50, weight=ft.FontWeight.BOLD, color="#1A6B4A", text_align=ft.TextAlign.CENTER),
                    ft.Text("MediPrenota", size=50, weight=ft.FontWeight.BOLD, color="#1A6B4A", text_align=ft.TextAlign.CENTER),
                    ft.Container(height=5),
                    ft.Text("Seleziona un'operazione per iniziare", size=13, color="#1A6B4A", text_align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                margin=ft.Margin(0, 0, 0, 15),
            ),
            # Row con wrap=True si adatta dinamicamente allo schermo disponibile
            ft.Row(
                controls=[
                    crea_card_home("Prenota", "Fissa appuntamento", ft.Icons.CALENDAR_MONTH, "#1A6B4A", vai_a_prenota),
                    crea_card_home("I tuoi impegni", "Visualizza i ticket", ft.Icons.SPACE_DASHBOARD, "#1A6B4A", vai_a_visualizza),
                    crea_card_home("Disdici", "Annulla visita", ft.Icons.CANCEL_OUTLINED, "#1A6B4A", vai_a_disdici),
                    crea_card_home("Area Medici", "Accesso protetto", ft.Icons.LOCK_PERSON, "#1A6B4A", vai_a_medici),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=12,
                run_spacing=12,
                wrap=True,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        tight=True,
        scroll=ft.ScrollMode.AUTO
    )

    # Inietta la home all'avvio
    contenitore_app.content = vista_home
    page.add(contenitore_app)


if __name__ == "__main__":
    ft.app(target=main)