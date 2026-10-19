# FILE//ORGANIZER™ [TACTICAL STREETWEAR EDITION]

Aplikasi Desktop Windows modern dengan tema **Industrial Brutalism & Streetwear** untuk mengorganisir file yang berserakan ke dalam folder harian secara otomatis, cepat, dan aman.

![Aesthetic](assets/icon.png)

---

## ⚡ Fitur Utama

1. **One-Click Folder Organization:**
   - Cukup pilih folder tujuan melalui tombol `[ BROWSE DIR ]` atau masukkan path folder.
   - Aplikasi otomatis mengindeks seluruh file dan menghitung folder harian tujuannya.

2. **Live Preview Matrix:**
   - Menampilkan tabel resolusi file yang terdeteksi sebelum proses dijalankan: status, nama file, ukuran, tanggal, dan folder tujuan.
   - Filter pencarian cepat untuk memfilter nama file secara instan.

3. **Opsi Pengaturan Fleksibel (Toggles):**
   - **Acuan Tanggal:** *Date Modified*, *Date Created*, atau *EXIF Photo Date* (mengambil tanggal asli kamera pada foto).
   - **Format Penamaan Folder:** `YYYY-MM-DD` (ISO), `DD-MM-YYYY`, `YYYY_MM_DD`, `YYYY.MM.DD`, `YYYY/MM`, dll.
   - **Scan Scope:** Hanya file utama (*root*) atau rekursif (termasuk file di dalam subfolder).
   - **Collision Policy:** Pop-up konfirmasi saat nama file bentrok, *Auto-Rename* (`file_1.ext`), *Skip*, atau *Overwrite*.

4. **Safety & 1-Click Undo Engine:**
   - Setiap eksekusi mencatat riwayat transaksi.
   - Tombol `[ << UNDO LAST RUN ]` mengembalikan seluruh file yang dipindahkan ke lokasi awalnya secara akurat serta membersihkan folder kosong yang sempat dibuat.

---

## 🚀 Cara Menjalankan

### Cara 1: Menggunakan File Standalone Executable (.EXE)
Jalankan file executable yang sudah dibuild:
```
dist/FileOrganizer.exe
```
*(Tidak memerlukan instalasi Python atau library apapun pada komputer tujuan)*

### Cara 2: Menjalankan via Python
```powershell
python main.py
```

### Cara 3: Melakukan Compile Sendiri ke .EXE
```powershell
python build_exe.py
```
Hasil file `.exe` akan otomatis tersimpan di folder `dist/FileOrganizer.exe`.
