import flet as ft
import urllib.parse
import time

def main(page: ft.Page):
    # --- КОНФИГУРАЦИЯ СТРАНИЦЫ ---
    page.title = "HEART VPN | MOBILE TERMINAL"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.window_width = 400
    page.window_height = 800
    page.padding = 40
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # ТВОИ ДАННЫЕ
    UUID = "80cf3da6-2101-4c11-8541-d11025a8aa6b"
    WORKER = "heart-vpn-worker-global.hameleonrblx.workers.dev"

    # Подключение шрифта
    page.fonts = {
        "DelaGothic": "https://github.com/google/fonts/raw/main/ofl/delagothicone/DelaGothicOne-Regular.ttf"
    }

    # --- ЛОГИКА ---
    def engage_system(e):
        # Визуальный фидбек
        status_label.value = "GENERATING ENCRYPTED LINK..."
        status_label.color = "#00ffff"
        progress_bar.visible = True
        page.update()
        
        time.sleep(1) # Эффект "загрузки"
        
        country = country_dd.value
        vless_link = (
            f"vless://{UUID}@{WORKER}:443"
            f"?encryption=none&security=tls&sni={WORKER}&type=ws&host={WORKER}"
            f"&path=%2F%3Fcountry%3D{urllib.parse.quote(country)}#HeartVPN_{country}"
        )
        
        # Копируем и запускаем
        page.set_clipboard(vless_link)
        page.launch_url(vless_link)
        
        # Обновляем интерфейс после запуска
        status_label.value = f"UPLINK ESTABLISHED: {country.upper()}"
        status_label.color = "#00ff00"
        progress_bar.visible = False
        logo.color = "#00ff00" # Меняем цвет лого при активации
        page.update()

    # --- UI ЭЛЕМЕНТЫ ---
    
    # Логотип с тенью
    logo = ft.Text(
        "HEART\nVPN",
        font_family="DelaGothic",
        size=60,
        color="#ff0000",
        text_align=ft.TextAlign.CENTER,
        weight=ft.FontWeight.BOLD,
        animate_opacity=300
    )

    sub_logo = ft.Text(
        "SECURE MOBILE ENCRYPTION",
        size=10,
        color="#555555",
        weight=ft.FontWeight.BOLD,
    )

    # Карточка выбора страны
    country_dd = ft.Dropdown(
        width=320,
        label="SELECT TARGET NODE",
        hint_text="Choose country...",
        border_color="#333333",
        focused_border_color="#ff0000",
        label_style=ft.TextStyle(color="#ff0000", font_family="DelaGothic", size=12),
        text_style=ft.TextStyle(font_family="DelaGothic", color="#ffffff"),
        bgcolor="#0a0a0a",
        options=[
            ft.dropdown.Option("Germany"),
            ft.dropdown.Option("United States"),
            ft.dropdown.Option("Kazakhstan"),
            ft.dropdown.Option("United Kingdom"),
        ],
        value="Germany",
    )

    # Индикатор прогресса
    progress_bar = ft.ProgressBar(width=300, color="#ff0000", bgcolor="#1a1a1a", visible=False)

    # Основная кнопка (Массивная)
    engage_btn = ft.Container(
        content=ft.Text("ENGAGE SYSTEM", font_family="DelaGothic", size=20, color="#ffffff"),
        alignment=ft.alignment.center,
        width=320,
        height=80,
        bgcolor="#ff0000",
        on_click=engage_system,
        border_radius=0, # Квадратный стиль
        ink=True, # Эффект нажатия
    )

    # Информационная панель
    info_panel = ft.Container(
        content=ft.Column([
            ft.Row([ft.Text("PROTOCOL:", size=10, color="#444"), ft.Text("VLESS + WS", size=10, color="#888")]),
            ft.Row([ft.Text("UUID:", size=10, color="#444"), ft.Text(f"{UUID[:8]}...{UUID[-8:]}", size=10, color="#888")]),
            ft.Row([ft.Text("ENCRYPTION:", size=10, color="#444"), ft.Text("NONE (TLS-WRAPPED)", size=10, color="#888")]),
        ], spacing=5),
        padding=20,
        bgcolor="#0a0a0a",
        border=ft.border.all(1, "#1a1a1a"),
    )

    status_label = ft.Text("SYSTEM STATUS: STANDBY", color="#444", size=12, font_family="DelaGothic")

    # Сборка экрана
    page.add(
        ft.Container(height=60),
        logo,
        sub_logo,
        ft.Container(height=50),
        country_dd,
        ft.Container(height=10),
        progress_bar,
        ft.Container(height=30),
        engage_btn,
        ft.Container(height=40),
        info_panel,
        ft.Container(expand=True),
        status_label,
        ft.Text("v1.0.4 PRO BUILD", size=9, color="#222")
    )

ft.app(target=main) 
