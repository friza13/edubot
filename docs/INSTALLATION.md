# Panduan Instalasi EduBot

Panduan ini memberikan instruksi terperinci untuk instalasi EduBot di sistem Linux, khususnya distribusi Edulite (berbasis Linux Mint).

## Persyaratan Sistem

- Sistem operasi Linux (dioptimalkan untuk Edulite/Linux Mint)
- Python 3.6 atau yang lebih baru
- pip (Pengelola paket Python)
- API key OpenAI

## Langkah-Langkah Instalasi

### 1. Instal Dependensi Sistem

Buka terminal dan jalankan perintah berikut untuk memperbarui daftar paket dan menginstal dependensi yang diperlukan:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-pyqt5 python3-keyring git
```

### 2. Unduh Kode Sumber EduBot

Kloning repositori EduBot dari GitHub:

```bash
git clone https://github.com/edulite/edubot.git
cd edubot
```

Atau, jika Anda telah menerima EduBot sebagai arsip, ekstrak dan navigasikan ke direktori:

```bash
cd path/to/edubot
```

### 3. Instal Dependensi Python

Instal semua paket Python yang diperlukan menggunakan pip:

```bash
pip3 install -r requirements.txt
```

Ini akan menginstal semua dependensi yang diperlukan seperti PyQt5, openai, requests, python-dotenv, dan keyring.

### 4. Dapatkan API Key OpenAI

Anda memerlukan API key OpenAI untuk menggunakan EduBot:

1. Kunjungi [OpenAI Platform](https://platform.openai.com/api-keys)
2. Buat akun atau masuk ke akun Anda
3. Buat API key baru
4. Salin API key tersebut (Anda akan memasukkannya ke EduBot saat pertama kali menjalankan aplikasi)

### 5. Jalankan EduBot

Jalankan aplikasi EduBot dengan perintah:

```bash
python3 edubot.py
```

Pada peluncuran pertama, Anda akan diminta untuk memasukkan API key OpenAI Anda.

## Instalasi untuk Penggunaan yang Lebih Mudah

### Membuat Shortcut Desktop

Untuk membuat shortcut desktop di Edulite/Linux Mint:

1. Buat file .desktop:

```bash
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/edubot.desktop << EOF
[Desktop Entry]
Name=EduBot
Comment=Asisten AI Desktop untuk Linux Edulite
Exec=python3 $(pwd)/edubot.py
Icon=$(pwd)/resources/edubot_icon.png
Terminal=false
Type=Application
Categories=Utility;Education;AI;
EOF
```

2. Buat file menjadi executable:

```bash
chmod +x ~/.local/share/applications/edubot.desktop
```

### Membuat Command Line Shortcut

Untuk memungkinkan Anda menjalankan EduBot dari terminal di mana saja:

```bash
echo 'alias edubot="python3 $(pwd)/edubot.py"' >> ~/.bashrc
source ~/.bashrc
```

Sekarang Anda dapat menjalankan EduBot cukup dengan mengetik `edubot` di terminal.

## Pemecahan Masalah

### 1. Masalah Dependensi

Jika Anda mengalami masalah dengan dependensi, coba instal dependensi secara manual:

```bash
pip3 install PyQt5==5.15.9 openai==1.3.0 requests==2.31.0 python-dotenv==1.0.0 keyring==24.2.0
```

### 2. Masalah API Key

Jika Anda ingin mereset API key:

```bash
python3 -c "import keyring; keyring.delete_password('edubot', 'openai_api_key')"
```

### 3. Masalah Hak Akses

Jika Anda mengalami masalah hak akses:

```bash
chmod +x edubot.py
chmod -R 755 src/
```

### 4. Masalah Python Interpreter

Jika Anda memiliki beberapa versi Python, pastikan untuk menggunakan Python 3:

```bash
python3 edubot.py
```

## Instalasi di Distribusi Linux Lainnya

### Arch Linux dan Turunannya

```bash
sudo pacman -Sy python python-pip python-pyqt5 python-keyring git
git clone https://github.com/edulite/edubot.git
cd edubot
pip install -r requirements.txt
python edubot.py
```

### Fedora

```bash
sudo dnf install python3 python3-pip python3-qt5 python3-keyring git
git clone https://github.com/edulite/edubot.git
cd edubot
pip3 install -r requirements.txt
python3 edubot.py
```

### OpenSUSE

```bash
sudo zypper install python3 python3-pip python3-qt5 python3-keyring git
git clone https://github.com/edulite/edubot.git
cd edubot
pip3 install -r requirements.txt
python3 edubot.py
```

## Penggunaan Virtual Environment (Opsional)

Untuk pengguna yang lebih berpengalaman, Anda mungkin ingin menggunakan virtual environment Python:

```bash
# Buat virtual environment
python3 -m venv edubot_env

# Aktifkan virtual environment
source edubot_env/bin/activate

# Instal dependensi
pip install -r requirements.txt

# Jalankan EduBot
python edubot.py

# Ketika selesai, deaktifkan virtual environment
deactivate
```

## Informasi Tambahan

Untuk informasi lebih lanjut tentang EduBot, lihat:

- [README.md](../README.md) - Untuk gambaran umum dan penggunaan dasar
- [ARCHITECTURE.md](ARCHITECTURE.md) - Untuk informasi tentang arsitektur aplikasi 