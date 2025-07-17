import streamlit as st
import json
import os
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
from pytz import timezone
from fpdf import FPDF

# Zona Waktu Indonesia
wib = timezone("Asia/Jakarta")

# File Data
DATA_FILE = "data_lomba.json"
USER_FILE = "users.json"
ACARA_FILE = "acara.json"
ABSEN_FILE = "absensi.json"
INVITE_FILE = "invite_codes.json"

if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["FIREBASE"]))
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://lomba-17an-default-rtdb.firebaseio.com/"
    })

# Session Init
if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.username = ""
if "login_error" not in st.session_state:
    st.session_state.login_error = ""
if "lupa_password" not in st.session_state:
    st.session_state.lupa_password = False
if "login_attempted" not in st.session_state:
    st.session_state.login_attempted = False
if "login_triggered" not in st.session_state:
    st.session_state.login_triggered = False

if not st.session_state.login_triggered:
    st.session_state.login_error = ""
    st.session_state.login_attempted = False
else:
    st.session_state.login_triggered = False

# Admin Akun Default
# Ambil data users dari Firebase
users_ref = db.reference("users")
users = users_ref.get() or {}

# Tambahkan admin jika belum ada
if "admin" not in users:
    users["admin"] = {
        "password": "merdeka45",
        "nama": "Administrator"
    }
    users_ref.set(users)

# Konversi akun admin lama jika masih dalam format string
if "admin" in users and isinstance(users["admin"], str):
    users["admin"] = {
        "password": users["admin"],
        "nama": "Administrator"
    }

# Pastikan semua user memiliki struktur dictionary
for uname, udata in list(users.items()):
    if isinstance(udata, str):
        users[uname] = {
            "password": udata,
             "nama": uname.capitalize()
        }

# Simpan hasil perbaikan kembali ke Firebase
users_ref.set(users)

def proses_login():
    user = st.session_state.get("login_user","").strip()
    pw = st.session_state.get("login_pass","").strip()
    st.session_state.login_triggered = True
    st.session_state.login_attempted = True
    if not user or not pw:
        st.session_state.login_error = "Username dan password tidak boleh kosong."
        return

    if user in users and users[user]["password"] == pw:
        st.session_state.login = True
        st.session_state.username = user
        st.session_state.login_error = ""
        st.session_state.login_attempted = False
    else:
        st.session_state.login_error = "Username atau password salah."

# Login/Register
st.title("🇮🇩Aplikasi Karang Taruna Bina Bhakti")
if not st.session_state.login:
    mode = st.selectbox("Pilih", ["Login", "Daftar Akun"])
    if mode == "Login":
        if not st.session_state.lupa_password:
            st.header("Login Anggota Karang Taruna")
            st.text_input("Username", key="login_user")
            st.text_input("Password", type="password", key="login_pass")
            user_input = st.session_state.get("login_user", "")
            pass_input = st.session_state.get("login_pass", "")
            st.button("Login", on_click=proses_login)
        
            if st.session_state.login_attempted and st.session_state.login_error:
                st.error(st.session_state.login_error)
                
            if st.button("Lupa Password?"):
                st.session_state.lupa_password = True
                st.rerun()
        else:
            st.header("Reset Password")
            lupa_nama = st.text_input("Nama Lengkap")
            username = st.text_input("Username")
            new_pw = st.text_input("Password Baru", type="password")

            if st.button("Reset Password"):
                if not lupa_nama or not username or not new_pw:
                    st.error("Semua kolom harus diisi.")
                elif username not in users:
                    st.error("Username tidak ditemukan.")
                elif users[username]["nama"].strip().lower() != lupa_nama.strip().lower():
                    st.error("Nama lengkap tidak cocok dengan data.")
                else:
                    users[username]["password"] = new_pw
                    save_json(USER_FILE, users)
                    st.success("Password berhasil direset. Silakan login kembali.")
                    st.session_state.lupa_password = False

            if st.button("Kembali ke Login"):
                st.session_state.lupa_password = False
                st.rerun()
        
    elif mode == "Daftar Akun":
        st.header("Daftar Akun Baru")
        full_name = st.text_input("Nama Lengkap")
        user = st.text_input("Username Baru (huruf kecil/angka tanpa spasi)")
        pw = st.text_input("Password Baru", type="password")
        kode = st.text_input("Kode Undangan")
        # Ambil data dari Firebase
        users_ref = db.reference("users")
        users = users_ref.get() or {}
        
        invite_ref = db.reference("invite")
        invite = invite_ref.get() or {"aktif": ""}

        if st.button("Daftar"):
            if not user or not pw or not kode:
                st.error("Semua kolom harus diisi.")
            elif not user.isalnum() or not user.islower() or " " in user:
                st.error("Username hanya boleh huruf kecil dan angka tanpa spasi.")
            elif user in users:
                st.error("Username sudah ada.")
            elif kode != invite["aktif"]:
                st.error("Kode undangan tidak valid.")
            else:
                users_ref.child(user).set({
                    "password": pw,
                    "nama": full_name
                })
                st.success("Akun berhasil dibuat. Silakan login.")
    st.stop()

def proses_logout():
    st.session_state.login = False
    st.session_state.username = ""
    st.session_state.login_error = False

# Sidebar: Logout + Admin Panel
st.sidebar.title(f"Hai, {users[st.session_state.username]['nama']}")
st.sidebar.button("Logout", on_click=proses_logout)

# Admin: Update Kode Undangan
if st.session_state.username == "admin":
    st.sidebar.title("Admin Panel")
    kode_baru = st.sidebar.text_input("Kode Undangan Baru")
    if st.sidebar.button("Perbarui Kode"):
        invite_ref = db.reference("invite")
        invite_ref.set({"aktif": kode_baru})
        st.sidebar.success("Kode diperbarui")

# Menu
menu = st.sidebar.selectbox("Menu", ["Manajemen Anggota", "Manajemen Lomba"])
# Manajemen Lomba
if menu == "Manajemen Lomba":
    
# Manajemen Anggota & Absensi
elif menu == "Manajemen Anggota":
    acara = load_json(ACARA_FILE, [])
    absen = load_json(ABSEN_FILE, {})

    if st.session_state.username == "admin":
        mode = st.selectbox("Pilih", ["Buat Acara", "Daftar Acara", "Kehadiran"])

        if mode == "Buat Acara":
            st.header("Buat Acara")
            judul = st.text_input("Judul Acara")
            waktu_str = st.text_input("Tanggal & Jam (dd-mm-yyyy hh:mm)")
            kode = st.text_input("Kode Absensi")

            if st.button("Simpan Acara"):
                try:
                    waktu = datetime.strptime(waktu_str, "%d-%m-%Y %H:%M")
                    acara.append({
                        "judul": judul,
                        "waktu": waktu.strftime("%d-%m-%Y %H:%M"),
                        "kode": kode
                    })
                    save_json(ACARA_FILE, acara)
                    st.success("Acara dibuat.")
                except:
                    st.error("Format waktu salah.")

        elif mode == "Daftar Acara":
            st.header("Filter Absensi Berdasarkan Tanggal")
            tgl_awal = st.date_input("Dari Tanggal")
            tgl_akhir = st.date_input("Sampai Tanggal")

            for i, ac in enumerate(acara):
                waktu_acara = datetime.strptime(ac["waktu"], "%d-%m-%Y %H:%M")
                if tgl_awal <= waktu_acara.date() <= tgl_akhir:
                    key = f"{ac['judul']} - {ac['waktu']}"
                    daftar = absen.get(key, [])

                    st.subheader(key)
                    st.write(f"Jumlah hadir: {len(daftar)}")
                    for username in daftar:
                        nama_lengkap = users.get(username, {}).get("nama", f"{username} (nama tidak ditemukan)")
                        st.write(f"✅ {nama_lengkap}")

                    # Tombol Edit & Hapus
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button("Edit", key=f"edit_{i}"):
                            st.session_state.editing_index = i
                    with col2:
                        # Di dalam loop acara:
                        if st.button("Hapus", key=f"hapus_{i}"):
                            st.session_state.hapus_index = i
                            st.rerun()

                        # Cek dan proses hapus di luar tombol
                        hapus_index = st.session_state.get("hapus_index", None)
                        if hapus_index is not None:
                            acara.pop(hapus_index)
                            save_json(ACARA_FILE, acara)
                            st.session_state.hapus_index = None
                            st.rerun()

                    # Form edit jika sedang diedit
                    if st.session_state.get("editing_index") == i:
                        st.markdown("**✏️ Edit Acara:**")

                        new_judul = st.text_input("Judul Baru", value=ac["judul"], key=f"judul_{i}")
                        new_waktu = st.text_input("Waktu Baru (dd-mm-yyyy hh:mm)", value=ac["waktu"], key=f"waktu_{i}")
                        new_kode = st.text_input("Kode Baru", value=ac["kode"], key=f"kode_{i}")

                        # Tampilkan error jika sebelumnya gagal
                        if st.session_state.get("edit_error") == i:
                            st.error("❌ Format waktu salah. Gunakan format: dd-mm-yyyy hh:mm.")

                        # Fungsi simpan — jangan panggil st.rerun() di sini
                        def simpan_perubahan():
                            try:
                                # Ambil data dari session_state
                                new_judul = st.session_state[f"judul_{i}"]
                                new_waktu = st.session_state[f"waktu_{i}"]
                                new_kode = st.session_state[f"kode_{i}"]

                                # Validasi waktu
                                datetime.strptime(new_waktu, "%d-%m-%Y %H:%M")

                                # Simpan perubahan
                                acara[i]["judul"] = new_judul
                                acara[i]["waktu"] = new_waktu
                                acara[i]["kode"] = new_kode
                                save_json(ACARA_FILE, acara)

                                st.session_state["edit_success"] = True
                                st.session_state["edit_success_index"] = i
                            except:
                                st.session_state["edit_error"] = i

                        # Tombol simpan — tanpa rerun di dalam fungsi
                        st.button("💾 Simpan Perubahan", key=f"simpan_{i}", on_click=simpan_perubahan)
                    # Jalankan rerun di luar callback
                    if st.session_state.get("edit_success"):
                        # Bersihkan state lalu rerun
                        del st.session_state["edit_success"]
                        del st.session_state["editing_index"]
                        if "edit_error" in st.session_state:
                            del st.session_state["edit_error"]
                        st.rerun()


        elif mode == "Kehadiran":
            st.header("Persentase Kehadiran")
            semua_user = [(u, users[u]["nama"]) for u in users if u != "admin"]
            total_acara = len(acara)
            for username, full_name in semua_user:
                hadir = sum(
                    username in absen.get(f"{a['judul']} - {a['waktu']}", [])
                    for a in acara
                )
            persen = (hadir / total_acara) * 100 if total_acara else 0
            st.write(f"{full_name} ({username}): {hadir}/{total_acara} hadir ({persen:.1f}%)")
    else:
        # Untuk user biasa (bukan admin): absen hari ini
        st.header("Absen Kehadiran Hari Ini")
        hari_ini = datetime.now(wib).strftime("%d-%m-%Y")
        aktif = [a for a in acara if a["waktu"].startswith(hari_ini)]

        if not aktif:
            st.info("Tidak ada acara hari ini.")
        else:
            pilihan = st.selectbox("Pilih Acara", [f"{a['judul']} - {a['waktu']}" for a in aktif])
            dipilih = next((a for a in aktif if f"{a['judul']} - {a['waktu']}" == pilihan), None)

            username = st.session_state.username
            full_name = users.get(username, {}).get("nama", "")
            st.text_input("Nama", value=full_name, disabled=True)
            kode_input = st.text_input("Masukkan Kode Absensi")

            if st.button("Absen"):
                if kode_input != dipilih["kode"]:
                    st.error("Kode salah.")
                else:
                    if pilihan not in absen:
                        absen[pilihan] = []
                    if st.session_state.username in absen[pilihan]:
                        st.warning("Sudah absen.")
                    else:
                        absen[pilihan].append(st.session_state.username)
                        save_json(ABSEN_FILE, absen)
                        st.success("Berhasil absen.")
