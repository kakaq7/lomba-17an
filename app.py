import streamlit as st
import json
import os
from datetime import datetime
from fpdf import FPDF
from pytz import timezone

# === Zona Waktu Indonesia ===
wib = timezone("Asia/Jakarta")

# === File Path ===
DATA_FILE = "data_lomba.json"
USER_FILE = "users.json"
ACARA_FILE = "acara.json"
ABSEN_FILE = "absensi.json"
INVITE_FILE = "invite_codes.json"

# === Load/Save ===
def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# === Session State ===
if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.username = ""

# === Akun Admin Default ===
users = load_json(USER_FILE, {})
if "admin" not in users:
    users["admin"] = "admin123"
    save_json(USER_FILE, users)

# === Login/Register ===
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
                st.success("Login berhasil. Silakan klik tombol Muat Ulang di browser Anda.")
                st.stop()
            else:
                st.error("Username atau password salah.")
    else:
        st.title("Daftar Akun Baru")
        user = st.text_input("Username Baru")
        pw = st.text_input("Password Baru", type="password")
        kode = st.text_input("Kode Undangan")
        invite = load_json(INVITE_FILE, {"aktif": []})
        if st.button("Daftar"):
            if user in users:
                st.error("Username sudah ada.")
            elif kode not in invite["aktif"]:
                st.error("Kode undangan tidak valid.")
            else:
                users[user] = pw
                save_json(USER_FILE, users)
                st.success("Akun berhasil dibuat.")
                st.stop()
    st.stop()

# === Setelah Login ===
st.sidebar.title("Selamat datang")
st.sidebar.write(f"👤 {st.session_state.username}")
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.success("Berhasil logout. Silakan refresh halaman.")
    st.stop()

# === Admin: Kode Undangan ===
if st.session_state.username == "admin":
    st.sidebar.title("Admin Panel")
    kode_baru = st.sidebar.text_input("Buat Kode Undangan Baru")
    if st.sidebar.button("Tambah Kode"):
        invites = load_json(INVITE_FILE, {"aktif": []})
        if kode_baru not in invites["aktif"]:
            invites["aktif"].append(kode_baru)
            save_json(INVITE_FILE, invites)
            st.sidebar.success("Kode ditambahkan")
        else:
            st.sidebar.warning("Kode sudah ada")

# === Menu Utama ===
menu = st.sidebar.selectbox("Menu", ["Manajemen Lomba", "Manajemen Anggota"])
st.title("Aplikasi Karang Taruna Bina Bhakti")

# === MANFA LOMBA ===
if menu == "Manajemen Lomba":
    data = load_json(DATA_FILE, {})
    st.header("📋 Tambah Lomba")
    nama = st.text_input("Nama Lomba Baru")
    if st.button("Tambah Lomba"):
        if nama in data:
            st.warning("Lomba sudah ada.")
        else:
            data[nama] = {"peserta": [], "pemenang": []}
            save_json(DATA_FILE, data)
            st.success("Lomba ditambahkan")

    if data:
        st.header("👥 Tambah Peserta & Juara")
        lomba = st.selectbox("Pilih Lomba", list(data.keys()))
        peserta = st.text_input("Nama Peserta")
        if st.button("Tambah Peserta"):
            if peserta not in data[lomba]["peserta"]:
                data[lomba]["peserta"].append(peserta)
                save_json(DATA_FILE, data)
                st.success("Peserta ditambahkan.")
            else:
                st.warning("Sudah terdaftar.")

        st.subheader("🏆 Tentukan Juara")
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

        st.header("📄 Lihat Juara & Download")
        for l, isi in data.items():
            if isi["pemenang"]:
                st.subheader(f"{l}")
                for i, p in enumerate(isi["pemenang"], 1):
                    st.write(f"Juara {i}: {p}")

        if st.button("Download PDF Juara"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Daftar Juara Lomba", ln=1, align="C")
            for l, isi in data.items():
                if isi["pemenang"]:
                    pdf.cell(200, 10, txt=f"Lomba: {l}", ln=1)
                    for i, p in enumerate(isi["pemenang"], 1):
                        pdf.cell(200, 10, txt=f"Juara {i}: {p}", ln=1)
            pdf.output("juara.pdf")
            with open("juara.pdf", "rb") as f:
                st.download_button("📥 Unduh PDF", f, file_name="juara.pdf")

# === MANFA ANGGOTA ===
if menu == "Manajemen Anggota":
    acara = load_json(ACARA_FILE, [])
    absen = load_json(ABSEN_FILE, {})

    if st.session_state.username == "admin":
        st.header("📅 Buat Acara")
        judul = st.text_input("Nama Acara")
        waktu_str = st.text_input("Tanggal & Jam (dd-mm-yyyy hh:mm)")
        kode = st.text_input("Kode Absensi")
        if st.button("Simpan Acara"):
            try:
                waktu = datetime.strptime(waktu_str, "%d-%m-%Y %H:%M")
                waktu_str_wib = waktu.strftime("%d-%m-%Y %H:%M")
                acara.append({"judul": judul, "waktu": waktu_str_wib, "kode": kode})
                save_json(ACARA_FILE, acara)
                st.success("Acara berhasil dibuat.")
            except:
                st.error("Format waktu salah.")

        st.header("📊 Daftar & Kelola Acara")
        if not acara:
            st.info("Belum ada acara.")
        else:
            for i, ac in enumerate(acara):
                key = f"{ac['judul']} - {ac['waktu']}"
                daftar = absen.get(key, [])
                st.subheader(key)
                if daftar:
                    for nama in daftar:
                        st.write(f"✅ {nama}")
                else:
                    st.write("❌ Belum ada yang absen")

                if st.button(f"✏️ Edit {key}"):
                    new_judul = st.text_input("Edit Nama Acara", value=ac["judul"], key=f"edit_judul_{i}")
                    new_waktu = st.text_input("Edit Tanggal & Jam (dd-mm-yyyy hh:mm)", value=ac["waktu"], key=f"edit_waktu_{i}")
                    new_kode = st.text_input("Edit Kode Absensi", value=ac["kode"], key=f"edit_kode_{i}")
                    if st.button(f"Simpan Perubahan {key}"):
                        acara[i] = {"judul": new_judul, "waktu": new_waktu, "kode": new_kode}
                        save_json(ACARA_FILE, acara)
                        st.success("Acara diperbarui.")
                        st.experimental_rerun()
                if st.button(f"🗑️ Hapus {key}"):
                    acara.pop(i)
                    save_json(ACARA_FILE, acara)
                    st.success("Acara dihapus.")
                    st.experimental_rerun()

    else:
        st.header("📍 Absensi Kehadiran")
        hari_ini = datetime.now(wib).strftime("%d-%m-%Y")
        aktif = [a for a in acara if a["waktu"].startswith(hari_ini)]
        if not aktif:
            st.info("Tidak ada acara hari ini.")
        else:
            pilihan = st.selectbox("Pilih Acara", [f'{a["judul"]} - {a["waktu"]}' for a in aktif])
            dipilih = next((a for a in aktif if f'{a["judul"]} - {a["waktu"]}' == pilihan), None)
            st.text_input("Nama", value=st.session_state.username, disabled=True)
            kode_input = st.text_input("Masukkan Kode Absensi")
            if st.button("Absen Sekarang"):
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
                        st.success("Absensi berhasil.")
