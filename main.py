import os, sys, json, time, threading, subprocess, zipfile, requests, winreg
import customtkinter as ctk
from datetime import datetime

# =================================================================
# HEART VPN - ULTIMATE GOTHIC MONOLITH
# WORKER: curly-wave-032c.hameleonrblx.workers.dev
# =================================================================

class HeartVPN_System:
    def __init__(self):
        self.root = os.path.join(os.environ['LOCALAPPDATA'], 'HeartVPN_Final')
        self.bin = os.path.join(self.root, 'bin')
        self.core_exe = os.path.join(self.bin, 'xray.exe')
        self.config_p = os.path.join(self.bin, 'config.json')
        
        # ТВОИ ЖИВЫЕ ДАННЫЕ
        self.worker_url = "curly-wave-032c.hameleonrblx.workers.dev" 
        self.uuid = "9a2e775b-ab2f-4f45-af3f-0b5664fb7c61"
        
        if not os.path.exists(self.bin): os.makedirs(self.bin)

    def download_core(self, log_func):
        if os.path.exists(self.core_exe): return True
        log_func("DOWNLOADING CORE ENGINE...")
        try:
            # Прямая ссылка на официальный стабильный Xray
            r = requests.get("https://github.com/XTLS/Xray-core/releases/latest/download/Xray-windows-64.zip", timeout=20)
            zip_p = os.path.join(self.root, "temp.zip")
            with open(zip_p, 'wb') as f: f.write(r.content)
            with zipfile.ZipFile(zip_p, 'r') as z: z.extractall(self.bin)
            os.remove(zip_p)
            return True
        except Exception as e:
            log_func(f"DL ERROR: {e}")
            return False

    def build_config(self):
        # Конфиг под твой Cloudflare Worker
        cfg = {
            "log": {"loglevel": "none"},
            "inbounds": [{"port": 10809, "listen": "127.0.0.1", "protocol": "socks", "settings": {"udp": True}}],
            "outbounds": [{
                "protocol": "vless",
                "settings": {
                    "vnext": [{
                        "address": self.worker_url,
                        "port": 443,
                        "users": [{"id": self.uuid, "encryption": "none"}]
                    }]
                },
                "streamSettings": {
                    "network": "ws",
                    "security": "tls",
                    "tlsSettings": {"serverName": self.worker_url},
                    "wsSettings": {"path": "/"}
                }
            }, {"protocol": "freedom", "tag": "direct"}]
        }
        with open(self.config_p, 'w') as f: json.dump(cfg, f, indent=4)

class HeartUI(ctk.CTk):
    def __init__(self, vpn):
        super().__init__()
        self.vpn = vpn
        self.title("HEART VPN PRO")
        self.geometry("850x550")
        self.configure(fg_color="#000000")
        
        # Заголовок в стиле Gothic One
        self.logo = ctk.CTkLabel(self, text="HEART", font=("Gothic A1", 50, "bold"), text_color="#FF0000")
        self.logo.pack(pady=(40, 10))
        
        self.status = ctk.CTkLabel(self, text="SYSTEM STANDBY", font=("Gothic A1", 16), text_color="#444")
        self.status.pack(pady=10)

        # Кнопка ENGAGE
        self.btn = ctk.CTkButton(self, text="ENGAGE", width=260, height=70, corner_radius=0,
                                 fg_color="#FF0000", hover_color="#990000", 
                                 font=("Gothic A1", 22, "bold"), command=self.toggle)
        self.btn.pack(pady=30)

        # Консоль логов
        self.console = ctk.CTkTextbox(self, height=160, fg_color="#050505", border_color="#111", 
                                      border_width=1, text_color="#00FF00", font=("Consolas", 12))
        self.console.pack(fill="x", padx=50, pady=20)
        self.log("HEART VPN READY. ALL SYSTEMS GO.")
        self.proc = None

    def log(self, t):
        self.console.insert("end", f"> {t}\n"); self.console.see("end")

    def toggle(self):
        if self.btn.cget("text") == "ENGAGE":
            threading.Thread(target=self.start, daemon=True).start()
        else:
            self.stop()

    def set_proxy(self, status):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1 if status else 0)
            winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, "127.0.0.1:10809")
            winreg.CloseKey(key)
        except: pass

    def start(self):
        self.status.configure(text="PUMPING...", text_color="#FFFF00")
        if self.vpn.download_core(self.log):
            self.vpn.build_config()
            self.proc = subprocess.Popen([self.vpn.core_exe, "run", "-c", self.vpn.config_p], 
                                         creationflags=0x08000000)
            self.set_proxy(True)
            self.btn.configure(text="DISCONNECT", fg_color="#222")
            self.status.configure(text="HEART ACTIVE", text_color="#FF0000")
            self.log(f"TUNNEL OPEN: {self.vpn.worker_url}")

    def stop(self):
        self.set_proxy(False)
        if self.proc: self.proc.terminate()
        os.system("taskkill /f /im xray.exe >nul 2>&1")
        self.btn.configure(text="ENGAGE", fg_color="#FF0000")
        self.status.configure(text="SYSTEM STANDBY", text_color="#444")
        self.log("TUNNEL CLOSED.")

if __name__ == "__main__":
    vpn_logic = HeartVPN_System()
    app = HeartUI(vpn_logic)
    app.mainloop()
