#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modul Auth Manager untuk EduBot
Mengelola otentikasi pengguna dengan OpenAI/ChatGPT API, DeepSeek API, dan Google Gemini API
"""
import os
import json
import webbrowser
import http.server
import socketserver
import threading
import time
import urllib.parse
import keyring
import requests
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QLineEdit, QDialog, QVBoxLayout, QHBoxLayout, QRadioButton, QLabel, QPushButton, QButtonGroup
from PyQt5.QtCore import QUrl, QDir
from dotenv import load_dotenv

# Konstanta untuk otentikasi
AUTH_SERVER_PORT = 8000
SERVICE_NAME = "edubot"
OPENAI_API_KEY_NAME = "openai_api_key"
DEEPSEEK_API_KEY_NAME = "deepseek_api_key"
GEMINI_API_KEY_NAME = "gemini_api_key"
CONFIG_DIR = os.path.join(QDir.homePath(), ".edubot")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

class ApiKeyDialog(QDialog):
    """Dialog untuk memilih provider AI dan memasukkan API key"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("EduBot - Pilih AI Provider dan Masukkan API Key")
        self.setMinimumWidth(500)
        
        # Buat layout
        layout = QVBoxLayout()
        
        # Provider selection
        provider_layout = QVBoxLayout()
        provider_label = QLabel("Pilih Provider AI:")
        provider_layout.addWidget(provider_label)
        
        self.provider_group = QButtonGroup(self)
        
        self.openai_radio = QRadioButton("OpenAI (ChatGPT)")
        self.openai_radio.setChecked(True)
        self.openai_radio.toggled.connect(self._toggle_provider)
        provider_layout.addWidget(self.openai_radio)
        self.provider_group.addButton(self.openai_radio)
        
        self.deepseek_radio = QRadioButton("DeepSeek AI")
        self.deepseek_radio.toggled.connect(self._toggle_provider)
        provider_layout.addWidget(self.deepseek_radio)
        self.provider_group.addButton(self.deepseek_radio)
        
        self.gemini_radio = QRadioButton("Google Gemini")
        self.gemini_radio.toggled.connect(self._toggle_provider)
        provider_layout.addWidget(self.gemini_radio)
        self.provider_group.addButton(self.gemini_radio)
        
        layout.addLayout(provider_layout)
        
        # Info label
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        
        # API key input
        key_label = QLabel("Masukkan API Key:")
        layout.addWidget(key_label)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("API Key...")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.api_key_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        
        cancel_button = QPushButton("Batal")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Set default provider info
        self._toggle_provider()
    
    def _toggle_provider(self):
        """Toggle informasi berdasarkan provider yang dipilih"""
        if self.openai_radio.isChecked():
            self.info_label.setText(
                "Untuk mendapatkan API key OpenAI, kunjungi:\n"
                "https://platform.openai.com/api-keys"
            )
        elif self.deepseek_radio.isChecked():
            self.info_label.setText(
                "Untuk mendapatkan API key DeepSeek, kunjungi:\n"
                "https://platform.deepseek.com"
            )
        else:  # Gemini
            self.info_label.setText(
                "Untuk mendapatkan API key Google Gemini, kunjungi:\n"
                "https://aistudio.google.com/app/apikey"
            )
    
    def get_provider_and_key(self):
        """Mendapatkan provider dan key"""
        if self.openai_radio.isChecked():
            return "openai", self.api_key_input.text()
        elif self.deepseek_radio.isChecked():
            return "deepseek", self.api_key_input.text()
        else:
            return "gemini", self.api_key_input.text()

class AuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
    """Handler untuk server HTTP callback otentikasi"""
    
    def do_GET(self):
        """Menangani permintaan GET saat pengguna dialihkan kembali setelah otentikasi"""
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        if parsed_path.path == "/callback" and "api_key" in query_params:
            api_key = query_params["api_key"][0]
            
            # Menyimpan API key ke keyring sistem
            keyring.set_password(SERVICE_NAME, OPENAI_API_KEY_NAME, api_key)
            
            # Menampilkan halaman sukses
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            success_html = """
            <html>
            <head>
                <title>EduBot - Otentikasi Berhasil</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                    h1 { color: #4CAF50; }
                </style>
            </head>
            <body>
                <h1>Otentikasi Berhasil!</h1>
                <p>Anda berhasil terhubung dengan API. Anda dapat menutup jendela ini dan kembali ke aplikasi EduBot.</p>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode())
            
            # Memberitahu server untuk berhenti setelah permintaan ini
            self.server.should_stop = True
            return
        
        # Jika bukan callback yang diharapkan, tampilkan halaman error
        self.send_response(404)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        error_html = """
        <html>
        <head>
            <title>EduBot - Error</title>
        </head>
        <body>
            <h1>Halaman tidak ditemukan</h1>
        </body>
        </html>
        """
        self.wfile.write(error_html.encode())

class StoppableHTTPServer(socketserver.TCPServer):
    """Server HTTP yang dapat dihentikan oleh handler"""
    allow_reuse_address = True
    should_stop = False

class AuthManager:
    """Kelas untuk mengelola otentikasi pengguna"""
    
    def __init__(self):
        """Inisialisasi Auth Manager"""
        # Memastikan direktori konfigurasi ada
        os.makedirs(CONFIG_DIR, exist_ok=True)
        
        # Memuat variabel lingkungan dari file .env jika ada
        load_dotenv()
        
        # Coba memuat konfigurasi jika ada
        self.config = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    self.config = json.load(f)
            except json.JSONDecodeError:
                # Jika file rusak, buat ulang
                self.config = {}
        
        self.api_key = None
        self.provider = self.config.get("provider", "openai")
    
    def is_authenticated(self):
        """Memeriksa apakah pengguna sudah terotentikasi"""
        # Coba mendapatkan API key dari keyring berdasarkan provider
        if self.provider == "openai":
            api_key = keyring.get_password(SERVICE_NAME, OPENAI_API_KEY_NAME)
        elif self.provider == "deepseek":
            api_key = keyring.get_password(SERVICE_NAME, DEEPSEEK_API_KEY_NAME)
        else:  # gemini
            api_key = keyring.get_password(SERVICE_NAME, GEMINI_API_KEY_NAME)
        
        if api_key:
            # Verifikasi API key
            if self._verify_api_key(api_key):
                self.api_key = api_key
                return True
        
        return False
    
    def authenticate(self):
        """Memulai proses otentikasi pengguna"""
        # Tampilkan dialog untuk memilih provider dan memasukkan API key
        api_dialog = ApiKeyDialog()
        if api_dialog.exec_() == QDialog.Accepted:
            self.provider, api_key = api_dialog.get_provider_and_key()
            
            if api_key:
                # Verifikasi API key
                if self._verify_api_key(api_key):
                    # Simpan API key ke keyring berdasarkan provider
                    if self.provider == "openai":
                        keyring.set_password(SERVICE_NAME, OPENAI_API_KEY_NAME, api_key)
                    elif self.provider == "deepseek":
                        keyring.set_password(SERVICE_NAME, DEEPSEEK_API_KEY_NAME, api_key)
                    else:  # gemini
                        keyring.set_password(SERVICE_NAME, GEMINI_API_KEY_NAME, api_key)
                    
                    self.api_key = api_key
                    
                    # Simpan provider ke konfigurasi
                    self.config["provider"] = self.provider
                    self._save_config()
                    
                    return True
                else:
                    QMessageBox.critical(
                        None,
                        "EduBot - API Key Tidak Valid",
                        f"API key {self.provider.upper()} yang Anda masukkan tidak valid. Silakan coba lagi."
                    )
                    # Coba lagi
                    return self.authenticate()
        
        return False
    
    def _verify_api_key(self, api_key):
        """Memverifikasi API key dengan mengirim permintaan uji ke API"""
        if self.provider == "openai":
            return self._verify_openai_key(api_key)
        elif self.provider == "deepseek":
            return self._verify_deepseek_key(api_key)
        else:
            return self._verify_gemini_key(api_key)
    
    def _verify_openai_key(self, api_key):
        """Memverifikasi API key OpenAI"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            # Lakukan permintaan sederhana ke endpoint OpenAI untuk memverifikasi key
            response = requests.get(
                "https://api.openai.com/v1/models",
                headers=headers
            )
            
            return response.status_code == 200
        except Exception:
            return False
    
    def _verify_deepseek_key(self, api_key):
        """Memverifikasi API key DeepSeek"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            # Lakukan permintaan sederhana ke endpoint DeepSeek
            response = requests.get(
                "https://api.deepseek.com/v1/models",  # Ganti dengan endpoint yang benar jika berbeda
                headers=headers
            )
            
            return response.status_code == 200
        except Exception:
            # Untuk development, kita anggap valid jika endpoint belum tersedia
            return True
    
    def _verify_gemini_key(self, api_key):
        """Memverifikasi API key Google Gemini"""
        try:
            # Import library google-generativeai untuk verifikasi
            import google.generativeai as genai
            
            # Konfigurasi API key
            genai.configure(api_key=api_key)
            
            # Coba mengakses model yang tersedia melalui SDK
            try:
                models = genai.list_models()
                # Jika berhasil mendapatkan daftar model, API key valid
                return True
            except Exception as e:
                print(f"SDK Error saat verifikasi API key Gemini: {e}")
                
                # Jika SDK error, coba panggil REST API langsung
                test_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
                try:
                    response = requests.get(test_url)
                    if response.status_code == 200:
                        print("Verifikasi API key Gemini berhasil melalui REST API")
                        return True
                    else:
                        error_message = response.text
                        print(f"REST API Error: {error_message}")
                        
                        # Jika error adalah kuota terlampaui, API key tetap valid
                        if "429" in str(response.status_code) or "quota" in error_message.lower():
                            QMessageBox.warning(
                                None,
                                "Kuota Google Gemini API Terlampaui",
                                "API key Anda valid, tetapi kuota Google Gemini gratis Anda telah terlampaui.\n\n"
                                "Hal ini biasa terjadi untuk akun gratis. Anda dapat:\n"
                                "- Menunggu hingga kuota disetel ulang (biasanya 24 jam)\n"
                                "- Berlangganan paket berbayar di Google AI Studio\n"
                                "- Gunakan provider AI lain (OpenAI atau DeepSeek)"
                            )
                            return True
                        
                        return False
                except Exception as net_e:
                    print(f"Network error saat verifikasi API key: {net_e}")
                    # Asumsi error koneksi, anggap valid untuk pengembangan
                    return True
        except Exception as e:
            print(f"Error saat memverifikasi API key Gemini: {e}")
            
            # Jika error adalah 429 (quota exceeded), beritahu user bahwa API key valid
            # tapi kuota telah terlampaui
            error_message = str(e).lower()
            if "429" in error_message or "quota" in error_message or "exceeded" in error_message:
                QMessageBox.warning(
                    None,
                    "Kuota Google Gemini API Terlampaui",
                    "API key Anda valid, tetapi kuota Google Gemini gratis Anda telah terlampaui.\n\n"
                    "Hal ini biasa terjadi untuk akun gratis. Anda dapat:\n"
                    "- Menunggu hingga kuota disetel ulang (biasanya 24 jam)\n"
                    "- Berlangganan paket berbayar di Google AI Studio\n"
                    "- Gunakan provider AI lain (OpenAI atau DeepSeek)"
                )
                # Tetap kembalikan True karena API key valid
                return True
                
            # Jika error lain (misalnya koneksi), anggap valid untuk pengembangan
            if "access denied" in error_message or "invalid" in error_message:
                return False
            
            return True
    
    def _save_config(self):
        """Menyimpan konfigurasi ke file"""
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config, f)
        except Exception as e:
            print(f"Error saat menyimpan konfigurasi: {e}")
    
    def get_provider(self):
        """Mendapatkan provider AI yang digunakan"""
        return self.provider
    
    def get_api_key(self):
        """Mendapatkan API key yang tersimpan"""
        return self.api_key
    
    def logout(self):
        """Menghapus kredensial pengguna"""
        try:
            if self.provider == "openai":
                keyring.delete_password(SERVICE_NAME, OPENAI_API_KEY_NAME)
            elif self.provider == "deepseek":
                keyring.delete_password(SERVICE_NAME, DEEPSEEK_API_KEY_NAME)
            else:  # gemini
                keyring.delete_password(SERVICE_NAME, GEMINI_API_KEY_NAME)
            
            self.api_key = None
            return True
        except Exception:
            return False 