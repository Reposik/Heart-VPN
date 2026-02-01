import customtkinter as ctk
import os
import json
import subprocess
import winreg
import urllib.request
import zipfile
import threading
import time
import sys

# Настройки темы
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class HeartVPNUltimate(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- КОНФИГУРАЦИЯ ---
        self.WORKER_URL = "heart-vpn-worker-global.hameleonrblx.workers.dev"
        self.UUID = "80cf3da6-2101-4c11-8541-d11025a8aa6b"
        
        # Ссылки
        self.XRAY_URL = "https://github.com/XTLS/Xray-core/releases/download/v1.8.4/Xray-windows-64.zip"
        self.FONT_URL = "https://github.com/google/fonts/raw/main/ofl/delagothicone/DelaGothicOne-Regular.ttf"
        
        # Пути
        self.APP_DATA = os.path.join(os.getenv('APPDATA'), 'HeartVPN_Core')
        self.XRAY_EXE = os.path.join(self.APP_DATA, 'xray.exe')
        self.CONFIG_JSON = os.path.join(self.APP_DATA, 'config.json')
        self.FONT_PATH = os.path.join(self.APP_DATA, 'DelaGothicOne-Regular.ttf')

        # Создаем папку если нет
        if not os.path.exists(self.APP_DATA):
            os.makedirs(self.APP_DATA)

        # 1. СНАЧАЛА ГРУЗИМ ШРИФТ (чтобы интерфейс сразу был красивым)
        self.load_custom_font()

        # Переменные состояния
        self.process = None
        self.is_running = False

        # --- ИНТЕРФЕЙС (GUI) ---
        self.setup_ui()

    def load_custom_font(self):
        """Скачивает и регистрирует шрифт Dela Gothic One"""
        if not os.path.exists(self.FONT_PATH):
            try:
                print("Downloading Font...")
                urllib.request.urlretrieve(self.FONT_URL, self.FONT_PATH)
            except Exception as e:
                print(f"Font Download Error: {e}")
        
        # Пытаемся загрузить шрифт в CustomTkinter
        try:
            ctk.FontManager.load_font(self.FONT_PATH)
            self.my_font = "Dela Gothic One" # Если успешно, используем его
        except Exception:
            self.my_font = "Arial" # Если ошибка, запасной вариант

    def setup_ui(self):
        self.title("HEART VPN | TERMINAL ACCESS")
        self.geometry("500x700")
        self.configure(fg_color="#000000") # Чистый черный
        self.resizable(False, False)

        # 1. Логотип (Теперь с твоим шрифтом!)
        self.logo_label = ctk.CTkLabel(
            self, 
            text="HEART VPN", 
            font=(self.my_font, 45), 
            text_color="#ff0000"
        )
        self.logo_label.pack(pady=(40, 5))

        self.sub_logo = ctk.CTkLabel(
            self, 
            text="SECURE GLOBAL TUNNELING", 
            font=("Montserrat", 10, "bold"), # Для мелкого текста лучше читаемый шрифт
            text_color="#00ffff",
            spacing=2
        )
        self.sub_logo.pack(pady=(0, 30))

        # 2. Выбор страны
        self.country_frame = ctk.CTkFrame(self, fg_color="#111", border_color="#333", border_width=1)
        self.country_frame.pack(pady=10, padx=40, fill="x")

        self.label_country = ctk.CTkLabel(self.country_frame, text="TARGET NODE", font=(self.my_font, 12), text_color="#888")
        self.label_country.pack(pady=(15, 5))

        self.country_var = ctk.StringVar(value="Germany")
        self.country_menu = ctk.CTkOptionMenu(
            self.country_frame,
            values=["Kazakhstan", "United States", "Germany", "United Kingdom"],
            variable=self.country_var,
            fg_color="#000",
            button_color="#ff0000",
            button_hover_color="#cc0000",
            dropdown_fg_color="#111",
            font=(self.my_font, 14), # Шрифт в меню
            dropdown_font=(self.my_font, 14), # Шрифт в выпадающем списке
            height=40
        )
        self.country_menu.pack(pady=(0, 20), padx=20, fill="x")

        # 3. Консоль
        self.console = ctk.CTkTextbox(
            self, 
            height=150, 
            fg_color="#050505", 
            text_color="#00ff00", 
            font=("Consolas", 12),
            activate_scrollbars=False,
            border_width=1,
            border_color="#222"
        )
        self.console.pack(pady=20, padx=40, fill="x")
        self.console.insert("0.0", "> SYSTEM READY...\n> WAITING FOR USER INPUT...\n")
        self.console.configure(state="disabled") 

        # 4. Главная кнопка
        self.btn_connect = ctk.CTkButton(
            self,
            text="INITIALIZE",
            font=(self.my_font, 20), # Кнопка с твоим шрифтом
            fg_color="#ff0000",
            hover_color="#b30000",
            height=70,
            corner_radius=0, # Острые углы для стиля
            command=self.toggle_vpn_thread
        )
        self.btn_connect.pack(pady=30, padx=40, fill="x")

        # 5. Статус
        self.status_label = ctk.CTkLabel(self, text="STATUS: STANDBY", text_color="#555", font=("Consolas", 10))
        self.status_label.pack(side="bottom", pady=15)

    def log(self, message):
        self.console.configure(state="normal")
        self.console.insert("end", f"> {message}\n")
        self.console.see("end") 
        self.console.configure(state="disabled")

    def toggle_vpn_thread(self):
        threading.Thread(target=self.toggle_vpn, daemon=True).start()

    def toggle_vpn(self):
        if self.is_running:
            self.stop_engine()
        else:
            self.start_engine()

    def download_core(self):
        if not os.path.exists(self.XRAY_EXE):
            self.log("CORE NOT FOUND. DOWNLOADING...")
            self.status_label.configure(text="DOWNLOADING ENGINE...", text_color="#00ffff")
            try:
                zip_path = os.path.join(self.APP_DATA, "core.zip")
                urllib.request.urlretrieve(self.XRAY_URL, zip_path)
                self.log("DOWNLOAD COMPLETE. EXTRACTING...")
                
                with zipfile.ZipFile(zip_path, 'r') as z:
                    z.extract('xray.exe', self.APP_DATA)
                
                os.remove(zip_path)
                self.log("CORE INSTALLED SUCCESSFULLY.")
                return True
            except Exception as e:
                self.log(f"ERROR: {str(e)}")
                self.status_label.configure(text="DOWNLOAD ERROR", text_color="#ff0000")
                return False
        return True

    def create_config(self):
        self.log(f"GENERATING CONFIG FOR: {self.country_var.get().upper()}")
        country = self.country_var.get()
        
        config = {
            "log": {"loglevel": "none"},
            "inbounds": [{"port": 10808, "protocol": "socks", "settings": {"udp": True, "auth": "noauth"}}],
            "outbounds": [{
                "protocol": "vless",
                "settings": {
                    "vnext": [{
                        "address": self.WORKER_URL,
                        "port": 443,
                        "users": [{"id": self.UUID, "encryption": "none"}]
                    }]
                },
                "streamSettings": {
                    "network": "ws",
                    "security": "tls",
                    "tlsSettings": {"serverName": self.WORKER_URL},
                    "wsSettings": {
                        "path": f"/?country={country.replace(' ', '%20')}",
                        "headers": {"Host": self.WORKER_URL}
                    }
                }
            }]
        }
        
        try:
            with open(self.CONFIG_JSON, 'w') as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            self.log(f"CONFIG ERROR: {e}")
            return False

    def set_proxy(self, enable=True):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0, winreg.KEY_WRITE)
            if enable:
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, "127.0.0.1:10808")
                self.log("WINDOWS PROXY: ENABLED (127.0.0.1:10808)")
            else:
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
                self.log("WINDOWS PROXY: DISABLED")
            winreg.CloseKey(key)
        except Exception as e:
            self.log(f"REGISTRY ERROR: {e}")

    def start_engine(self):
        self.btn_connect.configure(state="disabled", text="STARTING...")
        
        if not self.download_core():
            self.btn_connect.configure(state="normal", text="RETRY CONNECTION")
            return

        if not self.create_config():
            return

        try:
            self.log("STARTING XRAY ENGINE...")
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            self.process = subprocess.Popen(
                [self.XRAY_EXE, "run", "-c", self.CONFIG_JSON],
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            time.sleep(1)
            if self.process.poll() is None:
                self.set_proxy(True)
                self.is_running = True
                
                self.btn_connect.configure(state="normal", text="TERMINATE", fg_color="#1a1a1a")
                self.status_label.configure(text=f"SECURE TUNNEL: {self.country_var.get().upper()}", text_color="#00ff00")
                self.log("CONNECTION ESTABLISHED.")
            else:
                self.log("ENGINE CRASHED ON START.")
                self.btn_connect.configure(state="normal", text="INITIALIZE")

        except Exception as e:
            self.log(f"CRITICAL ERROR: {e}")
            self.btn_connect.configure(state="normal", text="INITIALIZE")

    def stop_engine(self):
        self.btn_connect.configure(state="disabled", text="STOPPING...")
        self.log("SHUTTING DOWN SERVICE...")
        
        self.set_proxy(False)
        
        if self.process:
            self.process.terminate()
            self.process = None
        
        subprocess.run("taskkill /f /im xray.exe", shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        self.is_running = False
        self.btn_connect.configure(state="normal", text="INITIALIZE", fg_color="#ff0000")
        self.status_label.configure(text="STATUS: DISCONNECTED", text_color="#555")
        self.log("SERVICE STOPPED.")

    def on_close(self):
        if self.is_running:
            self.stop_engine()
        self.destroy()

if __name__ == "__main__":
    app = HeartVPNUltimate()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
