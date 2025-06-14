#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EduBot - Aplikasi AI Desktop untuk Linux Edulite
"""
import os
import sys

# Tambahkan direktori src ke path agar dapat mengimpor modul
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Impor modul utama
from src.main import main

if __name__ == "__main__":
    # Jalankan aplikasi
    main() 