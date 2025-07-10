import streamlit as st
import json
import os
from fpdf import FPDF
from datetime import datetime

# ====== File Storage ======
ACCOUNT_FILE = "akun_karangtaruna.json"
INVITE_FILE = "invite_codes.json"
DATA_FILE = "data_lomba.json"
ABSENSI_FILE = "absensi_anggota.json"
ACARA_FILE = "daftar_acara.json"

# ====== Helpers ======
def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def load_accounts(): return load_json(ACCOUNT_FILE, {})
def save_accounts(data): save_json(ACCOUNT_FILE, data)
def load_invite_codes(): return load_json(INVITE_FILE, [])
def save_invite_codes(data): save_json(INVITE_FILE, data)
def load_data(): return load_json(DATA_FILE, {})
def save_data(data): save_json(DATA_FILE, data)
def load_absensi(): return load_json(ABSENSI_FILE, {})
def save_absensi(data): save_json(ABSENSI_FILE, data)
def load_acara(): return load_json(ACARA_FILE, [])
def save_acara(data): save_json(ACARA_FILE, data)

def is_acara_berlangsung(waktu_str):
    try:
        waktu = datetime.strptime(waktu_str, "%Y-%m-%d %H:%M")
        now = datetime.now()
        return waktu.date() == now.date()  # semua acara hari ini aktif
    except:
        return False

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Daftar Juara Lomba 17 Agustusan", ln=True, align="C")
    pdf.ln(5)
    ada = False
    for nama_lomba, info in data.items():
        if info.get("pemenang"):
            ada = True
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, f"Lomba: {nama_lomba}", ln=True)
            pdf.set_font("Arial", "", 11)
            for i, peserta in enumerate(info["pemenang"], 1):
                pdf.cell(0, 8, f"Juara {i}: {peserta}", ln=True)
            pdf.ln(4)
    if not ada:
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, "Belum ada lomba yang memiliki juara.", ln=True)
    file_path = "daftar_juara_lomba.pdf"
    pdf.output(file_path)
    return file_path

# ====== Session Login ======
if "login_success" not in st.session_state:
    st.session_state.login_success = False
if "username" not in st.session_state:
    st.session_state.username = ""

accounts = load_accounts()

if not st.session_state.login_success:
    menu_login = st.selectbox("Pilih Aksi", ["Login", "Daftar Akun Baru"])
    if menu_login == "Login":
        st.title("\U0001F512 Login Anggota Karang Taruna")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username in accounts and accounts[username] == password:
                st.session_state.login_success = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Username atau password salah")
        st.stop()
    else:
        st.title("\U0001F4DD Daftar Akun Baru")
        new_user = st.text_input("Buat Username")
        new_pass = st.text_input("Buat Password", type="password")
        invite_code = st.text_input("Kode Undangan")

        invite_codes = load_invite_codes()

        if st.button("Daftar"):
            if new_user in accounts:
                st.warning("Username sudah terdaftar.")
            elif not new_user or not new_pass or not invite_code:
                st.warning("Isi semua kolom.")
            elif invite_code not in invite_codes:
                st.error("Kode undangan tidak valid atau sudah digunakan.")
            else:
                accounts[new_user] = new_pass
                save_accounts(accounts)
                invite_codes.remove(invite_code)
                save_invite_codes(invite_codes)
                st.success("Akun berhasil dibuat. Silakan login.")
        st.stop()
else:
    st.sidebar.write(f"Hai, {st.session_state.username} \U0001F44B")
    if st.sidebar.button("\U0001F513 Logout"):
        st.session_state.clear()
        st.rerun()

    if st.session_state.username == "admin":
        st.sidebar.markdown("### \U0001F511 Buat Kode Undangan Baru")
        new_code = st.sidebar.text_input("Masukkan Kode Baru")
        if st.sidebar.button("Tambah Kode"):
            codes = load_invite_codes()
            if new_code in codes:
                st.sidebar.warning("Kode sudah ada.")
            elif new_code.strip() == "":
                st.sidebar.warning("Kode tidak boleh kosong.")
            else:
                codes.append(new_code)
                save_invite_codes(codes)
                st.sidebar.success(f"Kode '{new_code}' berhasil ditambahkan.")

# ====== Menu Utama ======
st.title("\U0001F1EE\U0001F1E9 Aplikasi Karang Taruna Bina Bhakti")
main_menu = st.sidebar.selectbox("Pilih Menu Utama", ["Manajemen Lomba", "Manajemen Anggota"])

# ====== Manajemen Anggota & Absensi ======
if main_menu == "Manajemen Anggota":
    absensi_data = load_absensi()
    acara_list = load_acara()

    if st.session_state.username == "admin":
        st.subheader("\U0001F4C5 Buat Acara Baru")
        nama_acara = st.text_input("Nama Acara")
        waktu_acara = st.text_input("Waktu Acara (format: YYYY-MM-DD HH:MM)")
        token_kode = st.text_input("Kode Unik Absensi")
        if st.button("➕ Simpan Acara"):
            try:
                datetime.strptime(waktu_acara, "%Y-%m-%d %H:%M")
                acara_list.append({"nama": nama_acara, "waktu": waktu_acara, "token": token_kode})
                save_acara(acara_list)
                st.success("Acara berhasil ditambahkan.")
            except:
                st.error("Format waktu salah. Gunakan YYYY-MM-DD HH:MM")
    else:
        st.subheader("✅ Absensi Kehadiran")

        # 🔍 DEBUG ACARA
        st.write("⏰ Debug sekarang:", datetime.now())
        for acara in acara_list:
            st.write(f"📅 Acara: {acara['nama']} - Waktu: {acara['waktu']} - Tampil: {is_acara_berlangsung(acara['waktu'])}")

        aktif = [a for a in acara_list if is_acara_berlangsung(a['waktu'])]
        if not aktif:
            st.info("Tidak ada acara yang sedang berlangsung hari ini.")
        else:
            selected = st.selectbox("Pilih Acara", [f"{a['nama']} ({a['waktu']})" for a in aktif])
            nama = st.text_input("Nama Anggota")
            kode = st.text_input("Masukkan Kode Absensi")
            acara_dipilih = next((a for a in aktif if f"{a['nama']} ({a['waktu']})" == selected), None)
            if st.button("✅ Absen Hadir"):
                if not kode or kode != acara_dipilih["token"]:
                    st.error("Kode absensi salah atau tidak valid.")
                else:
                    if selected not in absensi_data:
                        absensi_data[selected] = []
                    if nama in absensi_data[selected]:
                        st.warning(f"'{nama}' sudah absen di '{selected}'.")
                    else:
                        absensi_data[selected].append(nama)
                        save_absensi(absensi_data)
                        st.success(f"'{nama}' berhasil absen di '{selected}'.")

    st.markdown("### \U0001F4CB Daftar Kehadiran")
    for event, hadir in absensi_data.items():
        st.markdown(f"**{event}**")
        for orang in hadir:
            st.write(f"- {orang}")
