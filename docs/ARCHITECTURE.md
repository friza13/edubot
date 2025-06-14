# Arsitektur EduBot

Dokumen ini menjelaskan arsitektur aplikasi EduBot, termasuk struktur kode, alur kerja, dan komponen utama.

## Struktur Direktori

```
edubot/
├── requirements.txt    # Daftar dependensi Python
├── edubot.py           # Titik masuk aplikasi
├── README.md           # Dokumentasi utama
├── LICENSE             # Lisensi MIT
├── src/                # Kode sumber
│   ├── main.py         # Fungsi main untuk aplikasi
│   ├── auth_manager.py # Pengelola otentikasi
│   ├── main_window.py  # Antarmuka pengguna utama
│   └── chatgpt_api.py  # Integrasi dengan OpenAI API
├── resources/          # Sumber daya aplikasi
│   └── edubot_icon.png # Ikon aplikasi
└── docs/               # Dokumentasi tambahan
    └── ARCHITECTURE.md # Dokumen ini
```

## Komponen Utama

### 1. Titik Masuk Aplikasi (`edubot.py`)

File ini adalah titik masuk aplikasi. Ia mengimpor fungsi `main` dari `src/main.py` dan menjalankannya saat aplikasi dimulai.

### 2. Fungsi Main (`src/main.py`)

Fungsi ini:
- Menyiapkan aplikasi PyQt5
- Menginisialisasi `AuthManager`
- Memeriksa apakah pengguna sudah terotentikasi
- Mengarahkan pengguna ke proses otentikasi jika diperlukan
- Membuka jendela utama aplikasi setelah otentikasi

### 3. Pengelola Otentikasi (`src/auth_manager.py`)

Kelas `AuthManager` mengelola:
- Proses otentikasi pengguna dengan OpenAI API
- Penyimpanan API key menggunakan sistem keyring
- Verifikasi validitas API key
- Logout pengguna
- Pengelolaan konfigurasi

### 4. Jendela Utama (`src/main_window.py`)

Kelas `MainWindow` mengelola:
- Antarmuka pengguna utama dengan berbagai tab
- Interaksi pengguna dengan API ChatGPT
- Tab-tab untuk fitur berbeda: bantuan umum, bantuan terminal, penjelasan kode, pembuatan skrip, dan info sistem
- Menu aplikasi dan fungsi-fungsi lainnya

Kelas `ChatGPTThread` mengelola permintaan API di thread terpisah untuk mencegah pembekuan UI.

### 5. Integrasi ChatGPT (`src/chatgpt_api.py`)

Kelas `ChatGPTAPI` mengelola:
- Komunikasi dengan OpenAI API
- Pengelolaan riwayat chat untuk berbagai sesi
- Penerapan prompt sistem khusus untuk berbagai fitur
- Pembatasan jumlah token yang digunakan

## Aliran Data dan Alur Kerja

1. **Otentikasi Pengguna:**
   - Pengguna memulai aplikasi melalui `edubot.py`
   - `AuthManager` memeriksa apakah ada API key yang tersimpan
   - Jika tidak ada atau tidak valid, pengguna diminta untuk memasukkan API key
   - API key diverifikasi dengan OpenAI API dan disimpan menggunakan sistem keyring

2. **Interaksi Pengguna dengan UI:**
   - Setelah otentikasi, jendela utama ditampilkan
   - Pengguna berinteraksi dengan berbagai tab untuk fitur yang berbeda
   - Setiap interaksi dikirim ke thread terpisah untuk komunikasi dengan API

3. **Komunikasi dengan OpenAI API:**
   - Permintaan pengguna dikirim ke OpenAI API melalui kelas `ChatGPTAPI`
   - Respons dari API ditampilkan di UI
   - Riwayat chat dikelola untuk konteks percakapan yang berkelanjutan

4. **Fitur-Fitur Khusus:**
   - **Bantuan Terminal:** Mengirim prompt khusus untuk bantuan perintah terminal Linux
   - **Penjelasan Kode:** Mengekstrak dan mengirim kode dengan prompt yang meminta penjelasan
   - **Pembuatan Skrip:** Mengirim deskripsi skrip dengan prompt untuk membuat skrip yang dapat berjalan
   - **Info Sistem:** Mengumpulkan informasi sistem dan mengirimkannya sebagai konteks

## Keamanan

- API key disimpan menggunakan sistem keyring yang aman
- Tidak ada informasi sensitif yang disimpan dalam file teks biasa
- Komunikasi dengan OpenAI API menggunakan HTTPS
- Verifikasi API key dilakukan sebelum penggunaan

## Pengelolaan Sesi

- Riwayat chat dikelola secara terpisah untuk setiap fitur
- Prompt sistem khusus diterapkan untuk masing-masing fitur
- Riwayat chat dipotong secara otomatis untuk mengurangi penggunaan token

## Keterbatasan dan Area Pengembangan

- Saat ini hanya mendukung model gpt-3.5-turbo dan gpt-4
- Belum ada dukungan untuk pengaturan model atau parameter API yang disesuaikan oleh pengguna
- Dapat ditambahkan fitur untuk menyimpan dan memuat percakapan
- Dapat ditambahkan dukungan untuk fitur ChatGPT lainnya seperti plugin 