import os
import sys
import json
import time
import socket
import threading
import subprocess
import zipfile
import requests
import winreg
import ctypes
import psutil
import customtkinter as ctk
from datetime import datetime

# =================================================================
# HEART VPN - PUBLIC INFRASTRUCTURE EDITION
# VERSION: 3.0.0 | BYPASS MASTER: AZER
# =================================================================

class HeartVPN_Public:
    def __init__(self):
        self.root_dir = os.path.join(os.environ['LOCALAPPDATA'], 'HeartVPN_Public')
        self.bin_dir = os.path.join(self.root_dir, 'bin')
        self.core_exe = os.path.join(self.bin_dir, 'xray.exe')
        self.config_path = os.path.join(self.bin_dir, 'public_config.json')
        
        # ПУБЛИЧНЫЕ СЕРВЕРА (Сюда вписываешь свои данные)
        self.servers = [
            {"name": "HEART-NL-1", "ip": "185.255.1.1", "uuid": "ef87346a-7230-4e5c-9d6c-2f3b89e3456d", "port": 443},
            {"name": "HEART-DE-2", "ip": "95.216.2.2", "uuid": "7a8b9c0d-1234-5678-90ab-cdef12345678", "port": 443},
            {"name": "VAPI-SPECIAL", "ip": "1.2.3.4", "uuid": "00000000-0000-0000-0000-000000000000", "port": 443}
        ]
        
        self.active_server = self.servers[0]
        self.process = None
        
        if not os.path.exists(self.bin_dir):
            os.makedirs(self.bin_dir)

    def download_core(self, log):
        if os.path.exists(self.core_exe): return True
        log("Downloading Public Core...")
        url = "https://github.com/XTLS/Xray-core/releases/latest/download/Xray-windows-64.zip"
        try:
            r = requests.get(url)
            with open(os.path.join(self.root_dir, "temp.zip"), 'wb') as f: f.write(r.content)
            with zipfile.ZipFile(os.path.join(self.root_dir, "temp.zip"), 'r') as z: z.extractall(self.bin_dir)
            log("Public Core Ready.")
            return True
        except: return False

    def build_public_config(self):
        """Конфигурация для подключения к PUBLIC серверу через Reality"""
        config = {
            "log": {"loglevel": "none"},
            "inbounds": [{"port": 10809, "protocol": "socks", "settings": {"udp": True}}],
            "outbounds": [
                {
                    "protocol": "vless",
                    "settings": {
                        "vnext": [{
                            "address": self.active_server["ip"],
                            "port": self.active_server["port"],
                            "users": [{"id": self.active_server["uuid"], "flow": "xtls-rprx-vision"}]
                        }]
                    },
                    "streamSettings": {
                        "network": "tcp", "security": "reality",
                        "realitySettings": {"fingerprint": "chrome", "serverName": "google.com"}
                    },
                    "tag": "proxy"
                },
                {"protocol": "freedom", "tag": "direct"}
            ],
            "routing": {
                "rules": [
                    {"type": "field", "outboundTag": "proxy", "domain": ["geosite:youtube", "geosite:discord", "telegram.org"]},
                    {"type": "field", "outboundTag": "direct", "domain": ["geosite:ru"]}
                ]
            }
        }
        with open(self.config_path, 'w') as f: json.dump(config, f, indent=4)

    def manage_proxy(self, state):
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1 if state else 0)
        winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, "127.0.0.1:10809")

class App(ctk.CTk):
    def __init__(self, vpn):
        super().__init__()
        self.vpn = vpn
        self.title("HEART VPN PUBLIC")
        self.geometry("1000x650")
        
        # Дизайн
        self.sidebar = ctk.CTkFrame(self, width=250)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)
        
        ctk.CTkLabel(self.sidebar, text="HEART PUBLIC", font=("Impact", 30), text_color="#FF3333").pack(pady=20)
        
        # Выбор сервера
        ctk.CTkLabel(self.sidebar, text="ВЫБЕРИ СЕРВЕР:").pack(pady=5)
        self.server_menu = ctk.CTkOptionMenu(self.sidebar, values=[s["name"] for s in self.vpn.servers], command=self.change_srv)
        self.server_menu.pack(pady=10)

        self.main_area = ctk.CTkFrame(self, fg_color="#050505")
        self.main_area.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.btn_power = ctk.CTkButton(self.main_area, text="START PUBLIC VPN", width=300, height=80, 
                                       corner_radius=40, font=("Arial", 20, "bold"), fg_color="#333",
                                       hover_color="#555", command=self.run_vpn)
        self.btn_power.pack(expand=True)

        self.log_box = ctk.CTkTextbox(self.main_area, height=200, fg_color="#000", text_color="#00FF00")
        self.log_box.pack(fill="x", padx=20, pady=20)

    def change_srv(self, name):
        for s in self.vpn.servers:
            if s["name"] == name: self.vpn.active_server = s

    def log(self, t):
        self.log_box.insert("end", f"> {t}\n"); self.log_box.see("end")

    def run_vpn(self):
        if self.btn_power.cget("text") == "START PUBLIC VPN":
            threading.Thread(target=self.start, daemon=True).start()
        else:
            self.stop()

    def start(self):
        if self.vpn.download_core(self.log):
            self.vpn.build_public_config()
            self.vpn.process = subprocess.Popen([self.vpn.core_exe, "run", "-c", self.vpn.config_path], creationflags=0x08000000)
            self.vpn.manage_proxy(True)
            self.btn_power.configure(text="STOP VPN", fg_color="#FF3333")
            self.log(f"Connected to {self.vpn.active_server['name']}")

    def stop(self):
        self.vpn.manage_proxy(False)
        if self.vpn.process: self.vpn.process.terminate()
        os.system("taskkill /f /im xray.exe >nul 2>&1")
        self.btn_power.configure(text="START PUBLIC VPN", fg_color="#333")
        self.log("Disconnected.")

if __name__ == "__main__":
    App(HeartVPN_Public()).mainloop()
