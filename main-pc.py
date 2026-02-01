import customtkinter as ctk
import os
import urllib.request
import zipfile
import subprocess
import winreg

class HeartVPNRaw(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Ссылка на прямую загрузку ядра (пример с проверенного источника)
        # ВАЖНО: Обычно Xray идет в .zip, поэтому добавим распаковку
        self.XRAY_ZIP_URL = "https://github.com/XTLS/Xray-core/releases/download/v1.8.4/Xray-windows-64.zip"
        self.APP_DATA = os.path.join(os.getenv('APPDATA'), 'HeartVPN_Engine')
        self.XRAY_EXE = os.path.join(self.APP_DATA, 'xray.exe')
        
        if not os.path.exists(self.APP_DATA):
            os.makedirs(self.APP_DATA)

        self.setup_ui()

    def setup_ui(self):
        self.title("HEART VPN | GLOBAL TERMINAL")
        self.geometry("500x600")
        self.configure(fg_color="#000")

        self.logo = ctk.CTkLabel(self, text="HEART VPN", font=("Dela Gothic One", 45), text_color="#ff0000")
        self.logo.pack(pady=40)

        self.country_var = ctk.StringVar(value="Germany")
        self.menu = ctk.CTkOptionMenu(self, values=["Kazakhstan", "United States", "Germany", "United Kingdom"], 
                                      variable=self.country_var, fg_color="#111", button_color="#ff0000")
        self.menu.pack(pady=20)

        self.btn = ctk.CTkButton(self, text="INITIALIZE", fg_color="#ff0000", height=60, command=self.start_vpn)
        self.btn.pack(pady=30, padx=60, fill="x")

        self.status = ctk.CTkLabel(self, text="WAITING FOR COMMAND", text_color="#444", font=("Montserrat", 10))
        self.status.pack(side="bottom", pady=20)

    def download_and_extract(self):
        """Скачивает zip и достает только xray.exe"""
        if not os.path.exists(self.XRAY_EXE):
            self.status.configure(text="DOWNLOADING CORE FROM REMOTE REPO...", text_color="#00ffff")
            self.update()
            zip_path = os.path.join(self.APP_DATA, "core.zip")
            try:
                # Качаем
                urllib.request.urlretrieve(self.XRAY_ZIP_URL, zip_path)
                # Распаковываем
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extract('xray.exe', self.APP_DATA)
                os.remove(zip_path) # Удаляем архив за собой
                return True
            except Exception as e:
                self.status.configure(text=f"ERROR: {e}", text_color="#ff0000")
                return False
        return True

    def set_sys_proxy(self, enable=True):
        proxy_key = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, proxy_key, 0, winreg.KEY_WRITE) as key:
            if enable:
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, "127.0.0.1:10808")
            else:
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)

    def start_vpn(self):
        if self.download_and_extract():
            self.set_sys_proxy(True)
            # Эмуляция запуска (для реального запуска нужен еще файл config.json)
            self.btn.configure(text="SHUTDOWN", fg_color="#1a1a1a", command=self.stop_vpn)
            self.status.configure(text=f"ENCRYPTED TUNNEL: {self.country_var.get().upper()}", text_color="#00ff00")

    def stop_vpn(self):
        self.set_sys_proxy(False)
        # Убиваем процесс если он запущен
        os.system("taskkill /f /im xray.exe >nul 2>&1")
        self.btn.configure(text="INITIALIZE", fg_color="#ff0000", command=self.start_vpn)
        self.status.configure(text="STATUS: DISCONNECTED", text_color="#444")

if __name__ == "__main__":
    app = HeartVPNRaw()
    app.mainloop()
