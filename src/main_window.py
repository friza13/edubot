#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Window untuk aplikasi EduBot
"""
import os
import sys
import json
import platform
import subprocess
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QLineEdit, QPushButton, QTabWidget, 
    QLabel, QMessageBox, QAction, QMenu, QToolBar,
    QSplitter, QListWidget, QListWidgetItem, QFrame, QComboBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QFont, QTextCursor, QColor

from chatgpt_api import ChatGPTAPI

class MainWindow(QMainWindow):
    """Jendela utama aplikasi EduBot"""
    
    def __init__(self, auth_manager):
        """Inisialisasi jendela utama"""
        super().__init__()
        
        self.auth_manager = auth_manager
        self.api = ChatGPTAPI(auth_manager.get_api_key(), provider=auth_manager.get_provider())
        
        # Sesuaikan judul berdasarkan provider
        self.provider_name = "OpenAI (ChatGPT)"
        if auth_manager.get_provider() == "openai":
            self.provider_name = "OpenAI (ChatGPT)"
        elif auth_manager.get_provider() == "deepseek":
            self.provider_name = "DeepSeek AI"
        else:  # gemini
            self.provider_name = "Google Gemini"
        self.setWindowTitle(f"EduBot - Asisten AI untuk Linux dengan {self.provider_name}")
        self.setMinimumSize(900, 600)
        
        # Mengatur ikon aplikasi (jika tersedia)
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "edubot_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Membangun UI
        self._create_menu()
        self._create_ui()
        
        # Menampilkan pesan selamat datang
        self._display_welcome_message()
    
    def _create_menu(self):
        """Membuat menu aplikasi"""
        # Menu bar
        menubar = self.menuBar()
        
        # Menu File
        file_menu = menubar.addMenu("&File")
        
        # Logout
        logout_action = QAction("&Logout", self)
        logout_action.setStatusTip("Logout dari akun Anda")
        logout_action.triggered.connect(self._logout)
        file_menu.addAction(logout_action)
        
        # Keluar
        exit_action = QAction("&Keluar", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Keluar dari aplikasi")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Bantuan
        help_menu = menubar.addMenu("&Bantuan")
        
        # Tentang
        about_action = QAction("&Tentang", self)
        about_action.setStatusTip("Informasi tentang aplikasi")
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
        # Bantuan penggunaan
        help_action = QAction("&Bantuan Penggunaan", self)
        help_action.setStatusTip("Cara menggunakan aplikasi")
        help_action.triggered.connect(self._show_help)
        help_menu.addAction(help_action)
    
    def _create_ui(self):
        """Membuat antarmuka pengguna utama"""
        # Widget utama
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout utama
        main_layout = QVBoxLayout(central_widget)
        
        # Tampilkan informasi tentang provider
        provider_info = "AI Provider: " + self.provider_name
        provider_label = QLabel(provider_info)
        provider_label.setStyleSheet("font-weight: bold; color: #4285F4;")
        main_layout.addWidget(provider_label)
        
        # Tab widget untuk berbagai fitur
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Tab 1: Bantuan Umum (Chat)
        chat_tab = QWidget()
        self._setup_chat_tab(chat_tab)
        self.tab_widget.addTab(chat_tab, "Bantuan Umum")
        
        # Tab 2: Bantuan Terminal
        terminal_tab = QWidget()
        self._setup_terminal_tab(terminal_tab)
        self.tab_widget.addTab(terminal_tab, "Bantuan Terminal")
        
        # Tab 3: Penjelasan Kode
        code_tab = QWidget()
        self._setup_code_tab(code_tab)
        self.tab_widget.addTab(code_tab, "Penjelasan Kode")
        
        # Tab 4: Pembuatan Skrip
        script_tab = QWidget()
        self._setup_script_tab(script_tab)
        self.tab_widget.addTab(script_tab, "Pembuatan Skrip")
        
        # Tab 5: Info Sistem
        system_tab = QWidget()
        self._setup_system_tab(system_tab)
        self.tab_widget.addTab(system_tab, "Info Sistem")
    
    def _setup_chat_tab(self, tab):
        """Menyiapkan tab bantuan umum/chat"""
        layout = QVBoxLayout(tab)
        
        # Area riwayat chat
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        # Mengatur properti untuk menampilkan HTML dengan lebih baik
        self.chat_history.setAcceptRichText(True)
        self.chat_history.document().setDefaultStyleSheet("""
            body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 10pt; }
            .user-msg { background-color: #E8F5E9; padding: 10px; border-radius: 10px; margin: 8px 0; border-left: 4px solid #4CAF50; }
            .bot-msg { background-color: #E3F2FD; padding: 10px; border-radius: 10px; margin: 8px 0; border-left: 4px solid #2196F3; }
        """)
        self.chat_history.setStyleSheet("""
            QTextEdit {
                background-color: #F5F5F5;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        layout.addWidget(self.chat_history)
        
        # Area input dan tombol
        input_layout = QHBoxLayout()
        
        # Input teks
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Masukkan pertanyaan Anda di sini...")
        self.chat_input.returnPressed.connect(self._send_chat_message)
        input_layout.addWidget(self.chat_input)
        
        # Tombol kirim
        send_btn = QPushButton("Kirim")
        send_btn.clicked.connect(self._send_chat_message)
        input_layout.addWidget(send_btn)
        
        layout.addLayout(input_layout)
    
    def _setup_terminal_tab(self, tab):
        """Menyiapkan tab bantuan terminal"""
        layout = QVBoxLayout(tab)
        
        # Bagian atas untuk menjelaskan tujuan tab
        info_label = QLabel("Tanyakan bantuan tentang perintah terminal Linux, sintaks, atau cara mengatasi masalah terkait terminal")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Area riwayat chat untuk bantuan terminal
        self.terminal_history = QTextEdit()
        self.terminal_history.setReadOnly(True)
        # Mengatur properti untuk menampilkan HTML dengan lebih baik
        self.terminal_history.setAcceptRichText(True)
        self.terminal_history.document().setDefaultStyleSheet("""
            body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 10pt; }
            .user-msg { background-color: #E8F5E9; padding: 10px; border-radius: 10px; margin: 8px 0; border-left: 4px solid #4CAF50; }
            .bot-msg { background-color: #E3F2FD; padding: 10px; border-radius: 10px; margin: 8px 0; border-left: 4px solid #2196F3; }
            pre { background-color: #272822; color: #F8F8F2; padding: 8px; border-radius: 4px; font-family: 'Consolas', 'Courier New', monospace; }
        """)
        layout.addWidget(self.terminal_history)
        
        # Area input dan tombol
        input_layout = QHBoxLayout()
        
        # Input teks
        self.terminal_input = QLineEdit()
        self.terminal_input.setPlaceholderText("Tanyakan tentang perintah terminal Linux...")
        self.terminal_input.returnPressed.connect(self._send_terminal_question)
        input_layout.addWidget(self.terminal_input)
        
        # Tombol kirim
        send_btn = QPushButton("Tanya")
        send_btn.clicked.connect(self._send_terminal_question)
        input_layout.addWidget(send_btn)
        
        layout.addLayout(input_layout)
    
    def _setup_code_tab(self, tab):
        """Menyiapkan tab penjelasan kode"""
        layout = QVBoxLayout(tab)
        
        # Penjelasan
        info_label = QLabel("Masukkan kode di area kiri, lalu klik 'Jelaskan Kode' untuk mendapatkan penjelasan")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Splitter untuk kode dan penjelasan
        splitter = QSplitter(Qt.Horizontal)
        
        # Area input kode
        self.code_input = QTextEdit()
        self.code_input.setPlaceholderText("Tempel kode yang ingin dijelaskan di sini...")
        splitter.addWidget(self.code_input)
        
        # Area penjelasan kode
        self.code_explanation = QTextEdit()
        self.code_explanation.setReadOnly(True)
        self.code_explanation.setPlaceholderText("Penjelasan akan muncul di sini...")
        self.code_explanation.setAcceptRichText(True)
        self.code_explanation.document().setDefaultStyleSheet("""
            body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 9pt; line-height: 1.3; color: #333333; }
            h1 { color: #2196F3; margin-top: 10px; margin-bottom: 5px; font-size: 13pt; }
            h2 { color: #2196F3; margin-top: 8px; margin-bottom: 4px; font-size: 11pt; }
            h3 { color: #2196F3; margin-top: 6px; margin-bottom: 3px; font-size: 10pt; }
            p { margin: 5px 0; text-align: justify; }
            pre { background-color: #272822; color: #F8F8F2; padding: 5px; border-radius: 4px; 
                  font-family: 'Consolas', 'Courier New', monospace; font-size: 9pt; white-space: pre-wrap; }
            code { background-color: #F5F5F5; padding: 1px 3px; border-radius: 3px; 
                   font-family: 'Consolas', 'Courier New', monospace; font-size: 9pt; }
            ul, ol { margin-left: 15px; margin-top: 5px; margin-bottom: 5px; }
            li { margin: 3px 0; }
            b, strong { font-weight: normal; }
            .highlight { background-color: #FFECB3; color: #333333; padding: 1px 2px; border-radius: 2px; }
        """)
        splitter.addWidget(self.code_explanation)
        
        # Mengatur ukuran relatif
        splitter.setSizes([400, 400])
        layout.addWidget(splitter)
        
        # Tombol untuk meminta penjelasan
        explain_btn = QPushButton("Jelaskan Kode")
        explain_btn.clicked.connect(self._explain_code)
        layout.addWidget(explain_btn)
    
    def _setup_script_tab(self, tab):
        """Menyiapkan tab pembuatan skrip"""
        layout = QVBoxLayout(tab)
        
        # Penjelasan
        info_label = QLabel("Jelaskan skrip yang ingin dibuat di area input, lalu klik 'Buat Skrip'")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Splitter untuk deskripsi dan hasil skrip
        splitter = QSplitter(Qt.Horizontal)
        
        # Area deskripsi skrip
        description_widget = QWidget()
        description_layout = QVBoxLayout(description_widget)
        
        description_label = QLabel("Deskripsi Skrip:")
        description_layout.addWidget(description_label)
        
        self.script_description = QTextEdit()
        self.script_description.setPlaceholderText("Jelaskan skrip yang ingin Anda buat. Contoh: \"Buat skrip bash untuk mencadangkan semua file dalam direktori tertentu ke folder backup\"")
        description_layout.addWidget(self.script_description)
        
        splitter.addWidget(description_widget)
        
        # Area hasil skrip
        result_widget = QWidget()
        result_layout = QVBoxLayout(result_widget)
        
        result_label = QLabel("Hasil Skrip:")
        result_layout.addWidget(result_label)
        
        self.script_result = QTextEdit()
        self.script_result.setReadOnly(True)
        self.script_result.setPlaceholderText("Skrip akan muncul di sini...")
        self.script_result.setAcceptRichText(True)
        # Set font monospace untuk skrip
        font = QFont("Consolas", 9)
        self.script_result.setFont(font)
        self.script_result.document().setDefaultStyleSheet("""
            body { font-family: 'Consolas', 'Courier New', monospace; line-height: 1.2; font-size: 9pt; }
            pre { background-color: #272822; color: #F8F8F2; padding: 8px; border-radius: 5px; 
                  font-family: 'Consolas', 'Courier New', monospace; }
            .comment { color: #75715E; }
            .keyword { color: #F92672; font-weight: bold; }
            .string { color: #E6DB74; }
            .number { color: #AE81FF; }
            .function { color: #66D9EF; }
        """)
        result_layout.addWidget(self.script_result)
        
        splitter.addWidget(result_widget)
        
        # Mengatur ukuran relatif
        splitter.setSizes([400, 400])
        layout.addWidget(splitter)
        
        # Tombol untuk membuat skrip
        button_layout = QHBoxLayout()
        
        script_type_label = QLabel("Jenis Skrip:")
        button_layout.addWidget(script_type_label)
        
        self.script_type_combo = QComboBox()
        self.script_type_combo.addItems(["bash", "python", "powershell"])
        button_layout.addWidget(self.script_type_combo)
        
        button_layout.addStretch()
        
        generate_btn = QPushButton("Buat Skrip")
        generate_btn.clicked.connect(self._generate_script)
        button_layout.addWidget(generate_btn)
        
        save_btn = QPushButton("Simpan Skrip")
        save_btn.clicked.connect(self._save_script)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def _setup_system_tab(self, tab):
        """Menyiapkan tab info sistem"""
        layout = QVBoxLayout(tab)
        
        # Info sistem dasar
        system_info = self._get_system_info()
        
        # Tampilkan info sistem
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setHtml(system_info)
        layout.addWidget(info_text)
        
        # Input untuk menanyakan tentang sistem
        input_layout = QHBoxLayout()
        
        # Label
        input_label = QLabel("Tanyakan tentang sistem Anda:")
        input_layout.addWidget(input_label)
        
        # Input teks
        self.system_input = QLineEdit()
        self.system_input.setPlaceholderText("Contoh: Bagaimana cara memeriksa ruang disk yang tersedia?")
        self.system_input.returnPressed.connect(self._ask_system_question)
        input_layout.addWidget(self.system_input)
        
        # Tombol tanya
        ask_btn = QPushButton("Tanya")
        ask_btn.clicked.connect(self._ask_system_question)
        input_layout.addWidget(ask_btn)
        
        layout.addLayout(input_layout)
        
        # Area untuk respons
        self.system_response = QTextEdit()
        self.system_response.setReadOnly(True)
        self.system_response.setPlaceholderText("Respons akan muncul di sini...")
        self.system_response.setAcceptRichText(True)
        self.system_response.document().setDefaultStyleSheet("""
            body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 9pt; line-height: 1.3; }
            h3 { color: #4285F4; margin-top: 8px; margin-bottom: 4px; font-weight: bold; }
            p { margin: 5px 0; }
            ul, ol { margin-left: 20px; margin-top: 5px; margin-bottom: 5px; }
            li { margin: 3px 0; }
            code { background-color: #F5F5F5; padding: 1px 3px; border-radius: 3px; 
                   font-family: 'Consolas', 'Courier New', monospace; font-size: 9pt; }
            pre { background-color: #272822; color: #F8F8F2; padding: 8px; border-radius: 5px; 
                  font-family: 'Consolas', 'Courier New', monospace; font-size: 9pt; }
            .question { font-weight: bold; color: #2196F3; }
            .answer { }
        """)
        layout.addWidget(self.system_response)
    
    def _display_welcome_message(self):
        """Menampilkan pesan selamat datang di tab bantuan umum"""
        welcome_html = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; color: #333; padding: 10px;">
            <h2 style="color: #4CAF50; text-align: center;">Selamat Datang di EduBot</h2>
            <p style="text-align: center;">Asisten AI Desktop untuk Linux Edulite menggunakan {self.provider_name}</p>
            <p>Anda dapat menggunakan fitur-fitur berikut:</p>
            <ul>
                <li><b>Bantuan Umum:</b> Tanyakan apa saja seperti pada ChatGPT</li>
                <li><b>Bantuan Terminal:</b> Bantuan untuk perintah dan operasi terminal Linux</li>
                <li><b>Penjelasan Kode:</b> Dapatkan penjelasan untuk kode program</li>
                <li><b>Pembuatan Skrip:</b> Buat skrip otomatis untuk tugas Linux</li>
                <li><b>Info Sistem:</b> Lihat informasi sistem dan dapatkan bantuan terkait sistem</li>
            </ul>
            <p>Silakan mulai dengan mengetik pertanyaan Anda di kolom input di bawah.</p>
        </div>
        """
        # Gunakan setHtml alih-alih append untuk reset konten sepenuhnya
        self.chat_history.clear()
        self.chat_history.document().setHtml(welcome_html)
    
    def _send_chat_message(self):
        """Mengirim pesan dari tab bantuan umum ke ChatGPT API"""
        message = self.chat_input.text().strip()
        if not message:
            return
        
        # Tampilkan pesan pengguna dengan jelas
        self._append_user_message(self.chat_history, message)
        
        # Kosongkan input
        self.chat_input.clear()
        
        # Kirim ke API ChatGPT dan tampilkan respons
        self._get_ai_response(self.chat_history, message)
    
    def _send_terminal_question(self):
        """Mengirim pertanyaan terminal ke ChatGPT API"""
        question = self.terminal_input.text().strip()
        if not question:
            return
        
        # Tambahkan konteks Linux ke pertanyaan
        context = "Berikan bantuan untuk perintah terminal Linux. Jawaban yang berisi contoh perintah harus diberikan dalam bentuk kode (menggunakan tag <pre> untuk format). "
        full_question = context + question
        
        # Tampilkan pertanyaan pengguna
        self._append_user_message(self.terminal_history, question)
        
        # Kosongkan input
        self.terminal_input.clear()
        
        # Kirim ke API ChatGPT dan tampilkan respons
        self._get_ai_response(self.terminal_history, full_question)
    
    def _explain_code(self):
        """Meminta penjelasan kode dari ChatGPT API"""
        code = self.code_input.toPlainText().strip()
        if not code:
            QMessageBox.warning(self, "Input Kosong", "Masukkan kode yang ingin dijelaskan terlebih dahulu")
            return
        
        # Siapkan pertanyaan dengan konteks
        question = f"""Jelaskan kode berikut secara detail:

```
{code}
```

Berikan penjelasan terstruktur dengan menggunakan format Markdown:
1. Judul yang menjelaskan fungsi kode secara singkat
2. Penjelasan apa yang dilakukan kode secara keseluruhan
3. Bagaimana cara kerjanya dengan detil
4. Hal-hal penting yang perlu diperhatikan
5. Gunakan format paragraf yang baik dengan baris kosong antar paragraf
6. Gunakan istilah teknis dalam format code untuk nama fungsi atau variabel
7. Jangan gunakan format bold (**) dalam penjelasan, gunakan teks biasa
"""
        
        # Tampilkan pesan loading
        self.code_explanation.setHtml("<p>Mendapatkan penjelasan...</p>")
        
        # Mulai thread untuk mendapatkan respons dari API
        self.api_thread = ChatGPTThread(self.api, question)
        self.api_thread.response_received.connect(self._format_code_explanation)
        self.api_thread.start()
    
    def _format_code_explanation(self, response):
        """Format dan tampilkan penjelasan kode dengan cara yang sangat sederhana"""
        # Gunakan pendekatan yang lebih langsung dan sederhana
        # Hapus format markdown yang kompleks
        
        # Ganti newlines dengan <br>
        text = response.replace('\n', '<br>')
        
        # Tangani kode blok sangat sederhana
        if '```' in text:
            parts = text.split('```')
            for i in range(1, len(parts), 2):
                if i < len(parts):
                    # Ini adalah bagian kode
                    code = parts[i].strip()
                    if '\n' in code:
                        # Hapus baris pertama jika hanya berisi identifier bahasa
                        code_lines = code.split('\n', 1)
                        if len(code_lines) > 1 and not code_lines[0].strip():
                            code = code_lines[1]
                        else:
                            code = '\n'.join(code_lines)
                    
                    # Bungkus dalam pre tanpa highlight tambahan
                    parts[i] = f'<pre style="background-color: #272822; color: #F8F8F2; padding: 5px; border-radius: 4px; font-family: monospace; white-space: pre-wrap;">{code}</pre>'
            
            text = ''.join(parts)
        
        # Handle inline code blocks dengan sangat sederhana
        text = text.replace('`', '<code style="background-color: #F5F5F5; padding: 1px 3px; font-family: monospace;">')
        text = text.replace('`', '</code>')
        
        # Hilangkan semua markdown yang tersisa dan konversi ke plain HTML
        text = text.replace('**', '')  # Hapus semua bold markdown
        text = text.replace('*', '')   # Hapus semua italic markdown
        
        # Buat html sangat sederhana
        html = f'''
        <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; font-size: 9pt; line-height: 1.3; color: #333333; font-weight: normal;">
            <div style="padding: 10px;">
                {text}
            </div>
        </body>
        </html>
        '''
        
        # Tampilkan hasil
        self.code_explanation.setHtml(html)
    
    def _generate_script(self):
        """Membuat skrip dari deskripsi menggunakan ChatGPT API"""
        description = self.script_description.toPlainText().strip()
        if not description:
            QMessageBox.warning(self, "Input Kosong", "Masukkan deskripsi skrip yang ingin dibuat terlebih dahulu")
            return
        
        # Dapatkan jenis skrip
        script_type = self.script_type_combo.currentText()
        
        # Siapkan prompt yang lebih baik
        prompt = f"""Buat skrip {script_type} berdasarkan deskripsi berikut:

{description}

Skrip harus:
1. Berfungsi dengan baik di sistem Linux
2. Memiliki komentar yang jelas untuk setiap bagian
3. Memiliki error handling yang baik
4. Mengikuti best practices untuk {script_type}
5. Siap dijalankan tanpa modifikasi

Berikan HANYA skrip dalam format kode dengan tanda backtick (```) tanpa penjelasan tambahan.
"""
        
        # Tampilkan pesan loading
        self.script_result.setHtml("<p>Membuat skrip...</p>")
        
        # Mulai thread untuk mendapatkan respons dari API
        self.api_thread = ChatGPTThread(self.api, prompt)
        self.api_thread.response_received.connect(self._process_script_result)
        self.api_thread.start()
    
    def _process_script_result(self, response):
        """Memproses hasil pembuatan skrip dari API dengan pendekatan yang sangat sederhana"""
        try:
            # Coba ekstrak kode dari respons
            script = response.strip()
            
            # Cari kode dalam tanda ```
            import re
            code_blocks = re.findall(r'```(?:bash|sh|python|powershell)?\n(.*?)```', response, re.DOTALL)
            
            if code_blocks:
                # Ambil blok kode pertama
                script = code_blocks[0].strip()
            
            # Format HTML langsung dan sederhana tanpa menggunakan regex kompleks
            # yang dapat menyebabkan masalah dalam rendering
            script_type = self.script_type_combo.currentText()
            
            # Escape karakter khusus HTML
            script_escaped = script.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            
            # Buat HTML sederhana, tanpa format yang rumit
            html = f"""
            <html>
            <head>
                <style>
                    pre {{ 
                        background-color: #272822; 
                        color: #F8F8F2; 
                        padding: 10px; 
                        border-radius: 5px; 
                        font-family: 'Consolas', 'Courier New', monospace;
                        font-size: 9pt;
                        line-height: 1.2;
                        white-space: pre-wrap;
                    }}
                </style>
            </head>
            <body>
                <pre>{script_escaped}</pre>
            </body>
            </html>
            """
            
            # Tampilkan skrip
            self.script_result.setHtml(html)
            
        except Exception as e:
            # Jika terjadi kesalahan formatting, tampilkan dengan cara sederhana
            print(f"Error saat memformat skrip: {e}")
            self.script_result.setPlainText(script)
    
    def _save_script(self):
        """Menyimpan skrip yang dihasilkan"""
        script = self.script_result.toPlainText().strip()
        if not script:
            QMessageBox.warning(self, "Skrip Kosong", "Tidak ada skrip yang bisa disimpan")
            return
        
        # Dialog untuk memilih nama dan lokasi file
        from PyQt5.QtWidgets import QFileDialog
        
        # Tentukan ekstensi berdasarkan jenis skrip
        script_type = self.script_type_combo.currentText()
        if script_type == "bash":
            file_filter = "Bash Script (*.sh);;All Files (*)"
            default_name = "script.sh"
        elif script_type == "python":
            file_filter = "Python Script (*.py);;All Files (*)"
            default_name = "script.py"
        elif script_type == "powershell":
            file_filter = "PowerShell Script (*.ps1);;All Files (*)"
            default_name = "script.ps1"
        else:
            file_filter = "All Files (*)"
            default_name = "script.txt"
        
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Simpan Skrip", os.path.expanduser(f"~/{default_name}"), 
            file_filter
        )
        
        if file_name:
            try:
                # Dapatkan teks mentah tanpa formatting HTML
                raw_script = self.script_result.toPlainText()
                
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(raw_script)
                
                # Jika ini skrip bash, buat executable
                if file_name.endswith('.sh'):
                    try:
                        os.chmod(file_name, 0o755)
                    except:
                        # Abaikan error chmod pada Windows
                        pass
                
                QMessageBox.information(self, "Berhasil", f"Skrip berhasil disimpan ke {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menyimpan skrip: {str(e)}")
    
    def _ask_system_question(self):
        """Menanyakan pertanyaan tentang sistem ke ChatGPT API"""
        question = self.system_input.text().strip()
        if not question:
            return
        
        # Tambahkan konteks sistem ke pertanyaan
        system_info = self._get_system_info_text()
        context = f"Berdasarkan informasi sistem berikut:\n{system_info}\n\n"
        full_question = context + question
        
        # Tampilkan pertanyaan pengguna
        self.system_response.setHtml(f"<h3 class='question'>Pertanyaan:</h3><p>{question}</p><p><i>Mendapatkan respons...</i></p>")
        
        # Kosongkan input
        self.system_input.clear()
        
        # Mulai thread untuk mendapatkan respons dari API
        self.api_thread = ChatGPTThread(self.api, full_question)
        self.api_thread.response_received.connect(lambda response: self._format_system_response(question, response))
        self.api_thread.start()
    
    def _format_system_response(self, question, response):
        """Format respons sistem untuk tampilan yang lebih baik"""
        # Membersihkan output markdown dan mengubahnya menjadi HTML yang rapi
        
        # Escape karakter khusus HTML
        response = response.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        # Konversi newlines ke <br>
        response = response.replace('\n\n', '<br><br>')
        response = response.replace('\n', '<br>')
        
        # Tangani kode blok
        if '```' in response:
            parts = response.split('```')
            for i in range(1, len(parts), 2):
                if i < len(parts):
                    # Bagian kode
                    code = parts[i].strip()
                    # Hapus baris pertama jika hanya berisi identifier bahasa
                    if '<br>' in code:
                        code_parts = code.split('<br>', 1)
                        language = code_parts[0].strip()
                        if not language or language in ['bash', 'sh', 'python', 'cmd', 'powershell', 'ps1', 'json', 'xml', 'html']:
                            code = code_parts[1] if len(code_parts) > 1 else code
                    
                    # Buat pre tag dengan style inline
                    parts[i] = f'<pre>{code}</pre>'
            
            response = ''.join(parts)
        
        # Tangani inline code (format `)
        if '`' in response:
            temp = ''
            in_code = False
            parts = response.split('`')
            for i, part in enumerate(parts):
                if i % 2 == 1:  # Ini adalah bagian kode
                    temp += f'<code>{part}</code>'
                else:
                    temp += part
            response = temp
            
        # Tangani format bold dan italic (hapus markdown)
        response = response.replace('**', '')  # Hapus bold
        response = response.replace('*', '')   # Hapus italic
        
        # Tangani daftar dengan pendekatan yang berbeda, lebih sederhana dan langsung
        lines = response.split('<br>')
        formatted_html = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Deteksi daftar berurutan (numbered list)
            if line and line[0].isdigit() and '. ' in line:
                # Mulai div container untuk daftar
                formatted_html.append('<div class="list-container">')
                
                # Gunakan counter manual
                list_counter = 1
                
                # Loop untuk mengumpulkan semua item daftar berurutan
                while i < len(lines) and lines[i].strip() and lines[i].strip()[0].isdigit() and '. ' in lines[i].strip():
                    item_text = lines[i].strip().split('. ', 1)[1]
                    # Gunakan struktur div dengan nomor eksplisit dan style padding
                    formatted_html.append(f'<div class="list-item"><div class="list-number">{list_counter}.</div><div class="list-content">{item_text}</div></div>')
                    list_counter += 1
                    i += 1
                
                # Tutup div container
                formatted_html.append('</div>')
                
                # Jangan increment i lagi karena sudah diincrement dalam loop di atas
                continue
            
            # Deteksi daftar tidak berurutan (bullet list)
            elif line.startswith('- ') or line.startswith('* '):
                # Mulai div container untuk daftar
                formatted_html.append('<div class="list-container">')
                
                # Loop untuk mengumpulkan semua item daftar tidak berurutan
                while i < len(lines) and (lines[i].strip().startswith('- ') or lines[i].strip().startswith('* ')):
                    item_text = lines[i].strip()[2:].strip()
                    # Gunakan struktur div dengan bullet eksplisit
                    formatted_html.append(f'<div class="list-item"><div class="list-bullet">•</div><div class="list-content">{item_text}</div></div>')
                    i += 1
                
                # Tutup div container
                formatted_html.append('</div>')
                
                # Jangan increment i lagi karena sudah diincrement dalam loop di atas
                continue
            
            # Paragraf biasa
            elif line:
                formatted_html.append(f'<p>{line}</p>')
            else:
                # Baris kosong
                formatted_html.append('<br>')
            
            i += 1
        
        # Buat HTML lengkap dengan styling inline untuk memastikan tampilan yang konsisten
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 9pt; line-height: 1.3; color: #333333; }}
                h3 {{ color: #4285F4; margin-top: 10px; margin-bottom: 8px; }}
                p {{ margin: 8px 0; }}
                pre {{ background-color: #272822; color: #F8F8F2; padding: 8px; border-radius: 5px; 
                      font-family: 'Consolas', 'Courier New', monospace; font-size: 9pt; overflow-x: auto; }}
                code {{ background-color: #F5F5F5; padding: 1px 3px; border-radius: 3px; 
                       font-family: 'Consolas', 'Courier New', monospace; font-size: 9pt; }}
                .list-container {{ margin-left: 15px; margin-bottom: 10px; }}
                .list-item {{ display: flex; margin-bottom: 6px; }}
                .list-number {{ min-width: 20px; margin-right: 10px; text-align: right; }}
                .list-bullet {{ min-width: 20px; margin-right: 10px; text-align: center; }}
                .list-content {{ flex: 1; }}
                .question {{ font-weight: bold; color: #2196F3; }}
            </style>
        </head>
        <body>
            <h3 class='question'>Pertanyaan:</h3>
            <p>{question}</p>
            <h3>Jawaban:</h3>
            <div>
                {''.join(formatted_html)}
            </div>
        </body>
        </html>
        """
        
        # Update tampilan
        self.system_response.setHtml(html)
    
    def _get_system_info(self):
        """Mendapatkan informasi sistem dalam format HTML"""
        info_html = "<h3>Informasi Sistem</h3>"
        
        # Informasi dasar
        info_html += "<p><b>Sistem Operasi:</b> " + platform.system() + " " + platform.release() + "</p>"
        info_html += "<p><b>Versi OS:</b> " + platform.version() + "</p>"
        info_html += "<p><b>Arsitektur:</b> " + platform.machine() + "</p>"
        info_html += "<p><b>Nama Host:</b> " + platform.node() + "</p>"
        
        # Untuk informasi lebih lanjut yang specific untuk Linux
        if platform.system() == "Linux":
            try:
                # Kernel version
                kernel = subprocess.check_output("uname -r", shell=True).decode().strip()
                info_html += "<p><b>Versi Kernel:</b> " + kernel + "</p>"
                
                # Distribution info if available
                if os.path.exists("/etc/os-release"):
                    with open("/etc/os-release", "r") as f:
                        for line in f:
                            if line.startswith("PRETTY_NAME="):
                                distro = line.split("=")[1].strip().strip('"')
                                info_html += "<p><b>Distribusi:</b> " + distro + "</p>"
                                break
                
                # CPU info
                cpu_info = subprocess.check_output("cat /proc/cpuinfo | grep 'model name' | head -n 1", shell=True).decode()
                if cpu_info:
                    cpu_model = cpu_info.split(":")[1].strip()
                    info_html += "<p><b>CPU:</b> " + cpu_model + "</p>"
                
                # Memory info
                mem_info = subprocess.check_output("free -h | grep Mem", shell=True).decode().strip()
                if mem_info:
                    mem_parts = mem_info.split()
                    if len(mem_parts) >= 2:
                        total_mem = mem_parts[1]
                        info_html += "<p><b>Total RAM:</b> " + total_mem + "</p>"
            except:
                # Jika ada error, lewati
                pass
        
        return info_html
    
    def _get_system_info_text(self):
        """Mendapatkan informasi sistem dalam format teks biasa"""
        info = []
        
        # Informasi dasar
        info.append(f"Sistem Operasi: {platform.system()} {platform.release()}")
        info.append(f"Versi OS: {platform.version()}")
        info.append(f"Arsitektur: {platform.machine()}")
        info.append(f"Nama Host: {platform.node()}")
        
        # Untuk informasi lebih lanjut yang specific untuk Linux
        if platform.system() == "Linux":
            try:
                # Kernel version
                kernel = subprocess.check_output("uname -r", shell=True).decode().strip()
                info.append(f"Versi Kernel: {kernel}")
                
                # Distribution info if available
                if os.path.exists("/etc/os-release"):
                    with open("/etc/os-release", "r") as f:
                        for line in f:
                            if line.startswith("PRETTY_NAME="):
                                distro = line.split("=")[1].strip().strip('"')
                                info.append(f"Distribusi: {distro}")
                                break
                
                # CPU info
                cpu_info = subprocess.check_output("cat /proc/cpuinfo | grep 'model name' | head -n 1", shell=True).decode()
                if cpu_info:
                    cpu_model = cpu_info.split(":")[1].strip()
                    info.append(f"CPU: {cpu_model}")
                
                # Memory info
                mem_info = subprocess.check_output("free -h | grep Mem", shell=True).decode().strip()
                if mem_info:
                    mem_parts = mem_info.split()
                    if len(mem_parts) >= 2:
                        total_mem = mem_parts[1]
                        info.append(f"Total RAM: {total_mem}")
            except:
                # Jika ada error, lewati
                pass
        
        return "\n".join(info)
    
    def _append_user_message(self, text_widget, message):
        """Menambahkan pesan pengguna ke widget teks"""
        # Pastikan pesan terlihat jelas dengan format yang mencolok
        formatted_message = message.replace("\n", "<br/>")
        html = f'''
        <div class="user-msg">
            <b>Anda:</b><br/>
            {formatted_message}
        </div>
        '''
        text_widget.append(html)
        # Pastikan scroll ke posisi terbawah
        text_widget.verticalScrollBar().setValue(text_widget.verticalScrollBar().maximum())
    
    def _append_bot_message(self, text_widget, message):
        """Menambahkan pesan bot ke widget teks"""
        # Tentukan nama bot berdasarkan provider
        if self.auth_manager.get_provider() == "openai":
            bot_name = "EduBot (OpenAI)"
            color = "#42A5F5"  # Biru untuk OpenAI
        elif self.auth_manager.get_provider() == "deepseek":
            bot_name = "DeepBot"
            color = "#7E57C2"  # Ungu untuk DeepSeek
        else:  # gemini
            bot_name = "GeminiBot"
            color = "#26A69A"  # Teal untuk Gemini
        
        # Format pesan dengan HTML yang lebih baik
        formatted_message = message.replace("\n", "<br/>")
        html = f'''
        <div class="bot-msg" style="border-left-color: {color};">
            <b style="color: {color};">{bot_name}:</b><br/>
            {formatted_message}
        </div>
        '''
        text_widget.append(html)
        # Pastikan scroll ke posisi terbawah
        text_widget.verticalScrollBar().setValue(text_widget.verticalScrollBar().maximum())
    
    def _get_ai_response(self, text_widget, message):
        """Mendapatkan respons dari API ChatGPT dan menampilkannya"""
        # Tambahkan indikator loading
        if self.auth_manager.get_provider() == "openai":
            bot_name = "EduBot (OpenAI)"
        elif self.auth_manager.get_provider() == "deepseek":
            bot_name = "DeepBot"
        else:  # gemini
            bot_name = "GeminiBot"
            
        # Tambahkan indikator loading dengan ID unik
        loading_id = "loading_indicator"
        loading_html = f'<div id="{loading_id}" style="font-style: italic; margin: 5px 0;">{bot_name} sedang mengetik...</div>'
        text_widget.append(loading_html)
        text_widget.verticalScrollBar().setValue(text_widget.verticalScrollBar().maximum())
        
        # Mulai thread untuk mendapatkan respons dari API
        self.api_thread = ChatGPTThread(self.api, message)
        self.api_thread.response_received.connect(lambda response: self._process_api_response(text_widget, response))
        self.api_thread.start()
        
    def _process_api_response(self, text_widget, response):
        """Memproses dan menampilkan respons dari API"""
        # Sembunyikan dokumen sementara untuk menghindari refresh berkali-kali
        text_widget.setUpdatesEnabled(False)
        
        # Dapatkan HTML saat ini
        html = text_widget.toHtml()
        
        # Hapus indikator loading dengan mencari div loading_indicator
        if "loading_indicator" in html:
            loading_start = html.find('<div id="loading_indicator"')
            if loading_start >= 0:
                loading_end = html.find('</div>', loading_start) + 6
                html = html[:loading_start] + html[loading_end:]
                # Set HTML baru tanpa loading indicator
                text_widget.setHtml(html)
        
        # Tampilkan respons bot
        self._append_bot_message(text_widget, response)
        
        # Aktifkan kembali pembaruan UI
        text_widget.setUpdatesEnabled(True)
    
    def _logout(self):
        """Melakukan logout dari aplikasi"""
        provider_name = "OpenAI" if self.auth_manager.get_provider() == "openai" else "DeepSeek"
        
        reply = QMessageBox.question(
            self, 
            "Konfirmasi Logout", 
            f"Apakah Anda yakin ingin logout dari {provider_name}? Anda perlu memasukkan API key lagi saat membuka aplikasi nanti.",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.auth_manager.logout():
                QMessageBox.information(self, "Logout Berhasil", "Anda telah berhasil logout dari akun Anda.")
                self.close()
            else:
                QMessageBox.warning(self, "Logout Gagal", "Terjadi kesalahan saat melakukan logout.")
    
    def _show_about(self):
        """Menampilkan informasi tentang aplikasi"""
        about_text = f"""
        <h2>EduBot v1.0</h2>
        <p>Asisten AI Desktop untuk Linux Edulite dengan {self.provider_name}</p>
        <p>EduBot adalah aplikasi yang mengintegrasikan AI untuk memberikan bantuan
        terkait sistem Linux, pemrograman, dan pertanyaan umum lainnya.</p>
        <p>Dibuat untuk sistem operasi Linux Edulite (berbasis Linux Mint).</p>
        <p>&copy; 2023 Edulite</p>
        """
        
        QMessageBox.about(self, "Tentang EduBot", about_text)
    
    def _show_help(self):
        """Menampilkan bantuan penggunaan aplikasi"""
        help_text = """
        <h2>Bantuan Penggunaan EduBot</h2>
        
        <h3>Tab Bantuan Umum</h3>
        <p>Tanyakan apa saja seperti yang Anda lakukan di ChatGPT online.</p>
        
        <h3>Tab Bantuan Terminal</h3>
        <p>Tanyakan tentang perintah terminal Linux, sintaks, atau cara mengatasi masalah terkait terminal.</p>
        
        <h3>Tab Penjelasan Kode</h3>
        <p>Tempel kode program di panel kiri, lalu klik "Jelaskan Kode" untuk mendapatkan penjelasan.</p>
        
        <h3>Tab Pembuatan Skrip</h3>
        <p>Jelaskan skrip yang ingin dibuat di panel kiri, lalu klik "Buat Skrip" untuk menghasilkan skrip otomatis.</p>
        
        <h3>Tab Info Sistem</h3>
        <p>Lihat informasi dasar tentang sistem Anda dan tanyakan pertanyaan terkait sistem.</p>
        """
        
        QMessageBox.information(self, "Bantuan Penggunaan", help_text)

class ChatGPTThread(QThread):
    """Thread terpisah untuk berkomunikasi dengan API ChatGPT"""
    
    # Sinyal yang akan dipancarkan saat respons diterima
    response_received = pyqtSignal(str)
    
    def __init__(self, api, message):
        """Inisialisasi thread"""
        super().__init__()
        self.api = api
        self.message = message
    
    def run(self):
        """Menjalankan thread"""
        try:
            response = self.api.get_response(self.message)
            self.response_received.emit(response)
        except Exception as e:
            self.response_received.emit(f"Error: {str(e)}") 