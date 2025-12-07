# Shooting Schedule

Aplikasi Django untuk manajemen jadwal syuting video.

## Fitur
- Auth (login, register, logout) dengan peran Produser/Aktor
- Dashboard Produser: buat/edit/hapus/tandai selesai, lihat aktor yang join
- Dashboard Aktor: lihat jadwal tersedia, join/leave, lihat script/naskah
- Notifikasi sistem saat aktor join/leave (disimpan di DB)
- Reminder H-1: dashboard box dan management command `send_reminders`

## Setup
1. Buat virtualenv dan install dependensi:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
2. Migrasi database:
```bash
python manage.py makemigrations
python manage.py migrate
```
3. Buat superuser:
```bash
python manage.py createsuperuser
```
4. Jalankan server:
```bash
python manage.py runserver
```

## Konfigurasi Penting
- `AUTH_USER_MODEL = 'schedule.User'`
- `TIME_ZONE = 'Asia/Jakarta'`, `USE_TZ = True`
- Redirects: `LOGIN_URL='login'`, `LOGIN_REDIRECT_URL='dashboard'`, `LOGOUT_REDIRECT_URL='login'`

## Management Command (Reminder)
Kirim notifikasi untuk semua jadwal besok yang berstatus `confirmed`.
```bash
python manage.py send_reminders
```
Contoh cron (20:00 setiap hari):
```
0 20 * * * /path/to/venv/bin/python /path/to/project/manage.py send_reminders >> /var/log/send_reminders.log 2>&1
```

## Sample Data (opsional)
Masuk ke admin (`/admin/`), buat beberapa user:
- Produser: `role=producer`
- Aktor: `role=actor`

Buat jadwal via dashboard produser, lalu login sebagai aktor untuk melakukan join.

## Alur Uji Coba Utama
- Register akun produser dan aktor
- Produser login, buat jadwal
- Aktor login, join jadwal (status berubah menjadi `confirmed`)
- Aktor leave jadwal (jika tidak ada aktor lain, status kembali `available`)
- Produser tandai selesai (`completed`); jadwal tidak muncul di daftar tersedia aktor
- Jalankan `send_reminders` untuk membuat notifikasi H-1

## Catatan
- Untuk produksi, ganti `SECRET_KEY` dan matikan `DEBUG`.
- Tailwind via CDN digunakan untuk styling cepat.
# Syuting-management-system
