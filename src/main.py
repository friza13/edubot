#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EduBot - Aplikasi AI Desktop untuk Linux Edulite
"""
import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QCoreApplication

# Mengimpor komponen aplikasi
from auth_manager import AuthManager
from main_window import MainWindow

def main():
    """Fungsi utama yang menjalankan aplikasi EduBot"""
    # Mengatur informasi aplikasi
    QCoreApplication.setApplicationName("EduBot")
    QCoreApplication.setOrganizationName("Edulite")
    QCoreApplication.setOrganizationDomain("edulite.org")
    
    # Membuat instance aplikasi PyQt
    app = QApplication(sys.argv)
    
    # Inisialisasi manajer otentikasi
    auth_manager = AuthManager()
    
    # Memeriksa apakah pengguna sudah autentikasi
    if auth_manager.is_authenticated():
        # Jika sudah autentikasi, langsung buka jendela utama
        window = MainWindow(auth_manager)
        window.show()
    else:
        # Jika belum, lakukan proses autentikasi
        if auth_manager.authenticate():
            window = MainWindow(auth_manager)
            window.show()
        else:
            sys.exit(1)  # Keluar jika autentikasi gagal
    
    # Menjalankan event loop aplikasi
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 