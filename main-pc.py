import customtkinter as ctk
import os, json, subprocess, winreg, urllib.request, zipfile, threading, time

class HeartVPN_PC(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- ТВОИ ДАННЫЕ ---
        self.WORKER_URL = "heart-vpn-worker-global.hameleonrblx.workers.dev"
        self.UUID = "80cf3da6-2101-4c11-8541-d11025a8aa6b"
        self.XRAY_URL = "https://github.com/XTLS/Xray-core/releases/download/v1.8.4/Xray-windows-64.zip"
        self.FONT_URL = "https://github.com/google/fonts/raw/main/ofl/delagothicone/DelaGothicOne-Regular.ttf"
        
        self.APP_DATA = os.path.join(os.getenv('APPDATA'), 'HeartVPN_Core')
        self.XRAY_EXE = os.path.join(self.APP_DATA, 'xray.exe')
        self.CONFIG_JSON = os.path.join(self.APP_DATA, 'config.json')
        self.FONT_PATH = os.path.join(self.APP_DATA, 'DelaGothicOne-Regular.ttf')

        if not os.path.exists(self.APP_DATA): os.makedirs(self.APP_DATA)

        self.load_font()
        self.process = None
        self.is_running = False
        self.setup_ui()

    def load_font(self):
        if not os.path.exists(self.FONT_PATH):
            try: urllib.request.urlretrieve(self.FONT_URL, self.FONT_PATH)
            except: pass
        try:
            ctk.FontManager.load_font(self.FONT_PATH)
            self.main_font = "Dela Gothic One"
        except: self.main_font = "Arial"

    def setup_ui(self):
        self.title("HEART VPN | PC")
        self.geometry("450x650")
        self.configure(fg_color="#000")

        # LOGO
        ctk.CTkLabel(self, text="HEART VPN", font=(self.main_font, 40), text_color="#f00").pack(pady=(40, 5))
        ctk.CTkLabel(self, text="ENCRYPTED TUNNEL", font=("Arial", 10, "bold"), text_color="#0ff").pack(pady=(0, 30))

        # MENU
        self.country_var = ctk.StringVar(value="Germany")
        self.menu = ctk.CTkOptionMenu(self, values=["Kazakhstan", "United States", "Germany", "United Kingdom"], 
                                      variable=self.country_var, font=(self.main_font, 14),
                                      fg_color="#111", button_color="#f00", dropdown_font=(self.main_font, 12))
        self.menu.pack(pady=20)

        # CONSOLE
        self.console = ctk.CTkTextbox(self, height=120, fg_color="#050505", text_color="#0f0", font=("Consolas", 11))
        self.console.pack(pady=20, padx=40, fill="x")
        self.console.insert("0.0", "> SYSTEM READY\n")
        self.console.configure(state="disabled")

        # BUTTON
        self.btn = ctk.CTkButton(self, text="INITIALIZE", font=(self.main_font, 18), 
                                 fg_color="#f00", hover_color="#900", height=65, corner_radius=0, command=self.toggle_vpn)
        self.btn.pack(pady=20, padx=40, fill="x")

    def log(self, msg):
        self.console.configure(state="normal")
        self.console.insert("end", f"> {msg}\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    def toggle_vpn(self):
        threading.Thread(target=self.run_logic, daemon=True).start()

    def run_logic(self):
        if self.is_running:
            self.stop_vpn()
        else:
            self.start_vpn()

    def start_vpn(self):
        self.btn.configure(state="disabled", text="STARTING...")
        if not os.path.exists(self.XRAY_EXE):
            self.log("CORE NOT FOUND. DOWNLOADING...")
            zip_p = os.path.join(self.APP_DATA, "core.zip")
            urllib.request.urlretrieve(self.XRAY_URL, zip_p)
            with zipfile.ZipFile(zip_p, 'r') as z:
                z.extract('xray.exe', self.APP_DATA)
            os.remove(zip_p)
        
        country = self.country_var.get()
        config = {
            "inbounds": [{"port": 10808, "protocol": "socks", "settings": {"udp": True}}],
            "outbounds": [{
                "protocol": "vless",
                "settings": {"vnext": [{"address": self.WORKER_URL, "port": 443, "users": [{"id": self.UUID, "encryption": "none"}]}]},
                "streamSettings": {"network": "ws", "security": "tls", "tlsSettings": {"serverName": self.WORKER_URL},
                                  "wsSettings": {"path": f"/?country={country.replace(' ', '%20')}", "headers": {"Host": self.WORKER_URL}}}
            }]
        }
        with open(self.CONFIG_JSON, 'w') as f: json.dump(config, f)
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, "127.0.0.1:10808")
            winreg.CloseKey(key)
        except: self.log("PROXY ERROR")

        self.process = subprocess.Popen([self.XRAY_EXE, "run", "-c", self.CONFIG_JSON], creationflags=subprocess.CREATE_NO_WINDOW)
        self.is_running = True
        self.btn.configure(state="normal", text="TERMINATE", fg_color="#1a1a1a")
        self.log(f"CONNECTED: {country.upper()}")

    def stop_vpn(self):
        self.log("SHUTTING DOWN...")
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        if self.process: self.process.terminate()
        subprocess.run("taskkill /f /im xray.exe", shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        self.is_running = False
        self.btn.configure(text="INITIALIZE", fg_color="#f00")
        self.log("DISCONNECTED")

if __name__ == "__main__":
    app = HeartVPN_PC()
    app.mainloop()
