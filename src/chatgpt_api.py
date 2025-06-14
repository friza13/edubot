#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modul AI API untuk EduBot
Mengelola komunikasi dengan OpenAI API, DeepSeek API, dan Google Gemini API
"""
import os
import json
import openai
import requests
from datetime import datetime

class BaseAPI:
    """Kelas dasar untuk API AI"""
    
    def __init__(self, api_key):
        """Inisialisasi API dengan API key"""
        self.api_key = api_key
        self.chat_history = {}
    
    def clear_history(self, session_id="default"):
        """
        Menghapus riwayat chat untuk sesi tertentu
        
        Args:
            session_id (str, optional): ID sesi. Defaults to "default".
        """
        if session_id in self.chat_history:
            # Simpan prompt sistem jika ada
            system_prompts = [msg for msg in self.chat_history[session_id] if msg["role"] == "system"]
            
            # Reset riwayat dengan hanya menyimpan prompt sistem
            self.chat_history[session_id] = system_prompts

class OpenAIAPI(BaseAPI):
    """Kelas untuk berkomunikasi dengan API OpenAI"""
    
    def __init__(self, api_key):
        """Inisialisasi API dengan API key"""
        super().__init__(api_key)
        
        # Perbaikan untuk versi OpenAI terbaru - menghapus parameter proxies
        try:
            self.client = openai.OpenAI(api_key=api_key)
        except TypeError as e:
            if 'proxies' in str(e):
                # Alternatif jika 'proxies' menyebabkan masalah
                import httpx
                openai.api_key = api_key
                self.client = openai.OpenAI(
                    api_key=api_key,
                    http_client=httpx.Client()
                )
        
        # Model yang digunakan (default: gpt-3.5-turbo)
        self.model = "gpt-3.5-turbo"
    
    def get_response(self, message, session_id="default", system_prompt=None):
        """
        Mendapatkan respons dari ChatGPT untuk pesan tertentu
        
        Args:
            message (str): Pesan yang dikirim ke ChatGPT
            session_id (str): ID sesi untuk melacak riwayat chat
            system_prompt (str): Prompt sistem khusus untuk sesi ini
            
        Returns:
            str: Respons dari ChatGPT
        """
        # Pastikan sesi ada
        if session_id not in self.chat_history:
            self.chat_history[session_id] = []
            
            # Jika disediakan prompt sistem, tambahkan sebagai pesan pertama
            if system_prompt:
                self.chat_history[session_id].append({
                    "role": "system",
                    "content": system_prompt
                })
        
        # Tambahkan pesan pengguna ke riwayat
        self.chat_history[session_id].append({
            "role": "user",
            "content": message
        })
        
        try:
            # Kirim pesan ke API OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.chat_history[session_id],
                temperature=0.7,
                max_tokens=1000,
                n=1,
                stop=None
            )
            
            # Dapatkan konten respons
            content = response.choices[0].message.content
            
            # Tambahkan respons asisten ke riwayat
            self.chat_history[session_id].append({
                "role": "assistant",
                "content": content
            })
            
            # Batasi panjang riwayat (untuk menghemat token)
            if len(self.chat_history[session_id]) > 10:
                # Simpan prompt sistem jika ada
                system_prompts = [msg for msg in self.chat_history[session_id] if msg["role"] == "system"]
                
                # Potong riwayat, simpan 6 pesan terakhir
                self.chat_history[session_id] = system_prompts + self.chat_history[session_id][-6:]
            
            return content
        
        except Exception as e:
            print(f"Error saat berkomunikasi dengan API OpenAI: {e}")
            return f"Terjadi kesalahan: {str(e)}"
    
    def change_model(self, model_name):
        """
        Mengubah model ChatGPT yang digunakan
        
        Args:
            model_name (str): Nama model ChatGPT (misalnya "gpt-3.5-turbo", "gpt-4")
            
        Returns:
            bool: True jika berhasil, False jika gagal
        """
        try:
            # Coba dapatkan informasi model untuk memvalidasi
            self.client.models.retrieve(model_name)
            
            # Jika berhasil, ubah model
            self.model = model_name
            return True
        except Exception as e:
            print(f"Error saat mengubah model: {e}")
            return False

class DeepSeekAPI(BaseAPI):
    """Kelas untuk berkomunikasi dengan API DeepSeek"""
    
    def __init__(self, api_key):
        """Inisialisasi API dengan API key"""
        super().__init__(api_key)
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Model yang digunakan (default: deepseek-chat)
        self.model = "deepseek-chat"
    
    def get_response(self, message, session_id="default", system_prompt=None):
        """
        Mendapatkan respons dari DeepSeek untuk pesan tertentu
        
        Args:
            message (str): Pesan yang dikirim ke DeepSeek
            session_id (str): ID sesi untuk melacak riwayat chat
            system_prompt (str): Prompt sistem khusus untuk sesi ini
            
        Returns:
            str: Respons dari DeepSeek
        """
        # Pastikan sesi ada
        if session_id not in self.chat_history:
            self.chat_history[session_id] = []
            
            # Jika disediakan prompt sistem, tambahkan sebagai pesan pertama
            if system_prompt:
                self.chat_history[session_id].append({
                    "role": "system",
                    "content": system_prompt
                })
        
        # Tambahkan pesan pengguna ke riwayat
        self.chat_history[session_id].append({
            "role": "user",
            "content": message
        })
        
        try:
            # Siapkan payload untuk API DeepSeek
            payload = {
                "model": self.model,
                "messages": self.chat_history[session_id],
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            # Kirim pesan ke API DeepSeek
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                # Parse respons
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Tambahkan respons asisten ke riwayat
                self.chat_history[session_id].append({
                    "role": "assistant",
                    "content": content
                })
                
                # Batasi panjang riwayat (untuk menghemat token)
                if len(self.chat_history[session_id]) > 10:
                    # Simpan prompt sistem jika ada
                    system_prompts = [msg for msg in self.chat_history[session_id] if msg["role"] == "system"]
                    
                    # Potong riwayat, simpan 6 pesan terakhir
                    self.chat_history[session_id] = system_prompts + self.chat_history[session_id][-6:]
                
                return content
            else:
                error_message = f"Error code: {response.status_code} - {response.text}"
                print(error_message)
                return f"Terjadi kesalahan: {error_message}"
        
        except Exception as e:
            print(f"Error saat berkomunikasi dengan API DeepSeek: {e}")
            return f"Terjadi kesalahan: {str(e)}"
    
    def change_model(self, model_name):
        """
        Mengubah model DeepSeek yang digunakan
        
        Args:
            model_name (str): Nama model DeepSeek
            
        Returns:
            bool: True jika berhasil, False jika gagal
        """
        # Untuk saat ini, kita asumsikan model valid tanpa pengecekan
        self.model = model_name
        return True

class GeminiAPI(BaseAPI):
    """Kelas untuk berkomunikasi dengan Google Gemini API"""
    
    def __init__(self, api_key):
        """Inisialisasi API dengan API key"""
        super().__init__(api_key)
        self.api_key = api_key
        
        # Flag untuk mode fallback ke REST API
        self.use_rest_api = False
        self.rest_api_url = "https://generativelanguage.googleapis.com/v1beta/models"
        
        # System prompt default untuk mencegah respons generic
        self.default_system_prompt = (
            "Anda adalah asisten AI bernama GeminiBot yang informatif dan membantu. "
            "Jawablah pertanyaan pengguna dengan jelas, ringkas, dan bermanfaat. "
            "Jangan berikan daftar kemampuan Anda kecuali pengguna memintanya secara khusus. "
            "Jangan jelaskan bahwa Anda adalah model AI, cukup berikan respons yang relevan dengan pertanyaan. "
            "Gunakan bahasa yang sopan dan ramah. Berikan respons dalam bahasa Indonesia kecuali diminta menggunakan bahasa lain."
        )
        
        try:
            # Import Google Gemini library
            import google.generativeai as genai
            self.genai = genai
            
            # Konfigurasi API key
            self.genai.configure(api_key=api_key)
            
            # List model yang akan dicoba, dari yang paling disukai
            preferred_models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
            
            try:
                # Coba mendapatkan model yang tersedia
                models = self.genai.list_models()
                available_models = [model.name.split("/")[-1] for model in models]
                
                # Pilih model yang tersedia berdasarkan preferensi
                self.model_name = None
                for model in preferred_models:
                    if any(model in m for m in available_models):
                        self.model_name = model
                        break
                
                # Jika tidak ada model yang cocok, gunakan default
                if not self.model_name:
                    self.model_name = "gemini-2.0-flash"  # Default ke model terbaru
                
                # Inisialisasi model dengan konfigurasi khusus untuk menghindari respons default
                model_config = {
                    "temperature": 0.7,  # Sedikit lebih kreatif
                    "top_p": 0.9,        # Kontrol keberagaman respons
                    "top_k": 40          # Pertimbangkan lebih banyak token
                }
                
                self.model = self.genai.GenerativeModel(
                    model_name=self.model_name,
                    generation_config=model_config
                )
                print(f"Menggunakan model Gemini: {self.model_name}")
            except Exception as e:
                print(f"Error saat mendapatkan model: {e}")
                # Gunakan default jika gagal mendapatkan daftar model
                self.model_name = "gemini-2.0-flash"
                self.model = self.genai.GenerativeModel(self.model_name)
                
        except Exception as e:
            print(f"Error saat inisialisasi Gemini SDK: {e}")
            # Jika SDK tidak bisa diinisialisasi, gunakan REST API langsung
            self.use_rest_api = True
            self.model_name = "gemini-2.0-flash"
            print("Menggunakan REST API fallback untuk Gemini")
    
    def get_response(self, message, session_id="default", system_prompt=None):
        """
        Mendapatkan respons dari Google Gemini untuk pesan tertentu
        
        Args:
            message (str): Pesan yang dikirim ke Gemini
            session_id (str): ID sesi untuk melacak riwayat chat
            system_prompt (str): Prompt sistem khusus untuk sesi ini
            
        Returns:
            str: Respons dari Gemini
        """
        # Pastikan sesi ada
        if session_id not in self.chat_history:
            self.chat_history[session_id] = []
            
            # Inisialisasi chat
            if system_prompt:
                # Jika sistem prompt disediakan, gunakan sebagai awal chat
                self.chat_history[session_id].append({
                    "role": "system",
                    "content": system_prompt
                })
            else:
                # Jika tidak ada system prompt, gunakan default
                self.chat_history[session_id].append({
                    "role": "system",
                    "content": self.default_system_prompt
                })
        
        # Tambahkan pesan pengguna ke riwayat lokal
        self.chat_history[session_id].append({
            "role": "user",
            "content": message
        })
        
        # Buat prompt dengan system prompt
        prompt = message
        system_text = system_prompt if system_prompt else self.default_system_prompt
        combined_prompt = f"{system_text}\n\nPertanyaan pengguna: {message}\n\nBerikan jawaban yang relevan dan bermanfaat:"
        
        try:
            content = ""
            
            # Coba gunakan SDK terlebih dahulu jika tidak dalam mode fallback
            if not self.use_rest_api:
                try:
                    # Kirim pesan ke Gemini API via SDK
                    response = self.model.generate_content(combined_prompt)
                    
                    # Dapatkan respons
                    if hasattr(response, 'text'):
                        content = response.text
                    else:
                        content = str(response)
                except Exception as e:
                    print(f"SDK error: {e}, mencoba REST API")
                    self.use_rest_api = True
            
            # Gunakan REST API jika SDK gagal atau sudah dalam mode fallback
            if self.use_rest_api:
                # Buat payload untuk REST API
                payload = {
                    "contents": [{
                        "parts":[
                            {"text": "system: " + system_text},
                            {"text": "user: " + message}
                        ]
                    }],
                    "generationConfig": {
                        "temperature": 0.7,
                        "topK": 40,
                        "topP": 0.9
                    }
                }
                
                # Buat URL untuk request
                url = f"{self.rest_api_url}/{self.model_name}:generateContent?key={self.api_key}"
                
                # Kirim request
                response = requests.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json=payload
                )
                
                # Parse respons
                if response.status_code == 200:
                    try:
                        result = response.json()
                        content = result["candidates"][0]["content"]["parts"][0]["text"]
                    except Exception as e:
                        print(f"Error parsing REST API response: {e}")
                        content = "Error memproses respons dari API"
                else:
                    error_message = response.text
                    print(f"REST API error: {error_message}")
                    
                    # Jika error adalah kuota, beri pesan khusus
                    if "429" in str(response.status_code) or "quota" in error_message.lower():
                        content = (
                            "Maaf, kuota Google Gemini API Anda telah terlampaui. Ini umum terjadi dengan akun gratis.\n\n"
                            "Beberapa solusi:\n"
                            "1. Tunggu hingga kuota disetel ulang (biasanya 24 jam)\n"
                            "2. Berlangganan paket berbayar di Google AI Studio\n"
                            "3. Gunakan provider AI lain (OpenAI atau DeepSeek)\n\n"
                            "Anda dapat logout dan memilih provider lain di menu File > Logout."
                        )
                    else:
                        content = f"Error dari API ({response.status_code}): {error_message}"
            
            # Tambahkan respons asisten ke riwayat lokal
            self.chat_history[session_id].append({
                "role": "assistant",
                "content": content
            })
            
            # Batasi panjang riwayat (untuk menghemat token)
            if len(self.chat_history[session_id]) > 10:
                # Simpan prompt sistem jika ada
                system_prompts = [msg for msg in self.chat_history[session_id] if msg["role"] == "system"]
                
                # Potong riwayat, simpan 6 pesan terakhir
                self.chat_history[session_id] = system_prompts + self.chat_history[session_id][-6:]
            
            return content
        
        except Exception as e:
            error_message = str(e)
            print(f"Error saat berkomunikasi dengan API Gemini: {e}")
            
            # Pesan khusus untuk error quota exceeded
            if "429" in error_message or "quota" in error_message.lower() or "exceeded" in error_message.lower():
                return (
                    "Maaf, kuota Google Gemini API Anda telah terlampaui. Ini umum terjadi dengan akun gratis.\n\n"
                    "Beberapa solusi:\n"
                    "1. Tunggu hingga kuota disetel ulang (biasanya 24 jam)\n"
                    "2. Berlangganan paket berbayar di Google AI Studio\n"
                    "3. Gunakan provider AI lain (OpenAI atau DeepSeek)\n\n"
                    "Anda dapat logout dan memilih provider lain di menu File > Logout."
                )
            
            return f"Terjadi kesalahan: {error_message}"
    
    def change_model(self, model_name):
        """
        Mengubah model Gemini yang digunakan
        
        Args:
            model_name (str): Nama model Gemini (misalnya "gemini-pro", "gemini-pro-vision")
            
        Returns:
            bool: True jika berhasil, False jika gagal
        """
        try:
            # Perbarui model
            self.model_name = model_name
            self.model = self.genai.GenerativeModel(model_name)
            return True
        except Exception as e:
            print(f"Error saat mengubah model Gemini: {e}")
            return False

class ChatGPTAPI:
    """Kelas untuk mengelola dan menyediakan akses ke berbagai API AI"""
    
    def __init__(self, api_key, provider="openai"):
        """
        Inisialisasi ChatGPT API dengan provider yang dipilih
        
        Args:
            api_key (str): API key untuk provider yang dipilih
            provider (str): Provider AI ("openai", "deepseek", atau "gemini")
        """
        self.api_key = api_key
        self.provider = provider
        
        # Inisialisasi API yang sesuai
        if provider == "openai":
            self.api = OpenAIAPI(api_key)
        elif provider == "deepseek":
            self.api = DeepSeekAPI(api_key)
        else:  # gemini
            self.api = GeminiAPI(api_key)
    
    def get_response(self, message, session_id="default", system_prompt=None):
        """
        Mendapatkan respons dari AI untuk pesan tertentu
        
        Args:
            message (str): Pesan yang dikirim ke AI
            session_id (str): ID sesi untuk melacak riwayat chat
            system_prompt (str): Prompt sistem khusus untuk sesi ini
            
        Returns:
            str: Respons dari AI
        """
        return self.api.get_response(message, session_id, system_prompt)
    
    def get_terminal_help(self, command):
        """
        Mendapatkan bantuan untuk perintah terminal Linux
        
        Args:
            command (str): Perintah terminal yang ingin dijelaskan
            
        Returns:
            str: Penjelasan tentang perintah terminal
        """
        system_prompt = "Anda adalah asisten yang ahli dalam perintah terminal Linux. Berikan penjelasan yang jelas dan ringkas tentang perintah, opsi, dan contoh penggunaan."
        return self.get_response(f"Jelaskan perintah terminal Linux '{command}'", session_id="terminal", system_prompt=system_prompt)
    
    def explain_code(self, code, language=None):
        """
        Mendapatkan penjelasan untuk kode
        
        Args:
            code (str): Kode yang ingin dijelaskan
            language (str, optional): Bahasa pemrograman. Defaults to None.
            
        Returns:
            str: Penjelasan tentang kode
        """
        system_prompt = """
        Anda adalah asisten yang ahli dalam menjelaskan kode.
        
        Berikan penjelasan yang jelas dan terperinci tentang kode yang diberikan dengan mengikuti panduan berikut:
        1. Jelaskan fungsi utama kode secara keseluruhan
        2. Jelaskan cara kerjanya dengan detail
        3. Identifikasi komponen dan alur penting
        4. Gunakan bahasa yang sederhana dan mudah dipahami
        5. Gunakan format paragraf yang baik dengan baris kosong antar paragraf
        6. Gunakan teks biasa, hindari format bold atau italic
        7. Gunakan `code` untuk nama fungsi, variabel, dan istilah teknis
        8. Berikan konteks yang cukup untuk pemahaman
        9. Hindari jargon teknis yang berlebihan
        """
        
        message = f"Jelaskan kode berikut:\n\n```{language or ''}\n{code}\n```"
        return self.get_response(message, session_id="code_explanation", system_prompt=system_prompt)
    
    def generate_script(self, description, script_type="bash"):
        """
        Membuat skrip berdasarkan deskripsi
        
        Args:
            description (str): Deskripsi skrip yang ingin dibuat
            script_type (str, optional): Jenis skrip (bash, python, dll). Defaults to "bash".
            
        Returns:
            str: Skrip yang dihasilkan
        """
        system_prompt = f"Anda adalah asisten yang ahli dalam membuat skrip {script_type} untuk Linux. Berikan skrip yang berfungsi dengan baik, efisien, dan disertai komentar yang menjelaskan setiap bagian."
        message = f"Buat skrip {script_type} berdasarkan deskripsi berikut:\n\n{description}\n\nHanya berikan skrip lengkap yang siap dijalankan di Linux tanpa penjelasan tambahan."
        return self.get_response(message, session_id="script_generation", system_prompt=system_prompt)
    
    def get_system_help(self, question, system_info):
        """
        Mendapatkan bantuan terkait sistem
        
        Args:
            question (str): Pertanyaan tentang sistem
            system_info (str): Informasi sistem pengguna
            
        Returns:
            str: Bantuan terkait sistem
        """
        system_prompt = "Anda adalah asisten yang ahli dalam sistem operasi Linux. Berikan bantuan yang jelas dan terperinci berdasarkan informasi sistem yang diberikan."
        message = f"Berdasarkan informasi sistem berikut:\n\n{system_info}\n\n{question}"
        return self.get_response(message, session_id="system_help", system_prompt=system_prompt)
    
    def change_model(self, model_name):
        """
        Mengubah model AI yang digunakan
        
        Args:
            model_name (str): Nama model AI
            
        Returns:
            bool: True jika berhasil, False jika gagal
        """
        return self.api.change_model(model_name)
    
    def clear_history(self, session_id="default"):
        """
        Menghapus riwayat chat untuk sesi tertentu
        
        Args:
            session_id (str, optional): ID sesi. Defaults to "default".
        """
        self.api.clear_history(session_id) 