import streamlit as st
import json
import os
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

# Load/Save JSON
def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# Session Init
if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.username = ""

if st.session_state.get("rerun", False):
    st.session_state.rerun = False
    st.stop()

# Admin Akun Default
users = load_json(USER_FILE, {})
if "admin" not in users:
    users["admin"] = "admin123"
    save_json(USER_FILE, users)

# Login/Register
if not st.session_state.login:
    mode = st.selectbox("Pilih", ["Login", "Daftar Akun"])
    if mode == "Login":
        st.title("Login Karang Taruna")
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.button("Login"):
            if user in users and users[user] == pw:
                st.session_state.login = True
                st.session_state.username = user
                st.session_state.rerun = True
                st.stop()
            else:
                st.error("Username atau password salah.")
    else:
        st.title("Daftar Akun Baru")
        user = st.text_input("Username Baru")
        pw = st.text_input("Password Baru", type="password")
        kode = st.text_input("Kode Undangan")
        invite = load_json(INVITE_FILE, {"aktif": ""})
        if st.button("Daftar"):
            if user in users:
                st.error("Username sudah ada.")
            elif kode != invite["aktif"]:
                st.error("Kode undangan tidak valid.")
            else:
                users[user] = pw
                save_json(USER_FILE, users)
                st.success("Akun berhasil dibuat. Silakan login.")
    st.stop()

# Sidebar: Logout + Admin Panel
st.sidebar.title(f"Hai, {st.session_state.username}")
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.session_state.rerun = True
    st.stop()

# Admin: Update Kode Undangan
if st.session_state.username == "admin":
    st.sidebar.title("Admin Panel")
    kode_baru = st.sidebar.text_input("Kode Undangan Baru")
    if st.sidebar.button("Perbarui Kode"):
        invites = {"aktif": kode_baru}
        save_json(INVITE_FILE, invites)
        st.sidebar.success("Kode diperbarui")

# Menu
menu = st.sidebar.selectbox("Menu", ["Manajemen Lomba", "Manajemen Anggota"])
st.title("Aplikasi Karang Taruna Bina Bhakti")

# Manajemen Lomba
data = load_json(DATA_FILE, {})
if menu == "Manajemen Lomba":
    st.header("Tambah Lomba")
    nama = st.text_input("Nama Lomba")
    if st.button("Tambah Lomba"):
        if nama in data:
            st.warning("Lomba sudah ada.")
        else:
            data[nama] = {"peserta": [], "pemenang": []}
            save_json(DATA_FILE, data)
            st.success("Lomba ditambahkan.")

    if data:
        st.header("Tambah Peserta & Juara")
        lomba = st.selectbox("Pilih Lomba", list(data.keys()))
        peserta = st.text_input("Nama Peserta")
        if st.button("Tambah Peserta"):
            if peserta and peserta not in data[lomba]["peserta"]:
                data[lomba]["peserta"].append(peserta)
                save_json(DATA_FILE, data)
                st.success("Peserta ditambahkan.")

        st.subheader("Tentukan Juara")
        if data[lomba]["peserta"]:
            j1 = st.selectbox("Juara 1", data[lomba]["peserta"], key="j1")
            j2 = st.selectbox("Juara 2", data[lomba]["peserta"], key="j2")
            j3 = st.selectbox("Juara 3", data[lomba]["peserta"], key="j3")
            if st.button("Simpan Juara"):
                if len({j1, j2, j3}) < 3:
                    st.error("Juara tidak boleh sama.")
                else:
                    data[lomba]["pemenang"] = [j1, j2, j3]
                    save_json(DATA_FILE, data)
                    st.success("Juara disimpan.")

        st.header("Lihat Juara")
        for l, isi in data.items():
            if isi["pemenang"]:
                st.subheader(l)
                for i, p in enumerate(isi["pemenang"], 1):
                    st.write(f"Juara {i}: {p}")

        if st.button("Download PDF Juara"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, "Daftar Juara Lomba", ln=1, align="C")
            for l, isi in data.items():
                if isi["pemenang"]:
                    pdf.cell(200, 10, f"Lomba: {l}", ln=1)
                    for i, p in enumerate(isi["pemenang"], 1):
                        pdf.cell(200, 10, f"Juara {i}: {p}", ln=1)
            pdf.output("juara.pdf")
            with open("juara.pdf", "rb") as f:
                st.download_button("📥 Unduh PDF", f, file_name="juara.pdf")

# Manajemen Anggota & Absensi
elif menu == "Manajemen Anggota":
    acara = load_json(ACARA_FILE, [])
    absen = load_json(ABSEN_FILE, {})

    if st.session_state.username == "admin":
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
                st.session_state.rerun = True
                st.stop()
            except:
                st.error("Format waktu salah.")

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
                for nama in daftar:
                    st.write(f"✅ {nama}")

        st.header("Persentase Kehadiran")
        semua_user = [u for u in users if u != "admin"]
        total_acara = len(acara)
        for user in semua_user:
            hadir = sum(user in absen.get(f"{a['judul']} - {a['waktu']}", []) for a in acara)
            persen = (hadir / total_acara) * 100 if total_acara else 0
            st.write(f"{user}: {hadir}/{total_acara} hadir ({persen:.1f}%)")

    else:
        st.header("Absen Kehadiran Hari Ini")
        hari_ini = datetime.now(wib).strftime("%d-%m-%Y")
        aktif = [a for a in acara if a["waktu"].startswith(hari_ini)]
        if not aktif:
            st.info("Tidak ada acara hari ini.")
        else:
            pilihan = st.selectbox("Pilih Acara", [f"{a['judul']} - {a['waktu']}" for a in aktif])
            dipilih = next((a for a in aktif if f"{a['judul']} - {a['waktu']}" == pilihan), None)
            st.text_input("Nama", value=st.session_state.username, disabled=True)
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
