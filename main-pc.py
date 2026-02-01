import customtkinter as ctk
import json
import os

class HeartVPNGlobal(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("HEART VPN | GLOBAL EDITION")
        self.geometry("500x650")
        self.configure(fg_color="#000000")

        # Твой конфиг
        self.UUID = "80cf3da6-2101-4c11-8541-d11025a8aa6b"
        self.WORKER_HOST = "heart-vpn-worker-global.hameleonrblx.workers.dev"

        # UI элементы (лого, теглайн)
        self.logo = ctk.CTkLabel(self, text="HEART VPN", font=("Dela Gothic One", 45), text_color="#ff0000")
        self.logo.pack(pady=(50, 5))
        
        self.tagline = ctk.CTkLabel(self, text="GLOBAL COVERAGE ENABLED", font=("Montserrat", 12, "bold"), text_color="#00ffff")
        self.tagline.pack(pady=(0, 30))

        # Выбор страны
        self.country_var = ctk.StringVar(value="United States")
        self.country_menu = ctk.CTkOptionMenu(
            self,
            values=["Kazakhstan", "United States", "United Kingdom", "Germany"],
            variable=self.country_var,
            fg_color="#111", button_color="#ff0000", font=("Dela Gothic One", 16)
        )
        self.country_menu.pack(pady=20, padx=60, fill="x")

        # Кнопка
        self.btn_connect = ctk.CTkButton(
            self, text="ENGAGE", font=("Dela Gothic One", 20),
            fg_color="#ff0000", height=70, command=self.toggle_connection
        )
        self.btn_connect.pack(pady=40, padx=60, fill="x")

        self.status = ctk.CTkLabel(self, text="STATUS: DISCONNECTED", font=("Montserrat", 10), text_color="#333")
        self.status.pack(side="bottom", pady=20)

        self.is_connected = False

    def toggle_connection(self):
        if not self.is_connected:
            country = self.country_var.get().replace(" ", "%20")
            # Генерация ссылки для подключения
            vless_link = f"vless://{self.UUID}@{self.WORKER_HOST}:443?encryption=none&security=tls&sni={self.WORKER_HOST}&type=ws&host={self.WORKER_HOST}&path=%2F%3Fcountry%3D{country}#HeartVPN_{country}"
            
            print(f"GENERATED CONFIG: {vless_link}")
            
            # Имитация запуска ядра
            self.status.configure(text=f"CONNECTED TO {self.country_var.get().upper()}", text_color="#00ff00")
            self.btn_connect.configure(text="DISCONNECT", fg_color="#1a1a1a")
            self.is_connected = True
        else:
            self.status.configure(text="STATUS: DISCONNECTED", text_color="#333")
            self.btn_connect.configure(text="ENGAGE", fg_color="#ff0000")
            self.is_connected = False

if __name__ == "__main__":
    app = HeartVPNGlobal()
    app.mainloop()
