import os, sys, json, time, threading, subprocess, zipfile, requests, winreg, psutil
import customtkinter as ctk
from datetime import datetime

# =================================================================
# HEART VPN - GOTHIC EDITION (AZER EXCLUSIVE)
# FONTS: GOTHIC ONE STYLE | COLORS: PURE BLACK
# =================================================================

class HeartVPN_Engine:
    def __init__(self):
        self.root = os.path.join(os.environ['LOCALAPPDATA'], 'HeartVPN_Gothic')
        self.bin = os.path.join(self.root, 'bin')
        self.core = os.path.join(self.bin, 'xray.exe')
        self.cfg = os.path.join(self.bin, 'config.json')
        self.servers = [
            {"name": "HEART-0101", "ip": "185.255.1.1", "uuid": "ef87346a-7230-4e5c-9d6c-2f3b89e3456d"},
            {"name": "HEART-0102", "ip": "95.216.2.2", "uuid": "7a8b9c0d-1234-5678-90ab-cdef12345678"},
            {"name": "HEART-0103", "ip": "45.13.132.11", "uuid": "00000000-0000-0000-0000-000000000000"}
        ]
        if not os.path.exists(self.bin): os.makedirs(self.bin)

    def download(self, log_cb):
        if os.path.exists(self.core): return True
        log_cb("INITIALIZING CORE DOWNLOAD...")
        try:
            r = requests.get("https://github.com/XTLS/Xray-core/releases/latest/download/Xray-windows-64.zip")
            with open(os.path.join(self.root, "c.zip"), 'wb') as f: f.write(r.content)
            with zipfile.ZipFile(os.path.join(self.root, "c.zip"), 'r') as z: z.extractall(self.bin)
            return True
        except: return False

    def build_cfg(self, srv):
        c = {
            "inbounds": [{"port": 10809, "protocol": "socks", "settings": {"udp": True}}],
            "outbounds": [{
                "protocol": "vless",
                "settings": {"vnext": [{"address": srv["ip"], "port": 443, "users": [{"id": srv["uuid"], "flow": "xtls-rprx-vision"}]}]},
                "streamSettings": {"network": "tcp", "security": "reality", "realitySettings": {"fingerprint": "chrome", "serverName": "google.com"}}
            }, {"protocol": "freedom", "tag": "direct"}]
        }
        with open(self.cfg, 'w') as f: json.dump(c, f)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.engine = HeartVPN_Engine()
        self.active_srv = self.engine.servers[0]
        
        # UI SETTINGS
        self.title("HEART VPN")
        self.geometry("850x550")
        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#000000") # ЧЕРНЫЙ ФОН

        # FONTS (Gothic Style)
        self.main_font = ("Gothic A1", 24, "bold")
        self.ui_font = ("Gothic A1", 14)

        # SIDEBAR
        self.side = ctk.CTkFrame(self, width=220, fg_color="#050505", corner_radius=0)
        self.side.pack(side="left", fill="y")

        ctk.CTkLabel(self.side, text="HEART", font=("Gothic A1", 36, "bold"), text_color="#FF0000").pack(pady=30)
        
        self.srv_select = ctk.CTkOptionMenu(self.side, values=[s["name"] for s in self.engine.servers], 
                                            command=self.set_srv, fg_color="#111", button_color="#222", font=self.ui_font)
        self.srv_select.pack(pady=20, padx=10)

        # MAIN AREA
        self.main = ctk.CTkFrame(self, fg_color="#000000")
        self.main.pack(side="right", fill="both", expand=True)

        self.status = ctk.CTkLabel(self.main, text="SYSTEM READY", font=self.main_font, text_color="#333")
        self.status.pack(pady=40)

        self.power = ctk.CTkButton(self.main, text="ENGAGE", width=200, height=60, corner_radius=0,
                                   fg_color="#FF0000", hover_color="#880000", font=self.main_font,
                                   command=self.toggle)
        self.power.pack(pady=20)

        self.log_box = ctk.CTkTextbox(self.main, height=150, fg_color="#050505", border_color="#111", border_width=1, text_color="#555")
        self.log_box.pack(fill="x", padx=30, pady=20)
        self.proc = None

    def set_srv(self, name):
        for s in self.engine.servers:
            if s["name"] == name: self.active_srv = s

    def log(self, t):
        self.log_box.insert("end", f"> {t}\n"); self.log_box.see("end")

    def toggle(self):
        if self.power.cget("text") == "ENGAGE":
            threading.Thread(target=self.start, daemon=True).start()
        else:
            self.stop()

    def start(self):
        self.status.configure(text="PUMPING...", text_color="red")
        if self.engine.download(self.log):
            self.engine.build_cfg(self.active_srv)
            self.proc = subprocess.Popen([self.engine.core, "run", "-c", self.engine.cfg], creationflags=0x08000000)
            
            # Включаем прокси в реестре
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, "127.0.0.1:10809")
            
            self.power.configure(text="DISCONNECT", fg_color="#333")
            self.status.configure(text="HEART ACTIVE", text_color="#FF0000")
            self.log(f"TUNNEL OPENED: {self.active_srv['name']}")

    def stop(self):
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
        if self.proc: self.proc.terminate()
        os.system("taskkill /f /im xray.exe >nul 2>&1")
        self.power.configure(text="ENGAGE", fg_color="#FF0000")
        self.status.configure(text="SYSTEM READY", text_color="#333")
        self.log("TUNNEL CLOSED.")

if __name__ == "__main__":
    App().mainloop()
