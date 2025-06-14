# EduBot

EduBot adalah aplikasi desktop untuk sistem operasi Linux, khususnya untuk distribusi Edulite (berbasis Linux Mint), yang memiliki fungsionalitas serupa dengan Copilot di Windows. Aplikasi ini menggunakan ChatGPT sebagai inti dari fitur AI-nya.

## Fitur Utama

- **Bantuan Umum**: Tanyakan apa saja seperti yang Anda lakukan di ChatGPT online.
- **Bantuan Terminal**: Bantuan tentang perintah terminal Linux, sintaks, dan cara mengatasi masalah.
- **Penjelasan Kode**: Dapatkan penjelasan terperinci untuk kode program dalam berbagai bahasa.
- **Pembuatan Skrip**: Buat skrip otomatis untuk tugas-tugas di Linux.
- **Info Sistem**: Lihat informasi tentang sistem dan dapatkan bantuan terkait sistem.

## Persyaratan

- Python 3.6 atau lebih baru
- Distribusi Linux (dioptimalkan untuk Edulite/Linux Mint)
- API key OpenAI

## Instalasi

### 1. Instalasi Dependensi

```bash
# Install dependensi sistem
sudo apt update
sudo apt install python3-pip python3-pyqt5

# Clone repositori
git clone https://github.com/edulite/edubot.git
cd edubot

# Instalasi dependensi Python
pip3 install -r requirements.txt
```

### 2. Konfigurasi

Untuk menggunakan EduBot, Anda memerlukan API key OpenAI. API key ini akan diminta saat pertama kali menjalankan aplikasi.

Anda dapat mendapatkan API key dari [OpenAI Platform](https://platform.openai.com/api-keys).

### 3. Menjalankan Aplikasi

```bash
# Dari direktori edubot
python3 edubot.py
```

## Membuat Shortcut Desktop

Untuk membuat shortcut desktop di Edulite/Linux Mint:

1. Buat file .desktop:

```bash
cat > ~/.local/share/applications/edubot.desktop << EOF
[Desktop Entry]
Name=EduBot
Comment=Asisten AI Desktop untuk Linux Edulite
Exec=python3 /path/to/edubot/edubot.py
Icon=/path/to/edubot/resources/edubot_icon.png
Terminal=false
Type=Application
Categories=Utility;Education;AI;
EOF
```

2. Ganti `/path/to/edubot/` dengan path lengkap ke direktori edubot Anda.

3. Buat file menjadi executable:

```bash
chmod +x ~/.local/share/applications/edubot.desktop
```

## Penggunaan

Saat pertama kali menjalankan aplikasi, Anda akan diminta untuk memasukkan API key OpenAI Anda. Setelah itu, API key akan disimpan secara aman menggunakan sistem keyring, sehingga Anda tidak perlu memasukkannya lagi.

### Tab Bantuan Umum

Di tab ini, Anda dapat menanyakan apa saja seperti yang Anda lakukan di ChatGPT online.

### Tab Bantuan Terminal

Tab ini dirancang khusus untuk bantuan terkait terminal Linux. Tanyakan tentang perintah, sintaks, atau cara mengatasi masalah terkait terminal.

### Tab Penjelasan Kode

Tempel kode program di panel kiri, lalu klik "Jelaskan Kode" untuk mendapatkan penjelasan terperinci tentang kode tersebut.

### Tab Pembuatan Skrip

Jelaskan skrip yang ingin Anda buat di panel kiri, lalu klik "Buat Skrip" untuk menghasilkan skrip otomatis. Anda juga dapat menyimpan skrip tersebut ke file.

### Tab Info Sistem

Lihat informasi dasar tentang sistem Anda dan tanyakan pertanyaan terkait sistem.

## Keamanan

EduBot menyimpan API key OpenAI Anda menggunakan sistem keyring yang aman, dan tidak pernah mengirimkannya ke pihak ketiga selain OpenAI.

## Lisensi

EduBot dilisensikan di bawah [MIT License](LICENSE). 